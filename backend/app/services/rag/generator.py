"""Генератор ответов — строит промпт и дергает LLM (Claude или GPT)."""

import asyncio

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Системный промпт — задает поведение ассистента
SYSTEM_PROMPT = (
    "You are a helpful AI support assistant. "
    "Answer questions based on the provided knowledge base context. "
    "If you cannot find the answer in the context, say so honestly. "
    "Always be professional and concise."
)

# Дополнение, если контекст не найден — ну бывает, честно скажем
NO_CONTEXT_SUFFIX = (
    "\n\nNo relevant context was found in the knowledge base. "
    "Let the user know you don't have enough information to answer their question."
)


def build_prompt(
    chunks: list[dict],
    conversation_history: list,
    question: str,
) -> list[dict]:
    """
    Собираем messages[] для LLM — system, контекст, историю и вопрос.

    Берем максимум 6 последних сообщений из истории (3 пары user/assistant).
    """
    system_content = SYSTEM_PROMPT

    if chunks:
        # Склеиваем контекст из чанков — каждый с указанием источника
        context_parts = []
        for chunk in chunks:
            context_parts.append(
                f"[Source: {chunk['document_name']}]\n{chunk['content']}"
            )
        context_text = "Context from knowledge base:\n\n" + "\n\n".join(context_parts)
        system_content += "\n\n" + context_text
    else:
        # Нет контекста — предупреждаем AI, чтоб не выдумывал
        system_content += NO_CONTEXT_SUFFIX

    messages = [{"role": "system", "content": system_content}]

    # История — берем последние 6 сообщений (3 пары), не больше
    recent_history = conversation_history[-6:]
    for msg in recent_history:
        messages.append({"role": msg.role, "content": msg.content})

    # И наконец сам вопрос
    messages.append({"role": "user", "content": question})

    return messages


async def generate_answer(messages: list[dict], model: str) -> str:
    """Диспатчер — выбирает, какой LLM дернуть, по имени модели."""
    if model == "claude":
        return await call_claude(messages)
    if model == "gpt":
        return await call_gpt(messages)

    # Если вдруг какая-то неизвестная модель — ну ладно, дадим Claude по дефолту
    logger.warning("unknown_model_fallback", requested_model=model, fallback="claude")
    return await call_claude(messages)


async def call_claude(messages: list[dict]) -> str:
    """
    Вызов Anthropic Claude API.

    У Claude своя специфика — system передается отдельным параметром,
    а не в массиве messages. Так что разделяем.
    """
    client = AsyncAnthropic(
        api_key=settings.anthropic_api_key,
        timeout=60.0,
    )

    # Отделяем system от остальных сообщений — Anthropic API так требует
    system_text = ""
    user_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_text += msg["content"]
        else:
            user_messages.append(msg)

    # Попытка с одним retry — если упало, ждем 2 секунды и пробуем ещe раз
    for attempt in range(2):
        try:
            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                system=system_text,
                messages=user_messages,
                temperature=0.1,
                max_tokens=2048,
            )
            answer = response.content[0].text

            logger.info(
                "claude_response_generated",
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            )

            return answer

        except Exception:
            if attempt == 0:
                logger.warning("claude_api_retry", attempt=attempt + 1)
                await asyncio.sleep(2)
            else:
                logger.error("claude_api_failed", attempt=attempt + 1)
                raise

    # Сюда не должны добраться, но на всякий случай — mypy будет доволен
    msg = "Claude API: все попытки исчерпаны"
    raise RuntimeError(msg)


async def call_gpt(messages: list[dict]) -> str:
    """
    Вызов OpenAI GPT API.

    Тут попроще — messages передаются как есть, system в массиве.
    """
    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=60.0,
    )

    # Тоже один retry — стандартная практика
    for attempt in range(2):
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.1,
                max_tokens=2048,
            )
            answer = response.choices[0].message.content or ""

            logger.info(
                "gpt_response_generated",
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
            )

            return answer

        except Exception:
            if attempt == 0:
                logger.warning("gpt_api_retry", attempt=attempt + 1)
                await asyncio.sleep(2)
            else:
                logger.error("gpt_api_failed", attempt=attempt + 1)
                raise

    # Аналогично — unreachable, но для порядка
    msg = "GPT API: все попытки исчерпаны"
    raise RuntimeError(msg)

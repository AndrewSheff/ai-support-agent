"""Скрипт для заполнения БД демо-данными — запускай через python -m scripts.seed из backend/."""

import asyncio
import uuid
from pathlib import Path

from sqlalchemy import func, select

from app.config import settings
from app.core.security import hash_password
from app.database import async_session
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.message import Message
from app.models.user import User

# Папка для загрузок — берем из настроек
UPLOAD_DIR = Path(settings.upload_dir)

# Демо-юзеры — три бойца для тестов
DEMO_USERS = [
    {"email": "john@company.com", "name": "John Smith", "role": "user"},
    {"email": "sarah@company.com", "name": "Sarah Johnson", "role": "user"},
    {"email": "mike@company.com", "name": "Mike Chen", "role": "user"},
]

# Демо-документы с реалистичным бизнес-контентом
DEMO_DOCUMENTS = [
    {
        "original_name": "HR Policy.txt",
        "file_type": "txt",
        "content": (
            "HR Policy Document\n"
            "==================\n\n"
            "1. Vacation Policy\n"
            "All full-time employees are entitled to 20 paid vacation days per year. "
            "Vacation days accrue at a rate of 1.67 days per month. Unused vacation days "
            "can be carried over to the next year, up to a maximum of 5 days. Vacation "
            "requests must be submitted at least 2 weeks in advance through the HR portal.\n\n"
            "2. Sick Leave\n"
            "Employees receive 10 paid sick days per year. Sick days do not carry over "
            "between years. If you are sick for more than 3 consecutive days, a doctor's "
            "note is required. Please notify your manager before 9:00 AM if you will be "
            "absent due to illness.\n\n"
            "3. Remote Work Policy\n"
            "Employees may work remotely up to 3 days per week with manager approval. "
            "Remote work days must be scheduled in advance and logged in the attendance "
            "system. During remote work, employees must be available during core hours "
            "(10:00 AM - 4:00 PM). A stable internet connection and a quiet workspace "
            "are required for remote work.\n\n"
            "4. Dress Code\n"
            "The company follows a business casual dress code. On Fridays, casual attire "
            "is permitted. When meeting with clients, business professional attire is expected."
        ),
    },
    {
        "original_name": "IT Security Guidelines.txt",
        "file_type": "txt",
        "content": (
            "IT Security Guidelines\n"
            "======================\n\n"
            "1. Password Policy\n"
            "All passwords must be at least 12 characters long and include uppercase letters, "
            "lowercase letters, numbers, and special characters. Passwords must be changed "
            "every 90 days. Do not reuse any of your last 5 passwords. Never share your "
            "password with anyone, including IT support.\n\n"
            "2. VPN Access\n"
            "To set up VPN access, download the FortiClient application from the IT portal. "
            "Use your corporate credentials to log in. VPN must be used when accessing "
            "company resources from outside the office network. Contact the IT helpdesk "
            "at it-support@company.com if you experience connection issues.\n\n"
            "3. Two-Factor Authentication (2FA)\n"
            "2FA is mandatory for all company accounts. Set up 2FA using the Google "
            "Authenticator app or hardware security keys. Backup codes should be stored "
            "securely in a password manager. If you lose access to your 2FA device, "
            "contact IT security immediately.\n\n"
            "4. Incident Reporting\n"
            "Report any security incidents immediately to security@company.com. This "
            "includes phishing emails, suspicious activity, lost devices, and unauthorized "
            "access attempts. Do not attempt to investigate security incidents on your own."
        ),
    },
    {
        "original_name": "Onboarding Guide.txt",
        "file_type": "txt",
        "content": (
            "New Employee Onboarding Guide\n"
            "=============================\n\n"
            "1. First Day Checklist\n"
            "- Pick up your laptop and badge from the IT desk (Room 101)\n"
            "- Complete the onboarding paperwork with HR (Room 205)\n"
            "- Set up your email and Slack accounts\n"
            "- Attend the welcome orientation at 2:00 PM in the Main Conference Room\n"
            "- Meet your buddy (assigned mentor for your first month)\n\n"
            "2. Tools Setup\n"
            "You will need the following tools configured in your first week:\n"
            "- Email: Outlook (credentials provided by IT)\n"
            "- Communication: Slack (join #general and your team channel)\n"
            "- Project Management: Jira (ask your team lead for project access)\n"
            "- Code Repository: GitHub (request access via IT portal)\n"
            "- Documentation: Confluence (same credentials as Jira)\n"
            "- VPN: FortiClient (see IT Security Guidelines)\n\n"
            "3. Team Introduction\n"
            "Your manager will schedule a series of 1-on-1 meetings with key team members "
            "during your first two weeks. These meetings are designed to help you understand "
            "the team structure, ongoing projects, and how your role fits in. Don't hesitate "
            "to ask questions — everyone remembers what it's like to be new!\n\n"
            "4. Training\n"
            "Complete the mandatory compliance training within your first 30 days. Training "
            "modules are available on the Learning Portal. Your manager will also assign "
            "role-specific training materials."
        ),
    },
]

# Демо-разговоры — реалистичные вопросы и ответы
DEMO_CONVERSATIONS = [
    {
        "title": "Vacation Policy",
        "messages": [
            {
                "role": "user",
                "content": "What is the vacation policy?",
            },
            {
                "role": "assistant",
                "content": (
                    "According to our HR Policy, all full-time employees are entitled to "
                    "20 paid vacation days per year. Here are the key details:\n\n"
                    "- Vacation days accrue at 1.67 days per month\n"
                    "- Up to 5 unused days can be carried over to the next year\n"
                    "- Requests must be submitted at least 2 weeks in advance through the HR portal\n\n"
                    "Is there anything else you'd like to know about our vacation policy?"
                ),
                "model": "claude-sonnet-4-20250514",
            },
        ],
    },
    {
        "title": "VPN Setup",
        "messages": [
            {
                "role": "user",
                "content": "How to set up VPN?",
            },
            {
                "role": "assistant",
                "content": (
                    "To set up VPN access, follow these steps:\n\n"
                    "1. Download the FortiClient application from the IT portal\n"
                    "2. Install and open the application\n"
                    "3. Log in using your corporate credentials\n\n"
                    "Remember that VPN must be used whenever you're accessing company resources "
                    "from outside the office network. If you run into any issues, reach out "
                    "to the IT helpdesk at it-support@company.com."
                ),
                "model": "claude-sonnet-4-20250514",
            },
        ],
    },
    {
        "title": "Dress Code",
        "messages": [
            {
                "role": "user",
                "content": "Where can I find the dress code?",
            },
            {
                "role": "assistant",
                "content": (
                    "The dress code information is in our HR Policy document. Here's a summary:\n\n"
                    "- **Regular days**: Business casual attire\n"
                    "- **Fridays**: Casual attire is permitted\n"
                    "- **Client meetings**: Business professional attire is expected\n\n"
                    "If you need more specific guidance, feel free to ask your manager or HR."
                ),
                "model": "claude-sonnet-4-20250514",
            },
        ],
    },
    {
        "title": "Sick Leave",
        "messages": [
            {
                "role": "user",
                "content": "How many sick days do I get?",
            },
            {
                "role": "assistant",
                "content": (
                    "You receive **10 paid sick days per year**. Here are the important details:\n\n"
                    "- Sick days do not carry over between years\n"
                    "- If you're sick for more than 3 consecutive days, you'll need a doctor's note\n"
                    "- Please notify your manager before 9:00 AM if you'll be absent\n\n"
                    "Let me know if you have any other questions about our leave policies!"
                ),
                "model": "claude-sonnet-4-20250514",
            },
        ],
    },
    {
        "title": "Password Requirements",
        "messages": [
            {
                "role": "user",
                "content": "What's the password requirements?",
            },
            {
                "role": "assistant",
                "content": (
                    "Our IT Security Guidelines specify the following password requirements:\n\n"
                    "- **Minimum length**: 12 characters\n"
                    "- **Must include**: uppercase letters, lowercase letters, numbers, and special characters\n"
                    "- **Rotation**: Passwords must be changed every 90 days\n"
                    "- **History**: Cannot reuse any of your last 5 passwords\n"
                    "- **Never share** your password with anyone, including IT support\n\n"
                    "Additionally, Two-Factor Authentication (2FA) is mandatory for all accounts."
                ),
                "model": "claude-sonnet-4-20250514",
            },
        ],
    },
    {
        "title": "Remote Work",
        "messages": [
            {
                "role": "user",
                "content": "Can I work from home? What are the rules?",
            },
            {
                "role": "assistant",
                "content": (
                    "Yes, remote work is available! Here are the rules from our HR Policy:\n\n"
                    "- You can work remotely **up to 3 days per week** with manager approval\n"
                    "- Remote work days must be scheduled in advance and logged in the attendance system\n"
                    "- You must be available during **core hours (10:00 AM - 4:00 PM)**\n"
                    "- A stable internet connection and quiet workspace are required\n\n"
                    "Talk to your manager to get started with remote work arrangements."
                ),
                "model": "claude-sonnet-4-20250514",
            },
        ],
    },
]

# Размер вектора для эмбеддингов — 1536 (как у OpenAI ada-002)
EMBEDDING_DIM = 1536


async def main() -> None:
    """Главная функция — заполняет БД демо-данными. Идемпотентно, повторный запуск не ломает."""
    async with async_session() as session:
        # Проверяем, есть ли уже юзеры — если да, значит сид уже был
        user_count_result = await session.execute(select(func.count()).select_from(User))
        user_count = user_count_result.scalar_one()

        if user_count > 0:
            print("Database already seeded, skipping.")
            return

        print("Seeding database with demo data...")

        # --- 1. Создаем админа ---
        admin_password_hash = hash_password(settings.admin_default_password)
        admin_user = User(
            email=settings.admin_email,
            name=settings.admin_name,
            password_hash=admin_password_hash,
            role="admin",
            is_active=True,
        )
        session.add(admin_user)
        print(f"  + Admin: {settings.admin_email}")

        # --- 2. Создаем обычных юзеров ---
        created_users: list[User] = []
        default_password_hash = hash_password("Password123")

        for user_data in DEMO_USERS:
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                password_hash=default_password_hash,
                role=user_data["role"],
                is_active=True,
            )
            session.add(user)
            created_users.append(user)
            print(f"  + User: {user_data['email']}")

        # Флашим чтобы получить ID юзеров и админа
        await session.flush()

        # --- 3. Создаем документы ---
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        for doc_data in DEMO_DOCUMENTS:
            # Генерим уникальное имя файла для хранения
            file_id = uuid.uuid4()
            stored_filename = f"{file_id}.txt"
            file_path = UPLOAD_DIR / stored_filename

            # Пишем реальный файл на диск
            file_content = doc_data["content"]
            file_path.write_text(file_content, encoding="utf-8")
            file_size = file_path.stat().st_size

            # Создаем запись в БД
            document = Document(
                filename=stored_filename,
                original_name=doc_data["original_name"],
                file_type=doc_data["file_type"],
                file_size=file_size,
                status="indexed",
                chunk_count=3,
                uploaded_by=admin_user.id,
            )
            session.add(document)
            await session.flush()

            # Создаем мок-чанки с нулевыми эмбеддингами (для демо хватит)
            paragraphs = [p.strip() for p in file_content.split("\n\n") if p.strip()]
            # Берем максимум 3 чанка — по одному на смысловой блок
            chunk_texts = paragraphs[:3] if len(paragraphs) >= 3 else paragraphs
            zero_embedding = [0.0] * EMBEDDING_DIM

            for chunk_index, chunk_text in enumerate(chunk_texts):
                chunk = DocumentChunk(
                    document_id=document.id,
                    content=chunk_text,
                    chunk_index=chunk_index,
                    embedding=zero_embedding,
                    metadata_={"source": doc_data["original_name"], "chunk": chunk_index},
                )
                session.add(chunk)

            print(f"  + Document: {doc_data['original_name']} ({len(chunk_texts)} chunks)")

        # --- 4. Создаем разговоры с сообщениями ---
        for i, conv_data in enumerate(DEMO_CONVERSATIONS):
            # Распределяем разговоры между юзерами (по кругу)
            assigned_user = created_users[i % len(created_users)]

            conversation = Conversation(
                user_id=assigned_user.id,
                title=conv_data["title"],
            )
            session.add(conversation)
            await session.flush()

            for msg_data in conv_data["messages"]:
                message = Message(
                    conversation_id=conversation.id,
                    role=msg_data["role"],
                    content=msg_data["content"],
                    model=msg_data.get("model"),
                )
                session.add(message)

            print(f"  + Conversation: \"{conv_data['title']}\" ({assigned_user.name})")

        # Коммитим все разом
        await session.commit()
        print("\nDone! Database seeded successfully.")


if __name__ == "__main__":
    asyncio.run(main())

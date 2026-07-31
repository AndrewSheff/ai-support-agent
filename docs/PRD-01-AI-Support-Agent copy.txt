# PRD-01: AI Support Agent

## Product Requirements Document

**Версия**: 2.0
**Дата**: 2026-07-31
**Статус**: Draft
**Проект**: Repository 1 / AI Support Agent

---

## 1. Описание продукта

AI Support Agent — это корпоративная веб-платформа для создания внутреннего AI-ассистента компании. Платформа позволяет загружать документы компании (регламенты, инструкции, FAQ, базы знаний), после чего сотрудники могут задавать вопросы в чате и получать точные ответы на основе загруженных документов с указанием источников.

Система использует RAG (Retrieval-Augmented Generation) для поиска релевантных фрагментов документов и генерации ответов через LLM (Claude или GPT). Администратор управляет базой знаний, пользователями и видит аналитику использования.

**Ключевые характеристики**:
- Self-hosted (данные остаются внутри компании)
- Поддержка нескольких LLM-провайдеров (Anthropic Claude, OpenAI GPT)
- RAG с указанием источников в каждом ответе
- Ролевая модель (admin / user)
- Деплой одной командой через Docker Compose

---

## 2. Цель продукта

Показать потенциальным клиентам, что разработчик способен создать production-ready enterprise AI-систему с полным стеком: авторизация, RAG-пайплайн, чат в реальном времени, админ-панель, Docker-деплой. Это главный проект портфолио, демонстрирующий экспертизу в AI-интеграции.

---

## 3. Бизнес-задача

Компании тратят 2-5 часов в день на поиск информации во внутренних документах. HR отвечает на одни и те же вопросы. Новые сотрудники неделями ищут нужные регламенты. AI Support Agent сокращает время поиска информации с часов до секунд, снижает нагрузку на HR/support и ускоряет онбординг.

---

## 4. Целевая аудитория

- **Основная**: компании от 50 до 500 сотрудников с большим объемом внутренней документации
- **Покупатели**: CTO, VP of Engineering, Head of IT в средних компаниях
- **Пользователи**: все сотрудники компании (задают вопросы), HR/support (снижается нагрузка), администраторы (управляют системой)

---

## 5. Почему за это платят деньги

- Экономия 2-5 часов в день на каждого сотрудника при поиске информации
- Снижение нагрузки на HR/support на 40-60%
- Ускорение онбординга новых сотрудников в 3-5 раз
- Единая точка доступа к знаниям компании вместо разрозненных документов
- Ответы с указанием источников — доверие к AI
- Self-hosted решение — данные остаются внутри компании (compliance, GDPR)

---

## 6. Анализ аналогов

| Продукт | Цена | Плюсы | Минусы |
|---------|------|-------|--------|
| Glean | $10/user/mo | Enterprise search, интеграции | Дорого, SaaS only, нет self-hosted |
| Guru | $15/user/mo | Knowledge base, AI answers | Нет RAG, ограниченный AI |
| Danswer (open source) | Free | Open source, self-hosted | Сложная настройка, нет UI для бизнеса |
| CustomGPT | $99/mo | Простая настройка | SaaS only, нет контроля данных |
| ChatBot.com | $52/mo | Простой UI | Нет RAG, правила вместо AI |

**Наше преимущество**: self-hosted, полный контроль данных, простая установка через Docker, поддержка нескольких LLM-провайдеров, красивый современный UI, open-source.

---

## 7. MVP

MVP включает:

1. Регистрация и вход (JWT)
2. Чат с AI-ассистентом
3. История разговоров
4. Загрузка документов (PDF, DOCX, TXT)
5. RAG: поиск по документам и генерация ответов с источниками
6. Выбор AI-модели (Claude / GPT)
7. Админ-панель: управление пользователями, документами, просмотр статистики
8. Docker-деплой одной командой

---

## 8. Возможности после MVP

- Streaming ответов (SSE)
- Интеграция с Slack/Teams
- Webhooks для внешних систем
- Мультиязычность UI
- SSO (SAML/OIDC)
- Feedback на ответы (thumbs up/down) с обучением
- Автоматическая переиндексация при обновлении документов
- API для внешних интеграций
- Экспорт разговоров
- Кастомные промпты для разных отделов

---

## 9. Полный User Flow

### Flow 1: Первый запуск (Admin)
```
Открыть приложение → Страница входа → Ввести email/пароль администратора по умолчанию →
→ Принудительная смена пароля → Dashboard (пустой) → Перейти в Documents →
→ Загрузить первые документы → Дождаться индексации → Перейти в Chat →
→ Задать тестовый вопрос → Получить ответ с источниками → Убедиться что работает →
→ Перейти в Users → Создать пользователей
```

### Flow 2: Обычный пользователь
```
Открыть приложение → Страница входа → Ввести email/пароль →
→ Chat (главный экран) → Ввести вопрос → Получить ответ с источниками →
→ Продолжить диалог или начать новый → Посмотреть историю →
→ Открыть старый разговор → Продолжить
```

### Flow 3: Администратор управляет документами
```
Dashboard → Documents → Upload Document → Выбрать файлы →
→ Загрузка и прогресс → Статус: Processing → Статус: Indexed →
→ Документ доступен для поиска
```

### Flow 4: Администратор управляет пользователями
```
Dashboard → Users → Add User → Заполнить форму (email, name, role) →
→ Пользователь создан → Может изменить роль / деактивировать / удалить
```

---

## 10. User Stories

### Аутентификация
- US-01: Как пользователь, я хочу войти по email и паролю, чтобы получить доступ к системе
- US-02: Как пользователь, я хочу выйти из системы, чтобы защитить свой аккаунт
- US-03: Как администратор при первом входе, я хочу сменить пароль по умолчанию

### Чат
- US-04: Как пользователь, я хочу задать вопрос в чате и получить ответ на основе документов компании
- US-05: Как пользователь, я хочу видеть источники (название документа, страница), чтобы проверить ответ
- US-06: Как пользователь, я хочу вести многоходовый диалог, чтобы уточнять вопросы
- US-07: Как пользователь, я хочу начать новый разговор, чтобы сменить тему
- US-08: Как пользователь, я хочу выбрать AI-модель (Claude / GPT) для ответов
- US-09: Как пользователь, я хочу видеть, что AI "печатает" ответ (индикатор загрузки)

### История
- US-10: Как пользователь, я хочу видеть список моих прошлых разговоров
- US-11: Как пользователь, я хочу открыть прошлый разговор и продолжить его
- US-12: Как пользователь, я хочу удалить разговор
- US-13: Как пользователь, я хочу искать по своим разговорам

### Документы (Admin)
- US-14: Как администратор, я хочу загружать документы (PDF, DOCX, TXT)
- US-15: Как администратор, я хочу видеть статус обработки документа
- US-16: Как администратор, я хочу удалить документ из базы знаний
- US-17: Как администратор, я хочу видеть список всех документов с метаданными

### Пользователи (Admin)
- US-18: Как администратор, я хочу создавать пользователей
- US-19: Как администратор, я хочу деактивировать пользователя
- US-20: Как администратор, я хочу менять роль пользователя
- US-21: Как администратор, я хочу видеть список всех пользователей

### Dashboard (Admin)
- US-22: Как администратор, я хочу видеть общую статистику
- US-23: Как администратор, я хочу видеть график активности за последние 30 дней
- US-24: Как администратор, я хочу видеть топ-5 самых частых вопросов

---

## 11. Все экраны приложения

1. **Login** — страница входа
2. **Change Password** — принудительная смена пароля (первый вход)
3. **Chat** — основной экран чата (для всех пользователей)
4. **Dashboard** — панель администратора со статистикой
5. **Documents** — управление документами (admin)
6. **Users** — управление пользователями (admin)
7. **Settings** — настройки профиля пользователя
8. **404** — страница не найдена

---

## 12. Детальное описание каждого экрана

### 12.1 Login Page

**URL**: `/login`
**Доступ**: только неавторизованные пользователи. Если пользователь авторизован (есть валидный токен в localStorage), автоматический redirect на `/chat` (role=user) или `/dashboard` (role=admin).

**Layout**:
- Весь экран — фон `bg-slate-50`
- Центрированная карточка (shadcn Card) шириной 400px
- Карточка с `shadow-lg`, `rounded-xl`, белый фон
- Вертикальный отступ от верха — `mt-[20vh]` (20% высоты экрана)

**Содержимое карточки** (сверху вниз, padding 32px):

1. **Логотип** (центрирован):
   - Иконка `Bot` из lucide-react, размер 40px, цвет `text-primary`
   - Под ней текст "AI Support Agent", шрифт `text-2xl font-bold`, цвет `text-slate-900`
   - Подзаголовок "Sign in to your account", `text-sm text-slate-500`
   - Отступ снизу: 32px

2. **Форма** (вертикальный стек, gap 16px):
   - **Email field**:
     - Label: "Email" (`text-sm font-medium text-slate-700`)
     - Input: type="email", placeholder="you@company.com", shadcn Input
     - При ошибке валидации: красная рамка (`border-red-500`), текст ошибки под полем (`text-sm text-red-500`)
   - **Password field**:
     - Label: "Password"
     - Input: type="password", placeholder="Enter your password", shadcn Input
     - Иконка глаза справа внутри поля для показа/скрытия пароля (`Eye` / `EyeOff` из lucide)
     - При ошибке: аналогично email
   - **Кнопка Sign In**:
     - Ширина 100% (`w-full`)
     - shadcn Button variant="default" (primary цвет)
     - Текст: "Sign In"
     - Высота: 40px
     - Отступ сверху: 8px

3. **Сообщение об ошибке** (между формой и кнопкой, появляется при ошибке):
   - shadcn Alert variant="destructive"
   - Иконка `AlertCircle`
   - Текст ошибки: "Invalid email or password" или "Account is deactivated"
   - Анимация появления: fade-in 200ms

4. **Футер** (центрирован, под карточкой):
   - Текст "Powered by AI Support Agent", `text-xs text-slate-400`
   - Отступ сверху: 24px

**Состояния экрана**:

| Состояние | Что происходит |
|-----------|---------------|
| Default | Пустая форма, кнопка активна |
| Typing | Пользователь вводит данные, валидация при blur |
| Submitting | Кнопка disabled, вместо текста — Spinner (lucide Loader2, анимация spin), текст "Signing in..." |
| Error (credentials) | Alert "Invalid email or password", поля НЕ очищаются, пароль очищается |
| Error (deactivated) | Alert "Your account has been deactivated. Contact administrator." |
| Error (network) | Alert "Connection error. Please try again." |
| Success | Redirect на /chat или /dashboard (без промежуточного состояния) |

**Валидация**:
- Email: required, формат email (regex). Ошибка при blur: "Please enter a valid email"
- Password: required, минимум 1 символ. Ошибка при blur: "Password is required"
- Кнопка disabled, пока оба поля пустые
- Submit по нажатию Enter в любом поле

**Keyboard**:
- Tab: Email → Password → Sign In
- Enter: submit формы (из любого поля)
- Автофокус на поле Email при загрузке страницы

---

### 12.2 Change Password Page

**URL**: `/change-password`
**Доступ**: только авторизованные пользователи с `must_change_password = true`. Если `must_change_password = false` — redirect на `/chat` или `/dashboard`. Если не авторизован — redirect на `/login`.

**Layout**: идентичен Login (центрированная карточка 400px на `bg-slate-50`)

**Содержимое карточки** (padding 32px):

1. **Заголовок** (центрирован):
   - Иконка `Shield` из lucide, 40px, `text-amber-500`
   - Текст "Change Your Password", `text-2xl font-bold`
   - Подзаголовок "Please set a new password to continue", `text-sm text-slate-500`
   - Отступ снизу: 32px

2. **Форма** (gap 16px):
   - **New Password**:
     - Label: "New Password"
     - Input: type="password", placeholder="Enter new password"
     - Иконка глаза для показа/скрытия
   - **Confirm Password**:
     - Label: "Confirm Password"
     - Input: type="password", placeholder="Confirm new password"
     - Иконка глаза для показа/скрытия
   - **Требования к паролю** (под полями, всегда видны):
     - Список с иконками (Check зеленый если соблюдено, X красный если нет):
     - "At least 8 characters" — проверять в реальном времени
     - "Contains a letter" — проверять в реальном времени
     - "Contains a number" — проверять в реальном времени
   - **Кнопка "Update Password"**: w-full, primary, 40px

**Состояния**:

| Состояние | Описание |
|-----------|----------|
| Default | Пустая форма, индикаторы требований красные |
| Typing | Индикаторы требований обновляются в реальном времени |
| Passwords mismatch | Под Confirm Password: "Passwords do not match" (красный), только после blur на Confirm |
| All valid | Все индикаторы зеленые, пароли совпадают, кнопка активна |
| Submitting | Spinner в кнопке, "Updating..." |
| Error | Alert destructive с текстом ошибки |
| Success | Toast (sonner) "Password updated successfully", redirect на /chat или /dashboard через 1 сек |

**Валидация**:
- New Password: мин 8 символов, мин 1 буква, мин 1 цифра
- Confirm Password: должен совпадать с New Password
- Кнопка disabled, пока все требования не соблюдены и пароли не совпадают
- Submit по Enter

---

### 12.3 Chat Page (главный экран)

**URL**: `/chat` (без активного разговора), `/chat/:conversationId` (с активным разговором)
**Доступ**: все авторизованные пользователи (admin и user)

**Layout**: двухколоночный
```
┌─────────────────────────────────────────────────────────────────┐
│ [Sidebar 280px]  │         [Main Content Area]                  │
│                  │                                               │
│  ┌────────────┐  │  ┌─────────────────────────────────────────┐ │
│  │ New Chat   │  │  │                                         │ │
│  ├────────────┤  │  │        Message Area                     │ │
│  │ Search     │  │  │        (scrollable)                     │ │
│  ├────────────┤  │  │                                         │ │
│  │            │  │  │                                         │ │
│  │ Conver-    │  │  │                                         │ │
│  │ sation     │  │  │                                         │ │
│  │ List       │  │  │                                         │ │
│  │            │  │  │                                         │ │
│  │            │  │  ├─────────────────────────────────────────┤ │
│  ├────────────┤  │  │  [Model] [         Input          ][>] │ │
│  │ User Menu  │  │  └─────────────────────────────────────────┘ │
│  └────────────┘  │                                               │
└─────────────────────────────────────────────────────────────────┘
```

#### 12.3.1 Sidebar (левая панель)

**Размеры**: ширина 280px, высота 100vh, фон `bg-slate-900`, цвет текста `text-slate-100`
**Расположение**: фиксированная, слева
**Граница**: `border-r border-slate-800`

**Элементы** (сверху вниз):

1. **Кнопка "New Chat"** (верх sidebar, padding 16px):
   - shadcn Button variant="outline" с `border-slate-700 text-slate-100 hover:bg-slate-800`
   - Ширина 100%
   - Иконка `Plus` (lucide) слева, текст "New Chat"
   - Высота: 40px
   - onClick: создать новый разговор (POST /conversations), перейти на `/chat/:newId`

2. **Поле поиска** (под кнопкой, padding 0 16px):
   - Input с иконкой `Search` слева внутри поля
   - Placeholder: "Search conversations..."
   - Фон: `bg-slate-800`, рамка: `border-slate-700`
   - Поиск: фильтрация списка разговоров по title на клиенте (debounce 300ms)
   - Если поиск активен и ничего не найдено: текст "No conversations found" в списке
   - Кнопка `X` справа в поле для очистки (появляется только когда есть текст)

3. **Список разговоров** (scrollable, flex-1, overflow-y-auto):
   - Отступ сверху: 8px
   - Если разговоры есть, группировка по датам:
     - "Today" — разговоры за сегодня
     - "Yesterday" — за вчера
     - "Previous 7 Days" — за неделю
     - "Previous 30 Days" — за месяц
     - "Older" — старше месяца
   - Заголовок группы: `text-xs font-semibold text-slate-500 uppercase`, padding `px-4 py-2`
   - **Каждый элемент разговора**:
     - Padding: `px-4 py-3`
     - Курсор: pointer
     - Hover: `bg-slate-800`
     - Active (текущий разговор): `bg-slate-800 border-l-2 border-primary`
     - Первая строка: title (усечение ellipsis, max 1 строка), `text-sm font-medium text-slate-100`
     - Вторая строка: превью последнего сообщения (усечение, max 1 строка), `text-xs text-slate-400`
     - При hover — справа появляется кнопка `Trash2` (иконка, 16px, `text-slate-500 hover:text-red-400`)
     - Клик на элемент: переход на `/chat/:id`, загрузка сообщений
     - Клик на Trash2: модальное окно подтверждения удаления (см. раздел "Модальные окна")

4. **User Menu** (низ sidebar, padding 16px, border-top `border-slate-800`):
   - Фиксирован внизу sidebar
   - Аватар: кружок 32px с первой буквой имени, фон `bg-primary`, белый текст
   - Рядом: имя пользователя (`text-sm font-medium`), под ним роль (`text-xs text-slate-400`, "Admin" или "User")
   - Справа от имени: кнопка `LogOut` (иконка, `text-slate-400 hover:text-red-400`)
   - Клик на LogOut: удаление токена из localStorage, redirect на `/login`

**Sidebar на мобильных (<768px)**:
- Sidebar скрыта по умолчанию
- В Header (верх main area) появляется кнопка-гамбургер `Menu` (иконка, слева)
- Клик на гамбургер: sidebar выезжает слева поверх контента (overlay `bg-black/50`)
- Клик на overlay или на разговор: sidebar закрывается
- Анимация: slide-in 200ms ease-out

#### 12.3.2 Main Content Area

**Размеры**: `margin-left: 280px`, на мобильных — `margin-left: 0`
**Фон**: `bg-white`
**Flex**: column, height 100vh

##### Состояние: Нет активного разговора (Welcome Screen)

URL: `/chat`

**Содержимое** (центрировано по вертикали и горизонтали):
- Иконка `MessageSquare` из lucide, 48px, `text-slate-300`
- Текст "How can I help you today?", `text-2xl font-semibold text-slate-700`, margin-top 16px
- Подтекст "Ask me anything about your company's documents", `text-sm text-slate-500`, margin-top 8px
- **3 карточки-примера** (горизонтально, gap 16px, margin-top 32px):
  - Каждая: shadcn Card, ширина 200px, padding 16px, `hover:shadow-md cursor-pointer hover:border-primary transition-all`
  - Иконка сверху: `FileText` / `HelpCircle` / `BookOpen`, 24px, `text-primary`
  - Текст: конкретный пример вопроса, `text-sm text-slate-600`, 2 строки max
  - Примеры:
    1. "How do I submit a vacation request?"
    2. "What is the company's remote work policy?"
    3. "Where can I find the onboarding checklist?"
  - Клик на карточку: создать новый разговор, отправить этот вопрос как первое сообщение
- На мобильных: карточки вертикально (stack), ширина 100%

**Input Area** (всегда видна, низ экрана, даже на Welcome Screen):
- Контейнер: padding `px-4 py-4`, border-top `border-slate-200`, фон `bg-white`
- Максимальная ширина контента: 768px, центрировано
- **Model Selector** (слева от input):
  - shadcn Select, ширина 120px
  - Опции: "Claude" (default), "GPT"
  - Иконка `Sparkles` перед текстом
  - Значение сохраняется в localStorage между сессиями
- **Text Input** (центр):
  - shadcn Textarea, flex-1
  - Placeholder: "Type your message..."
  - min-height: 40px, max-height: 120px (auto-resize)
  - Resize: none (авторесайз по контенту)
  - Border-radius: 20px (pill shape)
  - Padding: `px-4 py-2`
- **Send Button** (справа от input):
  - Круглая кнопка 40px
  - Иконка `SendHorizontal` (lucide)
  - variant="default" (primary цвет)
  - Disabled: когда input пустой (только whitespace) или идет отправка
  - Стиль disabled: `opacity-50 cursor-not-allowed`

**Keyboard для Input**:
- `Enter`: отправить сообщение
- `Shift+Enter`: новая строка
- `Ctrl+Enter` / `Cmd+Enter`: отправить (альтернатива)
- При пустом поле Enter ничего не делает

##### Состояние: Активный разговор

URL: `/chat/:conversationId`

**Message Area** (scrollable, flex-1):
- `overflow-y-auto`, padding `px-4 py-6`
- Максимальная ширина сообщений: 768px, центрировано (`mx-auto`)
- Сообщения идут сверху вниз
- При загрузке — автоскролл к последнему сообщению
- При новом сообщении — автоскролл к нему (smooth scroll)
- Если пользователь проскроллил вверх больше чем на 200px — в правом нижнем углу появляется кнопка "scroll to bottom" (круглая, иконка `ChevronDown`, shadow)

**Каждое сообщение пользователя**:
- Группа: flex, gap 12px
- Аватар слева: кружок 32px, первая буква имени, `bg-slate-200 text-slate-600`
- Контент справа от аватара:
  - Имя: "You", `text-sm font-semibold text-slate-900`
  - Время: `text-xs text-slate-400`, формат "2:30 PM" (через 8px после имени, на той же строке)
  - Текст сообщения: `text-sm text-slate-700`, margin-top 4px, white-space: pre-wrap
- Отступ снизу: 24px

**Каждое сообщение AI**:
- Группа: flex, gap 12px
- Аватар слева: кружок 32px, иконка `Bot`, `bg-primary text-white`
- Контент справа от аватара:
  - Имя: "AI Assistant", `text-sm font-semibold text-slate-900`
  - Модель: badge после имени, `text-xs`, зеленый для Claude, синий для GPT (текст: "Claude" или "GPT")
  - Время: `text-xs text-slate-400`
  - Текст ответа: `text-sm text-slate-700`, margin-top 4px
  - Рендеринг markdown в ответе: заголовки, списки, bold, italic, code blocks (react-markdown + remark-gfm)
  - Code blocks: фон `bg-slate-100`, моноширинный шрифт, border-radius 8px, padding 12px
  - **Блок Sources** (если есть, под текстом ответа):
    - Margin-top: 12px
    - Заголовок: "Sources", `text-xs font-semibold text-slate-500 uppercase`, иконка `FileText` слева
    - Список источников (вертикальный, gap 4px):
      - Каждый источник: pill badge, `bg-slate-100 text-slate-600 text-xs px-3 py-1 rounded-full`
      - Текст: "{document_name}" (без page number — упрощение для MVP)
      - Tooltip при hover: "Relevance: {score}%" (показать relevance_score * 100)
      - Не кликабельные (документы нельзя скачивать из чата — только из Documents page)
- Отступ снизу: 24px

**Индикатор загрузки (AI typing)**:
- Появляется сразу после отправки сообщения пользователя
- Аватар AI + имя "AI Assistant"
- Вместо текста: 3 анимированных точки (bouncing dots animation, CSS)
- Текст под точками: "Thinking..." в `text-xs text-slate-400`
- Исчезает, когда приходит ответ от API

**Состояния Message Area**:

| Состояние | Описание |
|-----------|----------|
| Loading conversation | По центру: Spinner + "Loading conversation..." |
| Empty conversation | Текст "Start a conversation by typing a message below" по центру |
| Messages loaded | Лента сообщений |
| Sending message | Сообщение пользователя появляется сразу (optimistic), индикатор typing для AI |
| AI error | Вместо ответа AI — сообщение с красным фоном `bg-red-50`, иконка `AlertTriangle`: текст ошибки ("AI service is temporarily unavailable. Please try again."), кнопка "Retry" (отправить тот же вопрос повторно) |
| No documents | AI отвечает: "I don't have any documents to search through. Please ask an administrator to upload documents." (обычное сообщение AI, не ошибка) |
| Conversation not found | Redirect на `/chat` + toast "Conversation not found" |
| Network error | Toast (sonner): "Connection error. Please check your internet." |

---

### 12.4 Dashboard Page

**URL**: `/dashboard`
**Доступ**: только admin. Если role=user — redirect на `/chat`.

**Layout**:
- AppLayout с Sidebar (см. навигация)
- Контентная область с padding `p-8`
- Максимальная ширина контента: 1200px

**Содержимое** (сверху вниз):

1. **Header** (flex, justify-between, align-center):
   - Заголовок: "Dashboard", `text-2xl font-bold text-slate-900`
   - **Period Selector** (справа): shadcn ToggleGroup (3 кнопки):
     - "Today" | "7 Days" | "30 Days"
     - Default: "30 Days"
     - При переключении: все данные на странице обновляются

2. **Stat Cards** (grid 4 колонки, gap 16px, margin-top 24px):
   - На планшетах (<1024px): grid 2 колонки
   - На мобильных (<768px): grid 1 колонка

   Каждая карточка — shadcn Card, padding 24px:

   | Карточка | Иконка | Значение | Доп. инфо |
   |----------|--------|----------|-----------|
   | Total Users | `Users` (lucide), bg-blue-100 text-blue-600, circle 40px | Число (text-3xl font-bold) | "N active" (text-sm text-slate-500) |
   | Documents | `FileText`, bg-green-100 text-green-600 | Число | "N indexed" |
   | Conversations | `MessageSquare`, bg-purple-100 text-purple-600 | Число | За выбранный период |
   | Questions Today | `HelpCircle`, bg-amber-100 text-amber-600 | Число | "+N% vs previous" (зеленый если рост, красный если падение, иконка TrendingUp/TrendingDown) |

3. **Activity Chart** (margin-top 24px):
   - shadcn Card, padding 24px
   - Заголовок: "Activity", `text-lg font-semibold`
   - Линейный график (библиотека: recharts)
   - Ось X: даты (формат: "Jul 1", "Jul 2", ...)
   - Ось Y: количество вопросов
   - Линия: цвет primary, толщина 2px
   - Заливка под линией: primary с opacity 0.1
   - Tooltip при hover: "Jul 15: 22 questions"
   - Высота графика: 300px
   - Responsive: на мобильных высота 200px

4. **Нижний ряд** (grid 2 колонки, gap 16px, margin-top 24px):
   - На мобильных: grid 1 колонка

   **Top Questions** (левая колонка):
   - shadcn Card, padding 24px
   - Заголовок: "Top Questions", `text-lg font-semibold`
   - Таблица (shadcn Table):
     - Columns: "#" (40px), "Question" (flex-1), "Count" (80px, right-aligned)
     - 5 строк максимум
     - Нумерация: 1-5
     - Question: усечение ellipsis если длинный
     - Count: badge с числом, `bg-slate-100`

   **Recent Conversations** (правая колонка):
   - shadcn Card, padding 24px
   - Заголовок: "Recent Conversations", `text-lg font-semibold`
   - Список (5 элементов max):
     - Каждый элемент: flex, gap 12px, padding-y 8px, border-bottom
     - Аватар пользователя (кружок 32px, первая буква)
     - Имя пользователя (`text-sm font-medium`)
     - Превью вопроса (`text-sm text-slate-500`, усечение 1 строка)
     - Время (`text-xs text-slate-400`, формат: "2h ago", "Yesterday")

**Состояния**:

| Состояние | Описание |
|-----------|----------|
| Loading | Skeleton loaders: 4 карточки (прямоугольники с пульсацией), график (пульсирующий прямоугольник 300px), таблицы (5 строк скелетонов) |
| Loaded | Данные отображены |
| Empty (новый проект) | Карточки показывают 0, график — прямая линия на 0, таблицы — empty state "No data yet" |
| Error | Toast "Failed to load dashboard data" + кнопка Retry в каждой карточке |
| Period change | Все компоненты показывают skeleton на 200ms (или до загрузки данных) |

---

### 12.5 Documents Page

**URL**: `/documents`
**Доступ**: только admin

**Layout**:
- AppLayout с Sidebar
- Контентная область, padding `p-8`
- Максимальная ширина: 1200px

**Содержимое**:

1. **Header** (flex, justify-between, align-center):
   - Заголовок: "Documents", `text-2xl font-bold`
   - Кнопка "Upload Document": shadcn Button, иконка `Upload` слева, variant="default"

2. **Upload Zone** (появляется при клике на "Upload Document", margin-top 16px):
   - shadcn Card с dashed border (`border-2 border-dashed border-slate-300`)
   - Padding: 40px
   - Центрированный контент:
     - Иконка `CloudUpload`, 48px, `text-slate-400`
     - Текст: "Drag & drop files here", `text-lg font-medium text-slate-600`
     - Подтекст: "or click to browse", `text-sm text-slate-400`
     - Подтекст: "Supported: PDF, DOCX, TXT (max 50MB)", `text-xs text-slate-400`, margin-top 8px
   - Вся зона кликабельна (открывает file picker)
   - Drag over: `border-primary bg-primary/5`, текст "Drop files here" (меняется)
   - Accept: `.pdf, .docx, .txt`
   - Multiple: да (можно загрузить несколько файлов за раз)
   - После выбора файлов зона закрывается, файлы загружаются

3. **Upload Progress** (под upload zone, если есть активные загрузки):
   - Для каждого загружаемого файла:
     - Flex row: иконка типа файла (FileText для PDF, FileSpreadsheet для DOCX, FileCode для TXT), имя файла, размер, progress bar, процент
     - Progress bar: shadcn Progress, высота 4px
     - Статусы:
       - Uploading: синий progress bar, "Uploading... 45%"
       - Processing: желтый pulsating bar, "Processing..."
       - Indexed: зеленый, иконка Check, "Indexed"
       - Error: красный, иконка X, текст ошибки

4. **Filter Bar** (flex, gap 8px, margin-top 24px):
   - shadcn Tabs (4 tab-а): "All" | "Indexed" | "Processing" | "Error"
   - Каждый таб показывает count в badge: "All (42)", "Indexed (40)", "Processing (1)", "Error (1)"
   - Default: "All"

5. **Documents Table** (margin-top 16px):
   - shadcn Table

   | Column | Ширина | Описание |
   |--------|--------|----------|
   | Name | flex-1, min 200px | Иконка типа файла + original_name. Усечение ellipsis |
   | Type | 80px | Badge: "PDF" (bg-red-100 text-red-700), "DOCX" (bg-blue-100 text-blue-700), "TXT" (bg-slate-100 text-slate-700) |
   | Size | 100px | Формат: "245 KB", "1.2 MB", "15.4 MB" |
   | Status | 120px | Badge: "Indexed" (bg-green-100 text-green-700), "Processing" (bg-yellow-100 text-yellow-700, с pulsating dot animation), "Error" (bg-red-100 text-red-700) |
   | Chunks | 80px | Число чанков (только для indexed), "-" для processing/error |
   | Uploaded | 120px | Относительное время: "2h ago", "Yesterday", "Jul 15" |
   | Actions | 60px | Кнопка-иконка Trash2 (красная при hover) |

   - Строки: hover `bg-slate-50`
   - Сортировка: по умолчанию по дате (newest first), кликабельные заголовки колонок для сортировки
   - Error row: при hover на статус "Error" — tooltip с текстом ошибки (`error_message`)

6. **Пагинация** (под таблицей, margin-top 16px):
   - shadcn Pagination
   - 20 элементов на страницу
   - Показывается если total > 20
   - Текст: "Showing 1-20 of 42 documents"

**Состояния**:

| Состояние | Описание |
|-----------|----------|
| Loading | Skeleton table: 5 строк скелетонов |
| Empty (нет документов) | Центрированный empty state: иконка `FileText` 64px text-slate-300, "No documents yet", "Upload your first document to get started", кнопка "Upload Document" |
| Documents loaded | Таблица с данными |
| Uploading | Progress bars над таблицей |
| Delete confirmation | Модальное окно (см. "Модальные окна") |
| Error loading | Toast "Failed to load documents" + кнопка Retry |

---

### 12.6 Users Page

**URL**: `/users`
**Доступ**: только admin

**Layout**: AppLayout, padding `p-8`, max-width 1200px

**Содержимое**:

1. **Header**:
   - Заголовок: "Users", `text-2xl font-bold`
   - Кнопка "Add User": shadcn Button, иконка `UserPlus` слева

2. **Users Table** (margin-top 24px):
   - shadcn Table

   | Column | Ширина | Описание |
   |--------|--------|----------|
   | User | flex-1, min 200px | Аватар (кружок 32px, буква) + Name + Email под именем (text-sm text-slate-500) |
   | Role | 100px | shadcn Select inline: "Admin" / "User". Для текущего пользователя — disabled с tooltip "Cannot change own role" |
   | Status | 100px | Toggle switch: зеленый = Active, серый = Inactive. Для текущего пользователя — disabled с tooltip "Cannot deactivate yourself" |
   | Created | 120px | Дата: "Jul 15, 2026" |
   | Actions | 60px | Кнопка Trash2 (красная при hover). Для текущего пользователя — скрыта |

   - Строки: hover `bg-slate-50`
   - Сортировка: по дате создания (newest first)
   - Текущий пользователь (определяется по ID из JWT): строка с `bg-primary/5` и пометкой "(you)" после имени

3. **Пагинация**: 20 на страницу (аналогично Documents)

**Изменение роли** (inline в таблице):
- Клик на Select → выбор роли → сразу PATCH запрос
- При успехе: toast "Role updated"
- При ошибке: toast "Failed to update role", Select откатывается к прежнему значению

**Изменение статуса** (inline toggle):
- Клик на toggle → сразу PATCH запрос
- При деактивации: модальное окно подтверждения "Deactivate user {name}? They will not be able to log in." Кнопки: "Cancel" / "Deactivate" (destructive)
- При активации: без подтверждения, сразу PATCH
- При успехе: toast "User {activated/deactivated}"
- При ошибке: toast "Failed to update user", toggle откатывается

**Удаление** (кнопка Trash2):
- Модальное окно подтверждения (см. "Модальные окна")

**Состояния**:

| Состояние | Описание |
|-----------|----------|
| Loading | Skeleton table: 5 строк |
| Empty | "No users found" (маловероятно — всегда есть admin) |
| Loaded | Таблица с данными |
| Error | Toast "Failed to load users" + Retry |

---

### 12.7 Settings Page

**URL**: `/settings`
**Доступ**: все авторизованные пользователи

**Layout**: AppLayout, padding `p-8`, max-width 600px (центрировано)

**Содержимое** (вертикальный стек, gap 32px):

1. **Заголовок**: "Settings", `text-2xl font-bold`

2. **Profile Section** (shadcn Card, padding 24px):
   - Заголовок карточки: "Profile", `text-lg font-semibold`
   - **Name field**:
     - Label: "Name"
     - Input: text, текущее имя, editable
     - Валидация: required, 2-100 символов
   - **Email field**:
     - Label: "Email"
     - Input: text, текущий email, `disabled`, `bg-slate-50 text-slate-500`
     - Подпись: "Email cannot be changed", `text-xs text-slate-400`
   - **Role field**:
     - Label: "Role"
     - Badge: "Admin" или "User", не редактируемый
   - **Кнопка "Save Changes"**:
     - variant="default", disabled если имя не изменилось
     - При сохранении: PATCH /api/v1/users/{me}/profile (специальный эндпоинт)
     - Успех: toast "Profile updated"
     - Ошибка: toast с текстом ошибки

3. **Change Password Section** (shadcn Card, padding 24px):
   - Заголовок: "Change Password", `text-lg font-semibold`
   - **Current Password**: type="password", иконка глаза
   - **New Password**: type="password", иконка глаза
   - **Confirm New Password**: type="password", иконка глаза
   - **Требования к паролю** (аналогично Change Password Page):
     - "At least 8 characters"
     - "Contains a letter"
     - "Contains a number"
   - **Кнопка "Update Password"**:
     - variant="default"
     - Disabled пока не заполнены все поля и требования не соблюдены
     - Успех: toast "Password updated", все поля очищаются
     - Ошибка: inline alert "Invalid current password"

---

### 12.8 Not Found Page (404)

**URL**: любой несуществующий URL
**Доступ**: все

**Layout**:
- Если авторизован: AppLayout с Sidebar
- Если не авторизован: полный экран без sidebar

**Содержимое** (центрировано по вертикали и горизонтали):
- Текст "404" — `text-6xl font-bold text-slate-200`
- Текст "Page Not Found" — `text-xl font-semibold text-slate-600`, margin-top 8px
- Текст "The page you're looking for doesn't exist." — `text-sm text-slate-400`, margin-top 4px
- Кнопка "Go to Chat": shadcn Button variant="default", margin-top 24px, onClick navigate(`/chat`)

---

## 13. Навигация

### Sidebar Navigation (внутри AppLayout)

Sidebar навигация — это вертикальный список ссылок в Sidebar, расположенный между кнопкой "New Chat" / поиском и User Menu. На Chat Page навигация встроена в Chat Sidebar. На остальных страницах — отдельная sidebar.

**Для страниц Dashboard, Documents, Users, Settings** — используется отдельная Sidebar:

**Layout Sidebar (не Chat)**:
- Ширина: 280px, фон `bg-white`, border-right `border-slate-200`
- Верхняя часть: логотип "AI Support Agent" (иконка Bot + текст, padding 20px)
- Навигационные ссылки (vertical stack, padding 8px):

| Ссылка | Иконка | URL | Доступ |
|--------|--------|-----|--------|
| Chat | `MessageSquare` | /chat | Все |
| Dashboard | `LayoutDashboard` | /dashboard | admin |
| Documents | `FileText` | /documents | admin |
| Users | `Users` | /users | admin |
| Settings | `Settings` | /settings | Все |

- Каждая ссылка: padding `px-4 py-2.5`, border-radius 8px, `text-sm font-medium`
- Default: `text-slate-600 hover:bg-slate-100`
- Active (текущая страница): `bg-primary/10 text-primary font-semibold`
- Admin-only пункты не рендерятся для role=user (не скрываются CSS, а не рендерятся вообще)

- Нижняя часть (аналогично Chat Sidebar): User Menu

### Redirects

| Условие | Откуда | Куда |
|---------|--------|------|
| Не авторизован | Любая protected страница | /login |
| Авторизован | /login | /chat (user) или /dashboard (admin) |
| must_change_password=true | Любая страница | /change-password |
| role=user | /dashboard, /documents, /users | /chat |
| Авторизован, страница не существует | * | 404 page |

### URL Structure

| URL | Страница | Доступ |
|-----|----------|--------|
| /login | Login | Public |
| /change-password | Change Password | Auth + must_change_password |
| /chat | Chat (welcome) | Auth |
| /chat/:id | Chat (conversation) | Auth (owner only) |
| /dashboard | Dashboard | Admin |
| /documents | Documents | Admin |
| /users | Users | Admin |
| /settings | Settings | Auth |
| /* | 404 | All |

---

## 14. Модальные окна

### 14.1 Подтверждение удаления разговора

**Триггер**: клик на Trash2 в списке разговоров (Chat Sidebar)

- shadcn AlertDialog
- Overlay: `bg-black/50`
- Карточка: ширина 400px, padding 24px, centered
- **Заголовок**: "Delete Conversation"
- **Описание**: "Are you sure you want to delete '{conversation_title}'? This action cannot be undone."
- **Кнопки** (flex, justify-end, gap 8px):
  - "Cancel": variant="outline", onClick: закрыть модалку
  - "Delete": variant="destructive" (красная), onClick: DELETE /conversations/{id}
- **Состояния**:
  - Default: обе кнопки активны
  - Deleting: "Delete" disabled, spinner + "Deleting...", "Cancel" disabled
  - Success: модалка закрывается, разговор убирается из списка, toast "Conversation deleted", если был открыт — redirect на /chat
  - Error: toast "Failed to delete conversation", модалка закрывается
- Закрытие: Escape, клик на overlay, кнопка Cancel
- Focus trap: да (фокус не уходит за пределы модалки)

### 14.2 Подтверждение удаления документа

**Триггер**: клик на Trash2 в таблице документов

- shadcn AlertDialog (аналогично 14.1)
- **Заголовок**: "Delete Document"
- **Описание**: "Are you sure you want to delete '{document_name}'? All indexed data from this document will be removed from the knowledge base."
- **Кнопки**: "Cancel" / "Delete" (destructive)
- **Состояния**: аналогично 14.1
- Success: документ убирается из таблицы, toast "Document deleted", пагинация пересчитывается

### 14.3 Подтверждение удаления пользователя

**Триггер**: клик на Trash2 в таблице пользователей

- shadcn AlertDialog
- **Заголовок**: "Delete User"
- **Описание**: "Are you sure you want to delete user '{user_name}' ({user_email})? All their conversations will be permanently deleted."
- **Кнопки**: "Cancel" / "Delete" (destructive)
- **Состояния**: аналогично 14.1
- Success: пользователь убирается из таблицы, toast "User deleted"

### 14.4 Подтверждение деактивации пользователя

**Триггер**: клик на toggle Active→Inactive в таблице пользователей

- shadcn AlertDialog
- **Заголовок**: "Deactivate User"
- **Описание**: "Are you sure you want to deactivate '{user_name}'? They will not be able to log in."
- **Кнопки**: "Cancel" / "Deactivate" (variant="destructive")
- Success: toggle переключается, toast "User deactivated"
- При активации (Inactive→Active): без модалки, сразу PATCH

### 14.5 Модальное окно создания пользователя

**Триггер**: клик на "Add User" на странице Users

- shadcn Dialog (не AlertDialog — это форма, не подтверждение)
- Overlay: `bg-black/50`
- Карточка: ширина 480px, padding 24px
- **Заголовок**: "Add New User"
- **Форма** (vertical stack, gap 16px):

  | Поле | Тип | Placeholder | Валидация |
  |------|-----|-------------|-----------|
  | Name | text | "Full name" | Required, 2-100 символов |
  | Email | email | "user@company.com" | Required, формат email, уникальность (проверяется при submit) |
  | Role | Select | — | "User" (default) / "Admin" |

- **Кнопки** (flex, justify-end, gap 8px):
  - "Cancel": variant="outline"
  - "Create User": variant="default"
- **Валидация**:
  - При blur: проверка полей
  - Name: "Name is required" / "Name must be between 2 and 100 characters"
  - Email: "Email is required" / "Invalid email format"
  - Кнопка Create disabled пока форма невалидна
- **Состояния**:
  - Default: пустая форма, Create disabled
  - Valid: все поля заполнены корректно, Create enabled
  - Submitting: Create disabled, spinner + "Creating..."
  - Error (duplicate email): inline alert под email: "User with this email already exists"
  - Error (network): toast "Failed to create user"
  - **Success**: модалка меняет содержимое (НЕ закрывается):
    - Иконка Check в зеленом кружке (64px, центрировано)
    - Текст "User Created Successfully"
    - Блок с credentials (фон `bg-slate-50`, padding 16px, border-radius 8px):
      - "Email: user@company.com"
      - "Temporary Password: aB3dEf7h" (моноширинный шрифт, `font-mono`)
      - Кнопка "Copy Password" рядом с паролем (иконка Copy, при клике иконка меняется на Check на 2 секунды, копирует в clipboard)
    - Предупреждение: иконка AlertTriangle + "This password will only be shown once. Make sure to copy it.", `text-sm text-amber-600`
    - Кнопка "Done": variant="default", w-full, закрывает модалку
  - При закрытии модалки после создания: пользователь добавляется в таблицу (refetch)

### 14.6 Нет других модальных окон

Все остальные действия (изменение роли, настройки, и т.д.) выполняются inline, без модалок.

---

## 15. Все уведомления (Toast)

Используется библиотека `sonner` (toast notifications).

**Позиция**: bottom-right
**Длительность**: 4 секунды (auto-dismiss)
**Максимум одновременных**: 3 (новые вытесняют старые)
**Стиль**: shadcn-совместимый (рамка, тень)

### Полный список всех toast-уведомлений

#### Аутентификация
| Событие | Тип | Текст |
|---------|-----|-------|
| Login success | Нет toast (redirect) | — |
| Login error (credentials) | Нет toast (inline alert) | — |
| Login error (network) | Нет toast (inline alert) | — |
| Logout | success | "You have been logged out" |
| Password changed | success | "Password updated successfully" |
| Password change error | error | "Failed to update password" |
| Session expired (401) | warning | "Your session has expired. Please log in again." |

#### Чат
| Событие | Тип | Текст |
|---------|-----|-------|
| Conversation deleted | success | "Conversation deleted" |
| Delete conversation error | error | "Failed to delete conversation" |
| AI service error | Нет toast (inline в чате) | — |
| Network error при отправке | error | "Failed to send message. Please try again." |
| Conversation not found | error | "Conversation not found" |

#### Документы
| Событие | Тип | Текст |
|---------|-----|-------|
| Upload started | info | "Uploading {filename}..." |
| Upload complete | success | "{filename} uploaded successfully" |
| Upload error (type) | error | "Unsupported file type: {ext}. Allowed: PDF, DOCX, TXT" |
| Upload error (size) | error | "{filename} is too large. Maximum file size is 50MB." |
| Upload error (network) | error | "Failed to upload {filename}" |
| Upload error (duplicate) | error | "Document '{name}' already exists" |
| Document indexed | success | "{filename} has been indexed ({N} chunks)" |
| Document processing error | error | "Failed to process {filename}: {error_message}" |
| Document deleted | success | "Document deleted" |
| Delete document error | error | "Failed to delete document" |

#### Пользователи
| Событие | Тип | Текст |
|---------|-----|-------|
| User created | Нет toast (inline в модалке) | — |
| Create user error | error | "Failed to create user" |
| Role updated | success | "Role updated to {role}" |
| Role update error | error | "Failed to update role" |
| User activated | success | "User activated" |
| User deactivated | success | "User deactivated" |
| Status update error | error | "Failed to update user status" |
| User deleted | success | "User deleted" |
| Delete user error | error | "Failed to delete user" |
| Cannot self-delete | warning | "You cannot delete your own account" |
| Cannot self-deactivate | warning | "You cannot deactivate your own account" |

#### Настройки
| Событие | Тип | Текст |
|---------|-----|-------|
| Profile updated | success | "Profile updated" |
| Profile update error | error | "Failed to update profile" |

#### Общие
| Событие | Тип | Текст |
|---------|-----|-------|
| Network error (global) | error | "Connection error. Please check your internet." |
| Rate limited | warning | "Too many requests. Please wait a moment." |
| Server error (500) | error | "Something went wrong. Please try again later." |
| Clipboard copy | success | "Copied to clipboard" |

---

## 16. Полная архитектура приложения

```
┌─────────────────────────────────────────────────────────┐
│                        Client                           │
│  React + TypeScript + Vite + TailwindCSS + shadcn/ui    │
│  React Query (server state) + React Router (routing)    │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS
                        ▼
┌─────────────────────────────────────────────────────────┐
│                     Nginx (Reverse Proxy)                │
│              Static files + API proxy                    │
│              Port 80 (HTTP)                              │
└──────────┬────────────────────────────┬─────────────────┘
           │ /api/*                     │ /*
           ▼                            ▼
┌─────────────────────┐    ┌──────────────────────────────┐
│   FastAPI Backend    │    │    React SPA (static files)  │
│   Port 8000          │    └──────────────────────────────┘
│                      │
│  ┌────────────────┐  │
│  │   Auth Layer   │  │
│  │   (JWT)        │  │
│  ├────────────────┤  │
│  │   API Routes   │  │
│  ├────────────────┤  │
│  │   Services     │  │
│  ├────────────────┤  │
│  │   RAG Engine   │  │
│  ├────────────────┤  │
│  │   Models (ORM) │  │
│  └────────────────┘  │
└──────┬──────┬────────┘
       │      │
       ▼      ▼
┌──────────┐ ┌──────────┐   ┌──────────────┐
│PostgreSQL│ │  Redis   │   │  LLM APIs    │
│+ pgvector│ │ (cache)  │   │  (Anthropic, │
│Port 5432 │ │Port 6379 │   │   OpenAI)    │
└──────────┘ └──────────┘   └──────────────┘
```

**Nginx routing**:
- `/ ` → frontend static files (React SPA)
- `/api/*` → proxy_pass http://backend:8000
- `/docs` → proxy_pass http://backend:8000/docs (Swagger UI)
- SPA fallback: все неизвестные пути → index.html (для client-side routing)

---

## 17. Архитектура Backend

**Паттерн**: Router → Service → Model (SQLAlchemy ORM)

- **Routers** (`api/v1/`): HTTP-логика, парсинг запроса, валидация Pydantic, формирование ответа. Нет бизнес-логики.
- **Services** (`services/`): бизнес-логика, оркестрация. Работают с моделями напрямую через SQLAlchemy session.
- **Models** (`models/`): SQLAlchemy ORM модели. Маппинг на таблицы БД.
- **Schemas** (`schemas/`): Pydantic v2 модели. Request/response валидация и сериализация.
- **Core** (`core/`): security (JWT, hashing), exceptions, logging.
- **Tasks** (`tasks/`): фоновые задачи (обработка документов через FastAPI BackgroundTasks).

**Dependency Injection** (FastAPI Depends):
- `get_db()` → AsyncSession (SQLAlchemy async session)
- `get_current_user()` → User model (из JWT токена)
- `require_admin()` → User model (проверяет role=admin, 403 если нет)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, lifespan, middleware, CORS
│   ├── config.py                  # Pydantic Settings (из .env)
│   ├── database.py                # SQLAlchemy async engine, sessionmaker, get_db
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # get_current_user, require_admin, get_db
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Главный router, включает все sub-routers
│   │       ├── auth.py            # POST /login, POST /change-password
│   │       ├── chat.py            # CRUD /conversations, POST /messages
│   │       ├── documents.py       # CRUD /documents
│   │       ├── users.py           # CRUD /users
│   │       ├── dashboard.py       # GET /dashboard/*
│   │       └── health.py          # GET /health
│   │
│   ├── models/
│   │   ├── __init__.py            # Импорт всех моделей (для Alembic autogenerate)
│   │   ├── base.py                # DeclarativeBase с общими полями
│   │   ├── user.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── document.py
│   │   └── document_chunk.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                # LoginRequest, LoginResponse, ChangePasswordRequest
│   │   ├── chat.py                # ConversationCreate/Response, MessageCreate/Response
│   │   ├── document.py            # DocumentResponse, DocumentListResponse
│   │   ├── user.py                # UserCreate/Update/Response
│   │   ├── dashboard.py           # StatsResponse, ActivityResponse, TopQuestionsResponse
│   │   └── common.py              # PaginatedResponse (generic)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py        # authenticate, change_password, create_admin
│   │   ├── chat_service.py        # CRUD conversations, send_message
│   │   ├── document_service.py    # upload, list, delete
│   │   ├── user_service.py        # CRUD users
│   │   ├── dashboard_service.py   # get_stats, get_activity, get_top_questions
│   │   └── rag/
│   │       ├── __init__.py
│   │       ├── embeddings.py      # generate_embedding (OpenAI API)
│   │       ├── retriever.py       # search_similar_chunks (pgvector query)
│   │       ├── generator.py       # generate_answer (Claude/GPT API call)
│   │       └── processor.py       # parse_document, chunk_text, process_document
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py            # create_access_token, verify_token, hash_password, verify_password
│   │   ├── exceptions.py          # AppException, NotFoundError, ForbiddenError, handlers
│   │   └── logging.py             # structlog setup, request_id middleware
│   │
│   └── tasks/
│       ├── __init__.py
│       └── document_tasks.py      # process_document_task (background)
│
├── alembic/
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # fixtures: test_db, test_client, auth headers
│   ├── test_auth.py
│   ├── test_chat.py
│   ├── test_documents.py
│   ├── test_users.py
│   └── test_rag.py
│
├── uploads/                       # .gitignore'd, created at startup
├── requirements.txt
├── requirements-dev.txt
└── Dockerfile
```

---

## 18. Архитектура Frontend

**State Management**:
- Серверное состояние: React Query (TanStack Query v5). Кеш, автоматическая инвалидация, рефетч при focus.
- Auth state: React Context (`AuthContext`). Хранит: token, user object, isAuthenticated, isAdmin.
- UI state: локальный useState в компонентах.

**Routing**: React Router v6 с layout routes.

```
frontend/
├── src/
│   ├── main.tsx                   # ReactDOM.createRoot, providers
│   ├── App.tsx                    # Router setup, route definitions
│   │
│   ├── api/
│   │   ├── client.ts              # Axios instance, baseURL, interceptors (401 → logout)
│   │   ├── auth.ts                # login(), changePassword()
│   │   ├── chat.ts                # getConversations(), createConversation(), sendMessage(), etc.
│   │   ├── documents.ts           # uploadDocument(), getDocuments(), deleteDocument()
│   │   ├── users.ts               # getUsers(), createUser(), updateUser(), deleteUser()
│   │   └── dashboard.ts           # getStats(), getActivity(), getTopQuestions()
│   │
│   ├── components/
│   │   ├── ui/                    # shadcn/ui components (Button, Input, Card, Table, etc.)
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx      # Layout with sidebar for non-chat pages
│   │   │   ├── Sidebar.tsx        # Navigation sidebar (non-chat pages)
│   │   │   └── ProtectedRoute.tsx # Auth guard, role guard, must_change_password guard
│   │   ├── chat/
│   │   │   ├── ChatSidebar.tsx    # Chat-specific sidebar (conversations list)
│   │   │   ├── ChatMessage.tsx    # Single message (user or assistant)
│   │   │   ├── ChatInput.tsx      # Message input with model selector
│   │   │   ├── ChatSources.tsx    # Sources block under AI message
│   │   │   ├── ConversationList.tsx # Conversation list items
│   │   │   ├── ModelSelector.tsx  # Claude/GPT dropdown
│   │   │   ├── WelcomeScreen.tsx  # Welcome screen with example questions
│   │   │   └── TypingIndicator.tsx # Animated dots
│   │   ├── documents/
│   │   │   ├── DocumentUpload.tsx # Drag & drop upload zone
│   │   │   ├── DocumentTable.tsx  # Documents table
│   │   │   ├── UploadProgress.tsx # Upload/processing progress bars
│   │   │   └── StatusBadge.tsx    # Indexed/Processing/Error badge
│   │   ├── users/
│   │   │   ├── UserTable.tsx      # Users table with inline edit
│   │   │   └── AddUserModal.tsx   # Create user dialog
│   │   └── dashboard/
│   │       ├── StatCard.tsx       # Single stat card
│   │       ├── ActivityChart.tsx  # Recharts line chart
│   │       ├── TopQuestions.tsx   # Top questions table
│   │       └── RecentConversations.tsx # Recent conversations list
│   │
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── ChangePasswordPage.tsx
│   │   ├── ChatPage.tsx           # Full chat page with own sidebar
│   │   ├── DashboardPage.tsx
│   │   ├── DocumentsPage.tsx
│   │   ├── UsersPage.tsx
│   │   ├── SettingsPage.tsx
│   │   └── NotFoundPage.tsx
│   │
│   ├── hooks/
│   │   ├── useAuth.ts             # Login, logout, current user
│   │   ├── useConversations.ts    # React Query hooks for conversations
│   │   ├── useMessages.ts         # React Query hooks for messages
│   │   ├── useDocuments.ts        # React Query hooks for documents
│   │   ├── useUsers.ts            # React Query hooks for users
│   │   └── useDashboard.ts        # React Query hooks for dashboard
│   │
│   ├── contexts/
│   │   └── AuthContext.tsx        # Auth provider, token management
│   │
│   ├── lib/
│   │   ├── utils.ts               # cn(), formatDate(), formatFileSize(), truncate()
│   │   └── constants.ts           # API_URL, MODELS, MAX_MESSAGE_LENGTH, etc.
│   │
│   ├── types/
│   │   └── index.ts               # User, Conversation, Message, Document, etc.
│   │
│   └── styles/
│       └── globals.css            # @tailwind directives, custom animations
│
├── public/
│   └── favicon.svg                # Bot icon as favicon
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.ts
├── postcss.config.js
├── eslint.config.js
├── .prettierrc
└── Dockerfile
```

**Ключевые npm зависимости**:
- react, react-dom (v18)
- react-router-dom (v6)
- @tanstack/react-query (v5)
- axios
- tailwindcss, postcss, autoprefixer
- @radix-ui/* (через shadcn/ui)
- lucide-react (иконки)
- recharts (графики)
- react-markdown, remark-gfm (рендер markdown)
- sonner (toast notifications)
- clsx, tailwind-merge (утилиты)
- date-fns (форматирование дат)

**Dev dependencies**:
- typescript
- vite
- @types/react, @types/react-dom
- eslint, @typescript-eslint/*
- prettier

---

## 19. Архитектура AI (RAG Pipeline)

### Document Ingestion Pipeline

```
Upload File
    │
    ▼
Validate (type, size)
    │
    ▼
Save to disk (uploads/{uuid}.{ext})
    │
    ▼
Update DB status → "processing"
    │
    ▼
Parse Document
├── PDF → PyPDF2: extract text page by page
├── DOCX → python-docx: extract text paragraph by paragraph
└── TXT → read UTF-8
    │
    ▼
Clean Text
├── Remove excessive whitespace
├── Remove non-printable characters
├── Normalize unicode
    │
    ▼
Chunk Text
├── Strategy: split by paragraphs first, then by sentences if paragraph > 512 tokens
├── Chunk size: 512 tokens (measured by tiktoken, model: cl100k_base)
├── Overlap: 50 tokens (last 50 tokens of prev chunk prepended to next)
├── Minimum chunk size: 50 tokens (smaller chunks merged with previous)
    │
    ▼
Generate Embeddings
├── Model: OpenAI text-embedding-3-small
├── Dimensions: 1536
├── Batch: up to 100 chunks per API call (OpenAI batch limit)
├── Rate limiting: retry with exponential backoff (1s, 2s, 4s, max 3 retries)
    │
    ▼
Store in DB
├── Insert document_chunks with embeddings
├── Update document: status → "indexed", chunk_count = N
    │
    ▼
Done (or status → "error" with error_message if any step fails)
```

### Query Pipeline

```
User Question
    │
    ▼
Embed Question
├── Same model: text-embedding-3-small
├── Same dimensions: 1536
    │
    ▼
Vector Search (pgvector)
├── Query: SELECT * FROM document_chunks ORDER BY embedding <=> $1 LIMIT 5
├── Filter: cosine distance < 0.7 (similarity > 0.3)
├── If 0 results: return response "No relevant documents found"
    │
    ▼
Build Prompt
├── System prompt (see below)
├── Context: retrieved chunks with source info
├── Conversation history: last 6 messages (3 user + 3 assistant)
├── User question
    │
    ▼
Call LLM
├── Model selection based on user choice:
│   ├── "claude" → claude-sonnet-4-20250514
│   └── "gpt" → gpt-4o
├── Temperature: 0.1
├── Max tokens: 2048
├── Timeout: 60 seconds
├── Retry: 1 retry on timeout/5xx
    │
    ▼
Parse Response
├── Extract answer text
├── Attach source metadata (document_id, document_name, chunk_index, relevance_score, snippet)
    │
    ▼
Save to DB
├── Save user message
├── Save assistant message with model and sources
├── Update conversation title (if first message): first 50 chars of question
├── Update conversation updated_at
    │
    ▼
Return Response
```

### System Prompt (точный текст)

```
You are an AI assistant for a company. Your role is to answer questions based ONLY on the provided context from company documents.

Rules:
1. Answer questions using ONLY the information from the provided context below.
2. If the context does not contain enough information to answer the question, say: "I don't have enough information in the available documents to answer this question. Please try rephrasing or contact your administrator."
3. Always be professional and helpful.
4. When citing information, mention which document it comes from.
5. Do not make up information or use knowledge outside of the provided context.
6. Answer in the same language as the question.

Context from company documents:
---
{chunks_text}
---

Each chunk above is labeled with [Source: document_name].
```

**Формат chunks_text**:
```
[Source: Company Policy.pdf]
{chunk_1_content}

[Source: HR Guidelines.docx]
{chunk_2_content}

...
```

---

## 20. Архитектура базы данных

PostgreSQL 16 с расширением pgvector.

**Основные решения**:
- UUID v4 в качестве primary key для всех таблиц (gen_random_uuid())
- Soft delete (поле `is_deleted`) для conversations
- Hard delete для users, documents (каскадное удаление связанных данных)
- Timestamps (`created_at`, `updated_at`) для всех таблиц
- `updated_at` обновляется автоматически через SQLAlchemy event listener (before_update)
- Все строковые поля имеют максимальную длину (VARCHAR, не TEXT без ограничений) кроме content полей
- JSONB для структурированных данных (sources, metadata)
- HNSW индекс для pgvector (быстрый approximate nearest neighbor search)

---

## 21. ER-диаграмма

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│     users        │       │  conversations   │       │    messages      │
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│ id (PK, UUID)    │──1:N──│ id (PK, UUID)    │──1:N──│ id (PK, UUID)    │
│ email (UNIQUE)   │       │ user_id (FK)     │       │ conversation_id  │
│ name             │       │ title            │       │   (FK)           │
│ password_hash    │       │ is_deleted       │       │ role             │
│ role             │       │ created_at       │       │ content          │
│ is_active        │       │ updated_at       │       │ model            │
│ must_change_pw   │       └──────────────────┘       │ sources (JSONB)  │
│ created_at       │                                  │ created_at       │
│ updated_at       │                                  └──────────────────┘
└──────────────────┘
        │
        │ 1:N (uploaded_by)
        ▼
┌──────────────────┐       ┌──────────────────────┐
│   documents      │       │   document_chunks    │
├──────────────────┤       ├──────────────────────┤
│ id (PK, UUID)    │──1:N──│ id (PK, UUID)        │
│ filename         │       │ document_id (FK)     │
│ original_name    │       │ content (TEXT)        │
│ file_type        │       │ chunk_index (INT)    │
│ file_size        │       │ embedding (VECTOR)   │
│ status           │       │ metadata (JSONB)     │
│ page_count       │       │ created_at           │
│ chunk_count      │       └──────────────────────┘
│ uploaded_by (FK) │
│ error_message    │
│ created_at       │
│ updated_at       │
└──────────────────┘
```

---

## 22-23. Все таблицы, поля, индексы, ограничения

### Таблица: users

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Уникальный идентификатор |
| email | VARCHAR(255) | NOT NULL, UNIQUE | Email пользователя |
| name | VARCHAR(100) | NOT NULL | Имя пользователя |
| password_hash | VARCHAR(255) | NOT NULL | Хеш пароля (bcrypt) |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'user', CHECK (role IN ('admin', 'user')) | Роль |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | Активен ли аккаунт |
| must_change_password | BOOLEAN | NOT NULL, DEFAULT false | Требуется смена пароля |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата создания |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата обновления |

**Индексы**:
- `ix_users_email` UNIQUE на `email`
- `ix_users_is_active` на `is_active`

### Таблица: conversations

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Уникальный идентификатор |
| user_id | UUID | NOT NULL, FK → users(id) ON DELETE CASCADE | Владелец |
| title | VARCHAR(200) | NOT NULL, DEFAULT 'New Conversation' | Название |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT false | Soft delete |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата создания |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата обновления |

**Индексы**:
- `ix_conversations_user_id` на `user_id`
- `ix_conversations_user_deleted` на `(user_id, is_deleted)` — для выборки активных разговоров пользователя
- `ix_conversations_updated_at` на `updated_at DESC` — для сортировки по последнему обновлению

### Таблица: messages

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Уникальный идентификатор |
| conversation_id | UUID | NOT NULL, FK → conversations(id) ON DELETE CASCADE | Разговор |
| role | VARCHAR(20) | NOT NULL, CHECK (role IN ('user', 'assistant')) | Роль |
| content | TEXT | NOT NULL | Текст сообщения |
| model | VARCHAR(50) | NULL | Модель AI (только для assistant) |
| sources | JSONB | NULL | Источники (только для assistant) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата создания |

**Индексы**:
- `ix_messages_conversation_id` на `conversation_id`
- `ix_messages_conv_created` на `(conversation_id, created_at)` — для выборки сообщений в порядке

**Формат sources (JSONB)**:
```json
[
  {
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "document_name": "Company Policy.pdf",
    "chunk_index": 3,
    "relevance_score": 0.87,
    "snippet": "First 200 characters of the chunk text..."
  }
]
```

### Таблица: documents

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Уникальный идентификатор |
| filename | VARCHAR(255) | NOT NULL, UNIQUE | Имя файла в хранилище ({uuid}.{ext}) |
| original_name | VARCHAR(255) | NOT NULL | Оригинальное имя файла |
| file_type | VARCHAR(10) | NOT NULL, CHECK (file_type IN ('pdf', 'docx', 'txt')) | Тип файла |
| file_size | INTEGER | NOT NULL, CHECK (file_size > 0) | Размер в байтах |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'uploaded', CHECK (status IN ('uploaded', 'processing', 'indexed', 'error')) | Статус обработки |
| page_count | INTEGER | NULL | Кол-во страниц (для PDF) |
| chunk_count | INTEGER | NOT NULL, DEFAULT 0 | Кол-во чанков |
| uploaded_by | UUID | NOT NULL, FK → users(id) | Кто загрузил |
| error_message | TEXT | NULL | Текст ошибки |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата загрузки |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата обновления |

**Индексы**:
- `ix_documents_status` на `status`
- `ix_documents_uploaded_by` на `uploaded_by`
- `ix_documents_created_at` на `created_at DESC`

### Таблица: document_chunks

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Уникальный идентификатор |
| document_id | UUID | NOT NULL, FK → documents(id) ON DELETE CASCADE | Документ |
| content | TEXT | NOT NULL | Текст чанка |
| chunk_index | INTEGER | NOT NULL, CHECK (chunk_index >= 0) | Порядковый номер |
| embedding | VECTOR(1536) | NOT NULL | Вектор |
| metadata | JSONB | NOT NULL, DEFAULT '{}' | Метаданные |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата создания |

**Индексы**:
- `ix_chunks_document_id` на `document_id`
- `ix_chunks_embedding_hnsw` — HNSW на `embedding` с `vector_cosine_ops` (m=16, ef_construction=64)

**Формат metadata**:
```json
{
  "page_number": 5,
  "paragraph_index": 2
}
```

### SQL для создания расширения pgvector

```sql
create extension if not exists vector;
```

Выполняется в Alembic миграции перед созданием таблиц.

---

## 24-27. REST API (полная спецификация)

Базовый URL: `/api/v1`
Content-Type: `application/json` (кроме upload — `multipart/form-data`)
Авторизация: Header `Authorization: Bearer <jwt_token>`

### Общий формат ошибок

Все ошибки возвращаются в едином формате:

```json
{
  "detail": "Human-readable error message"
}
```

Для ошибок валидации Pydantic (422):
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error"
    }
  ]
}
```

### Общие коды ошибок

| Код | Когда | Body |
|-----|-------|------|
| 400 | Невалидные данные (бизнес-логика) | `{"detail": "описание"}` |
| 401 | Нет токена, невалидный токен, expired | `{"detail": "Not authenticated"}` |
| 403 | Нет прав (role, ownership) | `{"detail": "описание"}` |
| 404 | Ресурс не найден | `{"detail": "описание"}` |
| 409 | Конфликт (duplicate) | `{"detail": "описание"}` |
| 413 | Файл слишком большой | `{"detail": "описание"}` |
| 422 | Ошибка валидации Pydantic | массив ошибок |
| 429 | Rate limit | `{"detail": "Too many requests. Please try again later."}` |
| 500 | Внутренняя ошибка | `{"detail": "Internal server error"}` |
| 503 | AI сервис недоступен | `{"detail": "описание"}` |

### Пагинация (общий формат)

Все списковые эндпоинты возвращают:
```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "per_page": 20,
  "pages": 3
}
```

Query params: `page` (int, default=1, min=1), `per_page` (int, default=20, min=1, max=100)

---

### AUTH

#### POST /api/v1/auth/login

**Request**:
```json
{
  "email": "user@company.com",
  "password": "password123"
}
```
Валидация: email required + формат email, password required + min 1 char

**Response 200**:
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@company.com",
    "name": "John Doe",
    "role": "user",
    "must_change_password": false
  }
}
```

**Ошибки**:
| Код | Условие | Detail |
|-----|---------|--------|
| 401 | Неверный email или пароль | "Invalid email or password" |
| 403 | Аккаунт деактивирован | "Your account has been deactivated. Contact administrator." |
| 422 | Невалидный формат email | Pydantic validation error |
| 429 | >10 запросов/мин с одного IP | "Too many login attempts. Please try again later." |

#### POST /api/v1/auth/change-password

**Auth**: Required

**Request**:
```json
{
  "current_password": "old_password",
  "new_password": "NewPass123",
  "confirm_password": "NewPass123"
}
```

**Response 200**:
```json
{
  "message": "Password changed successfully"
}
```

Побочный эффект: `must_change_password` устанавливается в `false`.

**Ошибки**:
| Код | Условие | Detail |
|-----|---------|--------|
| 400 | Пароли не совпадают | "Passwords do not match" |
| 400 | Новый = текущему | "New password must differ from current password" |
| 400 | Не соблюдены требования | "Password must be at least 8 characters and contain both letters and numbers" |
| 401 | Неверный текущий пароль | "Invalid current password" |

---

### CONVERSATIONS

#### POST /api/v1/conversations

**Auth**: Required

**Request**: пустое тело `{}` или `{"title": "Custom title"}` (title optional, max 200 chars)

**Response 201**:
```json
{
  "id": "uuid",
  "title": "New Conversation",
  "created_at": "2026-07-31T12:00:00Z",
  "updated_at": "2026-07-31T12:00:00Z",
  "message_count": 0,
  "messages": []
}
```

#### GET /api/v1/conversations

**Auth**: Required
Возвращает только разговоры текущего пользователя (фильтр по user_id из JWT), is_deleted=false.

**Query params**:
- `search` (string, optional): поиск по title (ILIKE %search%)
- `page`, `per_page`

**Сортировка**: по `updated_at` DESC (последние обновленные сверху)

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "How to submit vacation request",
      "created_at": "2026-07-31T12:00:00Z",
      "updated_at": "2026-07-31T14:00:00Z",
      "message_count": 4,
      "last_message_preview": "According to the HR policy..."
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 50,
  "pages": 1
}
```

`last_message_preview`: первые 100 символов последнего сообщения assistant. Если нет сообщений — null.

#### GET /api/v1/conversations/{id}

**Auth**: Required (owner only)

**Response 200**:
```json
{
  "id": "uuid",
  "title": "How to submit vacation request",
  "created_at": "2026-07-31T12:00:00Z",
  "updated_at": "2026-07-31T14:00:00Z",
  "message_count": 4,
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "How do I submit a vacation request?",
      "model": null,
      "sources": null,
      "created_at": "2026-07-31T12:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "According to the HR policy, to submit a vacation request you need to...",
      "model": "claude-sonnet-4-20250514",
      "sources": [
        {
          "document_id": "uuid",
          "document_name": "HR Policy.pdf",
          "chunk_index": 3,
          "relevance_score": 0.87,
          "snippet": "To submit a vacation request, employees must..."
        }
      ],
      "created_at": "2026-07-31T12:01:00Z"
    }
  ]
}
```

**Ошибки**:
| Код | Условие | Detail |
|-----|---------|--------|
| 404 | Не найден или is_deleted=true | "Conversation not found" |
| 403 | Чужой разговор | "Access denied" |

#### DELETE /api/v1/conversations/{id}

**Auth**: Required (owner only)
**Действие**: soft delete (is_deleted=true). Сообщения НЕ удаляются.

**Response 204**: пустое тело

**Ошибки**: 404, 403 (аналогично GET)

#### POST /api/v1/conversations/{id}/messages

**Auth**: Required (owner only)

**Request**:
```json
{
  "content": "How do I submit a vacation request?",
  "model": "claude"
}
```

Валидация:
- `content`: required, min 1 char (trimmed), max 4000 chars
- `model`: optional, enum ["claude", "gpt"], default "claude"

**Response 200**:
```json
{
  "user_message": {
    "id": "uuid",
    "role": "user",
    "content": "How do I submit a vacation request?",
    "model": null,
    "sources": null,
    "created_at": "2026-07-31T12:00:00Z"
  },
  "assistant_message": {
    "id": "uuid",
    "role": "assistant",
    "content": "According to the HR policy...",
    "model": "claude-sonnet-4-20250514",
    "sources": [
      {
        "document_id": "uuid",
        "document_name": "HR Policy.pdf",
        "chunk_index": 3,
        "relevance_score": 0.87,
        "snippet": "To submit a vacation request..."
      }
    ],
    "created_at": "2026-07-31T12:01:00Z"
  },
  "conversation_title": "How do I submit a vacation request"
}
```

`conversation_title` возвращается всегда — клиент обновляет title в sidebar если изменился (автогенерация из первого вопроса).

**Побочные эффекты**:
- Если это первое сообщение в разговоре: `conversation.title` обновляется на первые 50 символов вопроса
- `conversation.updated_at` обновляется

**Ошибки**:
| Код | Условие | Detail |
|-----|---------|--------|
| 400 | Пустое содержимое | "Message content is required" |
| 400 | Слишком длинное | "Message is too long (maximum 4000 characters)" |
| 400 | Невалидная модель | "Invalid model. Supported models: claude, gpt" |
| 404 | Разговор не найден | "Conversation not found" |
| 403 | Чужой разговор | "Access denied" |
| 503 | AI API недоступен | "AI service is temporarily unavailable. Please try again later." |
| 503 | Нет документов | "No documents have been indexed yet. Please ask an administrator to upload documents." |

---

### DOCUMENTS (Admin only)

Все эндпоинты требуют role=admin. При role=user → 403 "Admin access required".

#### POST /api/v1/documents

**Auth**: Admin
**Content-Type**: multipart/form-data

**Request**: поле `file` — бинарный файл

**Валидация (на сервере)**:
- Файл обязателен. Нет файла → 400 "No file provided"
- Расширение: .pdf, .docx, .txt. Другое → 400 "Unsupported file type. Allowed: pdf, docx, txt"
- MIME type тоже проверяется (application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document, text/plain). Несоответствие → 400 "Invalid file content"
- Размер: max 50MB. Превышение → 413 "File too large. Maximum size is 50MB."
- Имя файла: original_name уникальность не требуется (filename в хранилище — UUID), но дубликат original_name → 409 "Document with this name already exists"

**Response 201**:
```json
{
  "id": "uuid",
  "original_name": "HR Policy.pdf",
  "file_type": "pdf",
  "file_size": 245760,
  "status": "uploaded",
  "page_count": null,
  "chunk_count": 0,
  "uploaded_by": {
    "id": "uuid",
    "name": "Admin"
  },
  "created_at": "2026-07-31T12:00:00Z"
}
```

**Побочный эффект**: запускается background task для обработки документа (parse → chunk → embed → index). Статус обновляется: uploaded → processing → indexed (или error).

#### GET /api/v1/documents

**Auth**: Admin

**Query params**:
- `status` (string, optional): фильтр по статусу
- `page`, `per_page`

**Сортировка**: по `created_at` DESC

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "original_name": "HR Policy.pdf",
      "file_type": "pdf",
      "file_size": 245760,
      "status": "indexed",
      "page_count": 15,
      "chunk_count": 42,
      "uploaded_by": {
        "id": "uuid",
        "name": "Admin"
      },
      "error_message": null,
      "created_at": "2026-07-31T12:00:00Z",
      "updated_at": "2026-07-31T12:02:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

#### GET /api/v1/documents/{id}

**Auth**: Admin

**Response 200**: один документ (тот же формат что элемент в items)

**Ошибки**: 404

#### DELETE /api/v1/documents/{id}

**Auth**: Admin

**Действие**: удаляет запись из БД (CASCADE удалит чанки), удаляет файл с диска.
Если файл на диске уже не существует — не ошибка, только лог warning.

**Response 204**: пустое тело

**Ошибки**: 404

---

### USERS (Admin only)

Все эндпоинты требуют role=admin.

#### GET /api/v1/users

**Auth**: Admin

**Query params**: `page`, `per_page`
**Сортировка**: по `created_at` DESC

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "email": "user@company.com",
      "name": "John Doe",
      "role": "user",
      "is_active": true,
      "created_at": "2026-07-31T12:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

#### POST /api/v1/users

**Auth**: Admin

**Request**:
```json
{
  "email": "newuser@company.com",
  "name": "Jane Smith",
  "role": "user"
}
```

Валидация:
- `email`: required, формат email, max 255 chars
- `name`: required, min 2 chars, max 100 chars
- `role`: optional, enum ["admin", "user"], default "user"

**Генерация временного пароля**: 8 символов, [a-zA-Z0-9], минимум 1 буква + 1 цифра. Хешируется bcrypt перед сохранением. `must_change_password` = true.

**Response 201**:
```json
{
  "id": "uuid",
  "email": "newuser@company.com",
  "name": "Jane Smith",
  "role": "user",
  "is_active": true,
  "temporary_password": "aB3dEf7h",
  "created_at": "2026-07-31T12:00:00Z"
}
```

`temporary_password` возвращается ТОЛЬКО при создании. Не сохраняется в plaintext в БД. Не логируется.

**Ошибки**:
| Код | Условие | Detail |
|-----|---------|--------|
| 409 | Email уже существует | "User with this email already exists" |
| 422 | Невалидные данные | Pydantic validation errors |

#### PATCH /api/v1/users/{id}

**Auth**: Admin

**Request** (любые поля, partial update):
```json
{
  "name": "New Name",
  "role": "admin",
  "is_active": false
}
```

Валидация: те же правила что при создании, но все поля optional.

**Защитные проверки** (403):
- Нельзя менять свою роль: `"Cannot change your own role"`
- Нельзя деактивировать себя: `"Cannot deactivate your own account"`
- Нельзя менять email (поле игнорируется, не ошибка)

**Response 200**: обновленный пользователь (без password/temporary_password)

**Ошибки**: 403, 404

#### DELETE /api/v1/users/{id}

**Auth**: Admin

**Защитные проверки**: нельзя удалить себя → 403 `"Cannot delete your own account"`

**Действие**: hard delete. CASCADE удалит все conversations и messages пользователя.

**Response 204**: пустое тело

**Ошибки**: 403, 404

---

### DASHBOARD (Admin only)

#### GET /api/v1/dashboard/stats

**Auth**: Admin

**Query params**: `period` (string, default="30d"): `"today"`, `"7d"`, `"30d"`

**Response 200**:
```json
{
  "total_users": 15,
  "active_users": 12,
  "total_documents": 42,
  "indexed_documents": 40,
  "total_conversations": 350,
  "questions_in_period": 87,
  "questions_change_percent": 12.5
}
```

`questions_change_percent`: сравнение с предыдущим аналогичным периодом. Если period=7d, сравниваем с 7 днями до этого. Может быть отрицательным. Null если нет данных за прошлый период.

#### GET /api/v1/dashboard/activity

**Auth**: Admin

**Query params**: `period` (string, default="30d"): `"7d"`, `"30d"`

**Response 200**:
```json
{
  "data": [
    {"date": "2026-07-01", "questions": 15},
    {"date": "2026-07-02", "questions": 22}
  ]
}
```

Каждый день в периоде, включая дни с 0 вопросов. Формат даты: ISO 8601 date (YYYY-MM-DD).

#### GET /api/v1/dashboard/top-questions

**Auth**: Admin

**Response 200**:
```json
{
  "items": [
    {"question": "How do I submit a vacation request?", "count": 15},
    {"question": "What is the remote work policy?", "count": 12},
    {"question": "Where is the onboarding checklist?", "count": 8},
    {"question": "How to request equipment?", "count": 5},
    {"question": "What are the office hours?", "count": 3}
  ]
}
```

Топ-5 вопросов за все время. "Вопрос" = первое сообщение (role=user) каждого разговора. Группировка по similarity (точное совпадение текста, не семантическое).

---

### SETTINGS

#### PATCH /api/v1/users/me/profile

**Auth**: Required (любой пользователь)

Специальный эндпоинт для изменения своего профиля (не admin-only).

**Request**:
```json
{
  "name": "New Name"
}
```

Только `name` можно менять. email, role — игнорируются.

**Response 200**:
```json
{
  "id": "uuid",
  "email": "user@company.com",
  "name": "New Name",
  "role": "user",
  "is_active": true,
  "created_at": "2026-07-31T12:00:00Z"
}
```

---

### HEALTH

#### GET /api/v1/health

**Auth**: НЕ требуется (публичный)

**Response 200** (все OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "ai": {
      "claude": {"status": "healthy"},
      "openai": {"status": "healthy"}
    }
  }
}
```

**Response 503** (проблема):
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "components": {
    "database": {"status": "unhealthy", "error": "Connection refused"},
    "redis": {"status": "healthy"},
    "ai": {
      "claude": {"status": "healthy"},
      "openai": {"status": "unhealthy", "error": "Invalid API key"}
    }
  }
}
```

Проверки:
- database: `SELECT 1` query
- redis: `PING` command
- claude: `anthropic.messages.create` с minimal request (опционально, можно проверять только наличие API key)
- openai: аналогично

Если хотя бы один компонент unhealthy — HTTP 503 (для Docker healthcheck).

---

## 28. Авторизация

### Механизм: JWT (JSON Web Tokens)

**Библиотека**: python-jose[cryptography]
**Алгоритм**: HS256
**Секретный ключ**: из переменной окружения `SECRET_KEY` (минимум 32 символа)

**Access Token**:
- Время жизни: 30 минут (настраивается через `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Payload:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@company.com",
  "role": "admin",
  "exp": 1690800000,
  "iat": 1690798200
}
```
- Хранение на клиенте: `localStorage` ключ `access_token`
- Передача: Header `Authorization: Bearer <token>`

**Refresh Token**: НЕ используется в MVP. При истечении access token — пользователь перенаправляется на /login.

**Поведение на клиенте**:
- При каждом API-запросе: Axios interceptor добавляет `Authorization` header
- При получении 401: удаляется token из localStorage, redirect на /login, toast "Your session has expired"
- При загрузке приложения: если token есть в localStorage — декодировать (без серверной проверки) для получения user info; первый API запрос проверит валидность

**Password Hashing**:
- Библиотека: passlib (CryptContext с bcrypt)
- Cost factor: 12 (по умолчанию passlib)
- Временный пароль при создании пользователя: 8 символов, [a-zA-Z0-9], минимум 1 буква и 1 цифра

**Пароль по умолчанию для первого admin**:
- Задается через env `ADMIN_DEFAULT_PASSWORD`
- При первом запуске (таблица users пуста): создается пользователь с `ADMIN_EMAIL`, `ADMIN_NAME`, `ADMIN_DEFAULT_PASSWORD`
- `must_change_password` = true (принудительная смена)

**Требования к паролю**:
- Минимум 8 символов
- Минимум 1 буква (a-z или A-Z)
- Минимум 1 цифра (0-9)
- Максимум 128 символов
- Regex: `^(?=.*[a-zA-Z])(?=.*\d).{8,128}$`

---

## 29. Роли пользователей

Две роли: `admin` и `user`.

| Действие | user | admin |
|----------|------|-------|
| Login / Logout | да | да |
| Change own password | да | да |
| Chat — задавать вопросы | да | да |
| Chat — выбирать модель | да | да |
| Conversations — список своих | да | да |
| Conversations — open свой | да | да |
| Conversations — delete свой | да | да |
| Conversations — доступ к чужим | нет | нет |
| Documents — view list | нет | да |
| Documents — upload | нет | да |
| Documents — delete | нет | да |
| Users — view list | нет | да |
| Users — create | нет | да |
| Users — update role/status | нет | да |
| Users — delete | нет | да (кроме себя) |
| Dashboard — view | нет | да |
| Settings — edit own profile | да | да |

**Первый admin**: создается автоматически при запуске (если users таблица пуста). Нельзя удалить последнего admin — проверка при DELETE: если в БД остается только 1 user с role=admin, вернуть 403 "Cannot delete the last administrator".

---

## 30. Политика безопасности

### Пароли
- Хешируются bcrypt (cost 12)
- Никогда не логируются
- Никогда не возвращаются в API (кроме temporary_password при создании)
- Не хранятся в plaintext нигде

### JWT
- Подписываются SECRET_KEY из .env
- HS256 алгоритм
- Проверка exp при каждом запросе
- Невалидный/expired → 401

### CORS
- Настраивается через `CORS_ORIGINS` в .env
- Default: `http://localhost,http://localhost:3000,http://localhost:5173`
- Credentials: true
- Methods: GET, POST, PATCH, DELETE, OPTIONS
- Headers: Authorization, Content-Type

### Rate Limiting (slowapi)
- Login: 10 req/min per IP
- API (authenticated): 60 req/min per user
- Document upload: 10 req/min per user
- При превышении: 429

### File Upload Security
- Проверка расширения: .pdf, .docx, .txt
- Проверка MIME type: application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document, text/plain
- Максимальный размер: 50MB
- Файлы сохраняются с UUID именем (не оригинальным)
- Директория uploads/ не доступна через web (Nginx не проксирует)
- Файлы не скачиваемые через API (в MVP)

### SQL Injection
- SQLAlchemy ORM с параметризованными запросами
- Нет raw SQL

### XSS
- React автоматически экранирует HTML
- react-markdown с sanitize (по умолчанию)
- Content-Security-Policy header через Nginx

### HTTP Security Headers (Nginx)
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:;
```

### Sensitive Data
- .env файл: в .gitignore, никогда не коммитится
- API keys: только в .env, не в коде
- Логи: не содержат паролей, токенов, тел запросов/ответов чата

---

## 31. Логирование

**Библиотека**: structlog (structured JSON logging)

**Формат**:
```json
{
  "timestamp": "2026-07-31T12:00:00.000Z",
  "level": "info",
  "event": "http_request",
  "request_id": "abc-123",
  "method": "POST",
  "path": "/api/v1/auth/login",
  "status": 200,
  "duration_ms": 45,
  "user_id": "uuid",
  "ip": "192.168.1.1"
}
```

**request_id**: генерируется middleware для каждого запроса (UUID4), добавляется ко всем логам в рамках запроса, возвращается в response header `X-Request-ID`.

### Что логируется (с уровнями)

| Событие | Уровень | Поля |
|---------|---------|------|
| HTTP запрос | INFO | method, path, status, duration_ms, user_id, ip |
| Login success | INFO | user_id, email, ip |
| Login failure | WARNING | email (не user_id!), ip, reason |
| Password changed | INFO | user_id |
| User created | INFO | user_id (admin), created_user_id |
| User deleted | INFO | user_id (admin), deleted_user_id |
| User deactivated | INFO | user_id (admin), target_user_id |
| Document uploaded | INFO | user_id, document_id, filename, file_size |
| Document processing started | INFO | document_id |
| Document indexed | INFO | document_id, chunk_count, duration_ms |
| Document processing error | ERROR | document_id, error |
| Document deleted | INFO | user_id, document_id |
| RAG query | INFO | user_id, conversation_id, model, chunks_found, duration_ms |
| RAG no results | WARNING | user_id, conversation_id |
| AI API error | ERROR | model, error, duration_ms |
| AI API timeout | ERROR | model, timeout_seconds |
| Rate limit hit | WARNING | user_id or ip, endpoint |
| Startup | INFO | version, config (без секретов) |
| Shutdown | INFO | — |
| DB connection error | CRITICAL | error |
| Redis connection error | ERROR | error |
| Unhandled exception | ERROR | error, traceback |

### Что НЕ логируется
- Пароли (ни plain, ни hash)
- JWT токены
- Содержимое сообщений чата (privacy)
- Полные тела HTTP запросов/ответов
- API keys
- File contents

### Вывод
- stdout (JSON, одна строка на событие)
- Docker: `docker-compose logs -f backend`
- Уровень: настраивается через `LOG_LEVEL` env (default: INFO, в production: INFO, в dev: DEBUG)

---

## 32. Мониторинг

- **Health endpoint**: `GET /api/v1/health` — проверка DB, Redis, AI APIs
- **Docker healthcheck**: в Dockerfile и docker-compose.yml
  - Backend: `curl -f http://localhost:8000/api/v1/health || exit 1`
  - Interval: 30s, timeout: 10s, retries: 3, start_period: 40s
  - PostgreSQL: `pg_isready -U postgres`
  - Redis: `redis-cli ping`
- **Метрики**: извлекаются из structured logs (не отдельный endpoint в MVP)
  - Response time (по полю duration_ms)
  - Error rate (по полю status >= 500)
  - AI response time (по полю duration_ms в RAG query events)
  - Document processing time

---

## 33. Docker

### Контейнеры

| Контейнер | Образ | Порт (внутренний) | Порт (внешний) |
|-----------|-------|-------------------|----------------|
| backend | Dockerfile.backend | 8000 | — (через nginx) |
| frontend | Dockerfile.frontend | 80 | — (через nginx) |
| postgres | postgres:16-alpine | 5432 | 5432 (для dev) |
| redis | redis:7-alpine | 6379 | 6379 (для dev) |
| nginx | nginx:alpine | 80 | 80 |

### Dockerfile backend (multi-stage)
```
Stage 1 (builder):
  FROM python:3.13-slim AS builder
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

Stage 2 (runtime):
  FROM python:3.13-slim
  RUN groupadd -r appuser && useradd -r -g appuser appuser
  WORKDIR /app
  COPY --from=builder /install /usr/local
  COPY app/ app/
  COPY alembic/ alembic/
  COPY alembic.ini .
  RUN mkdir -p uploads && chown appuser:appuser uploads
  USER appuser
  EXPOSE 8000
  HEALTHCHECK CMD curl -f http://localhost:8000/api/v1/health || exit 1
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile frontend (multi-stage)
```
Stage 1 (builder):
  FROM node:20-alpine AS builder
  WORKDIR /app
  COPY package*.json .
  RUN npm ci
  COPY . .
  RUN npm run build

Stage 2 (runtime):
  FROM nginx:alpine
  COPY --from=builder /app/dist /usr/share/nginx/html
  COPY nginx.conf /etc/nginx/conf.d/default.conf
  EXPOSE 80
```

### docker-compose.yml (структура)
```yaml
services:
  backend:
    build: ./backend
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - uploads:/app/uploads
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G

  frontend:
    build: ./frontend
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M

volumes:
  postgres_data:
  redis_data:
  uploads:
```

### nginx.conf
```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name _;

    client_max_body_size 55M;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy strict-origin-when-cross-origin;

    # API proxy
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # Swagger UI
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://backend;
    }

    # Frontend (SPA)
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
    }
}
```

---

## 34. GitHub Actions

### CI (.github/workflows/ci.yml)

```yaml
name: CI
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - Checkout
      - Setup Python 3.13
      - Cache pip
      - Install dependencies (requirements.txt + requirements-dev.txt)
      - Run ruff check (linter)
      - Run ruff format --check (formatter)
      - Run pytest with coverage
      - Upload coverage report

  frontend:
    runs-on: ubuntu-latest
    steps:
      - Checkout
      - Setup Node.js 20
      - Cache npm
      - npm ci
      - Run ESLint
      - Run tsc --noEmit (type check)
      - Run npm run build

  docker:
    runs-on: ubuntu-latest
    needs: [backend, frontend]
    steps:
      - Checkout
      - Setup Docker Buildx
      - Build backend image (no push)
      - Build frontend image (no push)
```

### CD (.github/workflows/cd.yml)

```yaml
name: CD
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - Checkout
      - Setup Docker Buildx
      - Login to GHCR (github token)
      - Build and push backend (tags: latest, sha-$GITHUB_SHA)
      - Build and push frontend (tags: latest, sha-$GITHUB_SHA)
```

---

## 35. Структура директорий проекта

```
ai-support-agent/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py
│   │   │       ├── auth.py
│   │   │       ├── chat.py
│   │   │       ├── documents.py
│   │   │       ├── users.py
│   │   │       ├── dashboard.py
│   │   │       └── health.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   ├── document.py
│   │   │   └── document_chunk.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── document.py
│   │   │   ├── user.py
│   │   │   ├── dashboard.py
│   │   │   └── common.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── document_service.py
│   │   │   ├── user_service.py
│   │   │   ├── dashboard_service.py
│   │   │   └── rag/
│   │   │       ├── __init__.py
│   │   │       ├── embeddings.py
│   │   │       ├── retriever.py
│   │   │       ├── generator.py
│   │   │       └── processor.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   ├── exceptions.py
│   │   │   └── logging.py
│   │   └── tasks/
│   │       ├── __init__.py
│   │       └── document_tasks.py
│   ├── alembic/
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_chat.py
│   │   ├── test_documents.py
│   │   ├── test_users.py
│   │   └── test_rag.py
│   ├── uploads/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── auth.ts
│   │   │   ├── chat.ts
│   │   │   ├── documents.ts
│   │   │   ├── users.ts
│   │   │   └── dashboard.ts
│   │   ├── components/
│   │   │   ├── ui/               # shadcn components
│   │   │   ├── layout/
│   │   │   │   ├── AppLayout.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── chat/
│   │   │   │   ├── ChatSidebar.tsx
│   │   │   │   ├── ChatMessage.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   ├── ChatSources.tsx
│   │   │   │   ├── ConversationList.tsx
│   │   │   │   ├── ModelSelector.tsx
│   │   │   │   ├── WelcomeScreen.tsx
│   │   │   │   └── TypingIndicator.tsx
│   │   │   ├── documents/
│   │   │   │   ├── DocumentUpload.tsx
│   │   │   │   ├── DocumentTable.tsx
│   │   │   │   ├── UploadProgress.tsx
│   │   │   │   └── StatusBadge.tsx
│   │   │   ├── users/
│   │   │   │   ├── UserTable.tsx
│   │   │   │   └── AddUserModal.tsx
│   │   │   └── dashboard/
│   │   │       ├── StatCard.tsx
│   │   │       ├── ActivityChart.tsx
│   │   │       ├── TopQuestions.tsx
│   │   │       └── RecentConversations.tsx
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── ChangePasswordPage.tsx
│   │   │   ├── ChatPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── DocumentsPage.tsx
│   │   │   ├── UsersPage.tsx
│   │   │   ├── SettingsPage.tsx
│   │   │   └── NotFoundPage.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useConversations.ts
│   │   │   ├── useMessages.ts
│   │   │   ├── useDocuments.ts
│   │   │   ├── useUsers.ts
│   │   │   └── useDashboard.ts
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx
│   │   ├── lib/
│   │   │   ├── utils.ts
│   │   │   └── constants.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── styles/
│   │       └── globals.css
│   ├── public/
│   │   └── favicon.svg
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── eslint.config.js
│   ├── .prettierrc
│   └── Dockerfile
│
├── docker/
│   └── nginx/
│       └── nginx.conf
│
├── docs/
│   └── ARCHITECTURE.md
│
├── screenshots/
│   ├── 01-login.png
│   ├── 02-chat.png
│   ├── 03-dashboard.png
│   ├── 04-documents.png
│   └── 05-mobile-chat.png
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── LICENSE (MIT)
```

---

## 36-37. План разработки и Definition of Done

### Задача 1: Инициализация проекта и базовая инфраструктура
**Оценка**: 3 часа

**Что сделать**:
- Создать полную структуру директорий backend/ и frontend/
- Настроить FastAPI: main.py (app, lifespan, middleware), config.py (Pydantic Settings из .env)
- Настроить SQLAlchemy: database.py (async engine, async sessionmaker, get_db dependency)
- Настроить Alembic: alembic.ini, env.py для async
- Настроить structlog: JSON формат, request_id middleware
- Создать docker-compose.yml с postgres и redis
- Создать .env.example с полным списком переменных
- Настроить React проект: Vite + TypeScript + Tailwind + shadcn/ui (init)
- Настроить Axios client с baseURL и interceptors
- Настроить React Router с пустыми страницами
- Настроить React Query provider
- Настроить sonner (toast provider)
- pyproject.toml, requirements.txt, requirements-dev.txt
- .gitignore для Python + Node + IDE + .env

**Definition of Done**:
- [ ] `docker-compose up -d postgres redis` поднимает БД (port 5432) и Redis (port 6379)
- [ ] `uvicorn app.main:app` запускается и отдает `{"status": "ok"}` на GET /api/v1/health
- [ ] `alembic init` завершается без ошибок, alembic.ini настроен на DATABASE_URL из .env
- [ ] Логи FastAPI выводятся в JSON формат в stdout
- [ ] Request ID middleware добавляет X-Request-ID header
- [ ] `npm run dev` запускает React dev server на порту 5173
- [ ] Tailwind работает (элемент с `bg-red-500` отображается красным)
- [ ] shadcn/ui Button рендерится корректно
- [ ] Axios client настроен на /api/v1
- [ ] React Router рендерит пустые страницы по URL
- [ ] .env.example содержит все переменные с описаниями
- [ ] .gitignore настроен

### Задача 2: Модели БД и миграции
**Оценка**: 2 часа

**Что сделать**:
- Создать Base model с общими полями (id, created_at, updated_at)
- Создать все SQLAlchemy модели: User, Conversation, Message, Document, DocumentChunk
- Включить pgvector extension в миграции
- Создать Alembic миграцию (autogenerate)
- Добавить auto-create admin user при первом запуске (в lifespan)
- Добавить SQLAlchemy event listener для auto-update updated_at

**Definition of Done**:
- [ ] `alembic upgrade head` создает все 5 таблиц
- [ ] pgvector extension включен (SELECT * FROM pg_extension WHERE extname='vector')
- [ ] Все индексы из спецификации созданы
- [ ] Все CHECK constraints работают (попытка вставить role='superadmin' → ошибка)
- [ ] Все FK constraints работают (cascade delete)
- [ ] UNIQUE constraint на users.email работает
- [ ] Admin-пользователь создается при первом запуске (если таблица пуста)
- [ ] Admin-пользователь НЕ создается повторно при перезапуске
- [ ] updated_at обновляется автоматически при update

### Задача 3: Аутентификация (Backend)
**Оценка**: 3 часа

**Что сделать**:
- core/security.py: create_access_token, verify_token, hash_password, verify_password, generate_temp_password
- services/auth_service.py: authenticate(email, password), change_password(user, old, new)
- api/deps.py: get_current_user, require_admin
- api/v1/auth.py: POST /login, POST /change-password
- Rate limiting на login (slowapi, 10 req/min per IP)
- core/exceptions.py: custom exceptions + FastAPI exception handlers
- Unit тесты: test_auth.py

**Definition of Done**:
- [ ] POST /login с валидными данными возвращает 200 + JWT + user info
- [ ] POST /login с невалидными данными возвращает 401
- [ ] POST /login для деактивированного аккаунта возвращает 403
- [ ] JWT payload содержит sub, email, role, exp, iat
- [ ] get_current_user извлекает пользователя из JWT и возвращает User model
- [ ] get_current_user возвращает 401 для невалидного/expired токена
- [ ] require_admin возвращает 403 для role=user
- [ ] POST /change-password с корректными данными меняет пароль, сбрасывает must_change_password
- [ ] POST /change-password валидирует все требования к паролю
- [ ] Rate limiting на login работает (11-й запрос за минуту → 429)
- [ ] Тесты (test_auth.py) проходят: минимум 10 тестов

### Задача 4: Управление пользователями (Backend)
**Оценка**: 2 часа

**Что сделать**:
- services/user_service.py: get_users, create_user, update_user, delete_user
- api/v1/users.py: GET /users, POST /users, PATCH /users/{id}, DELETE /users/{id}
- PATCH /users/me/profile: эндпоинт для изменения своего имени
- schemas/user.py: UserCreate, UserUpdate, UserResponse
- Пагинация (generic PaginatedResponse)
- Защитные проверки: нельзя удалить/деактивировать себя, нельзя удалить последнего admin
- Unit тесты: test_users.py

**Definition of Done**:
- [ ] GET /users возвращает список с пагинацией (page, per_page, total, pages)
- [ ] POST /users создает пользователя с временным паролем (8 символов, буквы+цифры)
- [ ] POST /users с дублирующимся email → 409
- [ ] POST /users для role=user → 403
- [ ] PATCH /users/{id}: обновляет name, role, is_active
- [ ] PATCH свою роль → 403 "Cannot change your own role"
- [ ] PATCH свой is_active=false → 403 "Cannot deactivate your own account"
- [ ] DELETE /users/{id} удаляет пользователя
- [ ] DELETE себя → 403 "Cannot delete your own account"
- [ ] DELETE последнего admin → 403 "Cannot delete the last administrator"
- [ ] PATCH /users/me/profile обновляет имя текущего пользователя
- [ ] Тесты (test_users.py) проходят: минимум 12 тестов

### Задача 5: Загрузка и обработка документов (Backend)
**Оценка**: 4 часа

**Что сделать**:
- services/document_service.py: upload_document, list_documents, delete_document
- services/rag/processor.py: parse_pdf, parse_docx, parse_txt, chunk_text
- tasks/document_tasks.py: process_document_task (background)
- api/v1/documents.py: POST /documents, GET /documents, GET /documents/{id}, DELETE /documents/{id}
- Валидация файлов (тип, размер, MIME)
- Хранение в uploads/{uuid}.{ext}
- Background processing (FastAPI BackgroundTasks)
- Unit тесты: test_documents.py

**Definition of Done**:
- [ ] POST /documents принимает PDF, DOCX, TXT файлы
- [ ] POST /documents отклоняет .exe, .zip и т.д. → 400
- [ ] POST /documents отклоняет файлы >50MB → 413
- [ ] Файл сохраняется в uploads/{uuid}.{ext}
- [ ] Статус документа: uploaded → processing → indexed
- [ ] PyPDF2 корректно извлекает текст из PDF
- [ ] python-docx корректно извлекает текст из DOCX
- [ ] TXT файлы читаются как UTF-8
- [ ] chunk_text разбивает текст на чанки 512 токенов с overlap 50
- [ ] Чанки < 50 токенов объединяются с предыдущим
- [ ] GET /documents возвращает список с пагинацией и фильтром по status
- [ ] DELETE /documents/{id} удаляет запись + файл + чанки (CASCADE)
- [ ] Для role=user все эндпоинты → 403
- [ ] Тесты (test_documents.py) проходят: минимум 10 тестов

### Задача 6: RAG Pipeline (Backend)
**Оценка**: 4 часа

**Что сделать**:
- services/rag/embeddings.py: generate_embedding (OpenAI API), batch embed for chunks
- services/rag/retriever.py: search_similar_chunks (pgvector cosine similarity)
- services/rag/generator.py: generate_answer (Claude API, GPT API), build_prompt
- Интеграция embeddings в document processing pipeline (generate embeddings for each chunk)
- Полный system prompt (см. раздел 19)
- Retry logic для API calls (exponential backoff)
- Unit тесты с мокированными API: test_rag.py

**Definition of Done**:
- [ ] generate_embedding вызывает OpenAI API и возвращает vector(1536)
- [ ] При индексации документа: для каждого чанка генерируется embedding и сохраняется в pgvector
- [ ] search_similar_chunks выполняет cosine similarity search и возвращает top-5 чанков
- [ ] Чанки с similarity < 0.3 отфильтровываются
- [ ] build_prompt собирает: system prompt + context chunks + conversation history (last 6 messages) + question
- [ ] generate_answer вызывает Claude или GPT API в зависимости от выбранной модели
- [ ] Claude: claude-sonnet-4-20250514, temperature 0.1, max_tokens 2048
- [ ] GPT: gpt-4o, temperature 0.1, max_tokens 2048
- [ ] Retry: 1 retry on timeout/5xx с backoff 2s
- [ ] Timeout: 60 секунд
- [ ] Ответ содержит sources metadata (document_id, document_name, chunk_index, relevance_score, snippet)
- [ ] Тесты (test_rag.py) проходят с мокированными API: минимум 8 тестов

### Задача 7: Чат API (Backend)
**Оценка**: 3 часа

**Что сделать**:
- services/chat_service.py: create_conversation, list_conversations, get_conversation, delete_conversation, send_message
- api/v1/chat.py: POST /conversations, GET /conversations, GET /conversations/{id}, DELETE /conversations/{id}, POST /conversations/{id}/messages
- Интеграция с RAG pipeline: send_message → embed question → search → generate → save
- Автогенерация title из первого вопроса (первые 50 символов)
- Soft delete (is_deleted=true)
- Search по title (ILIKE)
- last_message_preview (первые 100 символов последнего assistant message)
- Unit тесты: test_chat.py

**Definition of Done**:
- [ ] POST /conversations создает пустой разговор
- [ ] GET /conversations возвращает список (только свои, is_deleted=false, sorted by updated_at DESC)
- [ ] GET /conversations?search=vacation фильтрует по title
- [ ] GET /conversations/{id} возвращает разговор с сообщениями
- [ ] GET /conversations/{id} чужого → 403
- [ ] DELETE /conversations/{id} ставит is_deleted=true (не удаляет)
- [ ] POST /conversations/{id}/messages: сохраняет user message, вызывает RAG, сохраняет assistant message
- [ ] Первое сообщение: title обновляется на первые 50 символов вопроса
- [ ] conversation.updated_at обновляется при каждом сообщении
- [ ] model и sources сохраняются в assistant message
- [ ] При отсутствии индексированных документов → 503
- [ ] При ошибке AI API → 503
- [ ] Тесты (test_chat.py) проходят: минимум 12 тестов

### Задача 8: Dashboard API (Backend)
**Оценка**: 2 часа

**Что сделать**:
- services/dashboard_service.py: get_stats, get_activity, get_top_questions
- api/v1/dashboard.py: GET /dashboard/stats, GET /dashboard/activity, GET /dashboard/top-questions
- SQL агрегация: COUNT, GROUP BY date, period filtering
- questions_change_percent: сравнение с предыдущим периодом

**Definition of Done**:
- [ ] GET /dashboard/stats возвращает все метрики (total_users, active_users, total_documents, indexed_documents, total_conversations, questions_in_period, questions_change_percent)
- [ ] period=today: считает за сегодня (UTC), сравнивает со вчера
- [ ] period=7d: считает за 7 дней, сравнивает с предыдущими 7 днями
- [ ] period=30d: считает за 30 дней, сравнивает с предыдущими 30 днями
- [ ] GET /dashboard/activity возвращает массив {date, questions} за каждый день периода (включая дни с 0)
- [ ] GET /dashboard/top-questions возвращает 5 самых частых первых вопросов
- [ ] Все эндпоинты: admin-only (403 для user)
- [ ] Тесты: минимум 6 тестов

### Задача 9: Health Check + Swagger (Backend)
**Оценка**: 1 час

**Что сделать**:
- api/v1/health.py: GET /health (проверка DB, Redis, наличие API keys)
- FastAPI swagger: title, description, version, tags
- Описания эндпоинтов через docstrings
- Response model для каждого эндпоинта

**Definition of Done**:
- [ ] GET /health возвращает 200 если все компоненты healthy
- [ ] GET /health возвращает 503 если хотя бы один unhealthy
- [ ] DB check: SELECT 1
- [ ] Redis check: PING
- [ ] AI check: наличие ANTHROPIC_API_KEY и OPENAI_API_KEY в env
- [ ] Swagger UI доступен на /docs
- [ ] Все эндпоинты видны в Swagger с описаниями
- [ ] Response models указаны → Swagger показывает формат ответа

### Задача 10: Страница входа и авторизация (Frontend)
**Оценка**: 3 часа

**Что сделать**:
- contexts/AuthContext.tsx: AuthProvider, useAuth hook
- api/client.ts: Axios instance, interceptors (add auth header, handle 401)
- api/auth.ts: login(), changePassword()
- pages/LoginPage.tsx: полный UI по спецификации (раздел 12.1)
- pages/ChangePasswordPage.tsx: полный UI по спецификации (раздел 12.2)
- components/layout/ProtectedRoute.tsx: auth guard, role guard, must_change_password guard
- Все состояния: default, submitting, error, success
- Валидация форм на клиенте

**Definition of Done**:
- [ ] LoginPage рендерится по спецификации (карточка, поля, кнопка, футер)
- [ ] Валидация при blur: email формат, password not empty
- [ ] Submitting state: кнопка disabled, spinner, "Signing in..."
- [ ] Error state: Alert с текстом ошибки, пароль очищается
- [ ] Success: redirect на /chat (user) или /dashboard (admin)
- [ ] ChangePasswordPage: валидация в реальном времени (3 индикатора)
- [ ] ChangePasswordPage: passwords match проверка при blur на confirm
- [ ] ProtectedRoute: redirect на /login если нет токена
- [ ] ProtectedRoute: redirect на /change-password если must_change_password=true
- [ ] ProtectedRoute: redirect на /chat если role=user пытается открыть admin page
- [ ] Axios interceptor: 401 → удаление токена + redirect на /login + toast
- [ ] Token сохраняется/удаляется из localStorage
- [ ] Автофокус на email при загрузке Login
- [ ] Enter submits form

### Задача 11: Chat UI (Frontend)
**Оценка**: 4 часа

**Что сделать**:
- pages/ChatPage.tsx: двухколоночный layout (sidebar + main)
- components/chat/ChatSidebar.tsx: New Chat, search, conversation list, user menu
- components/chat/ConversationList.tsx: группировка по датам, hover actions
- components/chat/WelcomeScreen.tsx: приветствие + 3 карточки примеров
- components/chat/ChatMessage.tsx: user/assistant, аватары, время, markdown рендер
- components/chat/ChatSources.tsx: блок источников под ответом
- components/chat/ChatInput.tsx: textarea + model selector + send button
- components/chat/ModelSelector.tsx: Claude/GPT select
- components/chat/TypingIndicator.tsx: анимированные точки
- hooks/useConversations.ts, hooks/useMessages.ts: React Query hooks
- Мобильная адаптация: sidebar скрывается, hamburger menu

**Definition of Done**:
- [ ] Chat sidebar: список разговоров с группировкой по датам (Today, Yesterday, Previous 7 Days, Previous 30 Days, Older)
- [ ] Chat sidebar: поиск фильтрует список (debounce 300ms)
- [ ] Chat sidebar: "New Chat" создает разговор и переходит на него
- [ ] Chat sidebar: hover на разговор показывает кнопку удаления
- [ ] Chat sidebar: удаление показывает модалку подтверждения
- [ ] Welcome screen: 3 карточки, клик отправляет вопрос
- [ ] ChatMessage: user сообщения с аватаром (буква), время
- [ ] ChatMessage: assistant сообщения с Bot аватаром, badge модели, markdown рендер
- [ ] ChatSources: pill badges с именами документов, tooltip с relevance
- [ ] ChatInput: auto-resize textarea, max 120px
- [ ] ChatInput: Enter отправляет, Shift+Enter новая строка
- [ ] ChatInput: disabled когда пустой или отправляется
- [ ] ModelSelector: Claude/GPT, значение в localStorage
- [ ] TypingIndicator: 3 bouncing dots + "Thinking..."
- [ ] Автоскролл к последнему сообщению
- [ ] Кнопка "scroll to bottom" при скролле вверх >200px
- [ ] AI error: красный блок с текстом ошибки + Retry button
- [ ] Mobile: sidebar скрывается, hamburger menu, overlay
- [ ] Loading state: spinner "Loading conversation..."
- [ ] Empty conversation: текст "Start a conversation..."

### Задача 12: Admin UI — Dashboard (Frontend)
**Оценка**: 2 часа

**Что сделать**:
- pages/DashboardPage.tsx
- components/dashboard/StatCard.tsx, ActivityChart.tsx, TopQuestions.tsx, RecentConversations.tsx
- hooks/useDashboard.ts
- Recharts для графика
- Skeleton loaders

**Definition of Done**:
- [ ] 4 stat cards с иконками и цветами по спецификации
- [ ] questions_change_percent: зеленый + TrendingUp / красный + TrendingDown
- [ ] Recharts линейный график с tooltip
- [ ] Period toggle: Today / 7 Days / 30 Days
- [ ] Переключение периода обновляет все данные
- [ ] Top Questions таблица (5 строк)
- [ ] Recent Conversations список (5 элементов)
- [ ] Loading state: skeleton loaders для всех компонентов
- [ ] Empty state: "No data yet" в таблицах
- [ ] Responsive: 4→2→1 колонки для cards, 2→1 для bottom row

### Задача 13: Admin UI — Documents (Frontend)
**Оценка**: 3 часа

**Что сделать**:
- pages/DocumentsPage.tsx
- components/documents/DocumentUpload.tsx, DocumentTable.tsx, UploadProgress.tsx, StatusBadge.tsx
- hooks/useDocuments.ts
- Drag & drop (native HTML5, без библиотек)
- Polling для статуса Processing документов (каждые 5 секунд пока есть Processing)

**Definition of Done**:
- [ ] Upload zone: drag & drop + click, dashed border, accept .pdf/.docx/.txt
- [ ] Drag over state: border-primary, bg-primary/5
- [ ] Multiple file upload
- [ ] UploadProgress: progress bar для каждого файла
- [ ] Client-side валидация: тип файла, размер (<50MB)
- [ ] Document table: Name, Type (badge), Size, Status (badge), Chunks, Uploaded, Actions
- [ ] Status badges: Indexed (зеленый), Processing (желтый, pulsating), Error (красный)
- [ ] Error row: tooltip с error_message при hover на Error badge
- [ ] Filter tabs: All / Indexed / Processing / Error с count
- [ ] Пагинация (20 на страницу)
- [ ] Delete: модалка подтверждения
- [ ] Polling: каждые 5 секунд если есть документы со статусом Processing
- [ ] Empty state: иконка + "No documents yet" + кнопка Upload
- [ ] Loading state: skeleton table

### Задача 14: Admin UI — Users (Frontend)
**Оценка**: 2 часа

**Что сделать**:
- pages/UsersPage.tsx
- components/users/UserTable.tsx, AddUserModal.tsx
- hooks/useUsers.ts

**Definition of Done**:
- [ ] Users table: User (avatar+name+email), Role (inline select), Status (toggle), Created, Actions
- [ ] Current user row: bg-primary/5, "(you)" after name
- [ ] Current user: role select disabled, toggle disabled, trash hidden
- [ ] Role change: inline select → сразу PATCH → toast
- [ ] Status toggle: деактивация → модалка подтверждения, активация → сразу PATCH
- [ ] Delete: модалка подтверждения
- [ ] AddUserModal: форма (Name, Email, Role)
- [ ] AddUserModal success: показывает temporary password + Copy button
- [ ] AddUserModal: "This password will only be shown once" warning
- [ ] Пагинация (20 на страницу)
- [ ] Loading state: skeleton table

### Задача 15: Settings Page + Navigation Sidebar (Frontend)
**Оценка**: 2 часа

**Что сделать**:
- pages/SettingsPage.tsx
- pages/NotFoundPage.tsx
- components/layout/Sidebar.tsx (navigation sidebar для non-chat pages)
- components/layout/AppLayout.tsx (sidebar + content layout)
- Мобильная адаптация sidebar

**Definition of Done**:
- [ ] Settings: Profile section (edit name, readonly email, role badge)
- [ ] Settings: Save Changes disabled если имя не изменилось
- [ ] Settings: Change Password section (3 fields, requirements indicators)
- [ ] Settings: toast при успехе, inline alert при ошибке
- [ ] NotFoundPage: "404" + "Page Not Found" + "Go to Chat" button
- [ ] Sidebar: 5 navigation links (Chat, Dashboard, Documents, Users, Settings)
- [ ] Sidebar: admin-only links не рендерятся для user
- [ ] Sidebar: active link highlighted
- [ ] Sidebar: user menu в нижней части (avatar, name, role, logout)
- [ ] Mobile: sidebar collapsed, hamburger button

### Задача 16: Docker и деплой
**Оценка**: 3 часа

**Что сделать**:
- backend/Dockerfile (multi-stage)
- frontend/Dockerfile (multi-stage + nginx)
- docker-compose.yml (все 5 сервисов)
- docker/nginx/nginx.conf
- .env.example (финальная версия)
- Alembic миграция при старте backend (entrypoint: alembic upgrade head && uvicorn)

**Definition of Done**:
- [ ] `docker-compose build` собирает все образы без ошибок
- [ ] `docker-compose up -d` поднимает все 5 сервисов
- [ ] Приложение доступно на http://localhost (через nginx)
- [ ] /api/* проксируется на backend
- [ ] Swagger доступен на http://localhost/docs
- [ ] GET /api/v1/health возвращает 200 (все компоненты healthy)
- [ ] Login работает через nginx
- [ ] Загрузка файлов работает через nginx (client_max_body_size 55M)
- [ ] Данные БД сохраняются после рестарта (volume postgres_data)
- [ ] Uploads сохраняются после рестарта (volume uploads)
- [ ] `docker-compose logs -f backend` показывает JSON логи
- [ ] Non-root user в backend контейнере
- [ ] Healthcheck в docker-compose для postgres, redis, backend

### Задача 17: GitHub Actions CI/CD
**Оценка**: 2 часа

**Что сделать**:
- .github/workflows/ci.yml
- .github/workflows/cd.yml

**Definition of Done**:
- [ ] CI trigger: push to main/develop, PR to main
- [ ] CI backend: ruff check, ruff format --check, pytest
- [ ] CI frontend: eslint, tsc --noEmit, npm run build
- [ ] CI docker: build images (no push)
- [ ] CI: pip cache, npm cache
- [ ] CD trigger: push to main only
- [ ] CD: login to GHCR, build and push (tags: latest + sha)
- [ ] CI/CD yaml files синтаксически корректны

### Задача 18: README, скриншоты, финализация
**Оценка**: 2 часа

**Что сделать**:
- README.md по формату из раздела 45
- Скриншоты (5 штук) — создать seed data, сделать скриншоты
- LICENSE (MIT)
- ARCHITECTURE.md в docs/
- Финальная проверка: docker-compose up, полный flow

**Definition of Done**:
- [ ] README: Overview, Features, Screenshots, Tech Stack, Architecture, Quick Start, API, Env Variables, Development, Project Structure, Future Improvements, License
- [ ] 5 скриншотов с реалистичными данными (не lorem ipsum)
- [ ] LICENSE (MIT) в корне
- [ ] docs/ARCHITECTURE.md
- [ ] Полный flow проверен: login → upload → chat → dashboard
- [ ] Нет TODO, нет заглушек, нет хардкодов

---

## 38. План тестирования

### Unit тесты (pytest + httpx + pytest-asyncio)

**conftest.py fixtures**:
- `test_db`: тестовая PostgreSQL (testcontainers или отдельная БД), Alembic migrations
- `test_client`: AsyncClient (httpx) с FastAPI TestClient
- `admin_token`: JWT для admin user (fixture создает admin)
- `user_token`: JWT для обычного user
- `sample_document`: загруженный документ с чанками (мокированные embeddings)

**test_auth.py** (минимум 10 тестов):
1. Login с валидными данными → 200 + JWT
2. Login с неверным паролем → 401
3. Login с несуществующим email → 401
4. Login с деактивированным аккаунтом → 403
5. Login с пустым email → 422
6. Login с пустым паролем → 422
7. Change password с валидными данными → 200
8. Change password: неверный текущий пароль → 401
9. Change password: слабый новый пароль → 400
10. Change password: пароли не совпадают → 400
11. Change password: новый = текущему → 400
12. Доступ к protected route без токена → 401
13. Доступ к protected route с expired токеном → 401

**test_users.py** (минимум 12 тестов):
1. GET /users как admin → 200 + list
2. GET /users как user → 403
3. POST /users как admin → 201 + temporary_password
4. POST /users с дублирующимся email → 409
5. POST /users как user → 403
6. PATCH /users/{id}: обновить имя → 200
7. PATCH /users/{id}: обновить роль → 200
8. PATCH свою роль → 403
9. PATCH свой is_active=false → 403
10. DELETE /users/{id} → 204
11. DELETE себя → 403
12. DELETE последнего admin → 403
13. DELETE несуществующего → 404
14. PATCH /users/me/profile → 200

**test_documents.py** (минимум 10 тестов):
1. POST /documents с PDF → 201
2. POST /documents с DOCX → 201
3. POST /documents с TXT → 201
4. POST /documents с .exe → 400
5. POST /documents без файла → 400
6. POST /documents как user → 403
7. GET /documents → 200 + list
8. GET /documents?status=indexed → filtered list
9. DELETE /documents/{id} → 204
10. DELETE несуществующего → 404

**test_chat.py** (минимум 12 тестов):
1. POST /conversations → 201
2. GET /conversations → 200 + list (только свои)
3. GET /conversations?search=test → filtered list
4. GET /conversations/{id} → 200 + messages
5. GET чужого conversations/{id} → 403
6. DELETE /conversations/{id} → 204 (soft delete)
7. GET удаленного conversations/{id} → 404
8. POST /conversations/{id}/messages → 200 + user + assistant messages (mocked RAG)
9. POST /messages: пустой content → 400
10. POST /messages: content > 4000 chars → 400
11. POST /messages: невалидная модель → 400
12. POST /messages: первое сообщение → title обновляется

**test_rag.py** (минимум 8 тестов, мокированные API):
1. chunk_text: текст 1000 токенов → 2 чанка с overlap
2. chunk_text: текст 50 токенов → 1 чанк
3. chunk_text: текст 20 токенов → объединяется (не создается)
4. generate_embedding: mock OpenAI → vector(1536)
5. search_similar_chunks: pgvector query → top-5 results
6. search_similar_chunks: фильтр similarity < 0.3
7. generate_answer: mock Claude → answer + sources
8. generate_answer: mock GPT → answer + sources
9. build_prompt: system + context + history + question

---

## 39. Все Edge Cases

### Аутентификация
1. Пользователь вводит email с пробелами → trim перед проверкой
2. Пользователь вводит email в uppercase → lowercase перед проверкой
3. JWT token истек → 401, клиент redirect на login
4. JWT token подписан другим ключом → 401
5. JWT token с несуществующим user_id (user удален) → 401
6. Одновременный login с двух устройств → оба получают токены, оба работают
7. Пароль ровно 8 символов → принимается
8. Пароль 128 символов → принимается
9. Пароль 129 символов → отклоняется
10. Пароль только из букв → отклоняется
11. Пароль только из цифр → отклоняется
12. Первый admin при пустой БД: ADMIN_EMAIL/ADMIN_DEFAULT_PASSWORD не заданы → приложение не запускается (ошибка конфигурации)

### Чат
13. Пользователь отправляет пустое сообщение (только пробелы) → 400 (trim + check)
14. Сообщение ровно 4000 символов → принимается
15. Сообщение 4001 символ → 400
16. В БД нет ни одного индексированного документа → 503 "No documents have been indexed yet"
17. RAG не нашел релевантных чанков (все similarity < 0.3) → AI отвечает "I don't have enough information..."
18. Claude API вернул timeout → retry 1 раз, если опять timeout → 503
19. Claude API вернул 429 (rate limit) → 503 "AI service is temporarily unavailable"
20. Claude API вернул 500 → retry 1 раз, если опять 500 → 503
21. OpenAI API недоступен → аналогично Claude
22. Пользователь отправляет сообщение в удаленный (soft deleted) разговор → 404
23. Пользователь отправляет сообщение в чужой разговор → 403
24. Очень длинный ответ AI (>10000 символов) → сохраняется полностью, рендерится с прокруткой
25. Пользователь быстро отправляет 5 сообщений подряд → каждое обрабатывается последовательно (нет race condition)
26. Markdown в ответе AI: таблицы, code blocks, lists → рендерится через react-markdown
27. Первый вопрос длиннее 50 символов → title = первые 50 символов + "..."
28. Первый вопрос короче 50 символов → title = весь вопрос

### Документы
29. PDF без текста (сканированное изображение) → пустой текст → 0 чанков → status=indexed, chunk_count=0
30. PDF с паролем → PyPDF2 exception → status=error, error_message="Failed to read PDF: file is password protected"
31. Поврежденный PDF (не читается) → status=error, error_message="Failed to process file: invalid PDF format"
32. DOCX с только изображениями → пустой текст → 0 чанков
33. TXT файл с нестандартной кодировкой (не UTF-8) → попытка декодировать с fallback latin-1, если не удается → error
34. Очень большой документ (50MB PDF, 1000 страниц) → обрабатывается в background, не блокирует API
35. Файл с пустым содержимым → 0 чанков, status=indexed (не ошибка)
36. Upload двух файлов с одинаковым original_name → 409 на втором (в MVP duplicate names не разрешены)
37. Удаление документа с чанками, на которые ссылаются sources в messages → чанки удаляются (CASCADE), sources в messages сохраняются как JSONB (orphaned references OK)
38. Одновременная загрузка 10 файлов → все принимаются, обрабатываются последовательно в background
39. Upload файла ровно 50MB → принимается
40. Upload файла 50MB + 1 byte → 413

### Пользователи
41. Создание пользователя с email в uppercase → приводится к lowercase перед сохранением
42. Создание пользователя с пробелами в имени → допускается (имя может содержать пробелы)
43. Имя ровно 2 символа → принимается
44. Имя 1 символ → 422
45. Имя 100 символов → принимается
46. Имя 101 символ → 422
47. Удаление admin, когда есть ровно 2 admin-а → разрешено (1 останется)
48. Деактивированный пользователь пытается login → 403 (не 401, чтобы отличить от неверного пароля)
49. Admin меняет роль пользователя на admin → OK
50. Admin меняет роль admin на user → OK (если это не последний admin — проверять при смене роли тоже)

### Dashboard
51. Новый проект: 0 пользователей (кроме admin), 0 документов → все метрики 0, graph пустой
52. questions_change_percent: нет данных за прошлый период → null (не 0 и не Infinity)
53. Top questions: меньше 5 уникальных вопросов → возвращает сколько есть

### UI
54. Экран шириной < 375px → минимальная поддерживаемая ширина, не ломается
55. Очень длинное имя пользователя (100 символов) → truncate в sidebar и таблице
56. Очень длинное имя документа → truncate в таблице с ellipsis
57. Очень длинный вопрос в Top Questions → truncate с ellipsis
58. Браузер без localStorage (incognito mode некоторые) → приложение работает, но без persistence (каждый refresh → login)
59. Два tab-а в одном браузере → оба работают, logout в одном → другой получит 401 при следующем запросе → redirect на login

---

## 40. Требования к производительности

| Операция | Целевое время | Как обеспечивается |
|----------|---------------|--------------------|
| Login | < 300ms | bcrypt (cost 12) ~250ms |
| Список разговоров (50) | < 100ms | индекс на user_id + is_deleted |
| Открытие разговора (20 сообщений) | < 100ms | индекс на conversation_id + created_at |
| Vector search (100k чанков) | < 100ms | HNSW index |
| Полный RAG pipeline | < 15s | зависит от LLM API (3-10s) |
| Загрузка файла (HTTP ответ) | < 1s | файл сохраняется, обработка в background |
| Обработка PDF 10 страниц | < 10s | background task |
| Обработка PDF 100 страниц | < 60s | background task |
| Обработка PDF 500 страниц | < 300s | background task |
| Dashboard stats | < 200ms | агрегирующие SQL запросы с индексами |
| Список документов (100) | < 100ms | индексы, пагинация |
| Список пользователей (100) | < 100ms | пагинация |
| Frontend initial load | < 3s | Vite build, code splitting, gzip |
| Frontend navigation (SPA) | < 100ms | React Router, client-side |
| React Query cache | 5 min stale time | configurable per query |

---

## 41. Требования к масштабируемости

**MVP рассчитан на**:
- До 100 одновременных пользователей
- До 500 документов (до 50MB каждый)
- До 100,000 чанков в pgvector
- До 10,000 разговоров
- До 100,000 сообщений
- Один сервер (single instance)

**Bottlenecks в MVP**:
- Background tasks: FastAPI BackgroundTasks — один worker, документы обрабатываются последовательно
- pgvector HNSW: до 1M vectors без проблем
- PostgreSQL: single instance, до 100 concurrent connections

**Post-MVP масштабирование**:
- Celery + Redis для очереди задач (параллельная обработка документов)
- Горизонтальное масштабирование backend (stateless, JWT, shared DB)
- Read replicas PostgreSQL
- S3/MinIO для хранения файлов (вместо локального диска)
- Redis для кеширования частых dashboard запросов
- pgvector IVFFlat index при >1M vectors

---

## 42. Требования к UX/UI

### Цветовая схема
- Фон приложения: `bg-white` (main), `bg-slate-50` (secondary)
- Chat sidebar: `bg-slate-900` (темная)
- Navigation sidebar: `bg-white` с `border-r border-slate-200`
- Primary color: shadcn default (slate-900 / white)
- Accent colors: используются только для badges и иконок в stat cards

### Типографика
- Шрифт: Inter (Google Fonts, подключается в index.html)
- Base size: 14px (text-sm по умолчанию для контента)
- Headings: text-2xl font-bold для H1 на страницах
- Моноширинный: JetBrains Mono (для code blocks и паролей)

### Адаптивность
- Desktop: > 1024px — все колонки, sidebar видна
- Tablet: 768-1024px — sidebar collapsible, grid перестраивается
- Mobile: < 768px — sidebar скрыта, hamburger menu, stack layout
- Минимальная ширина: 375px (iPhone SE)

### Компоненты и поведение
- Все кнопки: cursor-pointer, hover state (осветление/затемнение)
- Disabled состояние: opacity-50, cursor-not-allowed
- Focus: visible focus ring (outline) для accessibility
- Transitions: 200ms ease для hover/active states
- Skeleton loaders: pulsating серые прямоугольники (Tailwind animate-pulse)
- Toast: sonner, bottom-right, 4 секунды, max 3 одновременно
- Таблицы: hover на строку bg-slate-50
- Модальные окна: overlay bg-black/50, centered, escape to close, focus trap
- Scroll: стандартный браузерный scrollbar (не кастомный)

### Доступность (Accessibility)
- Все input-ы имеют label (htmlFor)
- Все кнопки с иконками имеют aria-label
- Focus ring видим (не убираем outline)
- Contrast ratio: min 4.5:1 для текста
- Tab navigation работает для всех интерактивных элементов
- Role="dialog" для модальных окон
- Alert role для toast notifications
- aria-live="polite" для typing indicator

### Темная тема
- НЕ реализуется в MVP
- В Settings есть toggle Light/Dark — НЕ рендерить его вообще (не заглушка, а просто отсутствие)
- Готовность: использовать CSS variables от shadcn/ui для будущей поддержки

---

## 43. Что должно попасть на скриншоты GitHub

5 обязательных скриншотов (в README в формате image gallery):

1. **01-login.png**: чистая форма входа с логотипом, на светлом фоне
2. **02-chat.png**: активный разговор с 3-4 сообщениями (user + AI), видны источники, sidebar с 5-7 разговорами, выбрана модель Claude
3. **03-dashboard.png**: все 4 stat cards с ненулевыми данными, график активности за 30 дней (восходящий тренд), top questions (5 строк), recent conversations
4. **04-documents.png**: таблица с 5-8 документами разных типов и статусов, зона drag & drop сверху
5. **05-mobile-chat.png**: чат на экране 375px (iPhone SE), без sidebar, полноэкранный чат

**Требования к seed данным для скриншотов**:
- Минимум 3 пользователя (1 admin, 2 users)
- Минимум 5 документов (3 indexed, 1 processing, 1 error)
- Минимум 5 разговоров с сообщениями
- Реалистичные данные (не "Test document", а "Employee Handbook Q3 2026.pdf")
- Английский язык в данных (portfolio для зарубежных клиентов)

---

## 44. Что показать в демо-видео (60-90 сек)

| Время | Действие | Экран |
|-------|----------|-------|
| 0-5s | Открыть приложение, видна страница Login | Login |
| 5-10s | Ввести email/пароль admin, нажать Sign In | Login → Dashboard |
| 10-18s | Показать Dashboard: карточки, график, top questions | Dashboard |
| 18-28s | Перейти в Documents, drag & drop PDF файл, показать Processing → Indexed | Documents |
| 28-45s | Перейти в Chat, задать вопрос "What is the remote work policy?", получить ответ с источниками, задать follow-up "How many days per week?" | Chat |
| 45-52s | Выбрать GPT модель, задать еще вопрос, показать разницу в badge | Chat |
| 52-60s | Перейти в Users, создать нового пользователя, показать temporary password | Users |
| 60-70s | Logout, login как обычный пользователь, показать что нет admin-пунктов в sidebar | Chat (user) |
| 70-80s | Открыть DevTools, resize на мобильный, показать мобильную версию | Chat (mobile) |
| 80-90s | Открыть /docs (Swagger UI), показать список эндпоинтов, вызвать /health | Swagger |

**Важно**: видео должно быть записываемо без звука. Все действия должны быть понятны визуально.

---

## 45. Что описать в README

README.md структура (финальная):

```markdown
# AI Support Agent

> Enterprise AI assistant powered by RAG for internal knowledge management

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## Overview
AI Support Agent is a self-hosted enterprise platform that turns your company documents into an intelligent knowledge base. Employees can ask questions in natural language and receive accurate answers with source citations, powered by RAG (Retrieval-Augmented Generation).

## Features
- **AI Chat with RAG** — Ask questions, get answers based on your company documents with source citations
- **Multiple AI Models** — Switch between Claude (Anthropic) and GPT (OpenAI) per conversation
- **Document Management** — Upload PDF, DOCX, TXT files with automatic processing and indexing
- **Admin Dashboard** — Usage analytics, activity charts, and top questions
- **User Management** — Role-based access control (Admin/User), user creation with temporary passwords
- **Self-Hosted** — Full control over your data, deploy with Docker in minutes
- **Production Ready** — JWT auth, structured logging, health checks, CI/CD

## Screenshots
[5 скриншотов в gallery формате]

## Tech Stack
**Backend**: Python 3.13 · FastAPI · SQLAlchemy · PostgreSQL · pgvector · Redis
**Frontend**: React 18 · TypeScript · Vite · TailwindCSS · shadcn/ui · React Query
**AI/ML**: Anthropic Claude · OpenAI GPT · text-embedding-3-small · RAG
**DevOps**: Docker · Docker Compose · Nginx · GitHub Actions

## Architecture
[Текстовая диаграмма из раздела 16]

## Quick Start

### Prerequisites
- Docker & Docker Compose v2
- Anthropic API Key ([get one here](https://console.anthropic.com))
- OpenAI API Key ([get one here](https://platform.openai.com))

### Installation
git clone https://github.com/username/ai-support-agent.git
cd ai-support-agent
cp .env.example .env
# Edit .env — add your API keys and change default passwords
docker compose up -d
# Open http://localhost
# Default admin: admin@example.com / (password from .env)

## API Documentation
Interactive API docs (Swagger UI): http://localhost/docs

### Key Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/login | Authenticate user |
| POST | /api/v1/conversations/{id}/messages | Send message & get AI response |
| POST | /api/v1/documents | Upload document |
| GET | /api/v1/dashboard/stats | Dashboard statistics |
| GET | /api/v1/health | Health check |

## Environment Variables
[Таблица из .env.example с описаниями]

## Development

### Local Development (without Docker)
#### Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload

#### Frontend
cd frontend
npm install
npm run dev

### Running Tests
cd backend
pytest -v --cov=app

### Linting
cd backend && ruff check . && ruff format --check .
cd frontend && npm run lint && npx tsc --noEmit

## Project Structure
[Сокращенное дерево директорий]

## Future Improvements
- [ ] Streaming responses (Server-Sent Events)
- [ ] Slack & Microsoft Teams integration
- [ ] SSO support (SAML, OIDC)
- [ ] Response feedback (thumbs up/down) with fine-tuning
- [ ] Multi-language UI
- [ ] Advanced analytics & reporting
- [ ] Custom AI prompts per department
- [ ] Document auto-refresh on update
- [ ] Export conversations to PDF

## License
MIT — see [LICENSE](LICENSE) for details.
```

---

## Приложение A: .env.example (полный)

```env
# ============================================
# AI Support Agent — Environment Configuration
# ============================================
# Copy this file to .env and fill in the values.
# Lines starting with # are comments.

# ---------- Application ----------
APP_NAME=AI Support Agent
APP_VERSION=1.0.0
DEBUG=false
# Secret key for JWT signing. Generate with: openssl rand -hex 32
SECRET_KEY=CHANGE_ME_generate_with_openssl_rand_hex_32
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# ---------- Database ----------
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/ai_support_agent
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME_use_strong_password
POSTGRES_DB=ai_support_agent

# ---------- Redis ----------
REDIS_URL=redis://redis:6379/0

# ---------- AI API Keys ----------
# Get your key at: https://console.anthropic.com
ANTHROPIC_API_KEY=CHANGE_ME
# Get your key at: https://platform.openai.com/api-keys
OPENAI_API_KEY=CHANGE_ME
# Default model for new conversations: claude or gpt
DEFAULT_MODEL=claude
# OpenAI embedding model
EMBEDDING_MODEL=text-embedding-3-small

# ---------- Authentication ----------
# First admin account (created on first startup)
ADMIN_EMAIL=admin@example.com
ADMIN_NAME=Admin
# Change this! Admin must change password on first login.
ADMIN_DEFAULT_PASSWORD=CHANGE_ME
# JWT token expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ---------- CORS ----------
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost,http://localhost:3000,http://localhost:5173

# ---------- File Upload ----------
# Maximum upload file size in megabytes
MAX_FILE_SIZE_MB=50
# Directory for uploaded files (relative to backend/)
UPLOAD_DIR=./uploads

# ---------- Rate Limiting ----------
# General API rate limit (requests per minute per user)
RATE_LIMIT_PER_MINUTE=60
# Login rate limit (requests per minute per IP)
LOGIN_RATE_LIMIT_PER_MINUTE=10
```

---

## Приложение B: requirements.txt (backend)

```
fastapi==0.115.*
uvicorn[standard]==0.32.*
sqlalchemy[asyncio]==2.0.*
asyncpg==0.30.*
alembic==1.14.*
pydantic==2.10.*
pydantic-settings==2.7.*
python-jose[cryptography]==3.3.*
passlib[bcrypt]==1.7.*
python-multipart==0.0.*
httpx==0.28.*
structlog==24.*
slowapi==0.1.*
redis==5.*
pgvector==0.3.*
anthropic==0.42.*
openai==1.59.*
tiktoken==0.8.*
pypdf2==3.0.*
python-docx==1.1.*
react-markdown==9.*
```

## Приложение C: package.json основные зависимости (frontend)

```json
{
  "dependencies": {
    "react": "^18.3",
    "react-dom": "^18.3",
    "react-router-dom": "^6.28",
    "@tanstack/react-query": "^5.62",
    "axios": "^1.7",
    "lucide-react": "^0.460",
    "recharts": "^2.14",
    "react-markdown": "^9.0",
    "remark-gfm": "^4.0",
    "sonner": "^1.7",
    "clsx": "^2.1",
    "tailwind-merge": "^2.6",
    "date-fns": "^4.1"
  },
  "devDependencies": {
    "typescript": "^5.7",
    "vite": "^6.0",
    "@types/react": "^18.3",
    "@types/react-dom": "^18.3",
    "@vitejs/plugin-react": "^4.3",
    "tailwindcss": "^3.4",
    "postcss": "^8.4",
    "autoprefixer": "^10.4",
    "eslint": "^9.16",
    "@typescript-eslint/eslint-plugin": "^8.18",
    "prettier": "^3.4"
  }
}
```

---

**Конец PRD-01: AI Support Agent v2.0**

Этот документ является единственным источником требований для разработки.
Все решения приняты. Все edge cases описаны. Все состояния UI определены.
Разработчик не должен задавать ни одного уточняющего вопроса.

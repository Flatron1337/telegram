# 🎨 Telegram Theme Creator Bot

Асинхронный Telegram-бот на **Python 3.11+** и **aiogram 3**, который анализирует цветовую палитру загруженных изображений и автоматически генерирует гармоничные, контрастные темы для **Telegram Desktop** (`.tdesktop-theme`) и **Telegram Android** (`.attheme`) со встроенными обоями.

---

## 🌟 Ключевые особенности

- 🎯 **Интеллектуальный анализ цветов**: Алгоритм k-means кластеризации с инициализацией k-means++ для точного выделения акцентных и фоновых тонов.
- 👁️ **Гарантия читаемости (WCAG 2.1)**: Расчёт относительной яркости и коэффициента контрастности гарантирует четкий контраст текста на пузырях сообщений и фонах (соответствие AA/AAA).
- 📦 **Нативные форматы тем**:
  - **Telegram Desktop**: архив `.tdesktop-theme`, содержащий `colors.tdesktop-palette` и сжатые обои `background.jpg`.
  - **Telegram Android**: файл `.attheme` с точными 32-битными знаковыми ARGB-значениями и поддержкой обоев `wallpaper.jpg`.
- ⚡ **Неблокирующий Event Loop**: Все тяжелые операции Pillow и кодирования изображений вынесены в рабочий пул потоков через `asyncio.to_thread`.
- 🛡️ **Конфигурация через Pydantic Settings**: Типизированные настройки с маскированием секретов (`SecretStr`) и автоматической загрузкой из `.env`.
- 🧪 **Анти-слоп качество**: 100/100 по шкале `npx aislop`, полное покрытие модульными тестами.

---

## 🚀 Быстрый старт

### 1. Клонирование и настройка окружения

```bash
git clone https://github.com/Flatron1337/telegram.git
cd telegram/theme_creator
```

#### Вариант А: Использование `uv` (рекомендуется)
```bash
# Установка зависимостей
uv sync

# Запуск бота
uv run python -m bot.main
```

#### Вариант Б: Стандартный `pip`
```bash
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate

# Только прод-зависимости:
pip install -r requirements.txt

# Либо с зависимостями для разработки и тестов:
pip install -r requirements-dev.txt

# Запуск бота
python -m bot.main
```

---

### 2. Конфигурация `.env`

Создайте файл `.env` на основе примера:
```bash
cp .env.example .env
```

Укажите токен, полученный у [@BotFather](https://t.me/BotFather):
```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567
MAX_FILE_SIZE_MB=15
ENVIRONMENT=development
```

---

## 🧪 Тестирование и линтинг

Запуск всех модульных тестов:
```bash
python -m pytest
```

Проверка форматирования и линтинга через `ruff`:
```bash
python -m ruff check .
python -m ruff format --check .
```

Проверка качества кода через `aislop`:
```bash
npx aislop scan
```

---

## 🐳 Запуск через Docker

```bash
docker compose up -d --build
```

---

## 📂 Структура проекта

```text
theme_creator/
├── bot/
│   ├── config.py                 # Pydantic Settings конфигурация
│   ├── main.py                   # Точка входа aiogram 3 бота
│   ├── handlers/
│   │   ├── common.py             # Команды /start и /help
│   │   └── theme.py              # Обработка фото, документов и инлайн-кнопок
│   ├── keyboards/
│   │   └── theme_keyboards.py    # Инлайн-клавиатура выбора тем
│   ├── models/
│   │   └── color.py              # Классы Color, PaletteTheme, WCAG контраст, ARGB
│   └── services/
│       ├── color_extractor.py    # K-Means анализ, подбор цветов, рендер превью
│       ├── session_store.py      # In-memory сессионное хранилище тем с TTL
│       ├── theme_service.py      # Асинхронный фасад (asyncio.to_thread)
│       └── theme_generators/
│           ├── tdesktop.py       # Генератор .tdesktop-theme и colors.tdesktop-palette
│           └── android.py        # Генератор .attheme
├── tests/                        # Набор модульных тестов (pytest)
├── requirements.txt              # Production-зависимости
├── requirements-dev.txt          # Development/тестовые зависимости
├── pyproject.toml                # Конфигурация проекта, ruff и pytest
├── Dockerfile                    # Docker-образ
├── docker-compose.yml            # Сервис docker-compose
└── todo.md                       # Трекер задач и фаз проекта
```

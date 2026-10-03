# План реализации Telegram Theme Creator Bot

## Статус проекта
- [x] Инициализация репозитория и базовой структуры
- [x] Фаза 1: Движок извлечения цветов и генерации палитр (Завершено · 100/100 aislop)
- [x] Фаза 2: Генераторы файлов тем (TDesktop и Android) (Завершено · 100/100 aislop)
- [x] Фаза 3: Реализация Telegram-бота на aiogram 3 (Завершено · 100/100 aislop)
- [x] Фаза 4: Комплексное тестирование, документация и релиз (Завершено · 100/100 aislop)
- [x] Фаза 5: Улучшение генератора Android-тем (.attheme) и эргономики (Завершено · 100/100 aislop)
- [x] Фаза 6: Режимы экспорта и расширение настроек бота (Завершено · 100/100 aislop)
- [x] Фаза 7: Тестирование новых функций и контроль качества (Завершено · 100/100 aislop)
- [x] Фаза 8: Поддержка Telegram iOS (.tgios-theme) и мультиплатформенный экспорт (Завершено · 100/100 aislop)
- [x] Фаза 9: Telegram Mini App (Theme Studio) и функция прозрачности сообщений (Завершено · 100/100 aislop)

---


## Детальные задачи по фазам

### Фаза 1: Движок анализа изображений и генерации гармоничных палитр
- [x] Базовые конфигурационные файлы (`pyproject.toml`, `requirements.txt`, `.gitignore`)
- [x] Модели данных палитры (`Color`, `DominantColor`, `PaletteTheme`, WCAG 2.1 contrast, ARGB)
- [x] Алгоритм извлечения доминантных цветов из изображения (ускоренный k-means с k-means++ инициализацией)
- [x] Генератор светлой и тёмной темы на основе доминантных цветов:
  - Автоматический выбор акцентного цвета (primary/accent)
  - Подбор читаемого контрастного фона (background)
  - Генерация пузырей сообщений (incoming/outgoing bubbles)
  - Вычисление цветов текста и вспомогательных элементов с гарантией контраста
- [x] Генератор графического превью палитры (сводная карточка чата и цветов в PNG)
- [x] Unit-тесты для цветового движка и алгоритмов сжатия/кластеризации (`10/10 passed`)
- [x] Проверка качества кода через `npx aislop scan` (100 / 100 Healthy, 0 issues) и `pytest`

### Фаза 2: Генераторы тем для платформ Telegram
- [x] Спецификация и генератор палитры для Telegram Desktop (`colors.tdesktop-palette` + `colors.tdesktop-theme`)
- [x] Сборщик архива `.tdesktop-theme` (двойная палитра + сжатый `background.jpg`)
- [x] Полное покрытие токенов Telegram Desktop (480+ ключей на основе эталонной темы `KfrM3c2J_@my_themes_bot.tdesktop-theme`):
  - Окна, заголовки, оверлеи, кнопки (`windowBg`, `activeButton*`, `lightButton*`)
  - История чатов, диалоги, сообщения, пузыри (`history*`, `msgIn*`, `msgOut*`, `dialogs*`)
  - Боковые панели, папки, бейджи, звонки и медиаплеер (`sideBar*`, `call*`, `mediaview*`)
- [x] Спецификация и генератор формата Telegram Android (`.attheme`) с ARGB-ключами
- [x] Поддержка встроенных фоновых обоев в `.attheme` (нативные маркеры `WPS` / `WPE` с JPEG)
- [x] Полное покрытие токенов Telegram Android (550+ ключей на основе `l0X4KzrY_@my_themes_bot.attheme` и `NmscYuQc_@my_themes_bot (2).attheme`):
  - Проверена новая версия `NmscYuQc_@my_themes_bot (2).attheme` — 100% токенов уже учтены
  - Контекстные меню (`actionBarDefaultSubmenu*`) — устранено выпадение в белый фон
  - Аватары и заглушки профилей (`avatar_*`) — устранён дефолтный синий цвет
  - Диалоги и кнопки (`dialog*`) — устранено выпадение в дефолтный синий
  - Плееры, свитчи, бейджи, инпут-панели и вкладки папок (`actionBarTab*`, `player_*`, `switch*`)
- [x] Модульные тесты генераторов тем и проверка структуры архивов (`tests/test_theme_generators.py`)
- [x] Проверка качества кода через `npx aislop scan` (100 / 100 Healthy, 0 issues)

### Фаза 3: Telegram Bot на aiogram 3
- [x] Конфигурация приложения через `pydantic-settings` (`bot/config.py`, `tests/test_config.py`, `.env.example`)
- [x] Асинхронный сервис-координатор создания тем с вызовом CPU-операций через `asyncio.to_thread` (`ThemeService`)
- [x] Хэндлеры бота: `/start`, `/help` ([bot/handlers/common.py](file:///e:/telegram/theme_creator/bot/handlers/common.py))
- [x] Обработка входящих фото и несжатых изображений (документов) ([bot/handlers/theme.py](file:///e:/telegram/theme_creator/bot/handlers/theme.py))
- [x] Инлайн-клавиатура выбора опций и переключения превью ([bot/keyboards/theme_keyboards.py](file:///e:/telegram/theme_creator/bot/keyboards/theme_keyboards.py))
- [x] In-memory сессионное хранилище тем с автоматической очисткой по TTL (`ThemeSessionStore`)
- [x] Отправка сгенерированных файлов тем (.tdesktop-theme, .attheme) и превью-карточки пользователю
- [x] Защита от превышения лимитов размера файла и обработка ошибок валидации
- [x] Модульные тесты хэндлеров, клавиатур и сессий (`tests/test_handlers.py`, `tests/test_session_store.py`)

### Фаза 4: Тестирование, полировка и релиз
- [x] Полный набор модульных и интеграционных тестов (`23 passed`)
- [x] Шаблон `.env.example` и подробная документация `README.md`
- [x] Разделение зависимостей `requirements.txt` (prod) и `requirements-dev.txt` (dev), конфигурация `pyproject.toml`
- [x] Конфигурация Docker-развёртывания (`Dockerfile`, `docker-compose.yml`, `.dockerignore`)
- [x] Проверка соответствия стандартам `npx aislop scan` (100 / 100 Healthy, 0 issues) и линтера `ruff`

### Фаза 5: Улучшение генератора Android-тем (.attheme) и эргономики
- [x] Добавление метаданных темы в заголовок файла (`#name=...`, `#author=...`, `#dark=true`)
- [x] Расширение и обновление набора ключей Telegram Android:
  - Вкладки и бейджи папок (`actionBarTabActiveText`, `actionBarTabUnactiveText`, `actionBarTabLine`, `actionBarTabUnread*`)
  - Иконки контекстных подменю тулбара (`actionBarDefaultSubmenuItemIcon`)
  - Явные цвета текста входящих и исходящих сообщений (`chat_inText`, `chat_outText`)
  - Реакции, бейджи и интерактивные статусы (`chat_reactions*`, `reactions_bubble*`)
- [x] Оптимизация контрастности по стандарту WCAG 2.1:
  - Автоматический пересчёт контраста для `actionBarDefaultIcon`, `actionBarDefaultSearch`, `actionBarDefaultSubtitle` на фоне тулбара (гарантия контраста >= 4.5:1)
  - Ликвидация монотонности: разделение базового акцента, интерактивных кнопок и ссылок
- [x] Коррекция альфа-каналов селекторов нажатия (Ripple Effects):
  - Замена непрозрачных селекторов (`actionBarDefaultSelector`, `actionBarActionModeDefaultSelector`) на полупрозрачные слои (15–25% альфы) для плавной нативной анимации тапа
- [x] Очистка устаревших токенов (удаление неиспользуемых `chat_inAudioProgress`, `chat_outAudioProgress` и устаревших селекторов Android 4–5)

### Фаза 6: Режимы экспорта и расширение настроек бота
- [x] Поддержка легковесного режима тем без обоев (Lightweight Theme):
  - Генерация чистого `.attheme` без блока `WPS...WPE` (~15 КБ вместо 240 КБ), позволяющего пользователю сохранять собственные обои чата
- [x] Интерактивные настройки экспорта в боте:
  - Инлайн-кнопки переключения режима: «С обоями / Без обоев»
  - Настройка кастомного имени темы и автора перед скачиванием
- [x] Готовые стилистические пресеты (Theme Presets):
  - Добавление пресетов в стиле Cyberpunk Neon (Rem / Ram), AMOLED Pure Black, Minimalist Pastel
- [x] Поддержка генерации парных тем (Dual-theme Pack: Desktop + Android в одном сообщении или архиве)

### Фаза 7: Тестирование новых функций и контроль качества
- [x] Unit-тесты для метаданных `#name`, `#author`, `#dark` в `.attheme`
- [x] Тесты генерации легковесных `.attheme` без WPS/WPE и полных с JPEG
- [x] Валидация контрастности всех семантических ключей тулбара по формуле WCAG 2.1
- [x] Проверка регрессий: прогон `pytest` и `npx aislop scan` (поддержание 100/100 Healthy)

### Фаза 8: Поддержка Telegram iOS (.tgios-theme) и мультиплатформенный экспорт
- [x] Анализ и реверс-инжиниринг формата Telegram iOS на базе эталона `mnxtbpz_@my_themes_bot.tgios-theme`
- [x] Добавление зависимости `pyyaml>=6.0.0` в `requirements.txt` и `pyproject.toml`
- [x] Разработка генератора тем iOS (`bot/services/theme_generators/ios.py` -> `IosThemeGenerator`):
  - Полноценная поддержка YAML-структуры (318 семантических токенов: root, list, chatList, chat, actionSheet, contextMenu, notification)
  - Форматирование цветов без символа `#` (6-значный HEX для сплошных цветов, 8-значный AARRGGBB для полупрозрачных слоев)
  - Адаптивные параметры темы: `statusBar` (black/white), `keyboard` (dark/light), `dark` (true/false), `bgType`
- [x] Интеграция генератора iOS в сервис создания тем (`bot/services/theme_service.py`):
  - Добавление полей `ios_dark` и `ios_light` в структуру `ProcessedThemeResult`
  - Поддержка генерации тем для iPhone/iPad как из пользовательских изображений, так и из авторских пресетов
- [x] Обновление интерфейса и клавиатур бота (`bot/keyboards/theme_keyboards.py`):
  - Добавление ряда кнопок `🍎 iOS (Тёмная)` и `🍎 iOS (Светлая)`
  - Обновление пакетной выгрузки до `📦 Скачать всё (Desktop + Android + iOS)`
- [x] Обработка скачивания и доставка файлов (`bot/handlers/theme.py`):
  - Отправка файлов `theme_dark.tgios-theme` и `theme_light.tgios-theme`
  - Включение iOS-файлов в пакетное скачивание всех платформ
- [x] Документация и инструкции по установке (`bot/handlers/common.py`):
  - Добавление пошаговой инструкции для iPhone/iPad в команду `/help`
  - Обновление приветственного сообщения команды `/start`
- [x] Комплексное тестирование и валидация (`tests/test_theme_generators.py`, `tests/test_handlers.py`, `tests/test_theme_service.py`):
  - Валидация YAML-синтаксиса через `yaml.safe_load` для темных и светлых тем
  - 30/30 тестов успешно пройдено (`pytest`)
  - 100/100 Healthy, 0 issues, 0 warnings (`npx aislop scan`)

### Фаза 9: Telegram Mini App (Theme Studio) и функция прозрачности сообщений
- [x] Расширение модели данных прозрачности (`bot/models/color.py`):
  - Добавление метода `with_alpha_hex(alpha)` к классу `Color`
  - Добавление параметров `in_bubble_alpha` и `out_bubble_alpha` (0-255) в `PaletteTheme`
  - Добавление фабричного метода `with_transparency(in_alpha, out_alpha)`
- [x] Поддержка нативной прозрачности сообщений (Glassmorphism) на всех платформах:
  - **Android (`.attheme`)**: генерация 32-bit signed ARGB c настраиваемым альфа-каналом для `chat_inBubble`, `chat_outBubble` и выбранных состояний
  - **Telegram Desktop (`.tdesktop-theme`)**: генерация HEX `#aarrggbb` в `colors.tdesktop-palette` для токенов `msgInBg`, `msgInBgSelected`, `msgOutBg`, `msgOutBgSelected`
  - **Telegram iOS (`.tgios-theme`)**: генерация 8-символьного YAML-хекса `AARRGGBB` для входящих и исходящих баблов
- [x] Разработка Telegram Mini App (Web App) в директории `webapp/`:
  - `index.html`: интерактивная студия кастомизации тем с интеграцией `telegram-web-app.js`, симулятором живого Telegram-чата, пикерами цветов и слайдерами прозрачности
  - `style.css`: современный премиальный dark/glassmorphic UI, адаптивный под мобильные экраны и десктоп
  - `app.js`: мгновенный рендеринг изменений в чате, переключение пресетов, свитч прозрачности с размытием (`backdrop-filter`) и отправка данных в бота через `Telegram.WebApp.sendData()`
- [x] Интеграция веб-сервера `aiohttp` в бота (`bot/server.py`):
  - Раздача статики `webapp/` на порту 8080 (или через `WEBAPP_PORT`)
  - Запуск HTTP-сервера параллельно с long polling бота в `bot/main.py`
  - Endpoint `/health` для проверки доступности
- [x] Хэндлеры бота для Web App (`bot/handlers/theme.py`, `bot/keyboards/theme_keyboards.py`):
  - Команда `/studio` (и `/app`) для открытия Mini App с кнопками Reply и Inline `WebAppInfo`
  - Приём данных веб-приложения через фильтр `F.web_app_data`
  - Генерация и прямая выдача готовых файлов тем (`.tdesktop-theme`, `.attheme`, `.tgios-theme`) по настроенной в Mini App палитре с прозрачностью
- [x] Тестирование и контроль качества:
  - 35/35 тестов успешно пройдено (`tests/test_transparency.py`, `tests/test_server.py`)
  - 100/100 Healthy, 0 issues, 0 warnings (`npx aislop scan`)


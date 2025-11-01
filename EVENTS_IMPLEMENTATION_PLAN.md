# План реализации: Модуль локальных событий для Jekyll блога

**Общий прогресс: 85%** (17/20 шагов)

---

## Фаза 1: Конфигурация и инфраструктура ✅

- [x] **1.1** Создать `config/events.json` с городами, запросами и настройками
  - [x] Определить 2 группы городов (7+7)
  - [x] Настроить query templates (4 шаблона)
  - [x] Добавить параметры Google API и OpenAI

- [x] **1.2** Настроить GitHub Secrets
  - [x] Добавить `GOOGLE_API_KEY`
  - [x] Добавить `GOOGLE_SEARCH_ENGINE_ID`
  - [x] Добавить `OPENAI_API_KEY`

- [x] **1.3** Создать структуру директорий
  - [x] Создать `scripts/` для Python скриптов
  - [x] Создать `_data/events/` для markdown архива
  - [x] Убедиться что `_data/events.json` будет создан автоматически

---

## Фаза 2: Python скрипт сбора данных ✅

- [x] **2.1** Создать `scripts/fetch_events.py` - основной скрипт
  - [x] Функция `load_config()` - чтение config/events.json
  - [x] Функция `get_cities_for_today()` - определение группы по дню недели
  - [x] Функция `build_queries()` - генерация запросов из templates

- [x] **2.2** Реализовать интеграцию Google Custom Search API
  - [x] Функция `fetch_google_results(query)` - запрос к API
  - [x] Обработка пагинации (10 результатов)
  - [x] Retry логика (3 попытки)
  - [x] Обработка ошибок и пустых результатов

- [x] **2.3** Реализовать интеграцию OpenAI API
  - [x] Функция `analyze_with_openai(results, date)` - отправка в OpenAI
  - [x] Промпт с инструкциями извлечения событий
  - [x] Парсинг JSON ответа
  - [x] Валидация структуры (category, title, description, link, tags, event_date)
  - [x] Retry логика (3 попытки)

- [x] **2.4** Реализовать логику работы с events.json
  - [x] Функция `load_events_json()` - чтение существующего файла
  - [x] Функция `find_duplicate_by_link()` - поиск дубликатов
  - [x] Функция `merge_events()` - обновление или добавление событий
  - [x] Функция `save_events_json()` - сохранение с сортировкой по датам

- [x] **2.5** Реализовать создание markdown архива
  - [x] Функция `create_markdown_for_date(date)` - генерация .md файла
  - [x] Шаблон markdown с group by категориям
  - [x] Создание файла в `_data/events/YYYY-MM-DD.md`

- [x] **2.6** Реализовать cleanup старых событий (опционально)
  - [x] Функция `cleanup_old_events()` - удаление событий старше 365 дней
  - [x] Применяется только если `cleanup_enabled: true`

---

## Фаза 3: GitHub Actions workflows ✅

- [x] **3.1** Создать `.github/workflows/generate-events.yml`
  - [x] Триггер: schedule (cron: '0 3 * * *')
  - [x] Триггер: workflow_dispatch (ручной запуск)
  - [x] Checkout кода
  - [x] Setup Python 3.11
  - [x] Установка зависимостей (openai, requests)
  - [x] Запуск `scripts/fetch_events.py` с передачей secrets
  - [x] Git add + commit + push изменений
  - [x] Автор коммита: github-actions[bot]

- [x] **3.2** Создать `.github/workflows/test-events.yml`
  - [x] Триггер: только workflow_dispatch
  - [x] Dry-run режим (без коммита)
  - [x] Вывод логов для отладки

---

## Фаза 4: Страница /events и UI ✅

- [x] **4.1** Создать `_tabs/events.md`
  - [x] Front matter: layout, icon, order: 2
  - [x] Минимальный контент (layout сделает всё)

- [x] **4.2** Создать `_layouts/events.html`
  - [x] Чтение `site.data.events` из events.json
  - [x] Секция "Current Events" (event_date == today)
  - [x] Секция "Upcoming Events" (event_date > today), сортировка по дате
  - [x] Правая колонка: календарь/архив

- [x] **4.3** Реализовать календарь-селектор
  - [x] HTML: dropdown для выбора года/месяца
  - [x] JavaScript: обработка клика, открытие markdown страницы
  - [x] Генерация списка доступных дат из events.json

- [x] **4.4** Реализовать фильтры по категориям
  - [x] JavaScript: парсинг категорий из Current + Upcoming
  - [x] UI: кнопки/чипы для фильтрации
  - [x] Логика: показ/скрытие событий по категории

---

## Фаза 5: Стилизация ✅

- [x] **5.1** Добавить CSS в `assets/css/custom.css`
  - [x] Стили для `.events-container`
  - [x] Стили для `.current-events` и `.upcoming-events`
  - [x] Стили для `.event-card` (используя существующие переменные)
  - [x] Стили для календаря/селектора
  - [x] Стили для фильтров категорий
  - [x] Responsive дизайн (mobile/tablet/desktop)

---

## Фаза 6: Навигация и интеграция ✅

- [x] **6.1** Обновить sidebar navigation
  - [x] Добавить "events: Events" в `_data/locales/en.yml`
  - [x] Иконка: `fas fa-calendar-alt` (в _tabs/events.md)
  - [x] Order: 2 (перед Archives)

- [x] **6.2** Создать layout для архивных страниц
  - [x] Layout `event-day.html` для рендеринга архивных событий
  - [x] Создать коллекцию `event_archives` в _config.yml
  - [x] Обновить путь в fetch_events.py на `_event_archives/`
  - [x] Настроить permalink: `/events/archive/:name/`
  - [x] Кнопка "Back to Events"

---

## Фаза 7: Тестирование и деплой

- [ ] **7.1** Локальное тестирование
  - [ ] Запуск `scripts/fetch_events.py` вручную
  - [ ] Проверка создания events.json
  - [ ] Проверка создания markdown файлов
  - [ ] Проверка отображения на странице /events

- [ ] **7.2** Тестирование workflows
  - [ ] Ручной запуск test-events.yml
  - [ ] Проверка логов
  - [ ] Ручной запуск generate-events.yml
  - [ ] Проверка автоматического коммита

- [ ] **7.3** Проверка на production
  - [ ] Деплой на GitHub Pages
  - [ ] Проверка работы страницы /events
  - [ ] Проверка календаря и фильтров
  - [ ] Проверка mobile версии

---

## Технические детали

### Структура events.json
```json
{
  "2025-11-01": [
    {
      "found_date": "2025-11-01",
      "event_date": "2025-11-15",
      "category": "Culture",
      "title": "Art Festival",
      "description": "Description text",
      "link": "https://example.com",
      "tags": ["art", "festival"]
    }
  ]
}
```

### Google Queries оптимизация
- **28 запросов/день** (7 городов × 4 query templates)
- **Группа 1** (Пн, Ср, Пт): Gurnee, Waukegan, Libertyville, Vernon Hills, Mundelein, Round Lake Beach, Lindenhurst
- **Группа 2** (Вт, Чт, Сб, Вс): Grayslake, Wauconda, Park City, Gages Lake, Third Lake, Wadsworth, Beach Park

### Query Templates
1. `"{city} IL events news this week"`
2. `"{city} restaurants entertainment"`
3. `"{city} community business updates"`
4. `"{city} manufacturing local updates"`

### OpenAI промпт (черновик)
```
Current date: {today}

Analyze these search results and extract events. For each event:
- category: Choose from [Culture, Community, News, Food, Entertainment, Business, Manufacturing, Politics, Economy] or create new if needed
- title: Event name
- description: Brief description (2-3 sentences)
- link: Source URL
- tags: Array of relevant keywords (2-5 tags)
- event_date: YYYY-MM-DD format if date is mentioned in text, otherwise "unknown"

Return valid JSON array only, no markdown formatting.
```

### Обработка дубликатов
- Сравнение по полю `link`
- При совпадении: обновление title, description, tags, event_date
- Старые события остаются в events.json (не удаляются)
- Layout фильтрует по `event_date >= today`

### Data retention
- events.json растет неограниченно
- Cleanup: опционально, удаление событий старше 365 дней
- Markdown архив: не удаляется (история)

---

## Критерии готовности

✅ Все 20 шагов завершены
✅ Workflow запускается автоматически в 03:00 UTC
✅ Можно запустить вручную через GitHub Actions
✅ events.json обновляется корректно
✅ Дубликаты обрабатываются (по link)
✅ Страница /events отображает Current + Upcoming события
✅ Календарь работает, открывает архивные страницы
✅ Фильтры по категориям работают
✅ Стили соответствуют существующему дизайну блога
✅ Mobile версия работает корректно

---

## Секреты для настройки (GitHub Secrets)

Перед запуском добавить через `gh secret set`:
- `GOOGLE_API_KEY` - Google Custom Search API key
- `GOOGLE_SEARCH_ENGINE_ID` - Search Engine ID
- `OPENAI_API_KEY` - OpenAI API key

---

**Статус**: План утвержден, готов к реализации

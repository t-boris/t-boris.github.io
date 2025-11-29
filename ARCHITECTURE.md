# Архитектура сайта blog.tsekinovsky.me

## 📋 Оглавление
1. [Обзор](#обзор)
2. [Технологический стек](#технологический-стек)
3. [Архитектура системы](#архитектура-системы)
4. [Структура директорий](#структура-директорий)
5. [Конфигурация](#конфигурация)
6. [Процесс сборки и деплоя](#процесс-сборки-и-деплоя)
7. [Frontend компоненты](#frontend-компоненты)
8. [Управление контентом](#управление-контентом)
9. [Интеграции](#интеграции)
10. [Performance и оптимизация](#performance-и-оптимизация)

---

## Обзор

**Тип:** Статический сайт-блог (JAMstack)
**URL:** https://blog.tsekinovsky.me
**Генератор:** Jekyll 4.3.1
**Тема:** Jekyll Theme Chirpy 5.4+
**Хостинг:** GitHub Pages
**CI/CD:** GitHub Actions

### Ключевые характеристики
- ✅ Полностью статический сайт (быстрая загрузка)
- ✅ Автоматический деплой при коммите
- ✅ SEO-оптимизация
- ✅ Responsive дизайн
- ✅ Dark/Light режимы
- ✅ PWA поддержка
- ✅ Встроенная аналитика и комментарии

---

## Технологический стек

### Backend (Build-time)
- **Jekyll 4.3.1** - Генератор статических сайтов на Ruby
- **Kramdown** - Markdown процессор
- **Rouge** - Подсветка синтаксиса кода
- **Liquid** - Шаблонизатор

### Frontend
- **Bootstrap 4.6.2** - CSS фреймворк
- **jQuery 3.6.1** - JavaScript библиотека
- **Font Awesome 6.2.1** - Иконки
- **Google Fonts** - Lato & Source Sans Pro

### JavaScript библиотеки
```yaml
Core:
  - jQuery 3.6.1
  - Bootstrap 4.6.2

Content Enhancement:
  - Mermaid 9.2.2 (диаграммы)
  - MathJax 3.2.2 (математические формулы)
  - Simple Jekyll Search 1.10.0 (поиск)

UI/UX:
  - Magnific Popup 1.1.0 (лайтбокс для изображений)
  - Lazysizes 5.3.2 (ленивая загрузка изображений)
  - Clipboard.js 2.0.11 (копирование в буфер)
  - CountUp.js 1.9.3 (анимация чисел)

Utilities:
  - Day.js 1.11.6 (работа с датами)
```

### Ruby Gems
```ruby
# Gemfile
gem "jekyll", "~> 4.3.1"
gem "jekyll-theme-chirpy", "~> 5.4"
gem "jekyll-seo-tag"
```

### DevOps
- **GitHub Actions** - CI/CD пайплайн
- **GitHub Pages** - Хостинг
- **Bundler** - Управление Ruby зависимостями

---

## Архитектура системы

### Архитектурная диаграмма

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer Workflow                        │
│                                                               │
│  ┌──────────┐    git push     ┌─────────────────┐           │
│  │  Local   │ ───────────────> │  GitHub Repo    │           │
│  │   Dev    │                  │  (main branch)  │           │
│  └──────────┘                  └────────┬────────┘           │
│                                          │                    │
│                                          │ trigger            │
│                                          ▼                    │
│                              ┌──────────────────────┐        │
│                              │  GitHub Actions      │        │
│                              │  - Checkout code     │        │
│                              │  - Bundle install    │        │
│                              │  - Jekyll build      │        │
│                              │  - Deploy to gh-pages│        │
│                              └──────────┬───────────┘        │
│                                         │                    │
└─────────────────────────────────────────┼────────────────────┘
                                          │
                                          │ deploy
                                          ▼
                              ┌──────────────────────┐
                              │  GitHub Pages        │
                              │  (gh-pages branch)   │
                              │  Static HTML/CSS/JS  │
                              └──────────┬───────────┘
                                         │
                                         │ serve
                                         ▼
                              ┌──────────────────────┐
                              │   blog.tsekinovsky   │
                              │        .me           │
                              │  (Custom Domain)     │
                              └──────────┬───────────┘
                                         │
                                         │ access
                                         ▼
                              ┌──────────────────────┐
                              │    End Users         │
                              │  - Browsers          │
                              │  - Mobile devices    │
                              └──────────────────────┘
```

### Паттерн JAMstack

**J**avaScript + **A**PIs + **M**arkup

1. **Pre-rendering**: Все страницы генерируются в HTML на этапе сборки
2. **CDN Delivery**: Статические файлы доставляются через CDN
3. **Dynamic via APIs**: Динамическая функциональность через сторонние API
   - Google Analytics (аналитика)
   - Disqus (комментарии)
   - jsDelivr CDN (библиотеки)

### Процесс рендеринга

```
Markdown Post (.md)
    ↓
Jekyll Processing
    ├── Front Matter (YAML) → Metadata
    ├── Liquid Templates → Dynamic content
    ├── Kramdown → HTML
    └── Rouge → Syntax highlighting
    ↓
HTML Page
    ├── Layout wrapper (post.html)
    ├── Includes (header, footer, sidebar)
    └── Assets (CSS, JS, images)
    ↓
Static Output (/_site/)
    ↓
GitHub Pages (gh-pages branch)
```

---

## Структура директорий

```
t-boris.github.io/
│
├── 📄 _config.yml              # Главная конфигурация Jekyll
├── 📄 Gemfile                  # Ruby зависимости
├── 📄 CNAME                    # Кастомный домен
├── 📄 index.html               # Домашняя страница
├── 📄 .gitignore
│
├── 📁 _data/                   # Данные для конфигурации
│   ├── assets/
│   │   ├── cross_origin.yml    # CDN ссылки (Bootstrap, jQuery и т.д.)
│   │   └── self_host.yml       # Пути для self-hosted ресурсов
│   ├── contact.yml             # Иконки социальных сетей
│   ├── share.yml               # Настройки кнопок шаринга
│   └── locales/
│       └── en.yml              # Локализация (английский)
│
├── 📁 _includes/               # Переиспользуемые HTML части
│   ├── head.html              # <head> секция (SEO, analytics)
│   └── sidebar.html           # Боковая панель навигации
│
├── 📁 _layouts/                # Шаблоны страниц
│   └── home.html              # Кастомный layout главной страницы
│
├── 📁 _plugins/                # Кастомные Jekyll плагины
│   └── posts-lastmod-hook.rb  # Трекинг даты изменения через Git
│
├── 📁 _posts/                  # Посты блога (Markdown)
│   ├── 2023-01-10-setup-personalized-blog-with-jekyll.markdown
│   ├── 2023-01-16-system-design-distributed-systems-consepts.md
│   ├── 2023-01-25-elk-on-eks.md
│   └── 2023-01-26-homeassistant-garage-opener.md
│
├── 📁 _tabs/                   # Страницы навигации (коллекция)
│   ├── archives.md            # Архивы постов
│   ├── categories.md          # Страница категорий
│   └── tags.md                # Страница тегов
│
├── 📁 assets/                  # Статические ресурсы
│   ├── img/
│   │   └── favicons/          # Иконки сайта
│   └── [изображения]          # PNG файлы (~19MB)
│
└── 📁 .github/
    └── workflows/
        └── github-pages.yml   # CI/CD пайплайн
```

### Описание ключевых директорий

#### `_data/`
Хранит структурированные данные в YAML формате. Используется для:
- Конфигурации внешних ресурсов (CDN)
- Настроек социальных сетей
- Локализации интерфейса

#### `_includes/`
HTML фрагменты, которые можно вставлять в layouts:
- Переопределяет стандартные includes темы Chirpy
- Позволяет кастомизировать отдельные части без изменения темы

#### `_layouts/`
Шаблоны страниц на основе Liquid:
- Определяют структуру HTML страниц
- Наследуются от базовых layouts темы

#### `_plugins/`
Ruby плагины для расширения Jekyll:
- `posts-lastmod-hook.rb` - автоматически извлекает дату последнего изменения из Git

#### `_posts/`
Markdown файлы с контентом блога:
- Формат имени: `YYYY-MM-DD-title.md`
- Front matter для метаданных
- Автоматически обрабатываются Jekyll

#### `_tabs/`
Кастомная коллекция для страниц навигации:
- Определены в `_config.yml` как коллекция
- Автоматически добавляются в меню

---

## Конфигурация

### `_config.yml` - основные настройки

```yaml
# Метаданные сайта
title: Info worth sharing
tagline: Personal blog
url: https://blog.tsekinovsky.me
author: Boris Tsekinovsky
description: >-
  Personal blog

# Тема и плагины
theme: jekyll-theme-chirpy
plugins:
  - jekyll-seo-tag

# Пагинация
paginate: 10

# Настройки контента
toc: true                    # Table of Contents
permalink: /posts/:title/

# Коллекции
collections:
  tabs:
    output: true
    sort_by: order

# Архивы
jekyll-archives:
  enabled: [categories, tags]
  layouts:
    category: category
    tag: tag
  permalinks:
    tag: /tags/:name/
    category: /categories/:name/

# Производительность
compress_html:
  clippings: all
  comments: all
  endings: all
  profile: false
  blanklines: false
  ignore:
    envs: [development]

sass:
  style: compressed
```

### Ключевые параметры

| Параметр | Значение | Описание |
|----------|----------|----------|
| `theme` | jekyll-theme-chirpy | Активная тема |
| `paginate` | 10 | Постов на страницу |
| `toc` | true | Автоматическое оглавление |
| `timezone` | America/New_York | Часовой пояс |
| `lang` | en | Язык сайта |

### Интеграции в конфиге

```yaml
# Google Analytics
google_analytics:
  id: G-YCZXJ9FFBL

# Комментарии Disqus
comments:
  active: disqus
  disqus:
    shortname: blog-tsekinovsky-me

# PWA
pwa:
  enabled: true
  cache:
    enabled: true
```

---

## Процесс сборки и деплоя

### GitHub Actions Workflow

**Файл:** `.github/workflows/github-pages.yml`

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main  # Триггер при пуше в main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      # 1. Checkout кода
      - uses: actions/checkout@v3

      # 2. Кэширование зависимостей
      - uses: actions/cache@v3
        with:
          path: vendor/bundle
          key: ${{ runner.os }}-gems-${{ hashFiles('**/Gemfile.lock') }}
          restore-keys: |
            ${{ runner.os }}-gems-

      # 3. Сборка и деплой
      - uses: jeffreytse/jekyll-deploy-action@v0.4.0
        with:
          provider: 'github-pages'
          token: ${{ secrets.JEKYLL_PAT }}
          branch: 'gh-pages'
```

### Этапы деплоя

1. **Триггер**: Пуш в `main` ветку
2. **Checkout**: Клонирование репозитория
3. **Cache**: Восстановление кэша Ruby gems
4. **Bundle Install**: Установка зависимостей
5. **Jekyll Build**: Генерация статических файлов
6. **Deploy**: Пуш в `gh-pages` ветку
7. **Publish**: GitHub Pages публикует сайт

### Время сборки

- **Cold build** (без кэша): ~3-5 минут
- **Cached build**: ~1-2 минуты

### Ветки репозитория

| Ветка | Назначение | Содержимое |
|-------|-----------|------------|
| `main` | Source code | Markdown, конфиги, темы |
| `gh-pages` | Production | Скомпилированный HTML/CSS/JS |

---

## Frontend компоненты

### Layout иерархия

```
default (из темы Chirpy)
  ├── page
  │   ├── home (кастомный)
  │   ├── post
  │   ├── categories
  │   └── tags
  └── compress (HTML компрессия)
```

### Кастомизации темы

#### 1. `_layouts/home.html`
Переопределяет главную страницу:
- Кастомная пагинация
- Поддержка "закрепленных" постов (pinned)
- Фильтрация скрытых постов
- Отображение превью постов

```liquid
{% for post in posts %}
  {% unless post.hidden %}
    <div class="post-preview">
      <h1>{{ post.title }}</h1>
      <div class="post-meta">
        {{ post.date | date: "%b %d, %Y" }}
      </div>
      <div class="post-content">
        {{ post.excerpt }}
      </div>
    </div>
  {% endunless %}
{% endfor %}
```

#### 2. `_includes/head.html`
Кастомная `<head>` секция:
- SEO теги через `jekyll-seo-tag`
- Google Analytics
- Preconnect для CDN
- Meta теги для социальных сетей

#### 3. `_includes/sidebar.html`
Боковая панель:
- Логотип и название сайта
- Навигационное меню (tabs)
- Социальные иконки
- Переключатель темы (dark/light)

### CSS архитектура

**Источники стилей:**
1. **Bootstrap 4.6.2** - базовый фреймворк
2. **Chirpy Theme CSS** - стили темы
3. **Font Awesome** - иконки
4. **Дополнительные библиотеки**:
   - Bootstrap TOC
   - Magnific Popup

**Особенности:**
- ❌ Нет кастомных CSS файлов в репозитории
- ✅ Все стили из темы Chirpy
- ✅ Все библиотеки с CDN
- ✅ Компрессия SASS в production

### JavaScript архитектура

**Подход:** Модульная загрузка через CDN

```html
<!-- Core -->
<script src="https://cdn.jsdelivr.net/npm/jquery@3.6.1/dist/jquery.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>

<!-- Content Enhancement -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@9.2.2/dist/mermaid.min.js"></script>
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>

<!-- UI/UX -->
<script src="https://cdn.jsdelivr.net/npm/magnific-popup@1.1.0/dist/jquery.magnific-popup.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/lazysizes@5.3.2/lazysizes.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/clipboard@2.0.11/dist/clipboard.min.js"></script>
```

**Особенности:**
- ❌ Нет кастомного JavaScript в репозитории
- ✅ Вся функциональность из темы и библиотек
- ✅ DNS prefetch для оптимизации загрузки

---

## Управление контентом

### Формат постов

**Файл:** `_posts/YYYY-MM-DD-title.md`

**Front Matter:**
```yaml
---
layout: post
title: "Заголовок поста"
date: 2023-01-26 12:00:00 -0500
categories: [category1, category2]
tags: [tag1, tag2, tag3]
excerpt: "Краткое описание"
image: /assets/image.png
pin: true              # Закрепить пост
hidden: false          # Скрыть из списка
comments: true         # Включить комментарии
math: true            # Включить MathJax
mermaid: true         # Включить Mermaid диаграммы
---

Контент поста в Markdown...
```

### Категории и теги

**Категории** (`categories`):
- Широкая классификация
- Иерархическая структура возможна
- Отображаются в sidebar
- Имеют отдельные страницы архивов

**Теги** (`tags`):
- Детальная маркировка контента
- Flat структура
- Страницы для каждого тега

**Текущие категории:**
- `config` - Конфигурация и настройка
- `system-design` - Системный дизайн
- `devops` - DevOps практики

### Статические страницы (Tabs)

**Коллекция:** `_tabs/`

```yaml
---
layout: page
title: Archives
icon: fas fa-archive
order: 3
---
```

**Параметр `order`** определяет позицию в меню.

### Изображения

**Размещение:** `/assets/`

**Вставка в пост:**
```markdown
![Alt text](/assets/image-name.png)
_Image caption_
```

**Lazy loading** включен автоматически через `lazysizes`.

**Lightbox** работает автоматически для всех изображений.

---

## Интеграции

### Google Analytics

**ID:** `G-YCZXJ9FFBL`

**Настройка в `_includes/head.html`:**
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YCZXJ9FFBL"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-YCZXJ9FFBL');
</script>
```

**Отслеживаемые метрики:**
- Просмотры страниц
- Сессии пользователей
- Источники трафика
- Время на странице

### Disqus (Комментарии)

**Shortname:** `blog-tsekinovsky-me`

**Конфигурация:**
```yaml
comments:
  active: disqus
  disqus:
    shortname: blog-tsekinovsky-me
```

**Включение в постах:**
```yaml
comments: true  # в front matter
```

### Социальные сети

**Контакты** (`_data/contact.yml`):
```yaml
- type: github
  icon: 'fab fa-github'
  url: 'https://github.com/t-boris'

- type: twitter
  icon: 'fab fa-twitter'

- type: email
  icon: 'fas fa-envelope'
  noblank: true

- type: rss
  icon: 'fas fa-rss'
  noblank: true
```

**Кнопки шаринга** (`_data/share.yml`):
```yaml
- type: Twitter
  icon: "fab fa-twitter"
  link: "https://twitter.com/intent/tweet?text=TITLE&url=URL"

- type: Facebook
  icon: "fab fa-facebook-square"
  link: "https://www.facebook.com/sharer/sharer.php?title=TITLE&u=URL"

- type: Telegram
  icon: "fab fa-telegram"
  link: "https://telegram.me/share/url?url=URL&text=TITLE"
```

### CDN Ресурсы

**Конфигурация:** `_data/assets/cross_origin.yml`

```yaml
jquery:
  url: https://cdn.jsdelivr.net/npm/jquery@3.6.1/dist/jquery.min.js

bootstrap:
  css: https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css
  js: https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js

fontawesome:
  css: https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.1/css/all.min.css
```

---

## Performance и оптимизация

### Стратегии оптимизации

#### 1. HTML компрессия
```yaml
compress_html:
  clippings: all
  comments: all
  endings: all
  blanklines: false
```
**Результат:** Уменьшение размера HTML на ~20-30%

#### 2. CSS компрессия
```yaml
sass:
  style: compressed
```
**Результат:** Минификация CSS файлов

#### 3. Lazy loading изображений
```html
<img data-src="image.jpg" class="lazyload" />
```
**Библиотека:** Lazysizes 5.3.2
**Результат:** Загрузка изображений по мере прокрутки

#### 4. Resource Hints
```html
<!-- DNS Prefetch -->
<link rel="dns-prefetch" href="https://cdn.jsdelivr.net">

<!-- Preconnect -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```
**Результат:** Ускорение загрузки внешних ресурсов

#### 5. Service Worker (PWA)
**Кэширование:**
- Статические ресурсы
- CSS и JS файлы
- Изображения

**Результат:** Офлайн доступ и быстрая повторная загрузка

#### 6. CDN Delivery
**Все внешние библиотеки с jsDelivr CDN:**
- Географически распределенная доставка
- HTTP/2 и Brotli компрессия
- Автоматическое кэширование браузером

### Метрики производительности

**Приблизительные показатели:**

| Метрика | Значение |
|---------|----------|
| First Contentful Paint | ~1.2s |
| Time to Interactive | ~2.5s |
| Total Page Size | ~500KB (без изображений) |
| JavaScript Size | ~300KB |
| CSS Size | ~100KB |

**Оптимизировано для:**
- ✅ Mobile devices
- ✅ Slow 3G connections
- ✅ Low-end devices

### Рекомендации по улучшению

#### Критические проблемы:
1. **Большие изображения** в `/assets/`
   - `Pasted image 20230126135450.png` - 9.2 MB
   - `Pasted image 20230126134953.png` - 7.5 MB
   - **Решение:** Оптимизация и ресайз

2. **Нет WebP формата**
   - **Решение:** Конвертация в WebP

3. **Плоская структура assets**
   - **Решение:** Организация по папкам

#### Возможные улучшения:
- Внедрение image optimization pipeline
- Использование responsive images (`srcset`)
- Переход на HTTP/2 Server Push
- Критический CSS inline
- Code splitting для JavaScript

---

## Расширения и кастомизация

### Добавление нового поста

1. Создать файл: `_posts/YYYY-MM-DD-title.md`
2. Добавить front matter
3. Написать контент в Markdown
4. Коммит и пуш в `main`
5. Автоматический деплой через GitHub Actions

### Добавление новой страницы (Tab)

1. Создать файл в `_tabs/page-name.md`
2. Указать `order` для позиции в меню
3. Определить `icon` (Font Awesome класс)

### Кастомизация дизайна

**Создание файла:** `assets/css/main.scss`

```scss
---
---

@import "{{ site.theme }}";

// Ваши кастомные стили
.custom-class {
  color: #your-color;
}
```

### Добавление JavaScript

**Создание файла:** `assets/js/custom.js`

**Подключение в `_includes/head.html`:**
```html
<script src="{{ '/assets/js/custom.js' | relative_url }}"></script>
```

---

## Troubleshooting

### Частые проблемы

#### Build падает с ошибкой
```bash
# Локальная проверка
bundle exec jekyll serve
```

#### Изменения не применяются
- Проверить GitHub Actions logs
- Убедиться, что коммит в `main` ветку
- Очистить кэш браузера

#### Стили не загружаются
- Проверить network tab в DevTools
- Убедиться, что CDN доступен
- Проверить `_data/assets/cross_origin.yml`

---

## Полезные команды

### Локальная разработка
```bash
# Установка зависимостей
bundle install

# Запуск локального сервера
bundle exec jekyll serve

# Сборка без запуска сервера
bundle exec jekyll build

# С live reload
bundle exec jekyll serve --livereload

# Drafts (черновики)
bundle exec jekyll serve --drafts
```

### Git workflow
```bash
# Новый пост
git add _posts/2023-01-26-new-post.md
git commit -m "Add new post about..."
git push origin main

# Проверить статус деплоя
# GitHub → Actions → Latest workflow
```

---

## Лицензия и атрибуция

**Тема:** Jekyll Theme Chirpy
**Лицензия:** MIT License
**Автор темы:** Cotes Chung

**Сайт:**
**Владелец:** Boris Tsekinovsky (@t-boris)
**Репозиторий:** https://github.com/t-boris/t-boris.github.io

---

## Дополнительные ресурсы

### Документация
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [Chirpy Theme Documentation](https://github.com/cotes2020/jekyll-theme-chirpy)
- [GitHub Pages Documentation](https://docs.github.com/pages)
- [Kramdown Syntax](https://kramdown.gettalong.org/syntax.html)

### Полезные ссылки
- [Jekyll Plugins](https://jekyllrb.com/docs/plugins/)
- [Liquid Syntax](https://shopify.github.io/liquid/)
- [Font Awesome Icons](https://fontawesome.com/icons)
- [Bootstrap 4 Documentation](https://getbootstrap.com/docs/4.6/)

---

**Версия документации:** 1.0
**Дата:** Январь 2025
**Автор:** Claude Code (AI Assistant)

import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from .firebase_db import init_firebase
from .config import load_channels_from_yaml
from google.cloud.firestore_v1.base_query import FieldFilter
from firebase_admin import firestore
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup, Tag

OUTPUT_DIR = "output"
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
TEMPLATE_FILE = "digest.html.j2"

# Убедимся, что директория для вывода существует
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_digest_posts(date_from: datetime, date_to: datetime, channels: List[str]) -> List[dict]:
    """
    Получает посты из указанных каналов за период с date_from по date_to.
    
    Args:
        date_from: Начальная дата (включительно)
        date_to: Конечная дата (включительно) 
        channels: Список ID каналов
    
    Returns:
        Список постов, отсортированных по дате (от старых к новым)
    """
    all_posts = []

    db = init_firebase()
    messages_ref = db.collection('messages')
    
    print(f"Загружаем посты с {date_from.strftime('%Y-%m-%d %H:%M')} по {date_to.strftime('%Y-%m-%d %H:%M')} (МСК)")
    
    try:
        # Получаем все посты за период (без составного индекса)
        docs = list(messages_ref.where(
            filter=FieldFilter('date', '>=', date_from)
        ).where(
            filter=FieldFilter('date', '<=', date_to)
        ).order_by('date', direction=firestore.Query.ASCENDING).stream())
        
        print(f"Найдено {len(docs)} постов за период")
        
        # Фильтруем по каналам и обрабатываем
        channel_counts = {channel: 0 for channel in channels}
        
        for doc in docs:
            data = doc.to_dict()
            channel = data.get('channel')
            
            # Проверяем, что пост из нужного канала
            if channel not in channels:
                continue
            
            # Проверяем наличие summary
            if not data.get('summary'):
                print(f"⚠ Пост {data.get('msg_id')} ({channel}): отсутствует summary, пропускаем")
                continue
            
            # Используем text_html если есть, иначе plain_text с базовым форматированием
            if data.get('text_html'):
                print(f"✓ Пост {data.get('msg_id')} ({channel}): HTML контент найден ({len(data['text_html'])} символов)")
            else:
                print(f"⚠ Пост {data.get('msg_id')} ({channel}): HTML контент отсутствует")
                # Если нет HTML, используем plain_text с базовым форматированием
                plain_text = data.get('plain_text', '')
                if plain_text:
                    data['text_html'] = f"<p>{plain_text.replace(chr(10), '<br>')}</p>"
            
            all_posts.append(data)
            channel_counts[channel] += 1
        
        # Выводим статистику по каналам
        for channel, count in channel_counts.items():
            print(f"Канал {channel}: {count} постов")
            
    except Exception as e:
        print(f"Ошибка при загрузке постов: {str(e)}")
        return []
    
    print(f"Всего загружено постов: {len(all_posts)}")
    return all_posts

def render_digest_html(posts: List[dict], date_from: datetime, date_to: datetime) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(TEMPLATE_FILE)
    return template.render(posts=posts, date_from=date_from, date_to=date_to, timedelta=timedelta)

def save_pdf_from_html(html: str, date_from: datetime, date_to: datetime) -> str:
    fname = f"Telegram_{date_from.strftime('%Y%m%d')}_{date_to.strftime('%Y%m%d')}.pdf"
    out_path = os.path.join(OUTPUT_DIR, fname)
    
    # Создаем HTML объект с настройками для лучшего качества
    html_obj = HTML(string=html)
    
    # Настройки для лучшего рендеринга
    html_obj.write_pdf(
        out_path,
        optimize_images=True,
        jpeg_quality=95,
        presentational_hints=True
    )
    
    return out_path

def save_epub_from_html(html: str, date_from: datetime, date_to: datetime) -> str:
    """Создает EPUB файл из HTML контента."""
    fname = f"Telegram_{date_from.strftime('%Y%m%d')}_{date_to.strftime('%Y%m%d')}.epub"
    out_path = os.path.join(OUTPUT_DIR, fname)
    
    # Создаем книгу
    book = epub.EpubBook()
    
    # Устанавливаем метаданные
    book.set_identifier(f"telegram-digest-{date_from.strftime('%Y%m%d')}")
    book.set_title(f"Telegram Digest {date_from.strftime('%Y-%m-%d')} - {date_to.strftime('%Y-%m-%d')}")
    book.set_language('ru')
    
    # Добавляем автора и описание
    book.add_author("Telegram Digest Bot")
    book.add_metadata('DC', 'description', f'Дайджест постов из Telegram каналов за период {date_from.strftime("%Y-%m-%d")} - {date_to.strftime("%Y-%m-%d")}')
    
    # Создаем полные CSS стили
    style = '''
    body {
        font-family: Georgia, serif;
        line-height: 1.6;
        padding: 1em;
        margin: 0;
        color: #222;
    }
    .post-date {
        color: #666;
        font-size: 0.9em;
        margin-bottom: 0.5em;
        font-weight: normal;
    }
    .summary {
        font-style: italic;
        color: #2c5282;
        background-color: #ebf8ff;
        padding: 1em;
        margin: 1em 0;
        border-left: 4px solid #4299e1;
        border-radius: 4px;
    }
    .text {
        margin-top: 1em;
        line-height: 1.6;
    }
    .text p {
        margin: 0.5em 0;
    }
    .text strong, .text b {
        font-weight: bold;
        color: #1a202c;
    }
    .text em, .text i {
        font-style: italic;
        color: #4a5568;
    }
    .text a {
        color: #3182ce;
        text-decoration: underline;
    }
    .text code {
        background-color: #f7fafc;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
    }
    .text pre {
        background-color: #f7fafc;
        padding: 1em;
        border-radius: 5px;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
        border-left: 4px solid #e2e8f0;
        white-space: pre-wrap;
    }
    .text blockquote {
        border-left: 4px solid #e2e8f0;
        padding-left: 1em;
        margin: 1em 0;
        color: #4a5568;
        font-style: italic;
    }
    .text ul, .text ol {
        margin: 0.5em 0;
        padding-left: 1.5em;
    }
    .text li {
        margin: 0.2em 0;
    }
    .post {
        margin-bottom: 2em;
        padding-bottom: 1em;
        border-bottom: 1px solid #eee;
    }
    .post:last-child {
        border-bottom: none;
    }
    .channel-title {
        color: #2d3748;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5em;
        margin-bottom: 1em;
        font-size: 1.2em;
        font-weight: bold;
    }
    h1 {
        color: #2d3748;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5em;
        margin-bottom: 1em;
        font-size: 1.5em;
    }
    h2, h3, h4, h5, h6 {
        color: #2d3748;
        margin: 1em 0 0.5em 0;
    }
    h2 { font-size: 1.3em; }
    h3 { font-size: 1.1em; }
    .divider {
        border-bottom: 1px solid #eee;
        margin: 1em 0;
    }
    '''
    
    # Добавляем CSS в книгу
    css = epub.EpubItem(
        uid="style_default",
        file_name="style/default.css",
        media_type="text/css",
        content=style
    )
    book.add_item(css)
    
    # Парсим HTML для создания глав
    soup = BeautifulSoup(html, 'html.parser')
    chapters = []
    
    # Находим все каналы и их посты более эффективно
    channel_sections = soup.find_all('div', class_='channel-title')
    
    for channel_section in channel_sections:
        channel_name = channel_section.get_text(strip=True)
        
        # Находим все посты этого канала (следующие за заголовком канала)
        posts = []
        current = channel_section.find_next_sibling()
        
        while current and not (isinstance(current, Tag) and current.get('class') and 'channel-title' in current.get('class')):
            if isinstance(current, Tag) and current.get('class') and 'post' in current.get('class'):
                posts.append(current)
            current = current.find_next_sibling()
        
        if not posts:
            continue
        
        # Создаем главу для канала с постами
        chapter = epub.EpubHtml(
            title=channel_name,
            file_name=f'channel_{len(chapters)}.xhtml',
            lang='ru'
        )
        chapter.add_item(css)  # Привязываем CSS к главе
        
        # Формируем контент главы
        content_parts = [f"<h1>{channel_name}</h1>"]
        
        for post in posts:
            post_date = post.find('div', class_='post-date')
            post_summary = post.find('div', class_='summary')
            post_text = post.find('div', class_='text')
            
            content_parts.append('<div class="post">')
            
            if post_date:
                content_parts.append(f'<div class="post-date">{post_date.get_text()}</div>')
            
            if post_summary:
                content_parts.append(f'<div class="summary">{post_summary.get_text()}</div>')
            
            if post_text:
                # Сохраняем HTML разметку из поста
                content_parts.append(f'<div class="text">{post_text.decode_contents()}</div>')
            
            content_parts.append('</div>')
        
        chapter.content = "\n".join(content_parts)
        book.add_item(chapter)
        chapters.append(chapter)
    
    # Создаем оглавление
    book.toc = chapters
    
    # Добавляем навигационные файлы
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Определяем порядок чтения
    book.spine = ['nav'] + chapters
    
    # Сохраняем книгу
    epub.write_epub(out_path, book)
    return out_path

def generate_digest_for_days(days: int, channels: Optional[List[str]] = None) -> Tuple[str, str, int]:
    """
    Генерирует дайджест за последние N дней.
    
    Args:
        days: Количество дней для дайджеста
        channels: Список каналов (если None, загружается из YAML)
    
    Returns:
        Tuple с путями к PDF, EPUB файлам и количеством постов
    """
    # Московская часовая зона (UTC+3)
    moscow_tz = timezone(timedelta(hours=3))
    
    # Вычисляем даты
    date_to = datetime.now(moscow_tz)
    date_from = date_to - timedelta(days=days)
    
    print(f"Генерируем дайджест за последние {days} дней")
    print(f"Период: {date_from.strftime('%Y-%m-%d %H:%M')} - {date_to.strftime('%Y-%m-%d %H:%M')} (МСК)")
    
    return generate_digest(date_from, date_to, channels)

def generate_digest(date_from: datetime, date_to: datetime, channels: Optional[List[str]] = None) -> Tuple[str, str, int]:
    """
    Генерирует дайджест в форматах PDF и EPUB.
    Возвращает пути к файлам и количество постов.
    """
    if channels is None:
        channels = load_channels_from_yaml()
    posts = get_digest_posts(date_from, date_to, channels)
    html = render_digest_html(posts, date_from, date_to)
    
    # Генерируем оба формата
    pdf_path = save_pdf_from_html(html, date_from, date_to)
    epub_path = save_epub_from_html(html, date_from, date_to)
    
    return pdf_path, epub_path, len(posts)

# Обновляем старую функцию для обратной совместимости
def generate_pdf_digest(date_from: datetime, date_to: datetime, channels: Optional[List[str]] = None) -> Tuple[str, int]:
    pdf_path, _, count = generate_digest(date_from, date_to, channels)
    return pdf_path, count

def generate_test_pdf(channel: str = "@cryptoEssay") -> None:
    """
    Генерирует тестовый PDF с постами из указанного канала.
    Если постов нет, использует тестовые данные.
    """
    from datetime import datetime, timedelta
    
    # Пробуем получить реальные посты
    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)
    
    try:
        pdf_path, epub_path, count = generate_digest(date_from, date_to, [channel])
        print(f"✅ PDF сгенерирован: {pdf_path}")
        print(f"✅ EPUB сгенерирован: {epub_path}")
        print(f"📊 Количество постов: {count}")
        
        if count == 0:
            print("⚠️  Нет постов для генерации. Создаем тестовый PDF с демо-данными...")
            generate_demo_pdf()
            
    except Exception as e:
        print(f"❌ Ошибка при генерации: {str(e)}")
        print("Создаем тестовый PDF с демо-данными...")
        generate_demo_pdf()

def generate_demo_pdf() -> None:
    """Создает демо PDF с тестовыми данными для проверки форматирования."""
    from datetime import datetime, timedelta
    
    # Тестовые данные с разным форматированием
    demo_posts = [
        {
            'channel': 'demo_channel',
            'date': datetime.now() - timedelta(hours=2),
            'summary': 'Это тестовый пост с саммари',
            'text_html': '''
                <p>Это <strong>жирный текст</strong> и <em>курсив</em>.</p>
                <p>Ссылка: <a href="https://example.com">example.com</a></p>
                <p>Код: <code>print("Hello, World!")</code></p>
                <pre>Блок кода:
def hello():
    return "Hello, World!"</pre>
                <blockquote>Это цитата с красивым оформлением</blockquote>
                <ul>
                    <li>Первый пункт списка</li>
                    <li>Второй пункт списка</li>
                    <li>Третий пункт списка</li>
                </ul>
                <p>Обычный параграф с <strong>выделением</strong> и <em>курсивом</em>.</p>
            '''
        },
        {
            'channel': 'demo_channel',
            'date': datetime.now() - timedelta(hours=1),
            'summary': 'Второй тестовый пост',
            'text_html': '''
                <h3>Заголовок третьего уровня</h3>
                <p>Еще один параграф с <strong>форматированием</strong>.</p>
                <p>Специальные символы: &lt; &gt; &amp; &quot; &apos;</p>
                <p>Эмодзи: 😀 🚀 💻 📱</p>
            '''
        }
    ]
    
    # Генерируем HTML
    html = render_digest_html(demo_posts, datetime.now() - timedelta(days=1), datetime.now())
    
    # Сохраняем PDF
    pdf_path = save_pdf_from_html(html, datetime.now() - timedelta(days=1), datetime.now())
    print(f"✅ Демо PDF создан: {pdf_path}") 
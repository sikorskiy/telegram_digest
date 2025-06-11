import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from telegram_digest.firebase_db import init_firebase
from telegram_digest.config import load_channels_from_yaml
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
    LIMIT = 100
    all_posts = []

    db = init_firebase()
    messages_ref = db.collection('messages')
    
    for channel in channels:
        # Получаем 100 самых свежих постов по каналу
        docs = list(messages_ref.where(
            filter=FieldFilter('channel', '==', channel)
        ).order_by('date', direction=firestore.Query.DESCENDING).limit(LIMIT).stream())
        print(f"Найдено {len(docs)} постов для канала {channel} (сортировка по дате DESC):")
        for i, doc in enumerate(docs):
            data = doc.to_dict()
            print(f"{i+1}. date={data.get('date')}, summary={data.get('summary')}, text={data.get('plain_text')[:80] if data.get('plain_text') else ''}")
        
        # Получаем посты и сортируем их в обратном порядке (от старых к новым)
        posts = [doc.to_dict() for doc in docs]
        posts.sort(key=lambda x: x['date'])  # ASCENDING
        all_posts.extend(posts)
    
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
    HTML(string=html).write_pdf(out_path)
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
    
    # Создаем CSS стили
    style = '''
    body {
        font-family: Georgia, serif;
        line-height: 1.6;
        padding: 1em;
    }
    .post-date {
        color: #666;
        font-size: 0.9em;
        margin-bottom: 0.5em;
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
    }
    h1 {
        color: #2d3748;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5em;
        margin-bottom: 1em;
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
    
    # Находим все каналы
    channel_titles = soup.find_all('div', class_='channel-title')
    for channel_title in channel_titles:
        # Создаем главу для канала
        channel_chapter = epub.EpubHtml(
            title=channel_title.text,
            file_name=f'channel_{len(chapters)}.xhtml',
            lang='ru'
        )
        channel_chapter.content = f"<h1>{channel_title.text}</h1>"
        book.add_item(channel_chapter)
        chapters.append(channel_chapter)
        
        # Находим все посты этого канала
        current = channel_title.next_sibling
        while current and not (isinstance(current, Tag) and current.get('class') and 'channel-title' in current.get('class')):
            if isinstance(current, Tag) and current.get('class') and 'post' in current.get('class'):
                # Создаем главу для поста
                post_date = current.find('div', class_='post-date')
                post_summary = current.find('div', class_='summary')
                post_text = current.find('div', class_='text')
                
                chapter = epub.EpubHtml(
                    title=f"{post_date.text if post_date else ''} - {post_summary.text if post_summary else 'Post'}",
                    file_name=f'post_{len(chapters)}.xhtml',
                    lang='ru'
                )
                
                # Формируем контент главы
                content = []
                if post_date:
                    content.append(f"<div class='post-date'>{post_date.text}</div>")
                if post_summary:
                    content.append(f"<div class='summary'><i>{post_summary.text}</i></div>")
                    content.append("<br><br>")  # Добавляем два переноса строки после саммари
                if post_text:
                    content.append(f"<div class='text'>{post_text.decode_contents()}</div>")
                
                chapter.content = "\n".join(content)
                book.add_item(chapter)
                chapters.append(chapter)
            current = current.next_sibling
    
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

def generate_test_pdf(channel: str = "@cryptoEssay"):
    """
    Генерирует тестовый PDF с постами из указанного канала.
    Если постов нет, использует тестовые данные.
    """
    db = init_firebase()
    messages_ref = db.collection('messages')
    
    # Проверяем структуру данных
    print(f"\nПроверяем данные в базе для канала {channel}:")
    
    # 1. Проверяем все посты
    all_docs = list(messages_ref.limit(5).stream())
    print(f"\nПримеры постов в базе:")
    for doc in all_docs:
        data = doc.to_dict()
        print(f"- channel: {data.get('channel')}")
        print(f"  summary: {data.get('summary')}")
        print(f"  date: {data.get('date')}")
        print("---")
    
    # 2. Пробуем найти посты по каналу
    channel_docs = list(messages_ref.where(filter=FieldFilter('channel', '==', channel)).limit(5).stream())
    print(f"\nПосты для канала {channel}:")
    for doc in channel_docs:
        data = doc.to_dict()
        print(f"- channel: {data.get('channel')}")
        print(f"  summary: {data.get('summary')}")
        print(f"  date: {data.get('date')}")
        print("---")
    
    # 3. Пробуем найти посты с summary (исправленный запрос)
    # В Firestore для проверки на null используется оператор == с null
    summary_docs = list(messages_ref.where(filter=FieldFilter('summary', '!=', None)).limit(5).stream())
    print(f"\nПосты с summary (старый запрос с != None):")
    for doc in summary_docs:
        data = doc.to_dict()
        print(f"- channel: {data.get('channel')}")
        print(f"  summary: {data.get('summary')}")
        print(f"  date: {data.get('date')}")
        print("---")
    
    # Новый запрос для проверки - используем == null
    summary_docs_new = list(messages_ref.where(filter=FieldFilter('summary', '==', None)).limit(5).stream())
    print(f"\nПосты БЕЗ summary (запрос с == null):")
    for doc in summary_docs_new:
        data = doc.to_dict()
        print(f"- channel: {data.get('channel')}")
        print(f"  summary: {data.get('summary')}")
        print(f"  date: {data.get('date')}")
        print("---")
    
    # Теперь пробуем основной запрос - ищем посты где summary существует и не пустой
    # Сначала получаем все посты канала
    channel_posts = list(messages_ref.where(filter=FieldFilter('channel', '==', channel)).stream())
    # Фильтруем их в Python, чтобы найти те, у которых есть summary
    docs = [doc for doc in channel_posts if doc.to_dict().get('summary')]
    print(f"\nРезультат основного запроса:")
    print(f"Найдено постов: {len(docs)}")
    
    if docs:
        test_posts = []
        for doc in docs:
            post = doc.to_dict()
            print(f"\nОбрабатываем пост:")
            print(f"- summary: {post.get('summary')}")
            print(f"- text_html: {post.get('text_html')}")
            print(f"- date: {post.get('date')}")
            test_posts.append({
                'summary': post.get('summary', ''),
                'text_html': post.get('text_html', ''),
                'date': post.get('date')
            })
        test_posts.sort(key=lambda x: x['date'])
        print(f"\nПодготовлено постов для PDF: {len(test_posts)}")
    else:
        print("Постов не найдено, используем тестовые данные")
        test_posts = [
            {
                'summary': 'Это тестовое саммари 1',
                'text_html': '<b>Тестовый пост 1</b><br>Просто текст.',
                'date': datetime.now(timezone.utc) - timedelta(days=2)
            },
            {
                'summary': 'Это тестовое саммари 2',
                'text_html': 'Второй <i>тестовый</i> пост.',
                'date': datetime.now(timezone.utc) - timedelta(days=1)
            }
        ]
    
    date_from = datetime.now(timezone.utc) - timedelta(days=7)
    print("DEBUG: date_from вычислен:", date_from)
    date_to = datetime.now(timezone.utc)
    print("DEBUG: date_to вычислен:", date_to)
    print(f"\nПериод для PDF: {date_from} - {date_to}")
    
    try:
        print("\nГенерируем HTML...")
        html = render_digest_html(test_posts, date_from, date_to)
        print("HTML сгенерирован успешно")
        
        print("\nСохраняем PDF...")
        pdf_path = save_pdf_from_html(html, date_from, date_to)
        print(f"Тестовый PDF сгенерирован: {pdf_path}")
        print(f"Количество постов: {len(test_posts)}")
    except Exception as e:
        print(f"\nОшибка при генерации PDF: {str(e)}")
        print(f"Тип ошибки: {type(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        raise 
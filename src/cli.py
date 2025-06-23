import os
import asyncio
from datetime import *
from typing import *
import click
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from dotenv import load_dotenv
from .fetcher import fetch_posts, fix_text_formatting, update_entities_for_posts
from .summarizer import summarize
import typer
from .pdf_digest import generate_pdf_digest, generate_test_pdf, generate_digest_for_days
from .config import load_channels_from_yaml
from .html_converter import analyze_post_entities, find_posts_with_entities

# Загружаем переменные окружения
load_dotenv()

# Московская часовая зона (UTC+3)
MOSCOW_TZ = timezone(timedelta(hours=3))

def get_client() -> TelegramClient:
    """Создает и возвращает клиент Telegram."""
    session = os.getenv("TG_SESSION", "./storage/session_name.session")
    api_id = int(os.getenv("TG_API_ID", ""))
    api_hash = os.getenv("TG_API_HASH", "")
    
    if not api_id or not api_hash:
        raise ValueError("TG_API_ID and TG_API_HASH must be set in .env file")
    
    return TelegramClient(session, api_id, api_hash)

app = typer.Typer()

@app.command()
def test_connection():
    """Проверяет подключение к Telegram."""
    client = get_client()

    async def inner():
        try:
            await client.connect()
            if not await client.is_user_authorized():
                # Запрашиваем номер телефона
                phone = click.prompt("Введите номер телефона", type=str)
                await client.send_code_request(phone)
                
                try:
                    # Запрашиваем код подтверждения
                    code = click.prompt("Введите код подтверждения", type=str)
                    await client.sign_in(phone, code)
                except PhoneCodeInvalidError:
                    click.echo("Неверный код подтверждения")
                    return
                except SessionPasswordNeededError:
                    # Запрашиваем пароль двухфакторной аутентификации
                    password = click.prompt("Введите пароль двухфакторной аутентификации", type=str, hide_input=True)
                    await client.sign_in(password=password)
            
            click.echo("Подключение успешно установлено!")
            
        except Exception as e:
            click.echo(f"Ошибка при подключении: {str(e)}")
        finally:
            await client.disconnect()

    asyncio.run(inner())

async def fetch_posts_with_connect(client, channel_ids, days):
    await client.connect()
    try:
        await fetch_posts(client, channel_ids, days)
    finally:
        await client.disconnect()

@app.command()
def fix_formatting(days: int = typer.Option(7, "--days", "-d", help="Количество дней для обработки")):
    """
    Исправляет форматирование text_html в существующих постах.
    Перезаписывает text_html используя правильные методы Telethon.
    """
    client = get_client()
    
    async def inner():
        try:
            await client.connect()
            if not await client.is_user_authorized():
                typer.echo("❌ Не авторизован в Telegram. Сначала выполните test-connection", err=True)
                raise typer.Exit(1)
            
            await fix_text_formatting(client, days)
            
        except Exception as e:
            typer.echo(f"❌ Ошибка при исправлении форматирования: {str(e)}", err=True)
            raise typer.Exit(1)
        finally:
            await client.disconnect()
    
    asyncio.run(inner())

@app.command()
def update_entities(days: int = typer.Option(7, "--days", "-d", help="Количество дней для обработки")):
    """
    Обновляет entities для существующих постов.
    Получает оригинальные сообщения из Telegram и добавляет entities в базу.
    """
    client = get_client()
    
    async def inner():
        try:
            await client.connect()
            if not await client.is_user_authorized():
                typer.echo("❌ Не авторизован в Telegram. Сначала выполните test-connection", err=True)
                raise typer.Exit(1)
            
            await update_entities_for_posts(client, days)
            
        except Exception as e:
            typer.echo(f"❌ Ошибка при обновлении entities: {str(e)}", err=True)
            raise typer.Exit(1)
        finally:
            await client.disconnect()
    
    asyncio.run(inner())

@app.command()
def fetch(channels: Optional[str] = None, days: int = 7):
    """
    Загружает посты из указанных каналов.
    channels — список ID каналов через запятую или None (тогда берём из YAML).
    days — за сколько дней загружать посты.
    """
    if channels:
        channel_ids = [c.strip() for c in channels.split(",") if c.strip()]
    else:
        channel_ids = load_channels_from_yaml()
    if not channel_ids:
        typer.echo("❌ Список каналов пуст. Укажите --channels или заполните channels.yaml", err=True)
        raise typer.Exit(1)
    # print(f"[DEBUG] Используемые каналы ({len(channel_ids)}): {channel_ids}")
    client = get_client()
    asyncio.run(fetch_posts_with_connect(client, channel_ids, days))

@app.command()
def summarize_posts(batch: int = 50):
    """
    Заполняет поле summary для постов без дайджеста.
    batch — сколько документов обрабатывать за один запуск.
    """
    count = summarize(batch_size=batch)
    typer.echo(f"✅ Сформировано {count} саммари")

@app.command()
def analyze_post(
    msg_id: int = typer.Argument(..., help="ID сообщения для анализа"),
    channel: Optional[str] = typer.Option(None, "--channel", "-c", help="ID канала (если не указан, ищет во всех каналах)")
):
    """
    Анализирует entities конкретного поста по его номеру.
    Показывает текст, HTML, entities и их типы.
    """
    analyze_post_entities(msg_id, channel)

@app.command()
def find_entities(limit: int = typer.Option(10, "--limit", "-l", help="Максимальное количество постов для поиска")):
    """
    Находит посты, которые содержат entities.
    Показывает список постов с форматированием.
    """
    find_posts_with_entities(limit)

@app.command()
def pdf(
    from_: Optional[str] = typer.Option(None, "--from", help="Дата начала (YYYY-MM-DD), по умолчанию 7 дней назад"),
    to: Optional[str] = typer.Option(None, "--to", help="Дата конца (YYYY-MM-DD), по умолчанию сегодня"),
    channels: Optional[List[str]] = typer.Option(None, "--channels", help="Список каналов через пробел (по умолчанию из YAML)")
):
    """
    Генерирует PDF-дайджест по постам с summary за выбранный период и каналы.
    По умолчанию — последние 7 дней (МСК), каналы из YAML.
    Имя файла: Telegram_<YYYYMMDD>_<YYYYMMDD>.pdf
    """
    date_to = datetime.now(MOSCOW_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    if to:
        date_to = datetime.strptime(to, "%Y-%m-%d").replace(tzinfo=MOSCOW_TZ)
    date_from = date_to - timedelta(days=7)
    if from_:
        date_from = datetime.strptime(from_, "%Y-%m-%d").replace(tzinfo=MOSCOW_TZ)
    channel_list = channels if channels else None
    print(f"DEBUG: Запуск генерации PDF. date_from={date_from}, date_to={date_to}, channels={channel_list}")
    pdf_path, count = generate_pdf_digest(date_from, date_to, channel_list)
    print(f"DEBUG: Генерация PDF завершена. Путь: {pdf_path}, постов: {count}")
    if count == 0:
        typer.echo(f"❌ Нет постов с summary за выбранный период", err=True)
        raise typer.Exit(1)
    typer.echo(f"✓ {os.path.basename(pdf_path)} — {count} постов")

@app.command()
def digest(
    days: int = typer.Option(7, "--days", "-d", help="Количество дней для дайджеста"),
    channels: Optional[List[str]] = typer.Option(None, "--channels", help="Список каналов через пробел (по умолчанию из YAML)")
):
    """
    Генерирует дайджест (PDF + EPUB) за последние N дней.
    По умолчанию — последние 7 дней, каналы из YAML.
    """
    try:
        pdf_path, epub_path, count = generate_digest_for_days(days, channels)
        
        if count == 0:
            typer.echo(f"❌ Нет постов с summary за последние {days} дней", err=True)
            raise typer.Exit(1)
        
        typer.echo(f"✅ PDF: {os.path.basename(pdf_path)}")
        typer.echo(f"✅ EPUB: {os.path.basename(epub_path)}")
        typer.echo(f"📊 Постов в дайджесте: {count}")
        
    except Exception as e:
        typer.echo(f"❌ Ошибка при генерации дайджеста: {str(e)}", err=True)
        raise typer.Exit(1)

@app.command()
def pdf_test(channel: str = typer.Option("@cryptoEssay", "--channel", help="ID канала для тестового PDF")):
    """
    Генерирует тестовый PDF с постами из указанного канала.
    Если постов нет, использует тестовые данные.
    """
    generate_test_pdf(channel)

@app.command()
def export_post(
    msg_id: int = typer.Argument(..., help="ID сообщения для экспорта"),
    channel: Optional[str] = typer.Option(None, "--channel", "-c", help="ID канала (если не указан, ищет во всех каналах)"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Путь к файлу для сохранения (по умолчанию: post_{msg_id}.json)")
):
    """
    Экспортирует пост в JSON файл с полной информацией об entities.
    Полезно для отладки проблем с форматированием.
    """
    try:
        from .firebase_db import init_firebase
        from google.cloud.firestore_v1.base_query import FieldFilter
        from firebase_admin import firestore
        import json
        from datetime import datetime
        
        db = init_firebase()
        messages_ref = db.collection('messages')
        
        # Формируем запрос
        if channel:
            # Ищем в конкретном канале
            query = messages_ref.where('msg_id', '==', msg_id).where('channel', '==', channel)
        else:
            # Ищем во всех каналах
            query = messages_ref.where('msg_id', '==', msg_id)
        
        docs = list(query.stream())
        
        if not docs:
            typer.echo(f"❌ Пост с ID {msg_id} не найден")
            if channel:
                typer.echo(f"   Канал: {channel}")
            raise typer.Exit(1)
        
        # Берем первый найденный пост
        doc = docs[0]
        data = doc.to_dict()
        
        # Подготавливаем данные для экспорта
        export_data = {
            "msg_id": data.get('msg_id'),
            "channel": data.get('channel'),
            "date": data.get('date').isoformat() if data.get('date') else None,
            "plain_text": data.get('plain_text', ''),
            "text_html": data.get('text_html', ''),
            "summary": data.get('summary', ''),
            "entities": data.get('entities', []),
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "post_length": len(data.get('plain_text', '')),
                "entities_count": len(data.get('entities', [])),
                "has_html": bool(data.get('text_html')),
                "has_summary": bool(data.get('summary'))
            }
        }
        
        # Определяем имя файла
        if not output_file:
            output_file = f"post_{msg_id}.json"
        
        # Сохраняем в JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        typer.echo(f"✅ Пост {msg_id} экспортирован в {output_file}")
        typer.echo(f"📊 Информация:")
        typer.echo(f"   Канал: {data.get('channel')}")
        typer.echo(f"   Дата: {data.get('date')}")
        typer.echo(f"   Длина текста: {len(data.get('plain_text', ''))} символов")
        typer.echo(f"   Entities: {len(data.get('entities', []))}")
        typer.echo(f"   Есть HTML: {'Да' if data.get('text_html') else 'Нет'}")
        typer.echo(f"   Есть summary: {'Да' if data.get('summary') else 'Нет'}")
        
    except Exception as e:
        typer.echo(f"❌ Ошибка при экспорте поста {msg_id}: {str(e)}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 
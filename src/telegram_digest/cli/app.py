import os
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import click
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from dotenv import load_dotenv
from ..fetcher import fetch_posts
from telegram_digest.summarizer import summarize
import typer
from telegram_digest.pdf_digest import generate_pdf_digest, generate_test_pdf
from telegram_digest.config import load_channels_from_yaml

# Загружаем переменные окружения
load_dotenv()

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
def pdf(
    from_: Optional[str] = typer.Option(None, "--from", help="Дата начала (YYYY-MM-DD), по умолчанию 7 дней назад"),
    to: Optional[str] = typer.Option(None, "--to", help="Дата конца (YYYY-MM-DD), по умолчанию сегодня"),
    channels: Optional[List[str]] = typer.Option(None, "--channels", help="Список каналов через пробел (по умолчанию из YAML)")
):
    """
    Генерирует PDF-дайджест по постам с summary за выбранный период и каналы.
    По умолчанию — последние 7 дней (UTC), каналы из YAML.
    Имя файла: Telegram_<YYYYMMDD>_<YYYYMMDD>.pdf
    """
    date_to = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    if to:
        date_to = datetime.strptime(to, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    date_from = date_to - timedelta(days=7)
    if from_:
        date_from = datetime.strptime(from_, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    channel_list = channels if channels else None
    print(f"DEBUG: Запуск генерации PDF. date_from={date_from}, date_to={date_to}, channels={channel_list}")
    pdf_path, count = generate_pdf_digest(date_from, date_to, channel_list)
    print(f"DEBUG: Генерация PDF завершена. Путь: {pdf_path}, постов: {count}")
    if count == 0:
        typer.echo(f"❌ Нет постов с summary за выбранный период", err=True)
        raise typer.Exit(1)
    typer.echo(f"✓ {os.path.basename(pdf_path)} — {count} постов")

@app.command()
def pdf_test(channel: str = typer.Option("@cryptoEssay", "--channel", help="ID канала для тестового PDF")):
    """
    Генерирует тестовый PDF с постами из указанного канала.
    Если постов нет, использует тестовые данные.
    """
    generate_test_pdf(channel)

if __name__ == "__main__":
    app() 
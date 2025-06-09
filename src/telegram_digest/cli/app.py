import os
import asyncio
from datetime import datetime
from typing import List
import click
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from dotenv import load_dotenv
from ..fetcher import fetch_posts

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

@click.group()
def app():
    """Telegram Digest - инструмент для сбора и анализа постов из Telegram каналов."""
    pass

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

@app.command()
@click.argument("channels", nargs=-1, required=True)
@click.option("--days", default=1, help="Количество дней для загрузки")
@click.option("--limit", default=100, help="Максимальное количество постов для загрузки")
def fetch(channels: List[str], days: int, limit: int):
    """Загружает посты из указанных каналов за последние N дней."""
    client = get_client()

    async def inner():
        try:
            # Подключаемся к Telegram
            await client.connect()
            if not await client.is_user_authorized():
                raise ValueError("Not authorized. Please run test-connection first")
            
            # Запускаем загрузку
            await fetch_posts(client, channels, days, limit)
            
        except Exception as e:
            click.echo(f"Ошибка при загрузке: {str(e)}")
        finally:
            await client.disconnect()

    asyncio.run(inner())

if __name__ == "__main__":
    app() 
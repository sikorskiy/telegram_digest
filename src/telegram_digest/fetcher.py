import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from telethon import TelegramClient
from telethon.tl.types import Message, Channel
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import ChannelPrivateError, FloodWaitError
import html2text
from .firebase_db import upsert_post, start_run, end_run, check_saved_posts

async def fetch_posts(
    client: TelegramClient,
    channel_ids: List[str],
    days: int = 1,
    limit: int = 10
) -> None:
    """
    Загружает посты из указанных каналов за последние N дней.
    
    Args:
        client: Клиент Telegram
        channel_ids: Список ID каналов
        days: Количество дней для загрузки
        limit: Максимальное количество постов для загрузки
    """
    # Начинаем новый run
    run_id = start_run(days)
    
    try:
        # Создаем конвертер HTML в текст
        h2t = html2text.HTML2Text()
        h2t.ignore_links = False
        h2t.ignore_images = True
        
        # Вычисляем дату начала
        start_date = datetime.now() - timedelta(days=days)
        
        for channel_id in channel_ids:
            try:
                # Получаем информацию о канале
                channel = await client.get_entity(channel_id)
                if not isinstance(channel, Channel):
                    print(f"Пропускаем {channel_id}: не является каналом")
                    continue
                
                # Получаем полную информацию о канале
                full_channel = await client(GetFullChannelRequest(channel))
                
                # Получаем историю сообщений
                history = await client(GetHistoryRequest(
                    peer=channel,
                    limit=limit,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))
                
                added_count = 0
                min_date = None
                # Обрабатываем сообщения
                for message in history.messages:
                    # Конвертируем HTML в текст
                    plain_text = h2t.handle(message.message) if message.message else None
                    
                    # Преобразуем entities в список словарей
                    entities = []
                    if message.entities:
                        for entity in message.entities:
                            entity_dict = {
                                'type': entity.__class__.__name__,
                                'offset': entity.offset,
                                'length': entity.length
                            }
                            # Добавляем специфичные поля для разных типов entities
                            if hasattr(entity, 'url'):
                                entity_dict['url'] = entity.url
                            if hasattr(entity, 'user_id'):
                                entity_dict['user_id'] = entity.user_id
                            entities.append(entity_dict)
                    
                    # Сохраняем пост
                    result = upsert_post(
                        msg_id=message.id,
                        channel_id=channel_id,
                        date=message.date,
                        text_html=message.message,
                        plain_text=plain_text,
                        entities=entities
                    )
                    if result:
                        added_count += 1
                    # Определяем дату самого старого сообщения
                    if min_date is None or (message.date and message.date < min_date):
                        min_date = message.date
                
                print(f"Канал: {channel.title} (@{channel.username}) | считано: {len(history.messages)}, добавлено: {added_count}, самое старое: {min_date}")
                
            except ChannelPrivateError:
                print(f"Не удалось получить доступ к каналу {channel_id}: канал приватный")
            except FloodWaitError as e:
                print(f"Достигнут лимит запросов, ожидаем {e.seconds} секунд")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"Ошибка при загрузке канала {channel_id}: {str(e)}")
    
    finally:
        # Завершаем run
        end_run(run_id) 
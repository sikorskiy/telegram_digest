import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from telethon import TelegramClient
from telethon.tl.types import Message, Channel
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import ChannelPrivateError, FloodWaitError
from .firebase_db import upsert_post, start_run, end_run, check_saved_posts, init_firebase
from google.cloud.firestore_v1.base_query import FieldFilter
from firebase_admin import firestore
from .html_converter import convert_message_to_html

# Московская часовая зона (UTC+3)
MOSCOW_TZ = timezone(timedelta(hours=3))

async def fix_text_formatting(client: TelegramClient, days: int = 7) -> None:
    """
    Исправляет форматирование text_html в существующих постах за последние N дней.
    Перезаписывает text_html используя правильные методы Telethon.
    
    Args:
        client: Клиент Telegram
        days: Количество дней для обработки
    """
    from .firebase_db import init_firebase
    from google.cloud.firestore_v1.base_query import FieldFilter
    from firebase_admin import firestore
    
    db = init_firebase()
    messages_ref = db.collection('messages')
    
    # Вычисляем дату начала
    start_date = datetime.now(MOSCOW_TZ) - timedelta(days=days)
    print(f"Исправляем форматирование постов с {start_date.strftime('%Y-%m-%d %H:%M')} по {datetime.now(MOSCOW_TZ).strftime('%Y-%m-%d %H:%M')} (МСК)")
    
    # Получаем все посты за период
    docs = list(messages_ref.where(
        filter=FieldFilter('date', '>=', start_date)
    ).order_by('date', direction=firestore.Query.DESCENDING).stream())
    
    print(f"Найдено {len(docs)} постов для обработки")
    
    fixed_count = 0
    skipped_count = 0
    
    for doc in docs:
        try:
            data = doc.to_dict()
            msg_id = data.get('msg_id')
            channel_id = data.get('channel')
            
            if not msg_id or not channel_id:
                print(f"⚠ Пропускаем пост {doc.id}: отсутствует msg_id или channel")
                skipped_count += 1
                continue
            
            # Получаем оригинальное сообщение из Telegram
            try:
                channel = await client.get_entity(channel_id)
                message = await client.get_messages(channel, ids=msg_id)
                
                if not message:
                    print(f"⚠ Пост {msg_id} ({channel_id}): сообщение не найдено в Telegram")
                    skipped_count += 1
                    continue
                
                # Получаем правильный HTML с форматированием
                new_text_html = convert_message_to_html(message)
                old_text_html = data.get('text_html', '')
                
                # Сравниваем старый и новый HTML
                if new_text_html != old_text_html:
                    print(f"✓ Пост {msg_id} ({channel_id}): обновляем форматирование")
                    print(f"  Старый: {old_text_html[:100]}...")
                    print(f"  Новый: {new_text_html[:100]}...")
                    
                    # Обновляем в базе
                    doc.reference.update({
                        'text_html': new_text_html,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    })
                    fixed_count += 1
                else:
                    print(f"  Пост {msg_id} ({channel_id}): форматирование уже корректное")
                    skipped_count += 1
                
            except Exception as e:
                print(f"⚠ Ошибка при получении сообщения {msg_id} ({channel_id}): {str(e)}")
                skipped_count += 1
                continue
                
        except Exception as e:
            print(f"⚠ Ошибка при обработке документа {doc.id}: {str(e)}")
            skipped_count += 1
            continue
    
    print(f"\n============================")
    print(f"Исправлено постов: {fixed_count}")
    print(f"Пропущено постов: {skipped_count}")
    print(f"Всего обработано: {len(docs)}")
    print("============================\n")

async def fetch_posts(
    client: TelegramClient,
    channel_ids: List[str],
    days: int = 7,
    batch_size: int = 50
) -> None:
    """
    Загружает посты из указанных каналов за последние N дней батчами.
    
    Args:
        client: Клиент Telegram
        channel_ids: Список ID каналов
        days: Количество дней для загрузки
        batch_size: Размер батча для загрузки (по умолчанию 50)
    """
    total_added = 0
    total_channels = 0
    total_skipped_no_text = 0
    total_skipped_short = 0
    total_skipped_exists = 0
    # Начинаем новый run
    run_id = start_run(days)
    
    try:
        # Вычисляем дату начала в московском времени
        start_date = datetime.now(MOSCOW_TZ) - timedelta(days=days)
        print(f"Загружаем посты с {start_date.strftime('%Y-%m-%d %H:%M')} по {datetime.now(MOSCOW_TZ).strftime('%Y-%m-%d %H:%M')} (МСК)")
        
        for channel_id in channel_ids:
            try:
                # Получаем информацию о канале
                channel = await client.get_entity(channel_id)
                if not isinstance(channel, Channel):
                    print(f"Пропускаем {channel_id}: не является каналом")
                    continue
                
                total_channels += 1  # Увеличиваем счетчик обработанных каналов
                print(f"\nЗагружаем канал: {channel.title} (@{channel.username})")
                
                added_count = 0
                skipped_no_text = 0
                skipped_short = 0
                skipped_exists = 0
                total_fetched = 0
                offset_date = None
                offset_id = 0
                reached_old_date = False
                
                # Загружаем посты батчами до достижения нужной даты
                while not reached_old_date:
                    # Получаем батч сообщений
                    history = await client(GetHistoryRequest(
                        peer=channel,
                        limit=batch_size,
                        offset_date=offset_date,
                        offset_id=offset_id,
                        max_id=0,
                        min_id=0,
                        add_offset=0,
                        hash=0
                    ))
                    
                    if not history.messages:
                        print(f"Больше сообщений нет")
                        break
                    
                    # Обрабатываем сообщения в батче
                    batch_added = 0
                    batch_skipped_no_text = 0
                    batch_skipped_short = 0
                    batch_skipped_exists = 0
                    
                    for message in history.messages:
                        # Проверяем дату сообщения
                        if message.date:
                            msg_date = message.date
                            if msg_date.tzinfo is None:
                                msg_date = msg_date.replace(tzinfo=timezone.utc)
                            
                            if msg_date < start_date:
                                print(f"Достигнута дата {start_date.strftime('%Y-%m-%d %H:%M')} (МСК), останавливаемся")
                                reached_old_date = True
                                break
                        
                        # Используем raw_text от Telegram API (чистый текст без HTML)
                        plain_text = message.raw_text if message.raw_text else None
                        
                        # Фильтруем короткие посты (меньше 5 слов)
                        if plain_text and len(plain_text.split()) >= 5:
                            # Сериализуем entities для сохранения
                            serialized_entities = None
                            if message.entities:
                                serialized_entities = [serialize_entity(entity) for entity in message.entities]
                            
                            # Сохраняем пост с HTML-форматированием и entities
                            result = upsert_post(
                                msg_id=message.id,
                                channel_id=channel_id,
                                date=message.date,
                                text_html=convert_message_to_html(message),
                                plain_text=plain_text,
                                entities=serialized_entities
                            )
                            if result:
                                added_count += 1
                                batch_added += 1
                            else:
                                # Пост уже существует в базе
                                skipped_exists += 1
                                batch_skipped_exists += 1
                        else:
                            # Пропускаем короткие посты
                            if plain_text:
                                word_count = len(plain_text.split())
                                print(f"  Пропускаем короткий пост ({word_count} слов): {plain_text[:50]}...")
                                skipped_short += 1
                                batch_skipped_short += 1
                            else:
                                print(f"  Пропускаем пост без текста")
                                skipped_no_text += 1
                                batch_skipped_no_text += 1
                    
                    # Если достигли старой даты, выходим из цикла
                    if reached_old_date:
                        break
                    
                    total_fetched += len(history.messages)
                    
                    # Обновляем offset для следующего запроса (берем самое старое сообщение из батча)
                    if history.messages:
                        # Сообщения в history.messages идут от новых к старым
                        # Поэтому последнее сообщение в списке - самое старое
                        oldest_message = history.messages[-1]
                        offset_date = oldest_message.date
                        offset_id = oldest_message.id
                    
                    print(f"  Батч: {len(history.messages)} сообщений, добавлено: {batch_added}, пропущено (короткие: {batch_skipped_short}, без текста: {batch_skipped_no_text}, уже есть: {batch_skipped_exists}), всего: {added_count}, обработано: {total_fetched}")
                    
                    # Небольшая пауза между запросами
                    await asyncio.sleep(1)
                
                total_added += added_count  # Добавляем к общему счетчику
                total_skipped_no_text += skipped_no_text
                total_skipped_short += skipped_short
                total_skipped_exists += skipped_exists
                
                print(f"Канал: {channel.title} (@{channel.username}) | итого: добавлено {added_count}, пропущено (короткие: {skipped_short}, без текста: {skipped_no_text}, уже есть: {skipped_exists})")
                
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
        print("\n============================")
        print(f"Всего каналов обработано: {total_channels}")
        print(f"Всего постов добавлено: {total_added}")
        print(f"Всего пропущено:")
        print(f"  - без текста: {total_skipped_no_text}")
        print(f"  - короткие (<5 слов): {total_skipped_short}")
        print(f"  - уже в базе: {total_skipped_exists}")
        print("============================\n") 

def serialize_entity(entity) -> dict:
    """
    Сериализует entity Telethon в словарь для сохранения в Firestore.
    
    Args:
        entity: Объект entity из Telethon
        
    Returns:
        Словарь с данными entity
    """
    entity_data = {
        'type': type(entity).__name__,
        'offset': entity.offset,
        'length': entity.length
    }
    
    # Добавляем дополнительные атрибуты в зависимости от типа
    if hasattr(entity, 'url'):
        entity_data['url'] = entity.url
    if hasattr(entity, 'language'):
        entity_data['language'] = entity.language
    if hasattr(entity, 'document_id'):
        entity_data['document_id'] = entity.document_id
    if hasattr(entity, 'custom_emoji_id'):
        entity_data['custom_emoji_id'] = entity.custom_emoji_id
    
    return entity_data

async def update_entities_for_posts(client: TelegramClient, days: int = 7) -> None:
    """
    Обновляет entities для существующих постов за последние N дней.
    Получает оригинальные сообщения из Telegram и добавляет entities в базу.
    
    Args:
        client: Клиент Telegram
        days: Количество дней для обработки
    """
    from .firebase_db import init_firebase
    from google.cloud.firestore_v1.base_query import FieldFilter
    from firebase_admin import firestore
    
    db = init_firebase()
    messages_ref = db.collection('messages')
    
    # Вычисляем дату начала
    start_date = datetime.now(MOSCOW_TZ) - timedelta(days=days)
    print(f"Обновляем entities для постов с {start_date.strftime('%Y-%m-%d %H:%M')} по {datetime.now(MOSCOW_TZ).strftime('%Y-%m-%d %H:%M')} (МСК)")
    
    # Получаем все посты за период
    docs = list(messages_ref.where(
        filter=FieldFilter('date', '>=', start_date)
    ).order_by('date', direction=firestore.Query.DESCENDING).stream())
    
    print(f"Найдено {len(docs)} постов для обработки")
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for doc in docs:
        try:
            data = doc.to_dict()
            msg_id = data.get('msg_id')
            channel_id = data.get('channel')
            
            if not msg_id or not channel_id:
                print(f"⚠ Пропускаем пост {doc.id}: отсутствует msg_id или channel")
                skipped_count += 1
                continue
            
            # Проверяем, есть ли уже entities
            existing_entities = data.get('entities', [])
            if existing_entities:
                print(f"  Пост {msg_id} ({channel_id}): entities уже есть ({len(existing_entities)}), пропускаем")
                skipped_count += 1
                continue
            
            # Получаем оригинальное сообщение из Telegram
            try:
                channel = await client.get_entity(channel_id)
                message = await client.get_messages(channel, ids=msg_id)
                
                if not message:
                    print(f"⚠ Пост {msg_id} ({channel_id}): сообщение не найдено в Telegram")
                    skipped_count += 1
                    continue
                
                # Получаем entities из сообщения
                entities = message.entities or []
                
                if entities:
                    print(f"✓ Пост {msg_id} ({channel_id}): добавляем {len(entities)} entities")
                    
                    # Сериализуем entities для сохранения в Firestore
                    serialized_entities = [serialize_entity(entity) for entity in entities]
                    
                    # Обновляем в базе
                    doc.reference.update({
                        'entities': serialized_entities,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    })
                    updated_count += 1
                else:
                    print(f"  Пост {msg_id} ({channel_id}): entities нет в оригинальном сообщении")
                    skipped_count += 1
                
            except Exception as e:
                print(f"⚠ Ошибка при получении сообщения {msg_id} ({channel_id}): {str(e)}")
                error_count += 1
                continue
                
        except Exception as e:
            print(f"⚠ Ошибка при обработке документа {doc.id}: {str(e)}")
            error_count += 1
            continue
    
    print(f"\n============================")
    print(f"Обновлено постов: {updated_count}")
    print(f"Пропущено постов: {skipped_count}")
    print(f"Ошибок: {error_count}")
    print(f"Всего обработано: {len(docs)}")
    print("============================\n") 
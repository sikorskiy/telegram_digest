"""
Модуль для преобразования сообщений Telethon в HTML с сохранением форматирования.
Поддерживает все основные entity: bold, italic, underline, strikethrough, 
spoiler, ссылки, код, pre, mention и другие.
"""

import html
from typing import List, Tuple, Optional
from telethon.tl.types import Message


def deserialize_entity(entity_data: dict):
    """
    Десериализует entity из словаря обратно в объект.
    
    Args:
        entity_data: Словарь с данными entity
        
    Returns:
        Объект entity с атрибутами offset, length и другими
    """
    class DeserializedEntity:
        def __init__(self, data):
            self.offset = data.get('offset', 0)
            self.length = data.get('length', 0)
            self._type = data.get('type', 'Unknown')
            
            # Копируем дополнительные атрибуты
            for key, value in data.items():
                if key not in ['type', 'offset', 'length']:
                    setattr(self, key, value)
        
        def __repr__(self):
            return f"DeserializedEntity({self._type}, offset={self.offset}, length={self.length})"
    
    return DeserializedEntity(entity_data)


def convert_message_to_html(message: Message) -> str:
    """
    Конвертирует сообщение Telethon в HTML с сохранением форматирования.
    
    Args:
        message: Объект сообщения из Telethon
        
    Returns:
        HTML-строка с сохраненным форматированием
    """
    if not message.message:
        return ""
    
    # Получаем текст и entities
    text = message.message
    entities = message.entities or []
    
    # Обрабатываем entities и вставляем HTML-теги
    html_text = _process_entities(text, entities)
    
    # Заменяем переносы строк на <br>
    html_text = html_text.replace('\n', '<br>')
    
    # Обертываем в div с CSS для сохранения форматирования
    return f'<div style="white-space: pre-wrap;">{html_text}</div>'


def _process_entities(text: str, entities: List) -> str:
    """
    Обрабатывает entities и вставляет HTML-теги в нужные позиции.
    Работает с UTF-16 смещениями, которые использует Telegram.
    
    Args:
        text: Исходный текст
        entities: Список entity из сообщения
        
    Returns:
        Текст с вставленными HTML-тегами
    """
    if not entities:
        return _escape_html(text)

    # 1. Собираем границы тегов из entities
    boundaries = []
    for entity in entities:
        open_tag, close_tag = _get_entity_tag(entity)
        if open_tag and close_tag:
            # Смещения в UTF-16
            utf16_offset = entity.offset
            utf16_length = entity.length
            boundaries.append((utf16_offset, 'open', open_tag))
            boundaries.append((utf16_offset + utf16_length, 'close', close_tag))

    # 2. Сортируем границы: сначала по смещению, потом закрывающие теги перед открывающими
    boundaries.sort(key=lambda b: (b[0], b[1] == 'open'))

    # 3. Собираем итоговую строку по частям
    result_parts = []
    last_utf16_offset = 0
    
    # Кодируем текст в UTF-16 для корректных срезов
    text_utf16_encoded = text.encode('utf-16-le')

    for offset, type, tag in boundaries:
        # Проверяем, есть ли текст между последней и текущей позицией
        if offset > last_utf16_offset:
            # Делаем срез в байтах и декодируем обратно
            slice_bytes = text_utf16_encoded[last_utf16_offset*2 : offset*2]
            text_slice = slice_bytes.decode('utf-16-le')
            result_parts.append(_escape_html(text_slice))
        
        # Добавляем сам тег
        result_parts.append(tag)
        
        last_utf16_offset = offset

    # 4. Добавляем оставшийся кусок текста после последнего тега
    if last_utf16_offset * 2 < len(text_utf16_encoded):
        slice_bytes = text_utf16_encoded[last_utf16_offset*2:]
        text_slice = slice_bytes.decode('utf-16-le')
        result_parts.append(_escape_html(text_slice))

    return "".join(result_parts)


def _get_entity_tag(entity) -> Tuple[Optional[str], Optional[str]]:
    """
    Возвращает (открывающий_тег, закрывающий_тег) для entity.
    
    Args:
        entity: Объект entity из Telethon или десериализованный entity
        
    Returns:
        Кортеж с открывающим и закрывающим тегами
    """
    # Определяем тип entity
    if hasattr(entity, '_type'):
        # Десериализованный entity
        entity_type = entity._type
    else:
        # Оригинальный entity из Telethon
        entity_type = type(entity).__name__
    
    if entity_type == 'MessageEntityBold':
        return '<b>', '</b>'
    elif entity_type == 'MessageEntityItalic':
        return '<i>', '</i>'
    elif entity_type == 'MessageEntityUnderline':
        return '<u>', '</u>'
    elif entity_type == 'MessageEntityStrike':
        return '<s>', '</s>'
    elif entity_type == 'MessageEntitySpoiler':
        return '<span class="tg-spoiler">', '</span>'
    elif entity_type == 'MessageEntityCode':
        return '<code>', '</code>'
    elif entity_type == 'MessageEntityPre':
        return '<pre>', '</pre>'
    elif entity_type == 'MessageEntityTextUrl':
        url = getattr(entity, 'url', '#')
        return f'<a href="{url}">', '</a>'
    elif entity_type == 'MessageEntityUrl':
        # Для обычных URL нужно извлечь URL из текста
        return '<a href="#">', '</a>'  # Заглушка, нужно доработать
    elif entity_type == 'MessageEntityMention':
        # Mention обычно содержит @username
        return '<a href="https://t.me/">', '</a>'  # Заглушка, нужно доработать
    else:
        # Неизвестный тип entity - игнорируем
        print(f"Неизвестный тип entity: {entity_type}")
        return None, None


def _escape_html(text: str) -> str:
    """
    Экранирует HTML-символы в тексте.
    
    Args:
        text: Исходный текст
        
    Returns:
        Текст с экранированными HTML-символами
    """
    return html.escape(text)


# Функция для анализа entities конкретного поста
def analyze_post_entities(msg_id: int, channel_id: str = None):
    """
    Анализирует entities конкретного поста по его номеру.
    
    Args:
        msg_id: ID сообщения
        channel_id: ID канала (если не указан, ищет во всех каналах)
    """
    try:
        from .firebase_db import init_firebase
        from google.cloud.firestore_v1.base_query import FieldFilter
        from firebase_admin import firestore
        
        db = init_firebase()
        messages_ref = db.collection('messages')
        
        # Формируем запрос
        if channel_id:
            # Ищем в конкретном канале
            query = messages_ref.where('msg_id', '==', msg_id).where('channel', '==', channel_id)
        else:
            # Ищем во всех каналах
            query = messages_ref.where('msg_id', '==', msg_id)
        
        docs = list(query.stream())
        
        if not docs:
            print(f"❌ Пост с ID {msg_id} не найден")
            if channel_id:
                print(f"   Канал: {channel_id}")
            return
        
        # Берем первый найденный пост
        doc = docs[0]
        data = doc.to_dict()
        
        print(f"🔍 Анализ поста {msg_id}")
        print("=" * 60)
        print(f"Канал: {data.get('channel')}")
        print(f"Дата: {data.get('date')}")
        print(f"ID в базе: {doc.id}")
        
        # Анализируем текст
        plain_text = data.get('plain_text', '')
        text_html = data.get('text_html', '')
        
        print(f"\n📝 Текст ({len(plain_text)} символов):")
        print(f"'{plain_text[:200]}{'...' if len(plain_text) > 200 else ''}'")
        
        print(f"\n🔗 HTML ({len(text_html)} символов):")
        print(f"'{text_html[:200]}{'...' if len(text_html) > 200 else ''}'")
        
        # Анализируем entities (если есть)
        entities = data.get('entities', [])
        if entities:
            print(f"\n🏷️  Entities ({len(entities)}):")
            for i, entity_data in enumerate(entities, 1):
                # Десериализуем entity для анализа
                entity = deserialize_entity(entity_data)
                
                print(f"\n  {i}. Тип: {entity._type}")
                print(f"     offset: {entity.offset}")
                print(f"     length: {entity.length}")
                
                # Показываем выделенный текст
                start = entity.offset
                end = entity.offset + entity.length
                if start < len(plain_text) and end <= len(plain_text):
                    highlighted_text = plain_text[start:end]
                    print(f"     текст: '{highlighted_text}'")
                else:
                    print(f"     текст: [выход за границы текста]")
                
                # Дополнительные атрибуты
                if hasattr(entity, 'url'):
                    print(f"     url: {entity.url}")
                if hasattr(entity, 'language'):
                    print(f"     language: {entity.language}")
                if hasattr(entity, 'custom_emoji_id'):
                    print(f"     custom_emoji_id: {entity.custom_emoji_id}")
                
                # Получаем HTML теги
                open_tag, close_tag = _get_entity_tag(entity)
                if open_tag and close_tag:
                    print(f"     HTML: {open_tag}текст{close_tag}")
                else:
                    print(f"     HTML: не поддерживается")
        else:
            print(f"\n🏷️  Entities: нет")
        
        # Показываем summary
        summary = data.get('summary')
        if summary:
            print(f"\n📋 Summary: {summary}")
        else:
            print(f"\n📋 Summary: отсутствует")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка при анализе поста {msg_id}: {str(e)}")


# Функция для поиска постов с entities
def find_posts_with_entities(limit: int = 10):
    """
    Находит посты, которые содержат entities.
    
    Args:
        limit: Максимальное количество постов для поиска
    """
    try:
        from .firebase_db import init_firebase
        from firebase_admin import firestore
        
        db = init_firebase()
        messages_ref = db.collection('messages')
        
        # Получаем посты с entities
        docs = list(messages_ref.order_by('date', direction=firestore.Query.DESCENDING).limit(limit).stream())
        
        print(f"🔍 Поиск постов с entities (последние {limit}):")
        print("=" * 60)
        
        found_count = 0
        for doc in docs:
            data = doc.to_dict()
            entities = data.get('entities', [])
            
            if entities:
                found_count += 1
                msg_id = data.get('msg_id')
                channel = data.get('channel')
                plain_text = data.get('plain_text', '')
                
                print(f"\n📝 Пост {msg_id} (@{channel})")
                print(f"   Entities: {len(entities)}")
                print(f"   Текст: '{plain_text[:100]}{'...' if len(plain_text) > 100 else ''}'")
                
                # Показываем типы entity
                entity_types = [type(entity).__name__ for entity in entities]
                print(f"   Типы: {', '.join(entity_types)}")
        
        if found_count == 0:
            print("❌ Посты с entities не найдены")
        else:
            print(f"\n✅ Найдено постов с entities: {found_count}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка при поиске постов: {str(e)}")


# Функция для демонстрации типов entity
def demonstrate_entity_types():
    """Демонстрирует различные типы entity и их структуру."""
    
    # Создаем тестовые entity разных типов
    class MessageEntityBold:
        def __init__(self, offset, length):
            self.offset = offset
            self.length = length
    
    class MessageEntityItalic:
        def __init__(self, offset, length):
            self.offset = offset
            self.length = length
    
    class MessageEntityTextUrl:
        def __init__(self, offset, length, url):
            self.offset = offset
            self.length = length
            self.url = url
    
    class MessageEntityCode:
        def __init__(self, offset, length):
            self.offset = offset
            self.length = length
    
    class MessageEntityHashtag:
        def __init__(self, offset, length):
            self.offset = offset
            self.length = length
    
    # Примеры entity
    entities = [
        MessageEntityBold(0, 10),
        MessageEntityItalic(5, 8),
        MessageEntityTextUrl(0, 15, "https://google.com"),
        MessageEntityCode(5, 8),
        MessageEntityHashtag(0, 10)
    ]
    
    print("🔍 Демонстрация типов Entity в Telegram")
    print("=" * 50)
    
    for i, entity in enumerate(entities, 1):
        entity_type = type(entity).__name__
        print(f"\n{i}. Тип: {entity_type}")
        print(f"   offset: {entity.offset}")
        print(f"   length: {entity.length}")
        
        # Дополнительные атрибуты для специальных entity
        if hasattr(entity, 'url'):
            print(f"   url: {entity.url}")
        
        # Получаем HTML теги
        open_tag, close_tag = _get_entity_tag(entity)
        if open_tag and close_tag:
            print(f"   HTML: {open_tag}текст{close_tag}")
        else:
            print(f"   HTML: не поддерживается")
    
    print("\n" + "=" * 50)
    print("💡 Вывод: тип entity определяется классом объекта, а не параметрами!")


# Функция для тестирования
def test_converter():
    """Тестовая функция для проверки работы конвертера."""
    # Создаем тестовое сообщение (заглушка)
    class TestMessage:
        def __init__(self, text, entities=None):
            self.message = text
            self.entities = entities or []
    
    class MessageEntityBold:
        def __init__(self, offset, length):
            self.offset = offset
            self.length = length
    
    class MessageEntityItalic:
        def __init__(self, offset, length):
            self.offset = offset
            self.length = length
    
    class MessageEntityTextUrl:
        def __init__(self, offset, length, url):
            self.offset = offset
            self.length = length
            self.url = url
    
    # Тестовые случаи
    test_cases = [
        ("Простой текст", []),
        ("Жирный текст", [MessageEntityBold(0, 12)]),
        ("Курсивный текст", [MessageEntityItalic(0, 15)]),
        ("Жирный и курсив", [
            MessageEntityBold(0, 6),
            MessageEntityItalic(9, 8)
        ]),
        ("Ссылка на Google", [MessageEntityTextUrl(0, 15, "https://google.com")]),
        # Сложный случай с вложенными тегами
        ("Жирный текст с курсивом внутри", [
            MessageEntityBold(0, 25),
            MessageEntityItalic(12, 8)
        ]),
        # Случай с пересекающимися тегами (как в проблемном примере)
        ("Внутри ChatGPT нашли персоны", [
            MessageEntityBold(0, 30),
            MessageEntityTextUrl(20, 10, "https://example.com")
        ]),
    ]
    
    for text, entities in test_cases:
        message = TestMessage(text, entities)
        html_result = convert_message_to_html(message)
        print(f"Текст: {text}")
        print(f"HTML: {html_result}")
        print("-" * 50)


def debug_entity_processing(text: str, entities: List, step_by_step: bool = True):
    """
    Пошагово анализирует процесс конвертации entities в HTML.
    
    Args:
        text: Исходный текст
        entities: Список entities
        step_by_step: Показывать каждый шаг
    """
    print("🔍 ПОШАГОВЫЙ АНАЛИЗ АЛГОРИТМА HTML_CONVERTER")
    print("=" * 80)
    
    print(f"📝 Исходный текст ({len(text)} символов):")
    print(f"'{text}'")
    print()
    
    print(f"🏷️  Entities ({len(entities)}):")
    for i, entity in enumerate(entities, 1):
        entity_type = type(entity).__name__ if not hasattr(entity, '_type') else entity._type
        print(f"  {i}. {entity_type}: offset={entity.offset}, length={entity.length}")
        # Показываем выделенный текст
        start = entity.offset
        end = entity.offset + entity.length
        if start < len(text) and end <= len(text):
            highlighted_text = text[start:end]
            print(f"     текст: '{highlighted_text}'")
        else:
            print(f"     текст: [выход за границы текста]")
    print()
    
    if not entities:
        print("❌ Нет entities, возвращаем экранированный текст")
        escaped = _escape_html(text)
        print(f"Экранированный: '{escaped}'")
        return escaped
    
    # Шаг 1: Экранирование HTML
    print("🔧 ШАГ 1: Экранирование HTML-символов")
    text_escaped = _escape_html(text)
    print(f"До: '{text}'")
    print(f"После: '{text_escaped}'")
    print()
    
    # Шаг 2: Сортировка entities
    print("🔧 ШАГ 2: Сортировка entities по offset")
    sorted_entities = sorted(entities, key=lambda e: e.offset)
    for i, entity in enumerate(sorted_entities, 1):
        entity_type = type(entity).__name__ if not hasattr(entity, '_type') else entity._type
        print(f"  {i}. {entity_type}: offset={entity.offset}, length={entity.length}")
    print()
    
    # Шаг 3: Создание списка символов
    print("🔧 ШАГ 3: Создание списка символов")
    chars = list(text_escaped)
    print(f"Список символов: {chars}")
    print()
    
    # Шаг 4: Сбор позиций тегов
    print("🔧 ШАГ 4: Сбор позиций для вставки тегов")
    tag_positions = []
    for entity in sorted_entities:
        start_pos = entity.offset
        end_pos = entity.offset + entity.length
        open_tag, close_tag = _get_entity_tag(entity)
        
        if open_tag and close_tag:
            entity_type = type(entity).__name__ if not hasattr(entity, '_type') else entity._type
            print(f"  {entity_type}:")
            print(f"    открывающий тег '{open_tag}' на позиции {start_pos}")
            print(f"    закрывающий тег '{close_tag}' на позиции {end_pos}")
            
            tag_positions.append((start_pos, open_tag, 'open', entity))
            tag_positions.append((end_pos, close_tag, 'close', entity))
        else:
            entity_type = type(entity).__name__ if not hasattr(entity, '_type') else entity._type
            print(f"  {entity_type}: теги не поддерживаются")
    print()
    
    # Шаг 5: Сортировка позиций тегов
    print("🔧 ШАГ 5: Сортировка позиций тегов")
    tag_positions.sort(key=lambda x: x[0])
    for i, (pos, tag, tag_type, entity) in enumerate(tag_positions, 1):
        entity_type = type(entity).__name__ if not hasattr(entity, '_type') else entity._type
        print(f"  {i}. Позиция {pos}: {tag_type} тег '{tag}' для {entity_type}")
    print()
    
    # Шаг 6: Вставка тегов
    print("🔧 ШАГ 6: Вставка тегов с учетом вложенности")
    open_tags_stack = []
    offset = 0
    
    for pos, tag, tag_type, entity in tag_positions:
        entity_type = type(entity).__name__ if not hasattr(entity, '_type') else entity._type
        
        if tag_type == 'open':
            print(f"  Открывающий тег '{tag}' для {entity_type} на позиции {pos + offset}")
            chars.insert(pos + offset, tag)
            offset += len(tag)
            open_tags_stack.append((entity, tag))
            print(f"    Стек после добавления: {[e[1] for e in open_tags_stack]}")
        else:
            print(f"  Закрывающий тег '{tag}' для {entity_type} на позиции {pos + offset}")
            # Ищем соответствующий открывающий тег
            found = False
            for i, (stack_entity, stack_tag) in enumerate(open_tags_stack):
                if stack_entity == entity:
                    print(f"    Найден соответствующий открывающий тег '{stack_tag}' в стеке")
                    chars.insert(pos + offset, tag)
                    offset += len(tag)
                    open_tags_stack.pop(i)
                    found = True
                    break
            
            if not found:
                print(f"    ⚠️  Соответствующий открывающий тег не найден!")
            
            print(f"    Стек после удаления: {[e[1] for e in open_tags_stack]}")
        
        if step_by_step:
            current_text = ''.join(chars)
            print(f"    Текущий текст: '{current_text}'")
            print()
    
    # Шаг 7: Финальный результат
    print("🔧 ШАГ 7: Финальный результат")
    result = ''.join(chars)
    print(f"Результат: '{result}'")
    print()
    
    # Шаг 8: Добавление переносов строк и обертки
    print("🔧 ШАГ 8: Обработка переносов строк и обертки")
    result_with_br = result.replace('\n', '<br>')
    final_result = f'<div style="white-space: pre-wrap;">{result_with_br}</div>'
    print(f"С переносами строк: '{result_with_br}'")
    print(f"Финальный HTML: '{final_result}'")
    print()
    
    return final_result


def test_complex_entities():
    """
    Тестирует сложные случаи с entities для выявления проблем.
    """
    print("🧪 ТЕСТИРОВАНИЕ СЛОЖНЫХ СЛУЧАЕВ")
    print("=" * 80)
    
    # Создаем тестовые entity
    class MessageEntityBold:
        def __init__(self, offset, length):
            self.offset = offset
            self.length = length
    
    class MessageEntityItalic:
        def __init__(self, offset, length):
            self.offset = offset
            self.length = length
    
    class MessageEntityTextUrl:
        def __init__(self, offset, length, url):
            self.offset = offset
            self.length = length
            self.url = url
    
    # Тестовые случаи
    test_cases = [
        {
            "name": "Простой случай - один entity",
            "text": "Это жирный текст",
            "entities": [MessageEntityBold(0, 15)]
        },
        {
            "name": "Пересекающиеся entity",
            "text": "Внутри ChatGPT нашли персоны",
            "entities": [
                MessageEntityBold(0, 30),
                MessageEntityTextUrl(20, 10, "https://example.com")
            ]
        },
        {
            "name": "Вложенные entity",
            "text": "Жирный текст с курсивом внутри",
            "entities": [
                MessageEntityBold(0, 25),
                MessageEntityItalic(12, 8)
            ]
        },
        {
            "name": "Entity в конце текста",
            "text": "Обычный текст и жирный",
            "entities": [MessageEntityBold(15, 7)]
        },
        {
            "name": "Entity в начале текста",
            "text": "Жирный и обычный текст",
            "entities": [MessageEntityBold(0, 6)]
        },
        {
            "name": "Множественные entity",
            "text": "Первый жирный, второй курсив, третий ссылка",
            "entities": [
                MessageEntityBold(0, 12),
                MessageEntityItalic(14, 13),
                MessageEntityTextUrl(29, 7, "https://test.com")
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 ТЕСТ {i}: {test_case['name']}")
        print("-" * 60)
        
        try:
            result = debug_entity_processing(
                test_case['text'], 
                test_case['entities'], 
                step_by_step=False
            )
            print(f"✅ Успешно: {result}")
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
        
        print("-" * 60)


def export_post_to_json(msg_id: int, channel_id: str = None, output_file: str = None):
    """
    Экспортирует пост в JSON файл с полной информацией об entities.
    
    Args:
        msg_id: ID сообщения
        channel_id: ID канала (если не указан, ищет во всех каналах)
        output_file: Путь к файлу для сохранения
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
        if channel_id:
            # Ищем в конкретном канале
            query = messages_ref.where('msg_id', '==', msg_id).where('channel', '==', channel_id)
        else:
            # Ищем во всех каналах
            query = messages_ref.where('msg_id', '==', msg_id)
        
        docs = list(query.stream())
        
        if not docs:
            print(f"❌ Пост с ID {msg_id} не найден")
            if channel_id:
                print(f"   Канал: {channel_id}")
            return None
        
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
        
        print(f"✅ Пост {msg_id} экспортирован в {output_file}")
        print(f"📊 Информация:")
        print(f"   Канал: {data.get('channel')}")
        print(f"   Дата: {data.get('date')}")
        print(f"   Длина текста: {len(data.get('plain_text', ''))} символов")
        print(f"   Entities: {len(data.get('entities', []))}")
        print(f"   Есть HTML: {'Да' if data.get('text_html') else 'Нет'}")
        print(f"   Есть summary: {'Да' if data.get('summary') else 'Нет'}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Ошибка при экспорте поста {msg_id}: {str(e)}")
        return None


def test_post_conversion_from_json(json_file: str):
    """
    Тестирует конвертацию поста из JSON файла.
    
    Args:
        json_file: Путь к JSON файлу с данными поста
    """
    try:
        import json
        
        # Загружаем данные из JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            post_data = json.load(f)
        
        print(f"🧪 ТЕСТИРОВАНИЕ КОНВЕРТАЦИИ ПОСТА {post_data['msg_id']}")
        print("=" * 80)
        
        plain_text = post_data['plain_text']
        entities_data = post_data['entities']
        
        print(f"📝 Исходный текст ({len(plain_text)} символов):")
        print(f"'{plain_text}'")
        print()
        
        if not entities_data:
            print("❌ Нет entities для тестирования")
            return
        
        # Десериализуем entities
        entities = []
        for entity_data in entities_data:
            entity = deserialize_entity(entity_data)
            entities.append(entity)
        
        print(f"🏷️  Десериализованные entities ({len(entities)}):")
        for i, entity in enumerate(entities, 1):
            print(f"  {i}. {entity._type}: offset={entity.offset}, length={entity.length}")
            # Показываем выделенный текст
            start = entity.offset
            end = entity.offset + entity.length
            if start < len(plain_text) and end <= len(plain_text):
                highlighted_text = plain_text[start:end]
                print(f"     текст: '{highlighted_text}'")
            else:
                print(f"     текст: [выход за границы текста]")
        print()
        
        # Тестируем конвертацию
        print("🔧 ТЕСТИРОВАНИЕ КОНВЕРТАЦИИ:")
        result = debug_entity_processing(plain_text, entities, step_by_step=True)
        
        print("🔍 СРАВНЕНИЕ С ОРИГИНАЛЬНЫМ HTML:")
        original_html = post_data.get('text_html', '')
        print(f"Оригинальный HTML: '{original_html}'")
        print(f"Новый HTML: '{result}'")
        print(f"Совпадают: {'Да' if original_html == result else 'Нет'}")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {str(e)}")
        return None


def analyze_specific_entities_in_post(json_file: str):
    """
    Детально анализирует конкретные entities в посте.
    
    Args:
        json_file: Путь к JSON файлу с данными поста
    """
    try:
        import json
        
        # Загружаем данные из JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            post_data = json.load(f)
        
        plain_text = post_data['plain_text']
        entities_data = post_data['entities']
        
        print(f"🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ENTITIES В ПОСТЕ {post_data['msg_id']}")
        print("=" * 80)
        
        for i, entity_data in enumerate(entities_data, 1):
            entity = deserialize_entity(entity_data)
            
            print(f"\n📌 ENTITY {i}: {entity._type}")
            print(f"   offset: {entity.offset}")
            print(f"   length: {entity.length}")
            
            # Показываем выделенный текст
            start = entity.offset
            end = entity.offset + entity.length
            if start < len(plain_text) and end <= len(plain_text):
                highlighted_text = plain_text[start:end]
                print(f"   выделенный текст: '{highlighted_text}'")
                
                # Показываем контекст (50 символов до и после)
                context_start = max(0, start - 50)
                context_end = min(len(plain_text), end + 50)
                context = plain_text[context_start:context_end]
                
                # Выделяем entity в контексте
                if context_start < start:
                    before = context[:start - context_start]
                else:
                    before = ""
                
                if end < context_end:
                    after = context[end - context_start:]
                else:
                    after = ""
                
                print(f"   контекст: ...{before}[{highlighted_text}]{after}...")
            else:
                print(f"   выделенный текст: [выход за границы текста]")
            
            # Дополнительные атрибуты
            if hasattr(entity, 'url'):
                print(f"   url: {entity.url}")
            
            # Получаем HTML теги
            open_tag, close_tag = _get_entity_tag(entity)
            if open_tag and close_tag:
                print(f"   HTML теги: {open_tag}...{close_tag}")
            else:
                print(f"   HTML теги: не поддерживается")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Ошибка при анализе: {str(e)}")


if __name__ == "__main__":
    demonstrate_entity_types()
    print("\n" + "=" * 60 + "\n")
    test_converter()
    print("\n" + "=" * 60 + "\n")
    test_complex_entities() 
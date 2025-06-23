import os
import time
from typing import List, Dict, Any
import openai
import typer
from firebase_admin import firestore
from .firebase_db import init_firebase
from google.cloud.firestore_v1.base_query import FieldFilter

def summarize(batch_size: int = 50) -> int:
    """
    Генерирует саммари для сообщений без дайджеста в коллекции messages.
    batch_size: сколько документов обработать за один запуск
    """
    # Инициализируем API ключ один раз
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("❌ OPENAI_API_KEY не установлен")
        return 0
    
    db = init_firebase()
    messages_ref = db.collection('messages')
    # Новый синтаксис фильтрации
    query = messages_ref.where(filter=FieldFilter('summary', '==', None)).limit(batch_size)
    docs = list(query.stream())
    print(f"Найдено {len(docs)} сообщений без summary")
    
    processed_count = 0
    batch_updates = []  # Для батчевого обновления
    
    for doc in docs:
        try:
            data = doc.to_dict()
            plain = data.get('plain_text') or ""
            print(f"\nСообщение {doc.id}: plain_text длина={len(plain)}")
            
            if not plain.strip():
                print("Пропускаем: пустой plain_text")
                continue
                
            word_count = len(plain.split())
            if word_count < 50:
                print(f"Текст короткий (слов: {word_count}), помечаем как обработанный")
                batch_updates.append((doc.reference, {"summary": ""}))
                processed_count += 1
                continue
                
            print(f"Отправляем в OpenAI: {plain[:200]}{'...' if len(plain) > 200 else ''}")
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Сделай краткое саммари этого текста на русском языке (1-2 предложения):"},
                    {"role": "user", "content": plain}
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            summary = response.choices[0].message.content.strip()
            print(f"Получено summary: {summary}")
            batch_updates.append((doc.reference, {"summary": summary}))
            processed_count += 1
            
            # Rate limiting: пауза между запросами к OpenAI
            time.sleep(1)
            
        except Exception as e:
            print(f"Ошибка при обработке сообщения {doc.id}: {e}")
    
    # Батчевое обновление всех документов
    if batch_updates:
        batch = db.batch()
        for ref, data in batch_updates:
            batch.update(ref, data)
        batch.commit()
        print(f"Сохранено {len(batch_updates)} summary в базу данных")
    
    print(f"Всего обработано: {processed_count}")
    return processed_count 
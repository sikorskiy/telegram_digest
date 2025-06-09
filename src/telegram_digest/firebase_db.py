import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Инициализация Firebase
def init_firebase():
    """Инициализация Firebase."""
    # Проверяем, не инициализирован ли уже Firebase
    if not firebase_admin._apps:
        # Путь к файлу с учетными данными
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if not cred_path:
            raise ValueError("FIREBASE_CREDENTIALS_PATH must be set in .env file")
        
        # Инициализируем Firebase
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

# Получение клиента Firestore
db = init_firebase()

def upsert_post(
    msg_id: int,
    channel_id: str,
    date: datetime,
    text_html: str,
    plain_text: Optional[str],
    summary: Optional[str] = None,
    entities: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """Добавляет или обновляет пост."""
    print(f"Сохраняем пост {msg_id} из канала {channel_id}")
    
    post_ref = db.collection('posts').document(channel_id).collection('messages').document(str(msg_id))
    
    post_data = {
        'msg_id': msg_id,
        'channel_id': channel_id,
        'date': date,
        'text_html': text_html,
        'plain_text': plain_text,
        'summary': summary,
        'entities': entities or [],
        'updated_at': firestore.SERVER_TIMESTAMP
    }
    
    try:
        post_ref.set(post_data, merge=True)
        print(f"✅ Пост {msg_id} успешно сохранен")
    except Exception as e:
        print(f"❌ Ошибка при сохранении поста {msg_id}: {str(e)}")
        raise

def get_posts(
    channel_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Получает посты из канала за указанный период."""
    query = db.collection('posts').document(channel_id).collection('messages')
    
    if start_date:
        query = query.where('date', '>=', start_date)
    if end_date:
        query = query.where('date', '<=', end_date)
    
    query = query.order_by('date', direction=firestore.Query.DESCENDING)
    query = query.limit(limit)
    
    return [doc.to_dict() for doc in query.stream()]

def start_run(period_days: int) -> str:
    """Начинает новый run, возвращает его ID."""
    run_ref = db.collection('runs').document()
    
    run_data = {
        'started_at': firestore.SERVER_TIMESTAMP,
        'period_days': period_days,
        'status': 'running'
    }
    
    run_ref.set(run_data)
    return run_ref.id

def end_run(run_id: str) -> None:
    """Завершает run, устанавливая ended_at."""
    run_ref = db.collection('runs').document(run_id)
    
    run_ref.update({
        'ended_at': firestore.SERVER_TIMESTAMP,
        'status': 'completed'
    })

def get_latest_run() -> Optional[Dict[str, Any]]:
    """Получает информацию о последнем запуске."""
    query = db.collection('runs').order_by('started_at', direction=firestore.Query.DESCENDING).limit(1)
    
    docs = list(query.stream())
    if docs:
        return docs[0].to_dict()
    return None

def check_saved_posts(channel_id: str) -> None:
    """Проверяет сохраненные посты для канала."""
    print(f"\nПроверяем сохраненные посты для канала {channel_id}...")
    
    # Получаем документ канала
    channel_ref = db.collection('posts').document(channel_id)
    channel_doc = channel_ref.get()
    
    if not channel_doc.exists:
        print(f"❌ Канал {channel_id} не найден в базе данных")
        return
    
    # Получаем все сообщения
    messages = channel_ref.collection('messages').stream()
    messages = list(messages)
    
    print(f"✅ Найдено {len(messages)} постов")
    for msg in messages:
        data = msg.to_dict()
        print(f"- Пост {data['msg_id']} от {data['date']}: {data['plain_text'][:50]}...") 
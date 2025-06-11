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
) -> bool:
    """Добавляет или обновляет пост. Возвращает True, если добавлен, иначе False."""
    # Проверки на валидность поста
    if not msg_id or not channel_id or not date:
        return False
    if plain_text is None or (isinstance(plain_text, str) and not plain_text.strip()):
        return False
    if isinstance(plain_text, str) and len(plain_text.split()) < 5:
        return False
    doc_id = f"{channel_id}_{msg_id}"
    doc_ref = db.collection('messages').document(doc_id)
    if doc_ref.get().exists:
        return False
    post_data = {
        'msg_id': msg_id,
        'channel': channel_id,
        'date': date,
        'text_html': text_html,
        'plain_text': plain_text,
        'summary': summary,
        'entities': entities or [],
        'updated_at': firestore.SERVER_TIMESTAMP
    }
    try:
        doc_ref.set(post_data, merge=True)
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка при сохранении поста {msg_id}: {str(e)}")
        raise

def get_posts(
    channel_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Получает посты из канала за указанный период."""
    query = db.collection('messages').where('channel', '==', channel_id)
    
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
    
    query = db.collection('messages').where('channel', '==', channel_id)
    messages = list(query.stream())
    
    if not messages:
        print(f"❌ Нет постов для канала {channel_id} в коллекции messages")
        return
    
    print(f"✅ Найдено {len(messages)} постов")
    for msg in messages:
        data = msg.to_dict()
        if not data:
            continue
        if 'msg_id' not in data or data['msg_id'] is None or 'plain_text' not in data:
            print(f"[WARNING] Некорректный пост в базе: id={msg.id}, data={data}")
            continue
        plain = data.get('plain_text')
        if not isinstance(plain, str):
            print(f"[WARNING] Некорректный plain_text (не строка) в посте id={msg.id}: {plain}")
            plain = ""
        print(f"- Пост {data['msg_id']} от {data['date']}: {plain[:50]}...") 
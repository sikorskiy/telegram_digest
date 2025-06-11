import os
from firebase_admin import firestore
from telegram_digest.firebase_db import init_firebase

def migrate_to_flat_messages():
    db = init_firebase()
    print("Project id:", db.project)
    messages_flat = db.collection('messages')
    messages = list(db.collection_group('messages').stream())
    print(f"Найдено сообщений во всех messages: {len(messages)}")
    migrated = 0
    for msg_doc in messages:
        data = msg_doc.to_dict()
        # Получаем id канала из пути: posts/{channel}/messages/{msg_id}
        path_parts = msg_doc.reference.path.split('/')
        try:
            channel_id = path_parts[path_parts.index('posts') + 1]
        except Exception:
            channel_id = 'unknown'
        data['channel'] = channel_id
        doc_id = f"{channel_id}_{data.get('msg_id', msg_doc.id)}"
        messages_flat.document(doc_id).set(data)
        migrated += 1
        text = data.get('plain_text') or ""
        print(f"Мигрировано: {doc_id}, plain_text: {text[:50]}")
    print(f"Всего мигрировано сообщений: {migrated}")

if __name__ == "__main__":
    migrate_to_flat_messages() 
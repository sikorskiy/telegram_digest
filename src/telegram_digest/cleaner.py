import os
from telegram_digest.firebase_db import init_firebase

def clean_empty_and_short_posts():
    db = init_firebase()
    messages_ref = db.collection('messages')
    messages = list(messages_ref.stream())
    deleted = 0
    for msg in messages:
        data = msg.to_dict()
        plain = data.get('plain_text')
        word_count = len(plain.split()) if isinstance(plain, str) else 0
        if not isinstance(plain, str) or not plain.strip() or word_count < 5:
            print(f"[CLEAN] Удаляю пост {msg.id} (plain_text: {plain})")
            msg.reference.delete()
            deleted += 1
    print(f"Удалено {deleted} пустых или слишком коротких постов.")

if __name__ == "__main__":
    clean_empty_and_short_posts() 
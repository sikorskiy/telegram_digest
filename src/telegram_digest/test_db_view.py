from telegram_digest.firebase_db import init_firebase
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

CHANNEL = "cryptoEssay"  # или "@cryptoEssay", если так в базе
LIMIT = 10

def main():
    db = init_firebase()
    messages_ref = db.collection('messages')
    # Получаем 10 самых свежих постов по каналу
    docs = list(messages_ref.where(
        filter=FieldFilter('channel', '==', CHANNEL)
    ).order_by('date', direction=firestore.Query.DESCENDING).limit(LIMIT).stream())
    print(f"Найдено {len(docs)} постов для канала {CHANNEL} (сортировка по дате DESC):")
    for i, doc in enumerate(docs):
        data = doc.to_dict()
        print(f"{i+1}. date={data.get('date')}, summary={data.get('summary')}, text={data.get('plain_text')[:80] if data.get('plain_text') else ''}")

if __name__ == "__main__":
    main() 
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(os.environ['FIREBASE_AUTHKEY_PATH'])
firebase_admin.initialize_app(cred)

client = firestore.client()


def add(collection: str, document: str, v) -> bool:
    if not exists(collection, document):
        set(collection, document, v)
        return True

    return False


def set(collection: str, document: str, v):
    ref = client.collection(collection).document(document)
    ref.set(v)


def exists(collection: str, document: str) -> bool:
    return client.collection(collection).document(document).get().exists

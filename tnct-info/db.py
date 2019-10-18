import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(os.environ['FIREBASE_AUTHKEY_PATH'])
firebase_admin.initialize_app(cred, {'databaseURL': os.environ['FIREBASE_DBURL']})
db = firestore.client()


def set_value(collection: str, document: str, value: object):
    ref = db.collection(collection).document(document)
    ref.set(value)


def document_exists(collection: str, document_to_find: str):
    return db.collection(collection).document(document_to_find).get().exists

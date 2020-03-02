from telegram.ext import BasePersistence
from telegram.utils.helpers import enocde_conversations_to_json

from collections import defaultdict
import json


class SqlPersistence(BasePersistence):

    def __init__(self, database_connection, store_user_data=True, store_chat_data=False):
        self.store_user_data = store_user_data
        self.store_chat_data = store_chat_data

        self.db = database_connection

        self.user_data = defaultdict(dict)

        with self.db.cursor() as cur:
            results = cur.execute("SELECT * FROM USER_DATA")
            if results > 0:
                for user_id, data in cur.fetchall():
                    self.user_data[user_id] = json.loads(data)

    def get_user_data(self):

        return self.user_data.copy()

    def update_user_data(self, user_id, data):
        self.user_data[user_id] = data

    def flush(self):
        cur = self.db.cursor()

        cur.execute('DROP TABLE IF EXISTS USER_DATA;')
        cur.execute('CREATE TABLE USER_DATA (user_id INT, data VARCHAR(10000));')
        self.db.commit()

        counter = 0
        for user_id, defaultdict_data in self.user_data.items():
            data = json.dumps(defaultdict_data)
            cur.execute('INSERT INTO USER_DATA VALUES (%s, %s);', (user_id, data))
            counter += 1

            if counter % 20 == 0:
                self.db.commit()

        self.db.commit()

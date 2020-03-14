from telegram.ext import BasePersistence

from collections import defaultdict
import MySQLdb
import json
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def get_database_connection(mysql_host, mysql_user, mysql_passwd, mysql_db):
    return MySQLdb.connect(
        host=mysql_host,
        user=mysql_user,
        passwd=mysql_passwd,
        db=mysql_db,
        charset='utf8',
        )

class SqlPersistence(BasePersistence):

    def __init__(self, mysql_host, mysql_user, mysql_passwd, mysql_db, store_user_data=True, store_chat_data=False, store_bot_data=False):
        self.store_user_data = store_user_data
        self.store_chat_data = store_chat_data
        self.store_bot_data = store_bot_data
        self.mysql_host = mysql_host
        self.mysql_user = mysql_user
        self.mysql_passwd = mysql_passwd
        self.mysql_db = mysql_db

        self.db = get_database_connection(self.mysql_host, self.mysql_user, self.mysql_passwd, self.mysql_db)

        self.user_data = defaultdict(dict)
        self.chat_data = defaultdict(dict)
        self.conversations = dict()

        with self.db.cursor() as cur:
            results = cur.execute('SELECT * FROM USER_DATA')
            if results > 0:
                for user_id, data in cur.fetchall():
                    self.user_data[user_id] = json.loads(data)
            
            results = cur.execute('SELECT * FROM CHAT_DATA')
            if results > 0:
                for chat_id, data in cur.fetchall():
                    self.chat_data[chat_id] = json.loads(data)

            results = cur.execute('SELECT * FROM CONVERSATIONS')
            if results > 0:
                conversation_names = cur.fetchall()
                for conversation_name in conversation_names:
                    name = conversation_name[0]
                    if cur.execute(f'SELECT * FROM {name}_CONVERSATIONS') > 0:
                        for conversation_key, conversation_state in cur.fetchall():
                            key = tuple(json.loads(conversation_key))
                            state = json.loads(conversation_state)
                            self.conversations[name] = {key: state}
        self.db.close()

    def get_user_data(self):
        return self.user_data.copy()

    def get_chat_data(self):
        return self.chat_data.copy()

    def get_conversations(self, name):
        return self.conversations.get(name, {}).copy()

    def update_user_data(self, user_id, data):
        self.user_data[user_id] = data

    def update_chat_data(self, chat_id, data):
        self.chat_data[chat_id] = data

    def update_conversation(self, name, key, new_state):
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return
        self.conversations[name][key] = new_state

    def flush(self):
        self.db = get_database_connection(self.mysql_host, self.mysql_user, self.mysql_passwd, self.mysql_db)
        cur = self.db.cursor()

        cur.execute('DROP TABLE IF EXISTS USER_DATA;')
        cur.execute('CREATE TABLE USER_DATA (user_id INT, data VARCHAR(10000));')
        self.db.commit()
        logger.info('in flush')
        counter = 0
        for user_id, defaultdict_data in self.user_data.items():
            data = json.dumps(defaultdict_data)
            cur.execute('INSERT INTO USER_DATA VALUES (%s, %s);', (user_id, data))
            counter += 1

            if counter % 20 == 0:
                self.db.commit()

        self.db.commit()

        cur.execute('DROP TABLE IF EXISTS CHAT_DATA;')
        cur.execute('CREATE TABLE CHAT_DATA (chat_id INT, data VARCHAR(100));')
        self.db.commit()

        counter = 0
        for chat_id, defaultdict_data in self.chat_data.items():
            data = json.dumps(defaultdict_data)
            cur.execute('INSERT INTO CHAT_DATA VALUES (%s, %s);', (chat_id, data))
            counter += 1

            if counter % 20 == 0:
                self.db.commit()

        self.db.commit()

        cur.execute('DROP TABLE IF EXISTS CONVERSATIONS;')
        cur.execute('CREATE TABLE CONVERSATIONS (conversation_name VARCHAR(50));')
        self.db.commit()

        counter = 0
        for conversation_name, conversation_data in self.conversations.items():
            counter += 1
            cur.execute('INSERT INTO CONVERSATIONS VALUES (%s);', (conversation_name, ))
            cur.execute(f'DROP TABLE IF EXISTS {conversation_name}_CONVERSATIONS')
            cur.execute(f'CREATE TABLE {conversation_name}_CONVERSATIONS (conversation_key VARCHAR(50), conversation_state VARCHAR(50))')

            for key, state in conversation_data.items():
                cur.execute(f'INSERT INTO {conversation_name}_CONVERSATIONS VALUES (%s, %s)', (json.dumps(key), json.dumps(state)))
                counter += 1

                if counter % 20 == 0:
                    self.db.commit()


            self.db.commit()


        self.db.close()
        logger.info('done bye bye!!')


    def update_flush(self):
        self.db = get_database_connection(self.mysql_host, self.mysql_user, self.mysql_passwd, self.mysql_db)
        cur = self.db.cursor()

        cur.execute('DROP TABLE IF EXISTS USER_DATA;')
        cur.execute('CREATE TABLE USER_DATA (user_id INT, data VARCHAR(10000));')
        self.db.commit()
        logger.info('in flush')
        counter = 0
        for user_id, defaultdict_data in self.user_data.items():
            data = json.dumps(defaultdict_data)
            cur.execute('INSERT INTO USER_DATA VALUES (%s, %s);', (user_id, data))
            counter += 1

            if counter % 20 == 0:
                self.db.commit()

        self.db.commit()

        cur.execute('DROP TABLE IF EXISTS CHAT_DATA;')
        cur.execute('CREATE TABLE CHAT_DATA (chat_id INT, data VARCHAR(100));')
        self.db.commit()

        counter = 0
        for chat_id, defaultdict_data in self.chat_data.items():
            data = json.dumps(defaultdict_data)
            cur.execute('INSERT INTO CHAT_DATA VALUES (%s, %s);', (chat_id, data))
            counter += 1

            if counter % 20 == 0:
                self.db.commit()

        self.db.commit()

        cur.execute('DROP TABLE IF EXISTS CONVERSATIONS;')
        cur.execute('CREATE TABLE CONVERSATIONS (conversation_name VARCHAR(50));')
        self.db.commit()

        counter = 0
        for conversation_name, conversation_data in self.conversations.items():
            counter += 1
            cur.execute('INSERT INTO CONVERSATIONS VALUES (%s);', (conversation_name, ))
            cur.execute(f'DROP TABLE IF EXISTS {conversation_name}_CONVERSATIONS')
            cur.execute(f'CREATE TABLE {conversation_name}_CONVERSATIONS (conversation_key VARCHAR(50), conversation_state VARCHAR(50))')

            for key, state in conversation_data.items():
                cur.execute(f'INSERT INTO {conversation_name}_CONVERSATIONS VALUES (%s, %s)', (json.dumps(key), json.dumps(state)))
                counter += 1

                if counter % 20 == 0:
                    self.db.commit()


            self.db.commit()

        logger.info('update_flush done!')

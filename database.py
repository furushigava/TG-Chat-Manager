import sqlite3
import os
import base64
from config import *
class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect(config().path_to_database, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.name_to_id = {}
    def create_table(self, id, path_for_files):
        if not os.path.exists(path_for_files + f'\\{id}\\'):
            os.makedirs(path_for_files + f'\\{id}\\')
            os.makedirs(path_for_files + f'\\{id}\\document\\')
            os.makedirs(path_for_files + f'\\{id}\\voices\\')
            os.makedirs(path_for_files + f'\\{id}\\images\\')
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        for table in tables:
            if table[0] == id:
                return
        self.cursor.execute(f"""CREATE TABLE {id}
                  (message_text text, name_field text, surname_field text,
                   username text, type_field text, file_field text, who_sent text,
                   time_message text, read_message text)
               """)#who_sent: 0 - client, 1- bot(user)
        self.conn.commit()


    def get_ids(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        ids = self.cursor.fetchall()
        return ids
    def get_first_name_surname_username(self, id, name_to_id = ''):
        data = self.cursor.execute(f'SELECT * FROM "{id}" ORDER BY ROWID ASC LIMIT 1').fetchall()[0]
        name_field = base64.b64decode(data[1][2:len(data[1])-1]).decode('UTF-8')
        surname_field = base64.b64decode(data[2][2:len(data[2])-1]).decode('UTF-8')
        username = base64.b64decode(data[3][2:len(data[3])-1]).decode('UTF-8')
        if surname_field == 'None':
            string_name_surname = name_field
        else:
            string_name_surname = f'{name_field} {surname_field}'
        if name_to_id != '':
            name_to_id[string_name_surname] = id
            return string_name_surname, username, name_to_id
        else:
            return string_name_surname, username
    def read_all_messages(self, id):
        self.cursor.execute(f"UPDATE {id} SET read_message='1'").fetchall()
        self.conn.commit()
    def check_new_messages(self, id, return_text=False):
        data = self.cursor.execute(f"SELECT * FROM {id} WHERE read_message=0").fetchall()
        if return_text:
            if len(data) == 1:
                return 1, base64.b64decode(data[0][0][2:len(data[0][0])-1]).decode('UTF-8')
            else:
                return len(data), ''
        else:
            return len(data)
        
    def get_all_datas_by_id(self, id):
        datas = self.cursor.execute(f'SELECT * FROM {id}').fetchall()
        messages = []
        types = []
        files = []
        who_sents = []
        for data in datas:
            message_text = base64.b64decode(data[0][2:len(data[0])-1]).decode('UTF-8')
            name_field = base64.b64decode(data[1][2:len(data[1])-1]).decode('UTF-8')
            surname_field = base64.b64decode(data[2][2:len(data[2])-1]).decode('UTF-8')
            username = base64.b64decode(data[3][2:len(data[3])-1]).decode('UTF-8')
            type_field = data[4]
            file_field = base64.b64decode(data[5][2:len(data[5])-1]).decode('UTF-8')
            who_sent = data[6]
            time_message = data[7]
            read_message = data[8]  
            messages.append(message_text)
            types.append(type_field)
            files.append(file_field)
            who_sents.append(who_sent)
        if surname_field == 'None':
            name_surname_last = name_field
        else:
            name_surname_last = f'{name_field} {surname_field}' #if none
        id_normal = id[3:]
        return messages, types, files, who_sents, id_normal
    def write_db(self, id, message, name_field, surname_field, username, type_field, file_field, who_sent, time_message, read_message):
        message = base64.b64encode(bytes(str(message), 'utf-8'))
        name_field = base64.b64encode(bytes(str(name_field), 'utf-8'))
        surname_field = base64.b64encode(bytes(str(surname_field), 'utf-8'))
        username = base64.b64encode(bytes(str(username), 'utf-8'))   
        if file_field != '':
            file_field = base64.b64encode(bytes(str(file_field), 'utf-8'))
        query2 = f'''INSERT INTO {id}(message_text, name_field, surname_field, username, type_field, file_field, who_sent, time_message, read_message)
                VALUES ("{message}", "{name_field}", "{surname_field}", "{username}", "{type_field}", "{file_field}", {who_sent}, "{time_message}", {read_message})
                '''
        self.cursor.execute(query2)
        self.conn.commit()
    def delete_table(self, id):
        query2 = f"DROP TABLE {id}"
        self.cursor.execute(query2)
        self.conn.commit()
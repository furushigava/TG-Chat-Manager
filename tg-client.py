from os import path
from config import *
import datetime
import shutil
import telebot
import threading
import time
import sys
from database import DataBase
from PyQt5.QtGui import QFont#, QTextCursos
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon,  QMenu, QAction, QStyle, qApp
from PyQt5.QtCore import QSize
from interface import Ui_Form
from notify import Ui_Form_2
help_text = config().help_text
token = config().token_tg
path_for_files = config().path_for_files




        

class telegram_bot:
    def __init__(self):
        self.bot = telebot.TeleBot(token=token)
    def send_message(self, chat_id, message_type, file_path, message_text):
        send_func = {
            'text': lambda: self.bot.send_message(chat_id, message_text),
            'document': lambda: self.bot.send_document(chat_id, open(file_path, 'rb')),
            'photo': lambda: self.bot.send_photo(chat_id, open(file_path, 'rb')),
            'voice': lambda: self.bot.send_voice(chat_id, open(file_path, 'rb'))
        }
        
        try:
            send_func[message_type]()
            return 'good'
        except (FileNotFoundError, KeyError):
            print('Ошибка отправки сообщения или файл не найден!')
            return 'error'
        

class Notification(QMainWindow, Ui_Form_2):
    job_done = pyqtSignal()
    close_wind_signal = pyqtSignal()
    def __init__(self, count, text, name_surname, x, y):
        self.count = count
        self.text = text
        self.name_surname = name_surname

        self.close_wind_true = False
        super().__init__()
        self.move(x, y)
        self.setupUi(self)
        self.setWindowTitle("Уведомление")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.update()
        self.button_open_window.clicked.connect(self.show_wind)
        self.button_close_window.clicked.connect(self.close_wind)
    def close_wind(self):
        #self.close()
        self.close_wind_true = True
        self.close_wind_signal.emit()             
    def update(self):
        if self.count > 1 and self.text == '':
            self.msg.setText(f'{self.count} новых сообщений от {self.name_surname}')
            self.show()
        elif self.count == 1 and self.text != '':
            self.msg.setText(f'Новое сообщение от {self.name_surname}."{self.text}"')
            self.show()
        
    def show_wind(self):
        self.close()
        self.job_done.emit()

class Notifications(QThread):
    create_window = pyqtSignal(str)
    
    def __init__(self):
        QThread.__init__(self)
        self.db_class = DataBase()
        self.dict = {}
        
    def run(self):
        #print('here')
        while True:
                #count, text, name_surname, func -->
            ids = self.db_class.get_ids()
            self.notify_thread = []
            for id in ids:
                count, text = self.db_class.check_new_messages(id[0], return_text=True)
                name_surname, _= self.db_class.get_first_name_surname_username(id[0])
                if count < 1:
                    continue
                try:
                    count_last = self.dict[name_surname]
                    if count_last != count:
                        self.dict[name_surname] = count
                        string = f"{count} {text} {name_surname} update"
                        self.create_window.emit(string)
                except:
                    self.dict[name_surname] = count
                    self.create_window.emit(f"{count} {text} {name_surname} create")
            time.sleep(0.1)
                


class Main(QMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.status = 'show'
        self.selected_item = ''
        self.whatever_choice = 0
        self.next_x = 0
        self.next_y = 0
        self.name_bot = 'BOT'
        self.surname_bot = 'BOT'
        self.username_bot = 'BOT'
        self.name_to_id = {}
        self.db_class = DataBase() 
        self.bot = telegram_bot()
        self.update_periodically = threading.Thread(target=self.update_periodically)
        self.update_periodically.start()
        
        self.worker = Notifications()
        self.worker.create_window.connect(self.create_window_notification)
        self.worker.start() 
        self.notify_thread = []
        
        self.setupUi(self)
        self.update()
        self.setup()
        
    def create_window_notification(self, string):
        #print('2here')
        #Notifications.run -> передает сюда строку, она тут парсится и тут уже основная логика.
        count = int(string.split(' ')[0])
        text = string.split(' ')[1]
        name_surname = string.split(' ')[2]
        func = string.split(' ')[3]
        found = 0
        if func == 'update':
            for window in self.notify_thread:
                if window.name_surname == name_surname:
                    text_for_label = f'{count} новых сообщений от {name_surname}'
                    window.msg.setText(text_for_label)
                    if self.status == 'hidden':
                        #print('hidden')
                        window.close()
                        func = 'create'
                    else:
                        window.show()
                    found = 1
                    break
            if found == 0:
                func = 'create'
        if func == 'create':
            screen_geometry = QApplication.desktop().availableGeometry()
            screen_size = (screen_geometry.width(), screen_geometry.height())
            win_size = (self.frameSize().width(), self.frameSize().height())
            for window in self.notify_thread:
                if window.name_surname == name_surname and found == 1:
                    if window.msg.text() != text_for_label:
                        self.notify_thread.remove(window)
                        window.close()
            if self.next_x != 0 and self.next_y != 0 and len(self.notify_thread) > 0:
                #print('by next')
                x = self.next_x
                y = self.next_y
            else:
                #print('by start')
                x = screen_size[0] - win_size[0] + 440
                y = screen_size[1] - win_size[1]*len(self.notify_thread)*0.37 - 250
            
            self.notify_thread.append(Notification(count, text, name_surname, x, y))
            self.notify_thread[-1].job_done.connect(self.on_job_done)
            self.notify_thread[-1].close_wind_signal.connect(self.update_windows_notifications)
        
    def update_windows_notifications(self):
        i = 0
        close = ''
        while i < len(self.notify_thread):
            window = self.notify_thread[i]
            if window.close_wind_true:
                close = window
                break
            i += 1

        while i < len(self.notify_thread):
            window = self.notify_thread[i]
            if self.next_x != 0 and self.next_y != 0:
                window.hide()
                window.move(self.next_x, self.next_y)
            self.next_x = window.x()
            self.next_y = window.y()
            i += 1

        if self.status != 'hidden':
            #print(1)
            self.notify_thread.remove(close)
            for window_show in self.notify_thread:
                #print(4)
                window_show.show()  
        else:
            if len(self.notify_thread) == 1:
                self.next_x = close.x()
                self.next_y = close.y()
                close.hide()
                #close.show()
            elif len(self.notify_thread) > 1:
                close.close()
                self.notify_thread.remove(close)
                for window_show in self.notify_thread:
                    window_show.show()                  
            #except:
            #        self.notify_thread.remove(window)
    def on_job_done(self):
        self.notify_thread = []
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()

    def update_periodically(self):
        time.sleep(3)
        while True:
            self.update()
            time.sleep(1)

    def closeEvent(self, event):
        # Переопределить colseEvent
        event.ignore()
        self.hide()
        self.status = 'hidden'
        self.tray_icon.showMessage(
            "Tray Program",
            "Application was minimized to Tray",
            QSystemTrayIcon.Information,
            2000
        )
    def exit_func(self):
        self.update_periodically.stop()
        qApp.quit()
    def setup(self):
        self.font = QFont()
        self.font.setPointSize(13)
        self.update_button.setFont(self.font)
        self.delete_button.setFont(self.font)
        self.choice_button.setFont(self.font)
        self.text_edit.setFont(self.font)
        self.text_edit.setReadOnly(True)
        self.update_button.clicked.connect(self.update)
        self.delete_button.clicked.connect(self.delete)
        self.choice_button.clicked.connect(self.choice)
        self.listWidget.itemClicked.connect(self.listwidgetclicked)
        self.input_field.returnPressed.connect(self.send_message)
        
        
        self.setWindowTitle("Чат")
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show_window)
        hide_action.triggered.connect(self.hide_window)
        quit_action.triggered.connect(self.exit_func)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    def show_window(self):
        self.status = 'show'
        self.show()
    def hide_window(self):
        self.status = 'hidden'
        self.hide()
    def listwidgetclicked(self, item):
        self.selected_item = item.data(0)
    def update(self):
        self.listWidget.clear()
        ids = self.db_class.get_ids()
        for num, id in enumerate(ids):
            string_name_surname, _, self.name_to_id = self.db_class.get_first_name_surname_username(id[0], name_to_id=self.name_to_id)
            new_messages = self.db_class.check_new_messages(id[0])
            if new_messages == 1:
                string_name_surname += f'({new_messages} новое)'
            elif new_messages > 0:
                string_name_surname += f'({new_messages} новых)'
            self.listWidget.addItem(string_name_surname)
            if self.selected_item != '' and string_name_surname == self.selected_item:
                self.listWidget.item(num).setSelected(True)
            

    def delete(self):
        try:  
            choice_from_qlist = self.listWidget.selectedItems()[0].data(0)
            text = self.parse_name_from_qlist(choice_from_qlist)
            id = self.name_to_id[text]
        except:
            return
        result = QMessageBox.question(self, 'Уведомление', f"Вы уверены, что хотите удалить {text}?", QMessageBox.Yes, QMessageBox.No)
        if result == QMessageBox.Yes:
            self.db_class.delete_table(id)
            shutil.rmtree(path_for_files + '\\' + id)
            self.update()
        else:
            return
    def parse_text(self, text):
        if text[0] == '[' and text[-1] == ']':
            try:
                type_text = text.split(':', 1)[0][1:]
            except:
                return 'text', ''
            if type_text == 'Document' or type_text == 'document':
                type_text_fin = 'document'
            elif type_text == 'Voice' or type_text == 'voice':
                type_text_fin = 'voice'
            elif type_text == 'Photo' or type_text == 'photo':
                type_text_fin = 'photo'
            else:
                return 'text', ''
            try:
                path = text.split(':', 1)[1][:-1]
                if path == '':
                    print('Файл не указан!')
                    return 'False', ''
            except:
                print('Файл не указан!')
                return 'False', ''
            return type_text_fin, path
        else:
            return 'text', ''
    def send_message(self):
        if self.whatever_choice == 0:
            return
        text = self.input_field.text()
        type_text, path = self.parse_text(text)
        if type_text == 'False':
            return
        id_normal = self.label_id.text()[3:]
        id = 'id_' + id_normal
        self.db_class.write_db(id, text, self.name_bot, self.surname_bot, self.username_bot, f"{type_text}", f"{path}", "1", str(datetime.datetime.now()), "1")
        
        th = threading.Thread(target=self.bot.send_message, args=(id_normal, type_text, path, text, ))
        th.start()
        self.input_field.clear()
        self.choice(id)
        
    def parse_name_from_qlist(self, choice_from_qlist):
        parse_name = choice_from_qlist.split('(')
        i = 0
        name_surname = ''
        while i < len(parse_name) - 1:
            if i == 0:
                name_surname += parse_name[i]
            else:
                name_surname += '(' + parse_name[i]
            i += 1      
        if name_surname == '':
            name_surname = choice_from_qlist
        return name_surname 
    def choice(self, id=0):
        if id == 0:
            try:
                
                choice_from_qlist = self.listWidget.selectedItems()[0].data(0)
                text = self.parse_name_from_qlist(choice_from_qlist)
                id = self.name_to_id[text]
            except:
                #print('Ничего не выбрано!')
                return
        self.whatever_choice = 1
        #SET ALL MESSAGES READ - 1 
        self.db_class.read_all_messages(id)
        #print('Включи чтение')
        #self.update()
        messages, types, files, who_sents, id_normal = self.db_class.get_all_datas_by_id(id)
        #print(name_surname_last)
        #print(id_normal)
        name_surname, username = self.db_class.get_first_name_surname_username(id)
        self.name_surname.setText(name_surname)
        self.label_id.setText('ID:' + id_normal)
        self.label_username.setText('Username:@' + username)
        i = 0
        text = '<style>#xxx{background-color:rgba(139, 202, 186, 0.5);}</style>'
        while i < len(messages):
            message = messages[i]
            type_message = types[i]
            file_message = files[i]
            who_sent = who_sents[i]
            if who_sent == "1":
                text += '<p align=right id="xxx">'
            elif who_sent == '0':
                text += '<p align=left>'
            if type_message == 'text':
                text += f'[Text: {message}]</p>\n'
                self.text_edit.setHtml(text)
            elif type_message == 'document':
                text += f'[Document: {file_message}]\n'
                self.text_edit.setHtml(text)
            elif type_message == 'audio':
                text += f'[Audio: {file_message}]\n'
                self.text_edit.setHtml(text)
            elif type_message == 'voice':
                text += f'[Voice: {file_message}]\n'
                self.text_edit.setHtml(text)
            elif type_message == 'photo':
                text += f'[Photo: {file_message}]\n'
                self.text_edit.setHtml(text)
            #print(text)
            i += 1
            
        self.text_edit.setAlignment(Qt.AlignLeft)
        vsb = self.text_edit.verticalScrollBar()
        vsb.setValue(vsb.maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())










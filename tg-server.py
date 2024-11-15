from database import *
from config import *
import datetime
import telebot
import base64


help_text = config().help_text
token = config().token_tg
path_for_files = config().path_for_files


bot = telebot.TeleBot(token=token)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, help_text)
@bot.message_handler(content_types=['sticker'])
def send_error(message):
	bot.send_message(message.from_user.id, 'На данный момент стикеры не поддерживаются!Если в них имеется необходимость, то сделайте фото этого стикера и отправьте в виде фото.')
@bot.message_handler(content_types=['text', 'document', 'audio', 'voice', 'photo'])
def messanger(message):
    id = message.chat.id
    if id < 0:
        return
        #bot.send_message(id, "Бот не поддерживает чаты!")
    id = 'id_' + str(message.from_user.id)
    print(f'Accept message from {id[3:]}, type: {message.content_type}')
    date = str(datetime.datetime.now())
    file = ''
    db = DataBase()
    db.create_table(id, path_for_files)
    
    if message.content_type == 'document' or message.content_type == 'audio':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f'{path_for_files}\\{id}\\document\\' + str(message.document.file_name)
        file = message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
    elif message.content_type == 'voice':
        src = f"{path_for_files}\\{id}\\voices\\{message.voice.file_id}.ogg"
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file = message.voice.file_id
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file) 
    elif message.content_type == 'photo':
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = bot.get_file( message.photo[-1].file_id).file_path.split('/')[1] 
        src = f"{path_for_files}\\{id}\\images\\{file_name}.jpg"
        file = file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        #id_file = message.photo[-1].file_id
        #file_name_full = f"{path_for_files}\\{id}\\images\\{id_file}.png"

    db.write_db(id, message.text, message.from_user.first_name, message.from_user.last_name, message.from_user.username, message.content_type, file, "0", date, "0")
    
bot.polling()

#bot.reply_to(message, message.text)


#bot.reply_to(message, message.text)

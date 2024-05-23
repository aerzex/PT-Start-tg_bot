import os
import logging
import subprocess
import paramiko
from dotenv import load_dotenv
import re
from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import psycopg2
from psycopg2 import Error
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")

TOKEN = str(os.getenv("TOKEN"))

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')
    

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'



def findPhoneNumbers(update: Update, context):
    user_input = update.message.text

    phoneNumRegex = re.compile(r'[\+78]\s?[\(\-]?\d{3}[\)\-]?\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')
    phoneNumberList = phoneNumRegex.findall(user_input)

    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    
    phoneNumbers = '' 
    for i, phoneNumber in enumerate(phoneNumberList, start=1):
        phoneNumbers += f'{i}. {phoneNumber}\n'
        
    update.message.reply_text(phoneNumbers) 
    update.message.reply_text('Хотите добавить найденные номера телефонов в базу данных?(да/нет)', reply_markup=ReplyKeyboardMarkup([['да', 'нет']], one_time_keyboard=True))
    
    context.user_data['phoneNumberList'] = phoneNumberList
    
    return 'add_phone_numbers'

def addPhoneNumbers(update: Update, context):
    user_answer = update.message.text.lower()
    if user_answer == 'да':
        phoneNumberList = context.user_data['phoneNumberList']
        for phoneNumber in phoneNumberList:
            DatabaseConnect(f"INSERT INTO Numbers (number) VALUES ('{phoneNumber}');")
        update.message.reply_text('Номера добавлены в базу данных')
    else:
        update.message.reply_text('Номера не добавлены в базу данных')
    return ConversationHandler.END

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска электронных адресов: ')
    return 'find_email'

def findEmails(update: Update, context):
    user_input = update.message.text 

    EmailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b') 

    EmailList = EmailRegex.findall(user_input) 

    if not EmailList: 
        update.message.reply_text('Электронные почты не найдены')
        return ConversationHandler.END
    
    Emails = '' 
    for i, email in enumerate(EmailList, start=1):
        Emails += f'{i}. {email}\n' 
        
    update.message.reply_text(Emails) 
    update.message.reply_text('Хотите добавить найденные почты в базу данных?(да/нет)', reply_markup=ReplyKeyboardMarkup([['да', 'нет']], one_time_keyboard=True))
    
    context.user_data['EmailList'] = EmailList
    
    return 'add_emails'

def addEmails(update: Update, context):
    user_answer = update.message.text.lower()
    if user_answer == 'да':
        EmailList = context.user_data['EmailList']
        for email in EmailList:
            DatabaseConnect(f"INSERT INTO Emails (email) VALUES ('{email}');")
        update.message.reply_text('Почты добавлены в базу данных')
    else:
        update.message.reply_text('Почты не добавлены в базу данных')
    return ConversationHandler.END

def CheckPasswordCommand(update: Update, context):
    update.message.reply_text('Введите текст для проверки пароля: ')
    return 'verify_password'

def CheckPassword (update: Update, context):
    user_input = update.message.text 

    PasswordRegex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$')
    PasswordList = PasswordRegex.search(user_input) 

    if not PasswordList : 
        update.message.reply_text('Пароль простой')
        return 
    else : 
        update.message.reply_text('Пароль сложный') 

    return ConversationHandler.END 

def LinuxConnect(command) :
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    username = os.getenv('USER')
    password = os.getenv('PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    if data:
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        return data
    else:
        return 'Не удалось выполнить команду'


def ReleaseCommand(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(LinuxConnect('lsb_release -a'))   


def UnameCommand(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(LinuxConnect('uname -mprs'))

def UptimeCommand(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(LinuxConnect('uptime'))

def dfCommand(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(LinuxConnect('df -h'))

def freeCommand(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(LinuxConnect('free -h'))

def mpstatCommand(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(LinuxConnect('mpstat -P ALL 1 1'))

def wCommand(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(LinuxConnect('w'))

def last10Command(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(LinuxConnect('last -n 10'))

def critical5Command(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(LinuxConnect('journalctl -p 2 -b --no-pager -n 5'))

def split_message(message: str, max_length: int = 4096) -> list:
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

def psCommand(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    ps_output = LinuxConnect('ps -auxf')
    for part in split_message(ps_output):
        update.message.reply_text(part)

def serviceCommand(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    service_output = LinuxConnect('service --status-all')
    for part in split_message(service_output):
        update.message.reply_text(part)

def ssCommand(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(LinuxConnect('ss -tulpn'))

def dpkglistCommand(update: Update, context):
    update.message.reply_text('Выберите опции:\n 1. Чтобы вевести все пакеты введите all\n 2. Чтобы вевести пакеты с определенным именем введите имя пакета')
    return 'get_apt_list'

def dpkg(update: Update, context):
    if update.message.text == 'all':
        update.message.reply_text('Собираем информацию...')
        service_output = update.message.reply_text(LinuxConnect('dpkg --get-selections | grep -v deinstall | head -n 10'))
        for part in split_message(service_output):
            update.message.reply_text(part)

    else:
        update.message.reply_text('Собираем информацию...')
        service_output = update.message.reply_text(LinuxConnect('dpkg -s ' + update.message.text))
        for part in split_message(service_output):  
            update.message.reply_text(part)
    return ConversationHandler.END

def serviceCommand(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    service_output = LinuxConnect('service --status-all')
    for part in split_message(service_output):
        update.message.reply_text(part)

def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def DatabaseConnect(query):
    connection = None

    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_DATABASE,
            user=DB_USER,
            password=DB_PASSWORD,  
        )
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        data = cursor.fetchall()
        text = '' 
        for i in range(len(data)):
            text += f'{data[i]}\n' 
            connection.commit()
        logging.info("Команда успешно выполнена")
        return text
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")




def DockerReplLogs():
    try:
        command = f'cat ../var/lib/postgresql/data/log/postgresql.csv| grep -E "replication|recovery"'

        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise Exception(f'Ошибка при выполнении команды: {result.stderr}')

        return result.stdout
    except Exception as e:
        logging.error("Не удалось получить логи базы данных: %s", e)
        return "Не удалось получить логи базы данных."


def GetEmails(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(DatabaseConnect('SELECT * FROM Emails;'))

def GetPhoneNumbers(update: Update, context):
    update.message.reply_text('Собираем информацию...')
    update.message.reply_text(DatabaseConnect('SELECT * FROM Numbers;'))

def LogCommad(update: Update, context): 
    update.message.reply_text('Собираем информацию...')
    log_content = DockerReplLogs()
    if log_content:
        for part in split_message(log_content):
            update.message.reply_text(part)
    else:
        update.message.reply_text('Не удалось получить логи.')

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'add_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, addPhoneNumbers)],
        },
        fallbacks=[],
        allow_reentry=True
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'add_emails': [MessageHandler(Filters.text & ~Filters.command, addEmails)],
        },
        fallbacks=[],
        allow_reentry=True
    )


    convHandlerCheckPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', CheckPasswordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, CheckPassword)],
        },
        fallbacks=[]
    )

    convHandlerdpkg = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', dpkglistCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, dpkg)],
        },
        fallbacks=[]
    )



    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)	
    dp.add_handler(convHandlerCheckPassword)
    dp.add_handler(CommandHandler("get_release", ReleaseCommand))
    dp.add_handler(CommandHandler("get_uname", UnameCommand))
    dp.add_handler(CommandHandler("get_uptime", UptimeCommand))
    dp.add_handler(CommandHandler("get_df", dfCommand))
    dp.add_handler(CommandHandler("get_free", freeCommand))
    dp.add_handler(CommandHandler("get_mpstat", mpstatCommand))
    dp.add_handler(CommandHandler("get_w", wCommand))
    dp.add_handler(CommandHandler("get_auths", last10Command))
    dp.add_handler(CommandHandler("get_critical", critical5Command))
    dp.add_handler(CommandHandler("get_ps", psCommand))
    dp.add_handler(CommandHandler("get_ss", ssCommand))
    dp.add_handler(convHandlerdpkg)
    dp.add_handler(CommandHandler("get_services", serviceCommand))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(CommandHandler("get_repl_logs", LogCommad))
    dp.add_handler(CommandHandler("get_emails", GetEmails))
    dp.add_handler(CommandHandler("get_phone_numbers", GetPhoneNumbers))
	
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

import configparser
import logging
import mysql.connector
from logging.handlers import TimedRotatingFileHandler

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from yandex_translate import YandexTranslate

config = configparser.ConfigParser(allow_no_value=True)
config.read('etc/translate.conf')
upd = config.get('id', 'updater')
yandexApiKey = config.get('yandex', 'key')
#print(yandexApiKey)
user = config.get('db', 'user')
password = config.get('db', 'pass')
host = config.get('db', 'host')
database = config.get('db', 'dbname')
logfilename = 'log/translater.log'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger()
logformat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
loggerhandler = TimedRotatingFileHandler(logfilename, when="midnight", backupCount=30)
loggerhandler.setFormatter(logformat)
logger.addHandler(loggerhandler)

def keyboard():
    k = [[KeyboardButton('/setlang'), KeyboardButton('/mysetting')],
         [KeyboardButton('/start'), KeyboardButton('/about'), KeyboardButton('/help')],

         ]
    k_inline = ReplyKeyboardMarkup(k, one_time_keyboard=False)
    return k_inline

def start(bot, update):
    userid = update.message.from_user.id
    logger.info('Пользователь с ID:%s ввел комманду /start' % userid)

    bot.sendMessage(update.message.chat_id,
                    text='Мен - аудармашы ботпын.Аударуды қажет ететін сөзді немесе сөйлемді жазыңыз.\nАудару тілін өзгерту үшін келесі команданы жазыңыз: /setlang'
                         '\nҚазіргі аудару тілін анықтау үшін келесі команданы енгізіңіз: /mysetting'
                         '\nКөмек алу үшін келесі команданы жазыңыз: /help'
                         '\n\nЯ - бот переводчик. Введите слово или предложение для перевода.\nДля смены языка перевода, введите команду: /setlang'
                         '\nЧтобы узнать текущие настройки языка, введите команду: /mysetting'
                         '\nдля получения подсказки введите команду: /help', reply_markup = keyboard())


def about(bot, update):
    userid = update.message.from_user.id
    logger.info('Пользователь с ID:%s ввел комманду /about' % userid)
    bot.sendMessage(update.message.chat_id, text='developed by: M.N.')


def setlang(bot, update):
    #replytxt = update.message.text
    userid = update.message.from_user.id
    logging.info('Пользователь с ID: %s ввел команду: /setlang' % userid)
    inline = [[InlineKeyboardButton('English-Қазақ', callback_data='1'),
               InlineKeyboardButton("Қазақ-English", callback_data='2')],
              [InlineKeyboardButton('Русский-Қазақ', callback_data='3'),
               InlineKeyboardButton("Қазақ-Руский", callback_data='4')],
              [InlineKeyboardButton('Руский-English', callback_data='5'),
               InlineKeyboardButton("English-Руский", callback_data='6')],
              ]
    inlinebutton = InlineKeyboardMarkup(inline)
    #inlinebutton = ReplyKeyboardMarkup(inline)
    bot.sendMessage(update.message.chat_id,
                    text='Қажетін таңдаңыз\nВыберите необходимое',
                    reply_markup=inlinebutton)


def button(bot, update):
    lang_list = {"English-Қазақ" : 1,
                 "Қазақ-English" : 2,
                 "Русский-Қазақ" : 3,
                 "Қазақ-Руский" : 4,
                 "Руский-English" : 5,
                 "English-Руский" : 6
                 }
    query = update.callback_query
    # print(query)
    userid = query['message']['chat']['id']
    print(query.data)
    print(type(query.data))
    query.data = int(query.data)
    print(type(query.data))
    # userid = update.message.from_user.id
    logging.info('Пользователь с ID: %s выбрал callback: %s' % (userid, query.data))

    try:
        cnx = mysql.connector.connect(user=user, password=password,
                                      host=host,
                                      database=database)
        cursor = cnx.cursor()
        query1 = 'SELECT * FROM idlist WHERE telegramId = %s'
        cursor.execute(query1, (userid,))
        c = cursor.fetchone()
        if c:
            updQuery = 'update idlist set sourceLang = %s, targetLang = %s where telegramId = %s'
            print('I am if')
            if query.data == 1:
                cursor.execute(updQuery, ('en', 'kk', userid))
            elif query.data == 2:
                cursor.execute(updQuery, ('kk', 'en', userid))
            elif query.data == 3:
                cursor.execute(updQuery, ('ru', 'kk', userid))
            elif query.data == 4:
                cursor.execute(updQuery, ('kk', 'ru', userid))
            elif query.data == 5:
                cursor.execute(updQuery, ('ru', 'en', userid))
            elif query.data == 6:
                # print('q data = 6')
                cursor.execute(updQuery, ('en', 'ru', userid))
            cnx.commit()


        else:
            insQuery = 'INSERT INTO idlist VALUES (%s, %s, %s)'
            print('i am else')
            if query.data == 1:
                # print('q data == 1')
                cursor.execute(insQuery, (userid, 'en', 'kk',))
                # print('%s %s %s %s' %(insQuery, userid, 'en', 'kk'))
            elif query.data == 2:
                cursor.execute(insQuery, (userid, 'kk', 'en',))
            elif query.data == 3:
                cursor.execute(insQuery, (userid, 'ru', 'kk',))
            elif query.data == 4:
                cursor.execute(insQuery, (userid, 'kk', 'ru',))
            elif query.data == 5:
                cursor.execute(insQuery, (userid, 'ru', 'en',))
            elif query.data == 6:
                cursor.execute(insQuery, (userid, 'en', 'ru',))

            # print('else commit ')

            cnx.commit()

        # print('try commit')
        cnx.commit()
        #setlang(bot, update)
        bot.edit_message_text(text="Орындалды\nПрименено",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)


    except mysql.connector.Error as err:
        logging.error('Can\'t execute SQL query')
        logging.error(err)
        bot.sendMessage(update.message.chat_id,
                        text='Кешіріңіз. Дәл қазір өзгерістерді енгізу мүмкін емес.\nИзвините! На текущий момент не возможно применить настройки')
    finally:
        cursor.close()
        cnx.close()

    #return setlang(bot, update)


def translater(bot, update):
    replytxt = update.message.text
    # print(replytxt)
    userid = update.message.from_user.id
    # print(userid)
    translate = YandexTranslate(yandexApiKey)
    logging.info('Пользователь с ID: %s ввел сообщение: %s' % (userid, replytxt))
    try:
        cnx = mysql.connector.connect(user=user, password=password,
                                      host=host,
                                      database=database)
        cursor = cnx.cursor()
        query1 = 'SELECT * FROM idlist WHERE telegramId = %s'
        cursor.execute(query1, (userid,))
        c = cursor.fetchone()
        if c:
            s = c[1]
            t = c[2]
            st = '%s-%s' % (s, t)
            tr = translate.translate(replytxt, st)
            #print(tr)
            msg = tr['text']
            #print(msg)
            msg = u'%s' % msg[0]

            bot.sendMessage(update.message.chat_id,
                            text=msg)
        else:
            #print('not c')
            tr = translate.translate(replytxt, 'en')
            #print(tr)
            msg = tr['text']
            #print(msg)
            msg = u'%s' % msg[0]

            bot.sendMessage(update.message.chat_id, text=msg)

    except mysql.connector.Error as err:
        logging.error('Can\'t execute SQL query')
        logging.error(err)
        bot.sendMessage(update.message.chat_id, text='Извините! Не могу перевести')

def mysetting(bot, update):
    replytxt = update.message.text
    # print(replytxt)
    userid = update.message.from_user.id
    complience = {
        'en' : 'English',
        'ru' : 'Русский',
        'kk' : 'Қазақ'
    }
    logging.info('Пользователь с ID: %s ввел команду /mysetting')
    try:
        cnx = mysql.connector.connect(user=user, password=password,
                                      host=host,
                                      database=database)
        cursor = cnx.cursor()
        query1 = 'SELECT sourceLang, targetLang FROM idlist WHERE telegramId = %s'
        cursor.execute(query1, (userid,))
        c = cursor.fetchone()
        if c:
            c1 = c[0]
            c2 = c[1]
            c1_long = complience[c1]
            c2_long = complience[c2]
            c3_long = c1_long + '-' + c2_long
            #print(c3_long)
            bot.sendMessage(update.message.chat_id,
                            text='%s' %c3_long)
        else:
            bot.sendMessage(update.message.chat_id,
                            text='to English')

    except mysql.connector.Error as err:
        logging.error('Can\'t execute SQL query')
        logging.error(err)
        bot.sendMessage(update.message.chat_id,
                        text='Кешіріңіз. Дәл қазір ақпаратты алу мүмкін емес.\nИзвините! На текущий момент не возможно получить информацию')
    finally:
        cursor.close()
        cnx.close()



def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(upd)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("setlang", setlang))
    dp.add_handler(CommandHandler("mysetting", mysetting))
    dp.add_handler(CallbackQueryHandler(button))
    # dp.add_handler(MessageHandler([Filters.command], unknown))

    dp.add_handler(MessageHandler([Filters.text], translater))

    # dp.add_error_handler(error)


    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

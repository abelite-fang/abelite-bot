 # -*- coding: utf-8 -*-
from __future__ import print_function
import configparser
import logging
import telegram
import requests
import json
import re
import os

from flask import Flask, request
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (CommandHandler, ConversationHandler, 
                            Dispatcher, MessageHandler, Filters, StringRegexHandler, CallbackContext)
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)


# DEFINE

stateNone, statePrice, statePay, stateItem, stateRecord = range(5)
stateNone, stateSetURL, statePay, stateItem, stateRecord = range(5)

command_markup = [['/b'], ['/test'], ['/help']]


# CLASS

class User():
    def __init__(self, userid):
        self.userid = userid
        self.url = None
        self.category_markup = None
        self.payment_markup = None
        self.temp = None
    
    def isAllSet(self):
        text = ''
        print(self.category_markup)
        print(self.payment_markup)
        print(self.url)
        if self.url != None and self.category_markup != None and self.payment_markup != None:
            return 1
        if self.url == None:
            text += "url "
        if self.category_markup == None:
            text += "payment & category "
        text += "need setup. usage: /register_url $url"
        return text


# CONFIGS

## Load tokens and json file
config = configparser.ConfigParser()
config.read('token.txt')


## Initial bot with Telegram access token
#ValidUsers = {}
#ValidUsersList = []


ValidUsers = {'0': User('0')}
ValidUsersList = ['0']
bot = telegram.Bot(token=(config['CONFIG']['TOKEN']))


def initConfig():
    for i in config['USER']:
        user = User(i)
        if config['USER'][i] != None:
            user.url = config['USER'][i][1:-1]
            updateInfo(user)
        ValidUsersList.append(i)
        ValidUsers[i] = user

# SERVICE START
## Flask
app = Flask(__name__)
## Dispatcher for bot
dispatcher = Dispatcher(bot, None)

    

@app.route('/hook', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

def getUser(update):
    id = update.message.from_user.id
    if str(id) in ValidUsers:
        return ValidUsers[str(id)]
    return None
    


## acc_* : /b
### STATE 0/4
def acc_cate_handler(bot, update):
    try:
        user = getUser(update)
        if user.isAllSet() != 1:
            update.message.reply_text("/register first")
            return ConversationHandler.END
    except:
        update.message.reply_text("please contact bot admin")
        return ConversationHandler.END
    
    updateInfo(user)
    user.temp = dict()
    welcome_message = "Options:"
    update.message.reply_text(welcome_message, reply_markup=ReplyKeyboardMarkup(user.category_markup,one_time_keyboard=True))
    #update.message.reply_text(welcome_message, reply_markup=InlineKeyboardMarkup(user.category_markup))
    return statePrice


### STATE 1/4
def acc_price_handler(bot, update):  
    user = getUser(update)
    print("in price")
    recv = update.message.text
    if recv == 'cancel' or recv == '取消' or recv == 'c':
        return failed_handler(bot, update)
    user.temp['cate'] = recv
    welcome_message = "Cost:"
    update.message.reply_text(welcome_message)
    return statePay

### STATE 2/4
def acc_payment_handler(bot, update): 
    user = getUser(update)

    # Check input integer/float
    recv = update.message.text
    result = re.match('(\-?\d+(\.\d+)?)$', recv)
    
    if result == None:
        if recv.lower() == 'cancel' or recv == '取消' or recv == 'c':
            return failed_handler(bot, update)
        update.message.reply_text("Cost:")
        return statePay

    user.temp['price'] = update.message.text
    update.message.reply_text(
        "Payment Method:", 
        reply_markup=ReplyKeyboardMarkup(user.payment_markup, one_time_keyboard=True, resize_keyboard=True))
    return stateItem

### STATE 3/4
def acc_item_handler(bot, update):
    user = getUser(update)
    recv = update.message.text
    if recv == 'cancel' or recv == '取消' or recv == 'c':
        return failed_handler(bot, update)

    user.temp['costfrom'] = recv
    update.message.reply_text(
        "Log:",
        reply_markup=ReplyKeyboardMarkup([['取消']]))
    return stateRecord

### STATE 4/4
def acc_record_handler(bot, update):
    user = getUser(update)
    recv = update.message.text
    if recv == 'cancel' or recv == '取消' or recv == 'c':
        return failed_handler(bot, update)
    #print(text)
    user.temp['log'] = recv
    temp = user.temp
    if sendRecord(user) == 1:
        update.message.reply_text("Upload Error, please contact admin")
    else:
        update.message.reply_text(
            "\nUploaded", reply_markup=ReplyKeyboardRemove())

    user.temp = dict()
    return ConversationHandler.END

def failed_handler(bot, update):
    user = getUser(update)
    text = "Canceled!!"
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(command_markup))
    return ConversationHandler.END

def help_handler(bot, update):
    text = """/b - bookkeeping
/help - get this help message 
/test - check if webhook is working
/update - update payment methods and categories
/cancel - cancel all acting commands
/register - check registered
    """
    update.message.reply_text(text)
    return ConversationHandler.END

def testWorking_handler(bot, update):
    text = "alive"
    update.message.reply_text(text)
    return ConversationHandler.END

def start_handler(bot, update):
    try:
        user = getUser(update)
    except:
        update.message.reply_text("please contact bot admin")
        return ConversationHandler.END
    
    update.message.reply_text("you are able to use. try: /b or /help")
    return ConversationHandler.END

def who_handler(bot, update):
    # DEBUG FUNCTION
    mess = update.message
    text = "message_id: " + str(mess.message_id) + \
        "\nmy_userid: " + str(mess.from_user.id)
    
    #if mess.from_user.username:
    #    text = text + "\nmy_username: " + mess.from_user.username
    
    text = text + "\nreg:" + str(valid(str(mess.from_user.id)))
    
    update.message.reply_text(text)
    return ConversationHandler.END

def reg_handler(bot, update):
    #user = getUser(update)
    id, username = update.message.from_user.id, update.message.from_user.username
    
    if id not in ValidUsersList:
        #ValidUsers[str(id)] = User(id)
        #updateValidUsersList.append(id)
        update.message.reply_text("Not able to register now")
        return ConversationHandler.END
    
    result = ValidUsers[str(id)].isAllSet()
    if result != 1:
        update.message.reply_text(result)
    else:
        update.message.reply_text("Registered and clear to go")

    return ConversationHandler.END

def reg_token_handler(bot, update):
    # Send webhook url and send to User()
    id, username = update.message.from_user.id, update.message.from_user.username
    if valid(id) == -1:
        return ConversationHandler.END

    user = getUser(update)
    url = update.message.text[3:]

    try: 
        # Check webhook health
        r = requests.post(url, data={'checkWebhook':1})
        if r.text == 'OK':
            user.url = url
            updateInfo(user)
            update.message.reply_text('All set, check /register in case something got wrong')
    except:
        update.message.reply_text('please update url again or contact admin')
    
    return ConversationHandler.END

def updateInfo_handler(bot, update):
    user = ValidUsers[str(id)]
    updateInfo(user)
    return ConversationHandler.END

def updateInfo(user):
    # Update categories and payments from webhook
    #print(user.url)
    r = requests.get(user.url)
    parsed = json.loads(r.text)
    
    user.category_markup = [[element] for element in parsed['cate']]
    user.payment_markup = [[element] for element in parsed['pay']]
    user.category_markup.append(['取消'])
    user.payment_markup.append(['取消'])
    
def sendRecord(user):
    # Upload record to webhook
    r = requests.post(user.url, data=(user.temp))
    if r.text == "NOK": # return "NOK" or "OK"
        return 1
    return 0



def error_handler(update, callbackContext):
    try:
        raise callbackContext.error
    except:
        print("error")
    return ConversationHandler.END

def valid(id):
    return (1 if id in ValidUsersList else 0)


"""
 1: ask price                  float
 2: ask payment                string
 3: ask item (spotify of sth.) string
 4: record  >  string
"""

dispatcher.add_error_handler(error_handler)
dispatcher.add_handler(CommandHandler("start", start_handler))
dispatcher.add_handler(CommandHandler("whoami", who_handler))
dispatcher.add_handler(CommandHandler("test", testWorking_handler)) 
dispatcher.add_handler(CommandHandler(["help"], help_handler)) 
dispatcher.add_handler(CommandHandler("cancel", failed_handler  , filters=Filters.user(user_id=ValidUsersList))) 
dispatcher.add_handler(CommandHandler("register", reg_handler))
dispatcher.add_handler(CommandHandler("register_url", reg_token_handler, filters=Filters.user(user_id=ValidUsersList)))
dispatcher.add_handler(CommandHandler("update", updateInfo_handler, filters=Filters.user(user_id=ValidUsersList)))
dispatcher.add_handler(ConversationHandler(
	#conversation_timeout=60, 
	entry_points=[CommandHandler(["b"], acc_cate_handler)], 
	states={1: [MessageHandler(Filters.text, acc_price_handler)], 
		2: [MessageHandler(Filters.text, acc_payment_handler)],
		3: [MessageHandler(Filters.text, acc_item_handler)] ,
		4: [MessageHandler(Filters.text, acc_record_handler)] },
	fallbacks=[CommandHandler('cancel', failed_handler)],
    per_user=True,
    name="Accounting"
    )
)

initConfig()



if __name__ == "__main__":
    app.run(debug=True)


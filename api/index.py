import os
from dotenv import load_dotenv
import datetime

import logging

from typing import Optional
from fastapi import FastAPI
import telegram
from pydantic import BaseModel
from telegram import Update, Bot
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, Dispatcher, CallbackContext
from deta import Deta

load_dotenv()

TOKEN = os.getenv("TELE_TOKEN")
DETA_KEY = os.getenv("DETA_KEY")

logging.basicConfig(format="%(asctime)s - %(name)s - %(message)s", level=logging.INFO)

app = FastAPI()

deta = Deta(DETA_KEY)

cotm11_std_db = deta.Base("cotm11_std")
last_word_db = deta.Base("last_word")

ADMIN_ID = 403875924

class TelegramWebhook(BaseModel):
    update_id: int
    message: Optional[dict]
    edited_message: Optional[dict]
    channel_post: Optional[dict]
    edited_channel_post: Optional[dict]
    inline_query: Optional[dict]
    chosen_inline_result: Optional[dict]
    callback_query: Optional[dict]
    shipping_query: Optional[dict]
    pre_checkout_querry: Optional[dict]
    poll: Optional[dict]
    poll_answer: Optional[dict]

def start(update, context):
    """
    here check user_id and tell if they are cotm-11 or not
    """
    effective_chat = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello")

def last_words(update, context):
    """
    first check if user_id is from cotm-11 if so send every bodies last word
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text="Last Words")
    

def last_word(update, context):
    """
    check id then sends one last_word accordingly
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text="Last Word")
    
def my_last_word(update, context):
    """
    check id then sends users last_word
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text="Your last word")

def add_last_word(update, context):
    """
    check id and last_word
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text="Last word added")

now= datetime.datetime.now()

def cotm_11(update, context):
    """
    to insert cont11_std
    """
    user = update.effective_user or update.effective_chat
    cotm11Std_dict = user.to_dict()
    cotm11Std_dict['at']=now.strftime("%d/%m/%y, %H:%M")
    cotm11Std_dict['key'] = str(user.id)

    cotm11_std_db.put(cotm11Std_dict)
    update.message.reply_html(text="Good")

def fecth_cotm11_stds():
    """
    fetch cotm11_std
    """
    cotm11_stds = cotm11_std_db.fetch().items
    cotm11_std_ids = []
    for cotm11_std in cotm11_stds:
        cotm11_std_ids.append(cotm11_std["id"])
    return cotm11_std_ids


def get_cotm_11(update, context):
    """
    to get ids
    """
    effective_user = update.effective_user
    if effective_user.id != ADMIN_ID:
        update.message.reply_text(text="sry muchacho")
        return
    cotm11_std_ids=fecth_cotm11_stds()
    update.message.reply_text("Registered Ids: "+str(cotm11_std_ids))

def register_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('last_words', last_words))
    dispatcher.add_handler(CommandHandler('last_word', last_word))
    dispatcher.add_handler(CommandHandler('my_last_word', my_last_word))
    dispatcher.add_handler(CommandHandler('add_last_word', add_last_word))

    dispatcher.add_handler(CommandHandler('cotm_11', cotm_11))
    dispatcher.add_handler(CommandHandler('get_cotm_11', get_cotm_11))


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    register_handlers(dispatcher)
    updater.start_polling()
    updater.idle()

@app.post("/webhook")
def webhook(webhook_data: TelegramWebhook):
    bot = Bot(token=TOKEN)
    update = Update.de_json(webhook_data.__dict__, bot)
    dispatcher = Dispatcher(bot, None, workers=4, use_context=True)
    register_handlers(dispatcher)
    dispatcher.process_update(update)
    return {"status":"okay"}

@app.get("/")
def index():
    return {"status":"okay"}

import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler, ConversationHandler,
)
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
    ParseMode,
    error,
)
from telegram.ext.filters import Filters
from telegram.chataction import ChatAction
from bs4 import BeautifulSoup
from uuid import uuid4
import requests
from telegram.utils.helpers import escape_markdown
from bot import messages


def exam_ap_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
        context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIOA2EvpGPuvMDrLtioE7S4d'
                                                                             'plwkDZtAAKGCwACvnOBURIJI-dSD7TGIAQ',
                                  filename='AP exams.zip',
                                  caption='سوالات امتحانی برنامه سازی پیشرفته دکتر پایدار', timeout=60)
    except error.NetworkError as e:
        update.message.reply_text(text=messages['msg_network_error'])


def exam_discrete_bafghi_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT, timeout=300)
        context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIOGWEvqEl-8BKckRp3oqlRQZE'
                                                                             'fettOAAKWCwACvnOBUQP4XT_T7-rsIAQ',
                                  filename='Discrete exams & exe (Bafghi)',
                                  caption='تمرینات و امتحانات ریاضیات گسسته استاد بافقی', timeout=200)
    except error.NetworkError as e:
        update.message.reply_text(text=messages['msg_network_error'])


def exam_discrete_structure_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    try:
        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT, timeout=300)
        context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIOF2Evp3rOZ4ILOBWni6xh3Y97y'
                                                                             'ud6AAKUCwACvnOBUdfT2nMzrPC9IAQ',
                                  filename='Discrete Structure', caption='تمرینات ساختمان گسسته', timeout=300)

    except error.NetworkError as e:
        update.message.reply_text(text=messages['msg_network_error'])


def exam_fp_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='این بخش در حال بروزرسانی است، به زودی فایل های'
                                                                    ' مربوطه قرار خواهند گرفت')


def exam_ds_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkBAAIUVWE1xLqU2lUhw1O_toh68mkaFXe'
                                                                         '2AAKRCwAC5miwUTynOJTv3cEYIAQ',
                              filename='DS Ghiasi',
                              caption='فایل درس ساختمان داده غیاثی 99', timeout=60)


def exam_differential_equation(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='کانال حل تمرین نمونه سوالات(محمدیان):\n'
                                                                    'https://t.me/tamrin_moadelat_fum')

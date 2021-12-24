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


def src_fp_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIOJ2EvuoLom5UGUamAJyt1Vh-jKhrw'
                                                                         'AAJ4DAACvnOBUVgDsjQ4o52yIAQ',
                              filename='Fundamental Programming Sources.zip',
                              caption='کناب دایتل و جزوات', timeout=300)
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIONGEvvpe8Ed50EiOROx9N9kq6'
                                                                         '1sNdAAJ6DAACvnOBUc5tmQ3nPxXFIAQ',
                              filename='Sample Codes.zip',
                              caption='نمونه کد های مسائل کارگاه', timeout=300)
    # with open('./slides-abrishami.zip') as f:
    #     context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    #     print(context.bot.send_document(chat_id=update.effective_chat.id, document=f,
    #                                     filename='Slides DR.Abrishami',
    #                                     caption='اسلاید های استاد ابریشمی', timeout=3000))


def src_discrete_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIONmEvv79XY_bXBpIhlnDNMqbMNm9'
                                                                         'EAAJ7DAACvnOBUeySzm0kBgeOIAQ',
                              filename='Rosen Discrete Mathematics.pdf',
                              caption='منبع اصلی - روزن', timeout=3000)
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAION2EvwEM1JXSHvis_Pl9MHo'
                                                                         'DbwkNDAAJ9DAACvnOBUcV2FFEF0FoPIAQ',
                              filename='Solution Manual for Discrete Mathematics Rosen.pdf',
                              caption='پاسخنامه روزن', timeout=3000)


def src_ap_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='این بخش در حال بروزرسانی است، به زودی فایل های'
                                                                    ' مربوطه قرار خواهند گرفت')


def src_ds_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    #  buttons for linking DS videos to programming telegram channel
    buttons = [
        [  # first row
            InlineKeyboardButton('قسمت1', 'https://t.me/Azad_Developers/17205'),
            InlineKeyboardButton('قسمت2', 'https://t.me/Azad_Developers/17209'),
            InlineKeyboardButton('قسمت3', 'https://t.me/Azad_Developers/17214'),
        ], [
            InlineKeyboardButton('قسمت4', 'https://t.me/Azad_Developers/17229'),
            InlineKeyboardButton('قسمت5', 'https://t.me/Azad_Developers/17235'),
            InlineKeyboardButton('قسمت6', 'https://t.me/Azad_Developers/17243'),
        ], [
            InlineKeyboardButton('قسمت7', 'https://t.me/Azad_Developers/17248'),
            InlineKeyboardButton('قسمت8', 'https://t.me/Azad_Developers/17264'),
            InlineKeyboardButton('قسمت9', 'https://t.me/Azad_Developers/17279'),
        ], [
            InlineKeyboardButton('قسمت10', 'https://t.me/Azad_Developers/17298'),
            InlineKeyboardButton('قسمت11', 'https://t.me/Azad_Developers/17318'),
            InlineKeyboardButton('قسمت12', 'https://t.me/Azad_Developers/17328'),
        ], [
            InlineKeyboardButton('قسمت13', 'https://t.me/Azad_Developers/17344'),
            InlineKeyboardButton('قسمت14', 'https://t.me/Azad_Developers/17361'),
            InlineKeyboardButton('قسمت15', 'https://t.me/Azad_Developers/17373'),
        ], [
            InlineKeyboardButton('قسمت16', 'https://t.me/Azad_Developers/17386'),
            InlineKeyboardButton('قسمت17', 'https://t.me/Azad_Developers/17401'),
            InlineKeyboardButton('قسمت18', 'https://t.me/Azad_Developers/17415'),
        ], [
            InlineKeyboardButton('قسمت19', 'https://t.me/Azad_Developers/17428'),
            InlineKeyboardButton('قسمت20', 'https://t.me/Azad_Developers/17448'),
            InlineKeyboardButton('قسمت21', 'https://t.me/Azad_Developers/17464'),
        ], [
            InlineKeyboardButton('قسمت22', 'https://t.me/Azad_Developers/17479'),
            InlineKeyboardButton('قسمت23', 'https://t.me/Azad_Developers/17493'),
            InlineKeyboardButton('قسمت24', 'https://t.me/Azad_Developers/17505'),
        ], [
            InlineKeyboardButton('قسمت25', 'https://t.me/Azad_Developers/17537'),
            InlineKeyboardButton('قسمت26', 'https://t.me/Azad_Developers/17584'),
            InlineKeyboardButton('قسمت27', 'https://t.me/Azad_Developers/17595'),
        ], [
            InlineKeyboardButton('قسمت28', 'https://t.me/Azad_Developers/17602'),
            InlineKeyboardButton('قسمت29', 'https://t.me/Azad_Developers/17629'),
            InlineKeyboardButton('قسمت30', 'https://t.me/Azad_Developers/17633'),
        ], [
            InlineKeyboardButton('قسمت31', 'https://t.me/Azad_Developers/17647'),
            InlineKeyboardButton('قسمت32', 'https://t.me/Azad_Developers/17660'),
            InlineKeyboardButton('قسمت33', 'https://t.me/Azad_Developers/17670'),
        ], [
            InlineKeyboardButton('قسمت34', 'https://t.me/Azad_Developers/17727'),
            InlineKeyboardButton('قسمت35', 'https://t.me/Azad_Developers/17738'),
            InlineKeyboardButton('قسمت36', 'https://t.me/Azad_Developers/17755'),
        ],
        # [
        #     InlineKeyboardButton('قسمت37', 'https://t.me/Azad_Developers/17765'),
        #     InlineKeyboardButton('قسمت38', 'https://t.me/Azad_Developers/17773'),
        # ]
    ]
    update.message.reply_text(
        text='آموزش ساختمان داده(مدرس : سعید شهریوری):\n',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIOIWEvqc_csllZ8y0oKN-rIQg'
                                                                         'LW8qhAAKZCwACvnOBUctL9li_jBvzIAQ',
                              filename='DS & Algorithm by Weiss',
                              caption='منبع درس ساختمان داده', timeout=11)

    logging.info('{} {}({}): {}\n'.format(first_name, last_name, chat_id, update))
    # with open('./sources/DS/The Art of Computer Programming (vol. 3_ Sorting and Searching) (2nd ed.) [Knuth '
    #           '1998-05-04].pdf') as f:
    #     context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    #     print(context.bot.send_document(chat_id=update.effective_chat.id, document=f,
    #                                     filename='The Art of Computer Programming',
    #                                     caption='منبع در ساختمان داده', timeout=300))


def src_ai_abrishami_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkBAAIUSWE1woC5Hbb05QH22qiZoYz-'
                                                                         'lN0SAAKwCQACUYl4USxYqCkiFX8gIAQ',
                              file_name='AI(abrishami)',
                              caption='فایل های درس هوش مصنوعی استاد ابریشمی بهار 1400')


def src_os_allah_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkBAAMNYTUlPxO9KFaay6vLcNKSEU-xmUwAA'
                                                                         'qYJAAJRiXhR3fEWYGFDKTYgBA',
                              file_name='OS(allah bakhsh)',
                              caption='فایل های درس سیستم عامل الله بخش بهار 1400')


def src_differential_equation(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkBAANAYTuhePSMSrMZU89512Jr-hnyK'
                                                                         'gADSQkAAiwg4VGEWVkaYkOiHyAE',
                              file_name='معادلات دیفرانسیل ادوارز و پتی')
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkBAANCYTuiCtYpXKvCyNvLaEIYtD4X84Y'
                                                                         'AAkoJAAIsIOFRWMo8c14kmQsgBA',
                              file_name='پاسخ نامه معادلات دیفرانسیل ادوارز و پتی')
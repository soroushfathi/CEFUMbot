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


def college_getLatinArticles():
    url = ARTICLES_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    number_result = soup.find_all('td', attrs={
        'style': 'padding:5px; border:1px solid #E6E6E6; text-align:center !important;'})
    title_result = soup.find_all('td', attrs={
        'style': 'padding:5px; border:1px solid #E6E6E6; text-align: justify !important; direction: ltr; '})
    date_result = soup.find_all('td', attrs={'style': 'padding:5px; border:1px solid #E6E6E6;'})
    author_result = soup.find_all('td', attrs={'style': 'padding:5px; border:1px solid #E6E6E6;'})
    authors = [item.text for item in author_result]  # odds
    date = [item.text for item in date_result]  # even
    titles = [item.text for item in title_result]
    links = [item.a['href'] for item in title_result]
    return authors, titles, date, links


def college_latinArticles_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    authors, titles, date, links = college_getLatinArticles()
    txt = ''
    for t, a, d, l in list(zip(titles[:10], authors[1:20:2], date[0:20:2], links[:10])):
        txt += '📝{0} - <a href="{3}">{1}</a> - {2} \n'.format(a, t, d, l)
    buttons = [
        [InlineKeyboardButton('مراجعه به سایت', 'http://ce.um.ac.ir/index.php?option=com_groups&view=enarticles&'
                                                'edugroups=3105&cur_stu_title=&Itemid=694&lang=fa')],
    ]
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    update.message.reply_text(text=txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))


# def college_articles_keyboard(update: Update, context: CallbackContext) -> None:
#     query = update.callback_query
#     data = query.data
#     chat_id = query.message.chat_id
#     message_id = query.message.message_id
#     authors, titles, date, links = college_getLatinArticles()
#     txt = ''
#     for t, a, d, l in list(zip(titles[:15], authors[1:30:2], date[0:30:2], links[:15])):
#         txt += '📝{0} - <a href="{3}">{1}</a> - {2} \n'.format(a, t, d, l)
#     txt += '\n<a href="{}">مراجعه به سایت</a>\n'.format(ARTICLES_URL)
# button = [
#     [InlineKeyboardButton('مراجعه به سایت', 'http://ce.um.ac.ir/index.php?option=com_groups&view=enarticles&'
#                                             'edugroups=3105&cur_stu_title=&Itemid=694&lang=fa')],
# ]
# if data == 'extraArticles':
#     context.bot.send_chat_action(chat_id, ChatAction.TYPING)
#     context.bot.editMessageText(text=txt, chat_id=chat_id, message_id=message_id)
# context.bot.editMessageReplyMarkup(text=txt + '\n<a href="{}">مقالات بیشتر</a>\n'.format(ARTICLES_URL),
#                                    parse_mode=ParseMode.HTML,
#                                    reply_markup=InlineKeyboardMarkup(button),
#                                    chat_id=chat_id, message_id=message_id)


def college_persianArticles_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='به زودی فایل های مربوطه در این بخش قرار خواهند '
                                                                    'گرفت،\n با تشکر🙏🏻 ')


def college_books_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='به زودی فایل های مربوطه در این بخش قرار خواهند '
                                                                    'گرفت،\n با تشکر🙏🏻 ')


def college_press_handler(update: Update, context: CallbackContext) -> None:
    buttons = [
        [messages['btn_college_press_latinArticle'], messages['btn_college_press_books']],
        [messages['btn_college_press_persianArticle']],
        [messages['btn_back_home'], messages['btn_back_college']],
    ]
    update.message.reply_text(
        text=messages['msg_college_press'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def college_news_handler(update, context):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    url = BASE_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_result = soup.find_all('div', attrs={'class': 'aidanews2_positions'})
    title = [item.h1.a.text for item in title_result]
    date_time_result = soup.find_all('div', attrs={'class': 'aidanews2_botL'})
    date_time = [item.span.text for item in date_time_result]
    links = [item.h1.a['href'] for item in title_result]
    txt = ''
    for i in range(len(date_time) - 1):
        txt += '{}📌'.format(i + 1) + '<a href="ce.um.ac.ir{}">{}</a>'.format(links[i], title[i]) + '\n\t' + date_time[
            i] + '\n'
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    button = [
        [InlineKeyboardButton('مشاهده همه ی اخبار', 'http://ce.um.ac.ir/index.php?option=com_content&view=category'
                                                    '&id=102&Itemid=634&lang=fa')],
    ]
    update.message.reply_text(
        text=txt, parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(button)
    )
    context.bot.send_message(chat_id=131605711, text=str(update))
    logging.info('{} {}({}): {}\n'.format(first_name, last_name, chat_id, update))


def college_notification_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    url = BASE_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_result = soup.find_all('div', attrs={'class': 'aidanews2_positions'})
    title = [item.h1.a.text for item in title_result]
    links = [item.h1.a['href'] for item in title_result]
    date_time_result = soup.find_all('span', attrs={'class': 'aidanews2_date'})
    date_time = [item.text for item in date_time_result]
    txt = ''
    for i in range(5, len(date_time)):
        txt += '{}📌'.format(i - 4) + '<a href="ce.um.ac.ir{}">{}</a>'.format(links[i], title[i]) + \
               '\n\t' + date_time[i] + '\n'
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    button = [
        [InlineKeyboardButton('مشاهده همه ی اطلاعیه ها', 'http://ce.um.ac.ir/index.php?option=com_content&view=category'
                                                         '&id=113&Itemid=540&lang=fa')],
    ]
    update.message.reply_text(
        text=txt, parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(button)
    )


def college_teach_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='به زودی فایل های مربوطه در این بخش قرار خواهند '
                                                                    'گرفت،\n با تشکر🙏🏻 ')


def college_masters_handler(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    buttons = [
        [
            InlineKeyboardButton('برنامه سازی پیشرفته', callback_data='advance_programming'),
            InlineKeyboardButton('مدار منطقی', callback_data='logic_circuits'),
        ], [
            InlineKeyboardButton('مبانی کامپیوتر و برنامه سازی', callback_data='fundamental_programming'),
            InlineKeyboardButton('ریاضیات گسسته', callback_data='discrete_math'),
        ], [
            InlineKeyboardButton('زبان تخصصی', callback_data='advance_english'),
            InlineKeyboardButton('طراحی الگوریتم', callback_data='algorithm'),
            InlineKeyboardButton('ساختمان داده', callback_data='data_structure'),
        ], [
            InlineKeyboardButton('معارف', callback_data='maaref'),
            InlineKeyboardButton('اضافه کردن درس +', callback_data='add_subject')
        ]
    ]
    update.message.reply_text(
        text='درس مورد نظر را انتخاب کنید:',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return FIRST


def college_masters_ds_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('دکتر غیاثی شیرازی', callback_data='ghiasi'),
            InlineKeyboardButton('دکتر امین طوسی', callback_data='tosi'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_algorithm_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('دکتر نوری بایگی', callback_data='noriBaigi'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_ap_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('دکتر نوری بایگی', callback_data='noriBaigi'),
            InlineKeyboardButton('دکتر پایدار', callback_data='paydar'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_discrete_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('دکتر بافقی', callback_data='bafghi'),
            InlineKeyboardButton('دکتر غیاثی شیرازی', callback_data='ghiasi'),
        ], [
            InlineKeyboardButton('مجید میرزاوزیری', callback_data='mirzavaziri'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_logic_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('یاصر صداقت', callback_data='sedaghat'),
            InlineKeyboardButton('سارا ارشادی نسب', callback_data='ershadi'),
        ], [
            InlineKeyboardButton('مریم زمردی مقدم', callback_data='zomorodi'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_fp_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('سعید ابریشمی', callback_data='abrishami'),
            InlineKeyboardButton(' نوری بایگی', callback_data='noriBaigi'),
        ], [
            InlineKeyboardButton('احسان فضل ارثی', callback_data='fazlErsi'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_advEnglish_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('سعید عربان', callback_data='arban'),
            InlineKeyboardButton('عابدین واحدیان مظلوم', callback_data='vahedian'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_maaref_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id, text=messages['msg_maaref_masters'])
    return SECOND


def end_college_masters_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    first_name = query.message.chat.first_name
    last_name = query.message.chat.last_name
    # message_id = query.message.message_id
    if data == 'abrishami':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://s-abrishami.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_abrishami'], reply_markup=InlineKeyboardMarkup(button))
        # context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_masters_abrishami'])
        # context.bot.editMessageText(text=messages['msg_masters_abrishami'], chat_id=chat_id, message_id=message_id)
    elif data == 'noriBaigi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://nouribaygi.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_noriBaigi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'paydar':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://s-paydar.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_paydar'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'fazlErsi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://fazlersi.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_fazlErsi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'sedaghat':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://y_sedaghat.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_sedaghat'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'ershadi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_masters_ershadi'])
    elif data == 'bafghi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://ghaemib.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_bafghi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'ghiasi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://profsite.um.ac.ir/~k.ghiasi/')]]
        query.message.reply_text(text=messages['msg_masters_ghiasi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'harati':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://a.harati.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_harati'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'tosi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://amintoosi.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_tosi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'arban':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://araban.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_arban'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'zomorodi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://m_zomorodi.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_zomorodi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'vahedian':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://vahedian.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_vahedian'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'mirzavaziri':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_masters_mirzavaziri'])
    elif data == 'add_master':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text='اگر استاد مد نظر در لیست وجود ندارد، میتوانید'
                                                                        'اسم استاد را فقط با فرمت زیر(بین دو خط تیره)'
                                                                        ' ارسال کنید 🙏🏻: '
                                                                        '\n -نام استاد-')
        get_master(update, context)
    context.bot.send_message(chat_id=131605711, text=str(update))
    logging.info('{} {}({}): {}\n'.format(first_name, last_name, chat_id, update))
    # return ConversationHandler.END


def get_master(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, text='نام استاد دریافت شد✅پس از تایید در بات قرار داده میشود')
    context.bot.send_message(chat_id=131605711, text=update.message.text)


def college_masters_add_subject(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.editMessageText(chat_id=update.effective_chat.id, message_id=message_id,
                                text='اگر درس مد نظر در لیست وجود ندارد، میتوانید'
                                     'نام درس را فقط با فرمت زیر(بین دو آندرلاین)'
                                     ' ارسال کنید 🙏🏻: '
                                     '\n _نام درس_')


def get_subject(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, text='نام درس دریافت شد✅پس از تایید در بات قرار داده میشود')
    context.bot.send_message(chat_id=131605711, text=update.message.text)


def college_contact_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    URL = BASE_URL
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    contact_result = soup.find_all('ul', attrs={'class': 'contact-info'})
    contact_info = [item.li.text for item in contact_result]
    txt = '📍آدرس : {}'.format(contact_info) + '\n\n' + messages['msg_college_contact']
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
    buttons = [
        [InlineKeyboardButton('سایت مهندسی کامپیوتر', 'http://ce.um.ac.ir/index.php?lang=fa')],
        [InlineKeyboardButton('شماره تلفن های گروه کامپیوتر', 'http://118.um.ac.ir/%D8%AF%D8%A7%D9%86%D8%B4%DA%A9%D8%AF'
                                                              '%D9%87-%D9%87%D8%A7/%D8%AF%D8%A7%D9%86%D8%B4%DA%A9%D8%AF'
                                                              '%D9%87-%D9%85%D9%87%D9%86%D8%AF%D8%B3%DB%8C.html')],
    ]
    update.message.reply_text(text='پیوندها: ', reply_markup=InlineKeyboardMarkup(buttons))


def college_about_handler(update, context):
    # todo fix web scraping
    # url = BASE_URL
    # response = requests.get(url)
    # soup = BeautifulSoup(response.content, 'html.parser')
    # about_result = soup.find_all('div', attrs={'class': 'item-page'})
    # about_txt = [item.text for item in about_result]
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    button = [
        [InlineKeyboardButton('اطلاعات بیشتر', 'http://ce.um.ac.ir/index.php?option=com_content&view=article&id=134&'
                                               'Itemid=521&lang=fa')],
    ]
    update.message.reply_text(text=messages['msg_college_about'], reply_markup=InlineKeyboardMarkup(button))

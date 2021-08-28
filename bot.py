import logging

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
)
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InlineQueryResultDocument,
    InlineQueryResultCachedGif,
    InlineQueryResultGif,
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

BASE_URL = 'http://ce.um.ac.ir/index.php?lang=fa'
ARTICLES_URL = 'http://ce.um.ac.ir/index.php?option=com_groups&view=enarticles&edugroups=3105&cur_stu_title=&Itemid=694&lang=fa'

messages = {
    'msg_start': 'سلام {}، \n خوش امدی به ربات🙂، امیدوارم بتونم کمکت کنم🤠',
    'msg_contact': 'سروش فتحی 👨🏻‍💻، دانشجوی مهندسی کامپیوتر فردوسی ورودی 99🧑🏻‍🎓\n',
    'msg_main_handler': 'منوی اصلی🗂️:',
    'msg_select_src_subject': 'درس مورد نظر را انتخاب کنید(تمرین و امتحانات):',
    'msg_select_exe_subject': ' درس مورد نظر را انتخاب کنید(منابع و جزوات):',
    'msg_help': 'کار با ربات سادس😌 نیازی به راهنمایی نیست😜😆',
    'msg_college': 'گروه مهندسی کامپیوتر🖥 : ',
    'msg_college_press': 'انتشارات مهندسی کامپیوتر فردوسی مشهد: ',
    'msg_network_error': 'به دلیل سرعت پایین شبکه، ارسال فایل با مشکل مواجه شد😣 \n '
                         'به زودی مشکل را حل خواهیم کرد🤠\n'
                         'با تشکر از صبر شما🙏🏻',
    'msg_sending_time': 'به دلیل سرعت پایین شبکه، ارسال فایل ممکن '
                        'است پنج دقیقه طول بکشد😣 \n '
                        'به زودی مشکل را حل خواهیم کرد🤠\n'
                        'با تشکر از صبر شما🙏🏻',
    'msg_college_about': 'در سال ۱۳۴۹ هجری خورشیدی همزمان با دانشگاه تهران و دانشگاه صنعتی شریف، '
                         'رشته آمار و ماشین های حسابگر در مقطع کارشناسی در دانشکده علوم دانشگاه فردوسی مشهد تأسیس شد.'
                         ' بعدها این رشته به نام کامپیوتر تغییر نام یافت تا اینکه در سال ۱۳۶۷ گروه مهندسی کامپیوتر'
                         ' در دانشکده مهندسی شکل گرفت و پذیرش دانشجو در مقطع کارشناسی رشته مهندسی کامپیوتر گرایش نرم '
                         'افزار در دانشکده مهندسی آغاز گردید. گروه مهندسی کامپیوتر در سال ۱۳۷۴ پذیرش دانشجو در مقطع'
                         ' کارشناسی ارشد مهندسی کامپیوتر گرایش نرم افزار را آغاز کرد. در سال ۱۳۷۹ گرایش سخت افزار'
                         ' به گرایش های رشته مهندسی کامپیوتر گروه اضافه شد و پذیرش دانشجو در مقطع کارشناسی گرایش '
                         'سخت افزار شروع شد. گروه مهندسی کامپیوتر در سال ۱۳۸۵ پذیرش دانشجو در مقطع دکترای تخصصی '
                         'مهندسی کامپیوتر گرایش نرم افزار را شروع کرد. پذیرش دانشجو در مقاطع کارشناسی ارشد و دکترای'
                         ' تخصصی مهندسی کامپیوتر گرایش هوش مصنوعی به ترتیب در سال های ۱۳۸۷ و ۱۳۹۴ آغاز شد. گروه مهندسی '
                         'کامپیوتر از سال ۱۳۹۳ اقدام به پذیرش دانشجو در مقطع کارشناسی ارشد مهندسی فناوری اطلاعات گرایش '
                         'شبکه های کامپیوتری کرده است. علاوه بر این، گروه مهندسی کامپیوتر از مهرماه ۱۳۹۶ پذیرش دانشجو'
                         ' در مقطع کارشناسی ارشد مهندسی کامپیوتر گرایش معماری کامپیوتر (سخت افزار) را شروع خواهد کرد. ',
    'msg_college_contact': '''☎️تلفن:۰۵۱-۳۸۸۰۶۰۵۹
 📠نمابر: ۰۵۱-۳۸۸۰۷۱۸۱
📭كدپستی: ۹۱۷۷۹۴۸۹۷۴
📧پست الکترونیک: ce.um.ac.ir''',
    'msg_masters_noriBaigi': '🔎اطلاعات مربوطه استاد نوری بایگی، به زودی در این بخش قرار خواهد گرفت\n با تشکر🙏🏻',
    'msg_masters_sedaghat': '👨🏻‍🏫استاد یاصر صداقت\n'
                            ' ۰۵۱-۳۸۸۰۵۱۴۸ ☎️\n'
                            'y_sedaghat@um.ac.ir 📧\n'
                            '🗄تحصیلات: \n'
                            '\t🔰مرتبه علمی: استادیار\n'
                            '\t🔰آخرین مدرک تحصیلی: دکترای مهندسی کامپیوتر - معماری کامپیوتر\n'
                            '\t🔰محل اخذ آخرین مدرک تحصیلی: دانشگاه صنعتی شریف، تهران، ایران\n'
                            '\n✅سطح تدریس : پیشرفته\n'
                            '✅نمره دهی : خوب\n'
                            '🏷توضیحات: \n بجز حساسیت های الکیی ک داره دقیقا رو نظم و با برنامه و خیلی هم خوب تدریس میکنه n\
                            در این حد ک ارشادی جزوه صداقت رو درس میداد(۳ فصل آخرشو) \n '
                            'کلی هم نمره اضافه داره صداقت، کلاسای حل تمرینش همش امتیازیه 4و5 تا کوییز امتیازی داره \n '
                            'از اول ترم مشخص میکنه برنامشو طبق همون میره جلو\n '
                            '\nنظرات دانشجویان💡 : \n'
                            'https://t.me/ashnayi_ba_asatid/483\n'
                            'https://t.me/Comp_Professors/21\n'
                            'https://t.me/Comp_Professors/36\n',
    'msg_masters_nori': '🔎اطلاعات مربوطه استاد نوری، به زودی در این بخش قرار خواهد گرفت\n با تشکر🙏🏻',
    'msg_masters_bafghi': '👨🏻‍🏫استاد قائمی بافقی\n'
                          '۰۵۱-۳۸۸۰۵۰۶۲ ☎️\n'
                          ' ghaemib@um.ac.ir 📧\n'
                          '🗄تحصیلات: \n'
                          '\t\t\t🔰مرتبه علمی: دانشیار\n'
                          '\t\t\t🔰آخرین مدرک تحصیلی: دکترای مهندسی کامپیوتر - نرم افزار\n'
                          '\t\t\t🔰محل اخذ آخرین مدرک تحصیلی: دانشگاه صنعتی امیرکبیر، تهران، ایران\n\n'
                          '🏷توضیحات : \n استاد بیشترِ مباحث رو تدریس می کنه، یعنی از هر چیزی در حد نیاز میگه، مثلا '
                          'در درس گسسته مباحثی مانند مرتبه زمانی و ساختمان داده هم بیان میکنه. در بیان مطلب و تدریس '
                          'ضعیف هستند، در حدی که باید خودت بخونی 🙃 سرعت تدریسشون هم بالاس و رو یه مبحث نمیمونن\n'
                          'در ضمن تلگرام هم ندارن:) راه های ارتباطی ایمیل و سروش و واتس اپ :) \n'
                          '\nنظرات دانشجویان💡 : \n'
                          'https://t.me/Comp_Professors/58\n'
                          'https://t.me/Comp_Professors/64\n'
                          'https://t.me/Comp_Professors/31\n',
    'msg_masters_tosi': '🔎اطلاعات مربوطه استاد طوسی، به زودی در این بخش قرار خواهد گرفت\n با تشکر🙏🏻',
    'msg_masters_harati': '🔎اطلاعات مربوطه استاد هراتی، به زودی در این بخش قرار خواهد گرفت\n با تشکر🙏🏻',
    'msg_masters_paydar': '🔎اطلاعات مربوطه استاد پایدار، به زودی در این بخش قرار خواهد گرفت\n با تشکر🙏🏻',
    'msg_masters_ghiasi': '🔎اطلاعات مربوطه استاد غیاثی، به زودی در این بخش قرار خواهد گرفت\n با تشکر🙏🏻',
    'msg_masters_fazlErsi': '🔎اطلاعات مربوطه استادفضل ارثی، به زودی در این بخش قرار خواهد گرفت\n با تشکر🙏🏻',
    'msg_masters_abrishami': '👨🏻‍🏫استاد سعید ابریشمی\n'
                             '۰۵۱-۳۸۸۰۵۱۲۱ ☎️\n'
                             'تلگرام : @Sabrishami\n'
                             's-abrishami@um.ac.ir 📧\n'
                             '🗄تحصیلات: \n'
                             '\t🔰مرتبه علمی: استادیار\n'
                             '\t🔰آخرین مدرک تحصیلی: دکترای مهندسی کامپیوتر - نرم افزار\n'
                             '\n✅سطح تدریس : پیشرفته\n'
                             '✅نمره دهی : خوب\n'
                             '\nنظرات دانشجویان💡 : \n'
                             'https://t.me/ashnayi_ba_asatid/358\n'
                             'https://t.me/Comp_Professors/63\n',

    'btn_college': 'گروه مهندسی کامپیوتر🏫',
    'btn_exams_exe': 'تمرین و امتحانات📑',
    'btn_sources': 'منابع و جزوات📚',
    'btn_plans': 'طرح های پژوهشی جاری',
    'btn_contact': '📞تماس با من👨🏻‍💻',
    'btn_help': 'راهنمایی✅',

    'btn_college_masters': 'اساتید👨🏻‍🏫',
    'btn_college_news': 'اخبار📰',
    'btn_college_notification': 'اطلاعیه ها🔖',
    'btn_college_conference': 'کنفرانس ها و همایش ها🎥',
    'btn_college_about': 'درباره ما',
    'btn_college_pack': '📦بسته های کارشناسی',
    'btn_college_contact': 'راه های ارتباطی دانشکده📞',
    'btn_college_teach': 'آموزش',
    'btn_college_press': 'انتشارات📑',
    'btn_college_press_latinArticle': 'مقالات لاتین🧾',
    'btn_college_press_persianArticle': 'مقالات فارسی',
    'btn_college_press_books': 'کتاب ها📚',

    'btn_exe_fundamental_programming': 'مبانی برنامه نویسی ابریشمی',
    'btn_exe_advance_programming': 'برنامه سازی پیشرفته پایدار',
    'btn_exe_discrete_bafghi': 'ریاضیات گسسته بافقی',
    'btn_exe_discrete_structure': 'ساختمان گسسته',
    'btn_exe_data_structure': 'نمونه',

    'btn_src_fundamental_programming': 'مبانی کامپیوتر برنامه نویسی',
    'btn_src_advance_programming': 'برنامه سازی پیشرفته',
    'btn_src_discrete': 'ریاضیات گسسته',
    'btn_src_data_structure': 'ساختمان داده',

    'btn_back_home': 'خانه🏠',
    'btn_back_college': 'بازگشت🔙',
}

logging.basicConfig(filename='info.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s-%(filename)s-%(message)s-%(funcName)s')


def start(update, context):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    # write user data in file
    with open('./users/users_data.txt', 'a') as f:
        f.write(str(update) + '\n\n')
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_start'].format(first_name))
    main_menu_handler(update, context)
    logging.info('{} {}({}): {}\n'.format(first_name, last_name, chat_id, update))


# def echo(update, context):
#     context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def main_menu_handler(update, context):
    buttons = [
        [messages['btn_exams_exe'], messages['btn_sources']],
        [messages['btn_college']],
        [messages['btn_contact'], messages['btn_help']],
    ]
    update.message.reply_text(
        text=messages['msg_main_handler'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def exe_subject_handler(update, context):
    buttons = [
        [messages['btn_exe_fundamental_programming'], messages['btn_exe_advance_programming']],
        [messages['btn_exe_discrete_bafghi'], messages['btn_exe_discrete_structure']],
        [messages['btn_exe_data_structure']],
        [messages['btn_back_home']],
    ]
    update.message.reply_text(
        text=messages['msg_select_exe_subject'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def src_subject_handler(update, context):
    buttons = [
        [messages['btn_src_fundamental_programming'], messages['btn_src_advance_programming']],
        [messages['btn_src_discrete'], messages['btn_src_data_structure']],
        [messages['btn_back_home']]
    ]
    update.message.reply_text(
        text=messages['msg_select_src_subject'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


# TODO add conference & plans button (web scraping) & Packs
def college_handler(update, context):
    buttons = [
        [messages['btn_college_news'], messages['btn_college_press']],
        [messages['btn_college_teach'], messages['btn_college_masters'], messages['btn_college_notification']],
        [messages['btn_college_about'], messages['btn_college_contact']],
        [messages['btn_back_home']],
    ]
    update.message.reply_text(
        text=messages['msg_college'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


# ToDo get persian articles and books
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
        [InlineKeyboardButton('مقالات بیشتر+', callback_data='extraArticles'),
         InlineKeyboardButton('مراجعه به سایت', 'http://ce.um.ac.ir/index.php?option=com_groups&view=enarticles&'
                                                'edugroups=3105&cur_stu_title=&Itemid=694&lang=fa')],
    ]
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    update.message.reply_text(text=txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))


def college_articles_keyboard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    authors, titles, date, links = college_getLatinArticles()
    txt = ''
    for t, a, d, l in list(zip(titles[:15], authors[1:30:2], date[0:30:2], links[:15])):
        txt += '📝{0} - <a href="{3}">{1}</a> - {2} \n'.format(a, t, d, l)
    txt += '\n<a href="{}">مراجعه به سایت</a>\n'.format(ARTICLES_URL)
    # button = [
    #     [InlineKeyboardButton('مراجعه به سایت', 'http://ce.um.ac.ir/index.php?option=com_groups&view=enarticles&'
    #                                             'edugroups=3105&cur_stu_title=&Itemid=694&lang=fa')],
    # ]
    if data == 'extraArticles':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        context.bot.editMessageText(text=txt, chat_id=chat_id, message_id=message_id)
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
        txt += '{}📌'.format(i + 1) + '<a href="ce.um.ac.ir{}">{}</a>'.format(links[i], title[i]) + '\n\t' + date_time[i] + '\n'
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    button = [
        [InlineKeyboardButton('مشاهده همه ی اخبار', 'http://ce.um.ac.ir/index.php?option=com_content&view=category'
                                                    '&id=102&Itemid=634&lang=fa')],
    ]
    update.message.reply_text(
        text=txt, parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(button)
    )


def college_notification_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    url = BASE_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_result = soup.find_all('div', attrs={'class': 'aidanews2_positions'})
    title = [item.h1.a.text for item in title_result]
    date_time_result = soup.find_all('span', attrs={'class': 'aidanews2_date'})
    date_time = [item.text for item in date_time_result]
    txt = ''
    for i in range(5, len(date_time)):
        txt += '{}📌'.format(i - 4) + title[i] + '\n\t' + date_time[i] + '\n'
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    button = [
        [InlineKeyboardButton('مشاهده همه ی اطلاعیه ها', 'http://ce.um.ac.ir/index.php?option=com_content&view=category'
                                                         '&id=113&Itemid=540&lang=fa')],
    ]
    update.message.reply_text(
        text=txt,
        reply_markup=InlineKeyboardMarkup(button)
    )


def college_teach_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='به زودی فایل های مربوطه در این بخش قرار خواهند '
                                                                    'گرفت،\n با تشکر🙏🏻 ')


def college_masters_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    #  buttons for linking DS videos to programming telegram channel
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    buttons = [
        [  # first row
            InlineKeyboardButton('دکتر ابریشمی', callback_data='abrishami'),
            InlineKeyboardButton('دکتر نوری بایگی', callback_data='noriBaigi'),
        ], [
            InlineKeyboardButton('سارا ارشادی نسب', callback_data='ershadi'),
            InlineKeyboardButton('دکتر صداقت', callback_data='sedaghat'),
        ], [
            InlineKeyboardButton('دکتر غیاثی شیرازی', callback_data='ghiasi'),
            InlineKeyboardButton('دکتر فضل ارثی', callback_data='fazlErsi'),
        ], [
            InlineKeyboardButton('دکتر بافقی', callback_data='bafghi'),
            InlineKeyboardButton('دکتر امین طوسی', callback_data='tosi'),
        ], [
            InlineKeyboardButton('دکتر پایدار', callback_data='paydar'),
            InlineKeyboardButton('دکتر هراتی', callback_data='harati'),
        ],
    ]
    update.message.reply_text(
        text='برای دریافت اطلاعات، استاد مورد نظر را انتخاب کنید:',
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def college_masters_keyboard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
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


def contact_handler(update, context):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    buttons = [
        [
            InlineKeyboardButton('telegram', 'https://telegram.me/soroush_fathi'),
            InlineKeyboardButton('instagram', 'https://instagram.com/soroushfathi.pb')
        ], [
            InlineKeyboardButton('LinkedIn', 'www.linkedin.com/in/soroush-fathi-45aa07201'),
        ]
    ]
    update.message.reply_text(text=messages['msg_contact'], reply_markup=InlineKeyboardMarkup(buttons))
    logging.info('{} {}({}): {}\n'.format(first_name, last_name, chat_id, update))


def help_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_help'])


def back_home_handler(update: Update, context: CallbackContext) -> None:
    main_menu_handler(update, context)


def back_college_handler(update: Update, context: CallbackContext) -> None:
    college_handler(update, context)


def src_fp_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='این بخش در حال بروزرسانی است، به زودی فایل های'
                                                                    ' مربوطه قرار خواهند گرفت')


def src_discrete_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='این بخش در حال بروزرسانی است، به زودی فایل های'
                                                                    ' مربوطه قرار خواهند گرفت')


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
    update.message.reply_text(text=messages['msg_sending_time'])
    try:
        with open('./sources/DS/DS & Algorithms by Weiss.pdf') as f:
            context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
            context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename='DS & Algorithm by Weiss',
                                      caption='منبع درس ساختمان داده', timeout=600)
    except error.NetworkError as e:
        update.message.reply_text(text=messages['msg_network_error'])
    logging.info('{} {}({}): {}\n'.format(first_name, last_name, chat_id, update))
    # with open('./sources/DS/The Art of Computer Programming (vol. 3_ Sorting and Searching) (2nd ed.) [Knuth '
    #           '1998-05-04].pdf') as f:
    #     context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    #     context.bot.send_document(chat_id=update.effective_chat.id, document=f,
    #                               filename='The Art of Computer Programming',
    #                               caption='منبع در ساختمان داده', timeout=300)


# Start exam file handlers
def exam_ap_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        with open('./exams/AP.zip', 'rb') as file:
            context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
            context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename='AP exams.zip',
                                      caption='سوالات امتحانی برنامه سازی پیشرفته دکتر پایدار', timeout=60)
    except error.NetworkError as e:
        update.message.reply_text(text=messages['msg_network_error'])


def exam_discrete_bafghi_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        with open('./exams/discrete_bafghi.zip', 'rb') as file:
            context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT, timeout=300)
            context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename='Discrete exams & exe '
                                                                                                '(Bafghi)',
                                      caption='تمرینات و امتحانات ریاضیات گسسته استاد بافقی', timeout=200)
    except error.NetworkError as e:
        update.message.reply_text(text=messages['msg_network_error'])


def exam_discrete_structure_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_sending_time'])
    try:
        with open('./exams/discrete_structure.zip', 'rb') as file:
            context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT, timeout=300)
            context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename='Discrete Structure',
                                      caption='تمرینات ساختمان داده', timeout=300)
    except error.NetworkError as e:
        update.message.reply_text(text=messages['msg_network_error'])


def exam_fp_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='این بخش در حال بروزرسانی است، به زودی فایل های'
                                                                    ' مربوطه قرار خواهند گرفت')


def exam_ds_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='این بخش در حال بروزرسانی است، به زودی فایل های'
                                                                    ' مربوطه قرار خواهند گرفت')


# TODO InlineQueryResultGif
# def inlinequery(update: Update, context: CallbackContext) -> None:
#     query = update.inline_query.query
#     result = [
#         InlineQueryResultGif(
#             type='gif',
#             id=str(uuid4()),
#             gif_url='https://t.me/c/1342044227/478459',
#             # gif_width=7,
#             # gif_height=10,
#             # gif_duration=3,
#             thumb_url='https://t.me/c/1342044227/478459',
#             thumb_mime_type='video/mp4',
#             title='nori',
#             input_message_content=InputTextMessageContent(query),
#         )
#     ]
#     update.inline_query.answer(result)


def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query

    if query == "":
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Title",
            input_message_content=InputTextMessageContent(query.title()),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Bold",
            input_message_content=InputTextMessageContent(
                f"*{escape_markdown(query)}*", parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Italic",
            input_message_content=InputTextMessageContent(
                # f"_{escape_markdown(query)}_", parse_mode=ParseMode.MARKDOWN
                '<i>{}</i>'.format(query), parse_mode=ParseMode.HTML
            ),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Poem",
            input_message_content=InputTextMessageContent('<pre>{}</pre>'.format(query), parse_mode=ParseMode.HTML),
        ),
    ]
    update.inline_query.answer(results)


def main() -> None:
    """Run the Bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token='1914222564:AAFl7vn1ESo3oT9_65IicNKEWntq5RFuJOc', use_context=True)
    # request_kwargs={'proxy_url': 'https://t.me/proxy?server=162.55.171.113&port=443&secret=EE00000'
    #                                                    '000000000000000000000000000646c2e676f6f676c652e636f6d'}
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('exams_ap', exam_ap_file_handler))

    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exams_exe']), exe_subject_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_advance_programming']), exam_ap_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_discrete_bafghi']),
                                          exam_discrete_bafghi_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_discrete_structure']),
                                          exam_discrete_structure_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_data_structure']), exam_ds_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_fundamental_programming']),
                                          exam_fp_file_handler))

    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_sources']), src_subject_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_src_data_structure']), src_ds_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_src_discrete']), src_discrete_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_src_advance_programming']), src_ap_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_src_fundamental_programming']),
                                          src_fp_file_handler))

    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college']), college_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_news']), college_news_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_notification']),
                                          college_notification_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_press']), college_press_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_press_latinArticle']),
                                          college_latinArticles_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_press_persianArticle']),
                                          college_persianArticles_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_press_books']),
                                          college_books_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_contact']), college_contact_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_about']), college_about_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_masters']), college_masters_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_teach']), college_teach_handler))
    dispatcher.add_handler(CallbackQueryHandler(college_masters_keyboard))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_back_college']), back_college_handler))

    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_back_home']), back_home_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_contact']), contact_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_help']), help_handler))

    dispatcher.add_handler(InlineQueryHandler(inlinequery))
    # dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
    # Start hte Bot
    updater.start_polling()
    updater.idle()


main()

# token = '1914222564:AAFl7vn1ESo3oT9_65IicNKEWntq5RFuJOc'
# base_url = 'https://api.telegram.org/bot{}/getMe'.format(token)
# print(base_url)
# resp = requests.get(base_url)
# print(resp.text)

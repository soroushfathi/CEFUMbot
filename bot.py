from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
from telegram.ext.filters import Filters
import logging
from telegram.chataction import ChatAction
from telegram import ReplyKeyboardMarkup
import requests

messages = {
    'msg_start': 'سلام {}، \n خوش امدی به ربات🙂، امیدوارم بتونم کمکت کنم🤠',
    'msg_contact': 'سروش فتحی هستم👨🏻‍💻، دانشجوی مهندسی کامپیوتر فردوسی ورودی 99🧑🏻‍🎓\n'
                   'telegram = @soroush_fathi\n'
                   'instagram = soroushfathi.pb\n',
    'msg_main_handler': 'منوی اصلی🗂️:',
    'msg_select_subject': 'درس مورد نظر را انتخاب کندید:',
    'msg_help': 'کار با ربات سادس، نیازی به راهنمایی نیست😆😌',

    'btn_masters': 'اساتید👨🏻‍🏫',
    'btn_exams_exe': 'تمرین و امتحانات📑',
    'btn_sources': 'منابع و جزوات📚',
    'btn_contact': '📞تماس با من👨🏻‍💻',
    'btn_help': 'راهنمایی✅',
    'btn_college': 'دانشکده🏨',

    'btn_exe_fundamental_programming': 'مبانی برنامه نویسی',
    'btn_exe_advance_programming': 'برنامه سازی پیشرفته',
    'btn_exe_discrete': 'ریاضیات گسسته',
    'btn_exe_data_structure': 'ساختمان داده',
    'btn_src_fundamental_programming': 'مبانی برنامه نویسی',
    'btn_src_advance_programming': 'برنامه سازی پیشرفته',
    'btn_src_discrete': 'ریاضیات گسسته',
    'btn_src_data_structure': 'ساختمان داده',
    'btn_back': 'بازگشت',
}


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


# def echo(update, context):
#     context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def main_menu_handler(update, context):
    buttons = [
        [messages['btn_exams_exe'], messages['btn_sources'], messages['btn_masters']],
        [messages['btn_contact'], messages['btn_help'], messages['btn_college']]
    ]
    update.message.reply_text(
        text=messages['msg_main_handler'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def exe_subject_handler(update, context):
    buttons = [
        [messages['btn_exe_fundamental_programming'], messages['btn_exe_advance_programming']],
        [messages['btn_exe_discrete'], messages['btn_exe_data_structure']],
        [messages['btn_back']]
    ]
    update.message.reply_text(
        text=messages['msg_select_subject'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def src_subject_handler(update, context):
    buttons = [
        [messages['btn_src_fundamental_programming'], messages['btn_src_advance_programming']],
        [messages['btn_src_discrete'], messages['btn_src_data_structure']],
        [messages['btn_back']]
    ]
    update.message.reply_text(
        text=messages['msg_select_subject'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def contact_handler(update, context):
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_contact'])


def help_handler(update, context):
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_help'])


def back_handler(update, context):
    main_menu_handler(update, context)


def exam_ap_file_handler(update, context):
    chat_id = update.message.chat_id
    with open('./exams/AP.zip', 'rb') as file:
        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
        context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename='AP exams.zip',
                                  caption='سوالات امتحانی برنامه سازی پیشرفته دکتر پایدار', timeout=30)


def src_ds_file_handler(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=update.effective_chat.id, text='منبع ویدئویی(مدرس : سعید شهریوری):\n'
                                                                    'https://t.me/Azad_Developers/17205\n')
    with open('./sources/DS/DS & Algorithms by Weiss.pdf') as f:
        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
        context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename='DS & Algorithm by Weiss',
                                  caption='منبع درس ساختمان داده', timeout=600)
    with open('./sources/DS/The Art of Computer Programming (vol. 3_ Sorting and Searching) (2nd ed.) [Knuth '
              '1998-05-04].pdf') as f:
        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
        context.bot.send_document(chat_id=update.effective_chat.id, document=f,
                                  filename='The Art of Computer Programming',
                                  caption='منبع در ساختمان داده', timeout=6000)


def exam_discrete_file_handler(update, context):
    chat_id = update.message.chat_id
    with open('./exams/Discrete Mathematics.zip', 'rb') as file:
        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT, timeout=30)
        context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename='Discrete exams & exe',
                                  caption='تمرینات و امتحانات ریاضیات گسسته', timeout=600)


def main():
    updater = Updater(token='1914222564:AAFl7vn1ESo3oT9_65IicNKEWntq5RFuJOc', use_context=True)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('exams_ap', exam_ap_file_handler))
    # dispatcher.add_handler(CommandHandler('menu', main_menu_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exams_exe']), exe_subject_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_advance_programming']), exam_ap_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_discrete']), exam_discrete_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_sources']), src_subject_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_src_data_structure']), src_ds_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_back']), back_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_contact']), contact_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_help']), help_handler))
    # dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
    updater.start_polling()
    updater.idle()


main()

# token = '1914222564:AAFl7vn1ESo3oT9_65IicNKEWntq5RFuJOc'
# base_url = 'https://api.telegram.org/bot{}/getMe'.format(token)
# print(base_url)
# resp = requests.get(base_url)
# print(resp.text)

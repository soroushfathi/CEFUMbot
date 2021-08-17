from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import logging
from telegram.chataction import ChatAction
from telegram import Update
import requests

messages = {
    'msg_start': 'سلام {}، \n خوش امدی به ربات، امیدوارم بتونم کمکت کنم'
}


def start(update, context):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    # print(user)
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    update.message.reply_text(text='Here is CE FUM bot')
    context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_start'].format(first_name))


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def main():
    updater = Updater(token='1914222564:AAFl7vn1ESo3oT9_65IicNKEWntq5RFuJOc', use_context=True)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)
    updater.start_polling()
    updater.idle()


main()

# token = '1914222564:AAFl7vn1ESo3oT9_65IicNKEWntq5RFuJOc'
# base_url = 'https://api.telegram.org/bot{}/getMe'.format(token)
# print(base_url)
# resp = requests.get(base_url)
# print(resp.text)

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import requests
import json
import linkGrabber
import re
from collections import defaultdict
import time
import schedule

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.


def get_quote(category):
    url = "http://quotes.rest/qod.json"
    querystring = {"category": category}

    headers = {'Cache-Control': "no-cache",
        'Postman-Token': "9c43e1ac-8c80-4fda-85f3-eb66d514c502"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    response_text = response.json()
    quote_of_day = response_text['contents']['quotes'][0]['quote']
    quote_author = response_text['contents']['quotes'][0]['author']
    return "{}\n{}".format(quote_of_day, quote_author)


class code_search(object):
    def __init__(self, repo):
        self.repository = repo

    def get_urls(self):
        page = linkGrabber.Links(self.repository)
        links = page.find(href=re.compile("/blob/master/"), limit=None, duplicates=False)

        links_list = []
        for raw_link in links:
            if raw_link['href'].find('.ipynb') != -1:
                link = 'https://github.com' + raw_link['href'] + '?raw=true'
                links_list.append(link)
        return links_list

    @staticmethod
    def get_content(links_list):
        contents_list = []
        for url in links_list:
            contents = requests.get(url).json()
            contents_list.append(contents)
        return contents_list

    @staticmethod
    def search_key_words(contents_list, search_value):
        search_value = search_value.replace(" ", "")
        results_list = []

        for contents in contents_list:
            for i in range(len(contents['cells'])):
                if contents['cells'][i]['cell_type'] == 'code':
                    if [s for s in contents['cells'][i]['source'] if search_value in s.replace(" ", "")]:
                        content_text = ''.join(contents['cells'][i - 1]['source'])
                        content_code = ''.join(contents['cells'][i]['source'])
                        results_list.append([0, content_text])
                        results_list.append([1, content_code])

        return results_list

    @staticmethod
    def split_results_list(results_list):
        fixed_len = 1000
        split_dict = defaultdict()
        split_dict[0] = ''
        key = 0

        range_list = list(range(len(results_list)))  # list to iterate though the result list

        for i in range_list:
            cell = results_list[i]
            content = split_dict[key]

            space_left = fixed_len - len(split_dict[key])
            if space_left < 0:
                space_left = 0

            if space_left >= len(cell[1]):
                if cell[0] == 1:  # check if the text is code
                    split_dict[key] = content + ''.join(' ```\n{}\n``` '.format(cell[1]))
                else:
                    split_dict[key] = content + cell[1]

            elif space_left > 0:  # cut the string
                split_string = cell[1][:space_left]
                cell[1] = cell[1][space_left:]

                if cell[0] == 1:  # check if the text is code
                    split_dict[key] = content + ''.join(' ```\n{}\n``` '.format(split_string))
                else:
                    split_dict[key] = content + cell[1]

                range_list.insert(i, i)  # add the current cell to check in the next iteration

            else:
                key = key + 1  # start a new loop in the split dict
                split_dict[key] = ''
                range_list.insert(i, i)  # add the current cell to check in the next iteration

        return split_dict

def start(bot, update):
    update.message.reply_text("Hello! I am a code search bot! I will help you find code snippets."
                              + "\nSimply type in what you are looking for 😊"
                              +  "\n or greet me and I will inspire you!")

def handle_message(bot, update):
    global split, reply_markup, keyboards
    split = {1: 'code sample'}
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("sample", callback_data='sample')]])
    keyboards = []

    update_text = update.message.text

    # check for greetings
    if update_text not in greetings:
        # search code if not a greeting
        result = class_code_search.search_key_words(contents, update_text)
        if len(result) == 0:
            update.message.reply_text('Nothing found :( ')

        else:
            split = class_code_search.split_results_list(result)
            reply_count = len(split)
        #    try:
            if reply_count < 8:
                keyboards = []
                temp = []
                for page in split.keys():
                    keyboard = InlineKeyboardButton("{}".format(page), callback_data=page)
                    temp.append(keyboard)
                keyboards.append(temp)
                reply_markup = InlineKeyboardMarkup(keyboards)
                update.message.reply_text(split[0], reply_markup=reply_markup, parse_mode = 'Markdown')

            else:
                keyboards = []
                temp = []
                for page in split.keys():
                    keyboard = InlineKeyboardButton("{}".format(page), callback_data=page)
                    temp.append(keyboard)
                keyboards.append(temp)
                page_iterator = [InlineKeyboardButton("<<", callback_data='previous'), InlineKeyboardButton(">>", callback_data='next')]
                keyboards.append(page_iterator)
                reply_markup = InlineKeyboardMarkup(keyboards)
                update.message.reply_text(split[0], reply_markup=reply_markup, parse_mode = 'Markdown')
         #   except:
          #      update.message.reply_text('There was a conflicting markdown error :(')
    else:
        update.message.reply_text(quote)

def send_next_page(bot, update):
    global current_page
    query = update.callback_query
    iter = 8

    if query.data == 'next':
        max_len = len(keyboards[0])

        # check max length of pages
        if -(-max_len // iter) <= current_page +1:
            keyboards_pager = keyboards[1]
            keyboards_new = [keyboards_pager]
            reply_markup_new = InlineKeyboardMarkup(keyboards_new)
            bot.editMessageReplyMarkup(chat_id=query.message.chat_id,
                                       message_id=query.message.message_id,
                                       reply_markup=reply_markup_new)

        else:
            current_page = current_page + 1

            start = current_page * iter
            keyboards_split_content = keyboards[0][start:]
            keyboards_pager = keyboards[1]
            keyboards_new = [keyboards_split_content, keyboards_pager]
            reply_markup_new = InlineKeyboardMarkup(keyboards_new)
            bot.editMessageReplyMarkup(chat_id=query.message.chat_id,
                                message_id=query.message.message_id,
                                reply_markup=reply_markup_new)

    elif query.data == 'previous':
        current_page = current_page - 1

        start = current_page * iter
        if current_page < 0:
            start = 0

        keyboards_split_content = keyboards[0][start:]
        keyboards_pager = keyboards[1]
        keyboards_new = [keyboards_split_content, keyboards_pager]
        reply_markup_new = InlineKeyboardMarkup(keyboards_new)

        bot.editMessageReplyMarkup(chat_id=query.message.chat_id,
                            message_id=query.message.message_id,
                            reply_markup=reply_markup_new)

    else:
        start = current_page * iter

        keyboards_split_content = keyboards[0][start:]
        keyboards_pager = keyboards[1]
        keyboards_new = [keyboards_split_content, keyboards_pager]
        reply_markup_new = InlineKeyboardMarkup(keyboards_new)

        bot.sendMessage(text=split[int(query.data)],
                              chat_id=query.message.chat_id,
                              reply_markup=reply_markup_new,
                              parse_mode='Markdown')

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('If the bot does not respond to the messages - possibly' +
                              'it is a flooding control imposed by Telegram servers.' +
                              'Please wait 5-10 minutes to start using the bot.')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def update_data(t):
    global quote, contents
    quote = get_quote('inspire')
    url_list = class_code_search.get_urls()
    contents = class_code_search.get_content(url_list)

    print("Data updated ", t)


def main():
    global token, repository, greetings, quote, contents, class_code_search, current_page

    greetings = ('hello', 'hi', 'greetings', 'sup', 'hey', 'yo', 'code', 'pandas')
    repository = 'https://github.com/nurcity/Coding'

    current_page = 0
    current_page_dict = defaultdict()


    quote = get_quote('inspire')


    # initialize code search class
    class_code_search = code_search(repository)
    url_list = class_code_search.get_urls()
    contents = class_code_search.get_content(url_list)

    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # handle messages
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    updater.dispatcher.add_handler(CallbackQueryHandler(send_next_page))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    # update quote and content data
    schedule.every().day.at("19:00").do(update_data, 'It is 7pm')
    while True:
        schedule.run_pending()
        time.sleep(60)  # wait one minute

if __name__ == '__main__':
    main()
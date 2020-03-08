import configparser
import logging
import sys
from datetime import datetime

import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from logging_handler import logInline

import Admin as ad
from PortfolioUpdate import generate_email, compute, getPrice, computeOneStock, netWorth
from const import START_TEXT, HELP_TEXT, CONTACT_INFO_TEXT, PLEASE_TRY_AGAIN

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')


# ------------------------------------Private Function-------------
# Result format:

# [['AMZN', 5, 1895.85, 1938.27, '+1.53%', 212.1],
#  ['BLK', 10, 538.505, 484.25, '+1.21%', -542.55],
#  ['TWTR', 280, 36.2, 35.11, '+0.52%', -305.2],
#  ['C', 50, 79.8, 64.56, '-0.75%', -762.0],
#  ['Total', '', 28990.3, '', '', -1397.65]]

@run_async
def unknown(update, context):
    send_plain_text(update, context, "Sorry, I didn't understand that command.\nRun /help to see available options")


def validateStock(update, context, ticker):
    if ticker not in ad.getSymbolDict():
        send_plain_text(update, context, "Your stock is currently not supported! \n"
                                         "Email admin to have it added")
        return False
    return True


# -------------------------------------------------------
# INPUT VALIDATION

@run_async
@logInline
def add(update, context):
    try:
        user = ad.getUser(update.effective_chat.id)
        stock_symbol = context.args[0].upper()
        qty = float(context.args[1])
        paid = float(context.args[2])
        if validateStock(update, context, stock_symbol):
            stock = [stock_symbol, qty, paid]
            user.addStock(stock)
            send_plain_text(update, context,
                            "Added {} \nSymbol: {} \nQty: {} \nPrice: {}".format(ad.getSymbolDict()[stock[0]],
                                                                                    stock[0],
                                                                                    stock[1], stock[2]))
    except:
        send_plain_text(update, context, PLEASE_TRY_AGAIN)


@run_async
@logInline
def remove(update, context):
    chat_id = update.effective_chat.id
    user_portfolio = ad.getUserPortfolio(chat_id)
    try:
        stock_symbol = context.args[0].upper()
    except:
        send_plain_text(update, context, "Seems like you forgot stock symbol!")
        return
    if not validateStock(update, context, stock_symbol):
        return
    try:
        profit = computeOneStock(stock_symbol, user_portfolio)
        del user_portfolio[stock_symbol]
        msg = "Remove {} from your portfolio".format(ad.getSymbolDict()[stock_symbol])
        send_plain_text(update, context, msg)
        send_plain_text(update, context, "Profit and Loss for this stock: {}".format(profit))
        send_plain_text(update, context, "Here is your updated portfolio: {}".format(str(user_portfolio)))
    except KeyError:
        msg = "This stock is not in your portfolio, please check again!"
        send_plain_text(update, context, msg)


@run_async
@logInline
def my_portfolio(update, context):
    chat_id = update.effective_chat.id
    user = ad.getUser(chat_id)
    msg = "{} \nQty {} \nPurchased price {} \nTotal paid: {}"
    if not user.my_portfolio:
        send_plain_text(update, context, "Your portfolio is empty. /add now")
        return
    for k, v in user.my_portfolio.items():
        paid = round(float(v[0]) * float(v[1]), 2)
        send_plain_text(update, context, msg.format(k, v[0], v[1], paid))


@run_async
@logInline
def clear_all_stock(update, context):
    user = ad.getUser(update.effective_chat.id)
    user.my_portfolio = {}
    send_plain_text(update, context, "Cleared all stocks")


def start(update, context):
    ad.addUser(update.effective_chat.id, update.effective_user)
    send_html_text(update, context, START_TEXT.format(update.effective_user.full_name))


def send_plain_text(update, context, text):
    context.bot.send_message(update.effective_chat.id, text=text)


def send_html_text(update, context, text):
    context.bot.send_message(update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


@run_async
@logInline
def dog(update, context):
    url = get_url()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=url)


@run_async
@logInline
def profit_loss(update, context):
    data = compute(ad.getUserPortfolio(update.effective_chat.id))
    msg = ""
    try:
        stock_symbol = context.args[0].upper()
        if validateStock(update, context, stock_symbol):
            for s in data[:-1]:
                if s[0] == stock_symbol:
                    msg += "{} \nQty {} \nPaid {} \n" \
                       "Curr. Price {} \nToday Chg {}\nPL {} \n\n".format(s[0], s[1], s[2], s[3], s[4], s[5])
                break
    except:
        for s in data[:-1]:
            msg += "{} \nQty {} \nPaid {} \n" \
                   "Curr. Price {} \nToday Chg {}\nPL {} \n\n".format(s[0], s[1], s[2], s[3], s[4], s[5])
        msg += "Initial Capital: {} \nPL {} \n\n".format(data[-1][2], data[-1][5])
    finally:
        send_plain_text(update, context, msg)


@run_async
@logInline
def current_net_worth(update, context):
    try:
        total = netWorth(ad.getUserPortfolio(update.effective_chat.id))
        if not ad.getUserPortfolio(update.effective_chat.id):
            send_plain_text(update, context, "Your portfolio is empty. /add now")
            return
        send_plain_text(update, context, "My current net worth as of {} is {}".format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), total))
    except:
        send_plain_text(update, context, PLEASE_TRY_AGAIN)


@run_async
@logInline
def price(update, context):
    try:
        stock_symbol = context.args[0].upper()
        if validateStock(update, context, stock_symbol):
            send_plain_text(update, context,
                            "{} \nPrice: {}".format(ad.getSymbolDict().get(stock_symbol), getPrice(stock_symbol)))
    except:
        send_plain_text(update, context, "Input any stock to get the latest price!")


@run_async
@logInline
def email(update, context):
    # my_portfolio = {'AMZN': [5,1895.85], 'BLK': [10, 538.505],'TWTR': [280, 36.2], 'C':[50, 79.8]}
    user = ad.getUser(update.effective_chat.id)
    email_address = context.args[0]
    try:
        generate_email(user.my_portfolio, email_address)
        send_plain_text(update, context, "Email Sent")
    except:
        send_plain_text(update, context, PLEASE_TRY_AGAIN)


@run_async
@logInline
def _help(update, context):
    send_html_text(update, context, HELP_TEXT)


@logInline
def contact_us(update, context):
    send_html_text(update, context, CONTACT_INFO_TEXT)


@logInline
def contact(update, context):
    msg = ' '.join(context.args)
    msg_edited = "chat_id {} \nmsg: {}".format(update.effective_chat.id, msg)
    dev_team = ad.getDevTeam()
    for dev in dev_team:
        context.bot.send_message(dev, text=msg_edited)
    send_plain_text(update, context, "We have received your message, we will respond in a short while!")


def error_handler(update, context):
    send_plain_text(update, context, str("Something is missing! Please try again"))
    logger.error(" Error in Telegram Module has Occurred:", exc_info=True)


def main():
    ad.startAdmin()
    updater = Updater(config['telegram']['token'], use_context=True)
    dp = updater.dispatcher

    commands = [
        ["me", my_portfolio],
        ["start", start],
        ["add", add],
        ["remove", remove],
        ["price", price],
        ["profit", profit_loss],
        ["current_net_worth", current_net_worth],
        ["clear_all_stock", clear_all_stock],
        ["email", email],
        ["help", _help],
        ["dog", dog],
        ["contactus", contact_us],
        ["contact", contact],
    ]
    for command, function in commands:
        updater.dispatcher.add_handler(CommandHandler(command, function))

    dp.add_handler(MessageHandler(Filters.command, unknown))
    dp.add_handler(MessageHandler(Filters.text, unknown))

    dp.add_error_handler(error_handler)
    updater.start_polling(poll_interval=1.0, timeout=20)
    updater.idle()


if __name__ == '__main__':
    logger.info("Starting Bot")
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Terminated using Ctrl + C")
    ad.stopAdmin()
    logger.info("Exiting Bot")
    sys.exit()

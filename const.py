START_TEXT = """
Hello <b>{}</b>, Welcome to your personal Portfolio Assistant!

My name is Buffolio. I am here to assist you.
 
My job is to track your portfolio profit and loss based on current market price (from Yahoo Finance)! But I can also show you a random picture of cute dogs.

Click help to begin: 
/help
"""

HELP_TEXT = """--<i>Here is a list of commands</i>--

/me
View your own Portfolio.

/add <i>[Stock_symbol]</i> <i>[Quantity]</i> <i>[Purchased_Price]</i>
Bought 10 stocks at $2000. 
Eg: /add AMZN 10 2000
Sold 2 stocks at $1950.
Eg: /add AMZN -2 1950

/remove <i>[Stock_symbol]</i>
Remove the stock out of the Portfolio. 
Eg: /remove AMZN

/price <i>[Stock_symbol]</i>
Getting current market price for this stock

/profit
Compute Profit and Loss

/current_net_worth
Total market value

/email <i>[Your Email]</i>
Email yourself the updated Profit and Loss. 
Eg: /email abc@gmail.com

/help
Display this list again.

/dog
Get random <b>CUTE</b> dog pic. 
Release your stress

/clear_all_stock
<b>BEWARE</b> this command will clear all your stocks, restart your portfolio

/contactus
Display admin contact information.
"""

CONTACT_INFO_TEXT = """
Email: buffalo.bot@gmail.com
OR
/contact <i>[Your Message]</i>
Send us short query directly on Telegram
"""

PLEASE_TRY_AGAIN = """
Something's missing, please try again!
"""
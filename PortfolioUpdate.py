import re
import smtplib
import ssl
import time
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup


def sendEmail(row_body, email_address):
    sender_email = "buffolio.bot@gmail.com"
    receiver_email = email_address

    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Portfolio Report"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    # text = """\
    # PORFOLIO:
    # {table}

    # """

    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <style type="text/css">
          table {
            background: white;
            border-radius:3px;
            border-collapse: collapse;
            height: auto;
            max-width: 900px;
            padding:5px;
            width: 100%;
            animation: float 5s infinite;
          }
          th {
            color:#FFF8F4;
            background:#E7717D;
            border: solid 1px #656565;
            font-size:14px;
            font-weight: 600;
            padding:10px;
            text-align:center;
            vertical-align:middle;
          }
          tr {
            border: solid 1px #656565;
            color:black;
            font-size:16px;
            font-weight:normal;
          }
          tr:hover td {
            background:#4E5066;
            color:#FFFFFF;
            border-top: 1px solid #22262e;
          }
          td {
            background:#F8F6F7;
            padding:10px;
            text-align:left;
            vertical-align:middle;
            font-weight:300;
            font-size:13px;
            border-right: 1px solid #C1C3D1;
          }
        </style>
      </head>
      <body>
        <br> <br>
        My Portfolio Report<br><br>
        <table>
          <thead>
            <tr style="border: 1px solid #1b1e24;">
              <th>Stock</th>
              <th>Q.ty</th>
              <th>Paid</th>
              <th>Curr. Price</th>
              <th>Daily Chg</th>
              <th>Profit/Loss</th>
            </tr>
          </thead>
          <tbody>
          """

    #     row = """
    #             <tr>
    #               <td>AMZN</td>
    #               <td>100</td>
    #               <td>3</td>
    #               <td>4</td>
    #               <td>5</td>
    #               <td>6</td>
    #             </tr>
    #         """

    end = """
          </tbody>
        </table>
        <br>
        Share this bot: https://t.me/Buffolio_Bot
        <br>
        Thank you!
      </body>
    </html>
    """

    # text = text.format(table=tabulate(data))

    # Turn these into plain/html MIMEText objects
    # part1 = MIMEText(text, "plain")
    part2 = MIMEText(html + row_body + end, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    # message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )


def getSubStringBetweenMarket(s):
    pattern = "\((.*?)\)"
    substring = re.search(pattern, s).group(1)
    return substring


def cache(f):
    class cache(dict):
        def __init__(self, f):
            self.f = f

        def __call__(self, key):
            price, daily_change, last_updated = self[key]
            if time.mktime(time.gmtime()) - last_updated >= 1 * 60:
                self.call_f(key)
            return self[key][:2]

        def __missing__(self, key):
            return self.call_f(key)

        def call_f(self, key):
            ret = self[key] = self.f(key) + [time.mktime(time.gmtime())]
            return ret

    return cache(f)


@cache
def getPrice(t):
    url = "https://sg.finance.yahoo.com/quote/{ticket}?p={ticket}".format(ticket=t)
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    price = float((soup.find('span', {'data-reactid': '14'}).string).replace(',', ''))
    dailyChange = getSubStringBetweenMarket((soup.find('span', {'data-reactid': '16'}).string))
    return [price, dailyChange]


def netWorth(my_portfolio):
    total = 0
    for k in my_portfolio.keys():
        price = getPrice(k)
        total += price[0]*my_portfolio[k][0]
    return round(total, 2)


def compute(portfolio):
    # my_portfolio = {stock: [qty, paid,curr price, daily change, profit/loss]}
    my_portfolio = portfolio.copy()
    total = 0
    total_paid = 0
    for k in my_portfolio.keys():
        price = getPrice(k)
        pl_value = (price[0] - my_portfolio[k][1]) * my_portfolio[k][0]
        total_paid += my_portfolio[k][1] * my_portfolio[k][0]
        pl = float("%.2f" % round(pl_value, 2))
        total += pl
        price.append(pl)
        my_portfolio[k] = my_portfolio[k] + (price)
    result = []
    for k in my_portfolio.keys():
        result.append([k] + my_portfolio[k])
    result.append(['Total', '', float("%.2f" % round(total_paid, 2)), '', '', float("%.2f" % round(total, 2))])
    return (result)


def computeOneStock(stock_symbol, my_portfolio):
    price = getPrice(stock_symbol)
    pl_value = (price[0] - my_portfolio[stock_symbol][1]) * my_portfolio[stock_symbol][0]
    return float("%.2f" % round(pl_value, 2))


def generateRow(data):
    row = """
        <tr>
          <td><b>{ticket}</b></td>
          <td>{Qty}</td>
          <td>{Paid}</td>
          <td>{CurrPrice}</td>
          <td>{DailyChg}</td>
          <td>{pl}</td>
        </tr>
    """
    list_of_row = ''
    for r in data:
        list_of_row += row.format(ticket=r[0], Qty=r[1], Paid=r[2], CurrPrice=r[3], DailyChg=r[4], pl=r[5])

    return (list_of_row)


def generate_email(my_portfolio, email_address):
    data = compute(my_portfolio)
    row_body = generateRow(data)
    sendEmail(row_body, email_address)

import csv
import pickle
from datetime import datetime

from User import User

user_dict = {}
symbol_dict = {}

dev_team = []


def log(message):
    print("********************************")
    print("{} : {}".format(datetime.today(), message))
    print("********************************")


def getUserDict():
    return user_dict


def getDevTeam():
    return dev_team


def addDevTeam(admin):
    dev_team.append(str(admin))


def loadDevTeam():
    with open("./db/dev_team.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            dev_team.append(str(row[0]))


def saveDevTeam():
    with open("./db/dev_team.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for v in dev_team:
            writer.writerow([v])
    return True


def addStockSymbol(stock):
    symbol_dict[stock[0]] = stock[1]


# INPUT: ["TWTR", "Twitter", "Tech"]
def saveSymbolCSV(filename):
    with open("./db/" + filename + ".csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for k, v in symbol_dict.items():
            writer.writerow([k, v])
    return True


def loadSymbolCSV(filename):
    with open("./db/" + filename + ".csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            symbol_dict[row[0]] = row[1]


def saveUserDict(filename):
    global user_dict
    with open("./db/" + filename + ".pickle", 'wb') as handle:
        pickle.dump(user_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open("./db/" + filename + ".csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for k in user_dict.keys():
            user = user_dict[k]
            writer.writerow([user.chat_id, user.is_bot, user.full_name])


def loadUserDict(filename):
    global user_dict
    try:
        with open("./db/" + filename + '.pickle', 'rb') as handle:
            user_dict = pickle.load(handle)
    except IOError:
        log("User Dict data is not found, initialize to empty")


def getAllUser():
    result = ""
    for k, v in user_dict.items():
        result += v.getUser()
    return result


def getNumberOfUser(chat_id):
    return len(user_dict.keys())


def addUser(chat_id, effective_user):
    if chat_id in user_dict:
        user = user_dict.get(chat_id)
    else:
        user = User(chat_id)
    user.full_name = effective_user.full_name
    user.is_bot = effective_user.is_bot
    user.username = effective_user.username
    user.first_name = effective_user.first_name
    user.last_name = effective_user.last_name
    return user_dict.setdefault(chat_id, user)


def getUser(chat_id):
    user = user_dict.setdefault(chat_id, User(chat_id))
    return user


def getUserPortfolio(chat_id):
    return user_dict[chat_id].my_portfolio


def getSymbolDict():
    return symbol_dict


def startAdmin():
    log("Loading all App Data")
    loadSymbolCSV("constituents_csv")
    loadUserDict("userData")
    loadDevTeam()


def stopAdmin():
    log("Saving all App Data")
    saveSymbolCSV("constituents_csv")
    saveUserDict("userData")
    saveDevTeam()

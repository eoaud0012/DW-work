import telegram

chat_token = "6041435620:AAH-C98ovxjuHmKOFbDM7z-Y8lI88YK1UT4"
bot_id = "6055095538"


bot = telegram.Bot(token=chat_token)

def id_check():
    chat = telegram.Bot(token=chat_token)
    updates = chat.getUpdates()
    for u in updates:
        print(u.message['chat']['id'])

def send_msg():
    bot = telegram.Bot(token = chat_token)
    text = ""
    bot.sendMessage(chat_id = bot_id, text = text)

if __name__ == "__main__":
    id_check()


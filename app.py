import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN", "8140600221:AAFvotre_token_ici")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Salut Wright ! BOT EMPLOI CONGO 24h/24 en ligne ! Tape /offres")

@bot.message_handler(commands=['offres'])
def offres(m):
    bot.reply_to(m, "ACPE: 12 offres\nUnicongo: 5 offres\nTotal: 3 offres\nTape /payer")

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

@app.route("/")
def webhook_check():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{request.host}/{TOKEN}")
    return "Bot Wright 24h/24 OK !", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

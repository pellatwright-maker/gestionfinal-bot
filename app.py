import os
from flask import Flask, request
import telebot
import json
from datetime import datetime, timedelta

# === CONFIGURATION WRIGHT ===
JETON = os.environ.get("BOT_TOKEN", "8140xxxx")
NUMERO_MOBILE_MONEY = "066015932"
NOM_MOBILE_MONEY = "Wright"
PRIX_MOIS = 3000

bot = telebot.TeleBot(JETON)
app = Flask(__name__)

FICHIER_ABONNES = "/tmp/abonnes.json"
try:
    with open(FICHIER_ABONNES, "r") as f:
        ABONNES = json.load(f)
except:
    ABONNES = {}

ADMIN_ID = 0
MAILS_ANALYSES = 1614

def sauvegarder():
    try:
        with open(FICHIER_ABONNES, "w") as f:
            json.dump(ABONNES, f)
    except:
        pass

def est_abonne(user_id):
    user_id = str(user_id)
    if user_id not in ABONNES:
        return False
    fin = datetime.fromisoformat(ABONNES[user_id]["fin"])
    return fin > datetime.now()

@bot.message_handler(commands=['start'])
def commencer(m):
    global ADMIN_ID
    if ADMIN_ID == 0:
        ADMIN_ID = m.from_user.id
    bot.reply_to(m, f"Salut {m.from_user.first_name} ! 👋\n\n"
                    f"🔥 BOT EMPLOI CONGO - @Gestionfinal_bot\n"
                    f"Scan AGL, ACPE, Unicongo, Total, Bolloré\n"
                    f"Mails analysés: {MAILS_ANALYSES}\n\n"
                    f"Commandes:\n"
                    f"/search agl - Chercher une offre\n"
                    f"/offres - Voir les dernières offres\n"
                    f"/abonnement - S'abonner 3000F/mois\n"
                    f"/stats - Tableau de bord\n\n"
                    f"24h/24 OK !")

@bot.message_handler(commands=['search'])
def chercher(m):
    mot = m.text.split(" ",1)[1] if " " in m.text else ""
    if not mot:
        bot.reply_to(m, "Tape: /search agl ou /search bollore")
        return
    bot.reply_to(m, f"🔍 Recherche: {mot}\n\n

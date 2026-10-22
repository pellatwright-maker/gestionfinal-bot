import os
from flask import Flask, request
import telebot
from datetime import datetime

JETON = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(JETON, threaded=False)
app = Flask(__name__)

WA_1 = "https://whatsapp.com/channel/0029VaxSPRCJENxy7Nhq5s2Y"
WA_2 = "https://whatsapp.com/channel/0029Vb5pc270VycKAb1tc631"
WA_3 = "https://whatsapp.com/channel/0029Vb5zwt61noz9BxMaAz2g"
WA_4 = "https://whatsapp.com/channel/0029VazAVen90x2zI4HS5A2Z"

SITES_NATIONAUX = {
    "ACPE (officiel)": "https://www.acpe.cg",
    "Emploi.cg": "https://www.emploi.cg",
    "Unicongo": "https://www.unicongo.org",
    "Fonction Publique": "https://fonction-publique.gouv.cg",
    "AGL Congo": "https://www.aglgroup.com - Careers Congo",
    "TotalEnergies Congo": "https://jobs.totalenergies.com"
}

OFFRES_CACHE = {
    "ACPE": ["Spécialiste fret FLNG - Pointe-Noire", "Chef HSE - ENI Congo", "12 offres sur acpe.cg"],
    "AGL": ["Responsable Logistique - AGL Pointe-Noire", "Assistant RH Brazzaville"],
    "UNICOGO": ["Comptable Brazzaville - Unicongo", "Commercial Unicongo"],
    "TOTAL": ["Technicien TotalEnergies Pointe-Noire"]
}

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, f"🇨🇬 BOT EMPLOI CONGO V42 🇨🇬\nSalut {m.from_user.first_name} !\n\n/sites - Sites nationaux\n/whatsapp - 4 chaînes WhatsApp\n/search agl\n/offres\n\nGratuit H24\n\nChaîne 1: {WA_1}", parse_mode="Markdown")

@bot.message_handler(commands=['sites'])
def sites(m):
    txt = "🇨🇬 SITES NATIONAUX\n\n"
    for k,v in SITES_NATIONAUX.items():
        txt += f"*{k}:* {v}\n\n"
    bot.reply_to(m, txt, parse_mode="Markdown")

@bot.message_handler(commands=['whatsapp','wa','chaines'])
def whatsapp(m):
    txt = f"📲 MES 4 CHAINES WHATSAPP\n\n1️⃣ {WA_1}\n\n2️⃣ {WA_2}\n\n3️⃣ {WA_3}\n\n4️⃣ {WA_4}\n\nClique -> S'abonner"
    bot.reply_to(m, txt, parse_mode="Markdown")

@bot.message_handler(commands=['search'])
def search(m):
    mot = m.text.split(" ",1)[1].lower() if len(m.text.split())>1 else ""
    if not mot:
        bot.reply_to(m, "Ex: /search agl")
        return
    res = f"🔍 {mot.upper()}\n\n"
    for k,v in OFFRES_CACHE.items():
        if mot in k.lower() or any(mot in o.lower() for o in v):
            res += f"*{k}:*\n" + "\n".join([f"• {o}" for o in v]) + "\n\n"
    for k,v in SITES_NATIONAUX.items():
        if mot in k.lower():
            res += f"🌐 {k}: {v}\n\n"
    res += "\n📲 /whatsapp"
    bot.reply_to(m, res, parse_mode="Markdown")

@bot.message_handler(commands=['offres'])
def offres(m):
    txt = "📋 OFFRES DU JOUR\n\n"
    for k,v in OFFRES_CACHE.items():
        txt += f"*{k}:* {', '.join(v[:2])}\n\n"
    bot.reply_to(m, txt, parse_mode="Markdown")

@app.route('/' + JETON, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok",200

@app.route("/")
def home():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{request.host}/"+JETON)
    return f"V42 4 Chaines OK {datetime.now()}",200

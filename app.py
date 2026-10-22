import os
from flask import Flask, request, jsonify
import telebot
from datetime import datetime
import json
import requests

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

FICHIER_OFFRES = "offres.json"
TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "@Gestionfinal_bot")

def detect_categorie(texte):
    t = texte.lower()
    if any(m in t for m in ["secrétaire", "comptable", "assistant", "gestion", "admin", "rh"]):
        return "Administration"
    if any(m in t for m in ["chauffeur", "livreur", "logistique"]):
        return "Logistique"
    if any(m in t for m in ["commercial", "vente", "marketing"]):
        return "Commerce"
    if any(m in t for m in ["informatique", "developpeur"]):
        return "Informatique"
    return "Autres"

def save_offre_auto(texte, categorie="Autres"):
    # Sauvegarde json
    try:
        offres = []
        if os.path.exists(FICHIER_OFFRES):
            with open(FICHIER_OFFRES, "r", encoding="utf-8") as f:
                offres = json.load(f)
        offres.insert(0, {"texte": texte, "categorie": categorie, "date": datetime.now().isoformat()})
        with open(FICHIER_OFFRES, "w", encoding="utf-8") as f:
            json.dump(offres[:300], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erreur save json: {e}")

    # Envoie direct dans ton canal Telegram
    try:
        msg = f"🔥 *{categorie}* - Offre WhatsApp\n\n{texte}\n\n🇨🇬 _Auto via 056608621_"
        bot.send_message(TELEGRAM_CHANNEL, msg, parse_mode="Markdown")
        print(f"✅ Offre WhatsApp envoyée sur {TELEGRAM_CHANNEL}")
    except Exception as e:
        print(f"Erreur envoi Telegram: {e}")

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, f"🇨🇬 BOT EMPLOI CONGO V43 🇨🇬\nSalut {m.from_user.first_name} !\n\n/sites - Sites nationaux\n/whatsapp - 4 chaînes WhatsApp\n/search agl\n/offres\n\nGratuit H24 - Connecté à WhatsApp 056608621\n\nChaîne 1: {WA_1}", parse_mode="Markdown")

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
    # Ajoute les dernières offres WhatsApp
    if os.path.exists(FICHIER_OFFRES):
        try:
            with open(FICHIER_OFFRES, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    txt += "\n📲 *DERNIÈRES WHATSAPP:*\n"
                    for o in data[:3]:
                        txt += f"• {o['texte'][:80]}...\n"
        except:
            pass
    bot.reply_to(m, txt, parse_mode="Markdown")

# --- ROUTE WHATSAPP - LE PLUS IMPORTANT ---
@app.route("/api/new_offre", methods=["POST"])
def new_offre_api():
    data = request.get_json()
    texte = data.get("text", "")
    print(f"📩 Offre reçue de WhatsApp 056608621: {texte[:100]}")
    if len(texte) > 20:
        cat = detect_categorie(texte)
        save_offre_auto(texte, cat)
        return jsonify({"ok": True, "categorie": cat}), 200
    return jsonify({"ok": False}), 400

@app.route('/' + JETON, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok",200

@app.route("/")
def home():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{request.host}/"+JETON)
    return f"V43 WhatsApp 056608621 OK - {datetime.now()}",200

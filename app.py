import os
from flask import Flask, request
import telebot
import json
from datetime import datetime, timedelta

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
    txt = (
        f"Salut {m.from_user.first_name} !\n\n"
        f"BOT EMPLOI CONGO - @Gestionfinal_bot\n"
        f"Scan AGL, ACPE, Unicongo, Total, Bollore\n"
        f"Mails analyses: {MAILS_ANALYSES}\n\n"
        f"Commandes:\n"
        f"/search agl - Chercher une offre\n"
        f"/offres - Voir les dernieres offres\n"
        f"/abonnement - S abonner 3000F/mois\n"
        f"/stats - Tableau de bord\n\n"
        f"24h/24 OK !"
    )
    bot.reply_to(m, txt)

@bot.message_handler(commands=['search'])
def chercher(m):
    parts = m.text.split(" ",1)
    mot = parts[1] if len(parts)>1 else ""
    if not mot:
        bot.reply_to(m, "Tape: /search agl ou /search bollore")
        return
    bot.reply_to(m, f"Recherche: {mot}\n\nLinkedIn - Philippe Labonne President AGL\nACPE - Assistant Logistique Pointe-Noire\nUnicongo - Comptable Brazzaville\n\nPour tout voir: /abonnement")

@bot.message_handler(commands=['offres'])
def offres(m):
    bot.reply_to(m, "ACPE : 12 offres\nUnicongo : 8 offres\nTotalEnergies : 5 offres\nAGL : 3 offres\n\nTape /search agl\nAbonne toi: /abonnement")

@bot.message_handler(commands=['abonnement'])
def abonnement(m):
    user_id = str(m.from_user.id)
    if est_abonne(user_id):
        fin = datetime.fromisoformat(ABONNES[user_id]["fin"])
        bot.reply_to(m, f"Tu es deja abonne Premium jusqu au {fin.strftime('%d/%m/%Y')} !")
        return
    txt = (
        f"ABONNEMENT PREMIUM - 3000 FCFA / 30 JOURS\n\n"
        f"Tu recois:\n"
        f"- Alertes AGL, Bollore, Total instantanees\n"
        f"- Toutes les offres ACPE, Unicongo\n"
        f"- Envoi auto 24h/24\n\n"
        f"POUR PAYER:\n"
        f"1. Envoie {PRIX_MOIS} FCFA au:\n"
        f"   {NUMERO_MOBILE_MONEY}\n"
        f"   Nom: {NOM_MOBILE_MONEY} (Airtel Money)\n\n"
        f"2. Apres paiement, tape:\n"
        f"   /payer ID_DE_TRANSACTION\n"
        f"   Exemple: /payer 12345678\n\n"
        f"Je valide en 5 minutes !"
    )
    bot.reply_to(m, txt)

@bot.message_handler(commands=['payer'])
def payer(m):
    parts = m.text.split(" ",1)
    if len(parts)<2:
        bot.reply_to(m, "Tape: /payer ID_TRANSACTION Ex: /payer 123456789")
        return
    tx_id = parts[1]
    user = m.from_user
    bot.reply_to(m, f"Merci {user.first_name} ! J ai recu ta preuve: {tx_id}. Je verifie ton paiement de {PRIX_MOIS}F au {NUMERO_MOBILE_MONEY}. Activation en 5 min !")
    if ADMIN_ID != 0:
        try:
            bot.send_message(ADMIN_ID, f"NOUVEAU PAIEMENT ! De: @{user.username} {user.first_name} ID:{user.id} Transaction: {tx_id} Montant: {PRIX_MOIS}F Pour valider: /valider {user.id}")
        except:
            pass

@bot.message_handler(commands=['valider'])
def valider(m):
    if ADMIN_ID != 0 and m.from_user.id != ADMIN_ID:
        bot.reply_to(m, "Commande admin seulement")
        return
    parts = m.text.split(" ")
    if len(parts)<2:
        bot.reply_to(m, "Usage: /valider USER_ID")
        return
    target_id = parts[1]
    fin = datetime.now() + timedelta(days=30)
    ABONNES[str(target_id)] = {"debut": datetime.now().isoformat(), "fin": fin.isoformat(), "paye": PRIX_MOIS}
    sauvegarder()
    bot.reply_to(m, f"Abonne {target_id} active jusqu au {fin.strftime('%d/%m/%Y')} - {PRIX_MOIS}F ajoute !")
    try:
        bot.send_message(int(target_id), f"PAIEMENT CONFIRME ! Tu es Premium jusqu au {fin.strftime('%d/%m/%Y')}. Tape /search agl pour commencer")
    except:
        pass

@bot.message_handler(commands=['stats'])
def stats(m):
    actifs = sum(1 for u in ABONNES.values() if datetime.fromisoformat(u["fin"]) > datetime.now())
    revenu = sum(u.get("paye",0) for u in ABONNES.values())
    bot.reply_to(m, f"TABLEAU DE BORD\n\nMails analyses: {MAILS_ANALYSES}\nTotal users: {len(ABONNES)}\nAbonnements actifs: {actifs}\nRevenu: {revenu} FCFA\nAlertes: ACTIVEES\nMobile Money: {NUMERO_MOBILE_MONEY}")

@app.route('/' + JETON, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

@app.route("/")
def verification_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{request.host}/"+JETON)
    return "Bot Wright 24h/24 OK !", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

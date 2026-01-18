import os
import discord
import google.generativeai as genai
from flask import Flask
from threading import Thread

# --- RÉCUPÉRATION DES VARIABLES SECRÈTES ---
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

# --- CONFIGURATION DE L'IA (GOOGLE GEMINI) ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIGURATION DU BOT ---
# C'est ici que tu personnalises les connaissances de ton bot !
CONTEXTE_VSCRIPT = """
Tu es l'assistant support officiel du serveur Discord VScript.
Ton rôle est d'aider les utilisateurs avec les scripts FiveM vendus ou offerts par VScript.
Sois toujours poli, concis et professionnel. Utilise des émojis pour être agréable.

INFOS SUR LES SCRIPTS :
1. Script Météo (/meteo) :
   - Fonction : Change la météo et l'heure en temps réel.
   - Accès : Réservé aux admins/staff.
   - Problème fréquent : Si le menu ne s'ouvre pas, vérifier les permissions ACE.

2. Script Coordonnées (/coord) :
   - Fonction : Copie la position (vector3/vector4) pour les devs.
   - Prix : Gratuit.

3. Installation générale :
   - Toujours mettre 'ensure nom_du_script' dans le server.cfg.
   - Vérifier qu'il n'y a pas d'erreurs dans la console F8 ou serveur.

Si la question ne concerne pas VScript ou FiveM, réponds gentiment que tu ne peux pas aider sur ce sujet.
"""

# --- PARTIE SERVEUR WEB (POUR GARDER LE BOT EN VIE) ---
app = Flask('')

@app.route('/')
def home():
    return "Le Bot VScript est en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- PARTIE DISCORD ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Connecté en tant que {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Le bot répond uniquement s'il est mentionné (@Bot)
    if client.user.mentioned_in(message):
        async with message.channel.typing():
            try:
                # Nettoyage du message utilisateur
                user_message = message.content.replace(f'<@{client.user.id}>', '').strip()
                
                # Envoi à l'IA
                prompt = f"{CONTEXTE_VSCRIPT}\n\nQuestion utilisateur : {user_message}\nRéponse :"
                response = model.generate_content(prompt)
                
                # Gestion de la longueur max Discord (2000 caractères)
                reply = response.text
                if len(reply) > 2000:
                    reply = reply[:1990] + "..."
                
                await message.channel.send(reply)
                
            except Exception as e:
                print(f"Erreur : {e}")
                await message.channel.send("❌ Une erreur est survenue. Vérifiez ma configuration.")

# --- LANCEMENT FINAL ---
keep_alive()
client.run(DISCORD_TOKEN)

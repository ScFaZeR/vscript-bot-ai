import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread

# 1. Configuration des clés
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# 2. Configuration de l'IA (On utilise le modèle Flash, plus rapide et gratuit)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Configuration Discord
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

# 4. Serveur Web pour garder le bot allumé (Flask)
app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 5. Cerveau du Bot
@client.event
async def on_ready():
    print(f'✅ Connecté en tant que {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Si on mentionne le bot
    if client.user in message.mentions:
        try:
            # Nettoyer le message (enlever la mention)
            prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
            
            # Indiquer que le bot réfléchit
            async with message.channel.typing():
                # Demander à Gemini
                response = model.generate_content(prompt)
                
                # Répondre sur Discord
                await message.channel.send(response.text)
                
        except Exception as e:
            # En cas d'erreur, on l'affiche dans les logs Render ET sur Discord pour comprendre
            print(f"❌ ERREUR CRITIQUE : {e}")
            await message.channel.send(f"⚠️ Erreur technique : {e}")

# Lancement
keep_alive()
client.run(DISCORD_TOKEN)

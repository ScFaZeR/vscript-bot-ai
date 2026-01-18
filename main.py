import discord
import os
import requests
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# --- SERVEUR WEB ---
app = Flask('')

@app.route('/')
def home():
    return "Bot en ligne (Version Stable) !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- INTELLIGENCE ARTIFICIELLE ---
def ask_gemini(prompt, model="gemini-1.5-flash"):
    # On utilise l'URL officielle de Google
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ Erreur Google ({response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ Erreur Connexion : {e}"

# --- DIAGNOSTIC (!debug) ---
def list_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            return "\n".join([m for m in models if 'gemini' in m])
        return f"Erreur : {response.text}"
    except Exception as e:
        return str(e)

# --- BOT DISCORD ---
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Connecté en tant que {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Commande de secours pour voir les modèles
    if message.content == "!debug":
        await message.channel.send("🔍 Recherche...")
        liste = list_models()
        await message.channel.send(f"✅ Modèles disponibles :\n```{liste}```")
        return

    # Discussion avec le bot
    if client.user in message.mentions:
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        
        async with message.channel.typing():
            # CORRECTION ICI : On appelle directement le modèle 1.5 Flash qui marche
            reponse = ask_gemini(prompt, "gemini-1.5-flash")
            
            # Gestion de la limite de caractères Discord (2000 max)
            if len(reponse) > 1900: 
                reponse = reponse[:1900] + "... (message coupé)"
            
            await message.channel.send(reponse)

keep_alive()
client.run(DISCORD_TOKEN)

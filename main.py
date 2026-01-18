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
    return "Bot en ligne (Mode 2.5 Flash) !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- INTELLIGENCE ARTIFICIELLE ---
def ask_gemini(prompt):
    # On utilise le modèle validé par ta capture d'écran
    model = "gemini-2.5-flash"
    
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

    if client.user in message.mentions:
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        
        async with message.channel.typing():
            reponse = ask_gemini(prompt)
            
            if len(reponse) > 1900: 
                reponse = reponse[:1900] + "... (suite coupée)"
            
            await message.channel.send(reponse)

keep_alive()
client.run(DISCORD_TOKEN)

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
    return "Bot en ligne (Version 2026) !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- INTELLIGENCE ARTIFICIELLE ---
def ask_gemini(prompt, model="gemini-2.0-flash"):
    # On tente le modèle 2.0 Flash (Standard 2026)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ Erreur {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ Erreur Connexion : {e}"

# --- LISTE DES MODÈLES DISPONIBLES (Diagnostic) ---
def list_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            # On filtre pour garder que les modèles "generateContent"
            chat_models = [m for m in models if 'gemini' in m]
            return "\n".join(chat_models)
        return f"Erreur récupération : {response.text}"
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

    # Commande de diagnostic (Si ça plante encore, tape !debug)
    if message.content == "!debug":
        await message.channel.send("🔍 Recherche des modèles disponibles en 2026...")
        liste = list_models()
        await message.channel.send(f"✅ Modèles trouvés :\n```{liste}```")
        return

    # Discussion normale
    if client.user in message.mentions:
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        async with message.channel.typing():
            # On essaie le modèle 2.0
            reponse = ask_gemini(prompt, "gemini-2.0-flash")
            
            # Si le 2.0 échoue (404), on essaie le 1.5 Pro au cas où
            if "404" in reponse:
                 reponse = ask_gemini(prompt, "gemini-1.5-pro")
            
            if len(reponse) > 1900: reponse = reponse[:1900] + "..."
            await message.channel.send(reponse)

keep_alive()
client.run(DISCORD_TOKEN)

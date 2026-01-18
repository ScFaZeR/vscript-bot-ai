import discord
import os
import requests
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# --- SERVEUR WEB (Pour Render) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot en ligne et prêt !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- INTELLIGENCE ARTIFICIELLE (Mode Direct) ---
def ask_gemini(prompt):
    # On tape directement sur l'URL de Google, sans passer par la librairie buguée
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            # On récupère le texte dans la réponse complexe de Google
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            # Si Google refuse, on affiche pourquoi (Erreur précise)
            return f"❌ Erreur Google ({response.status_code}): {response.text}"
            
    except Exception as e:
        return f"❌ Erreur de connexion : {e}"

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

    # Si le bot est mentionné
    if client.user in message.mentions:
        # Nettoyage du message
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        
        if prompt:
            async with message.channel.typing():
                reponse_ia = ask_gemini(prompt)
                # Discord limite les messages à 2000 caractères, on coupe si c'est trop long
                if len(reponse_ia) > 1900:
                    reponse_ia = reponse_ia[:1900] + "... (message coupé)"
                await message.channel.send(reponse_ia)
        else:
            await message.channel.send("Oui ? Pose-moi une question !")

# Lancement
keep_alive()
client.run(DISCORD_TOKEN)

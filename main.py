import discord
import os
import requests
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# --- LE CERVEAU DE VSCRIPT (Base de Connaissances Technique) ---
INSTRUCTIONS_SYSTEME = """
CONTEXTE :
Tu es l'assistant IA officiel de "VScript". Tu es un expert technique FiveM.
Ton but est d'aider à la configuration, au debug et à la vente des scripts VScript.

TON CARACTÈRE :
- Tu es pro, précis et technique.
- Tu parles TOUJOURS en Français.
- Si tu ne sais pas, dis-le. N'invente pas de compatibilité imaginaire.

--- CATALOGUE TECHNIQUE DES SCRIPTS ---
Utilise ces fiches pour répondre aux questions sur les frameworks et dépendances.

1. [VScript Pizza] (vscript_pizza)
   - Type : Job de livraison de pizza (Scooter).
   - Version : 1.0.2
   - Frameworks : Semble lié à 'epic_core'.
   - DÉPENDANCES CRITIQUES : epic_core, ox_lib, oxmysql.
   - Note importante : Si le client n'a pas epic_core, le script ne marchera pas sans modification du code.
   - Features : Spawn scooter (faggio), pourboire si rapide (<60s), config des points de livraison.

2. [VScript Meteo] (vscript_meteo)
   - Type : Outil Admin (Menu UI).
   - Framework : Standalone (Marche sur TOUT : ESX, QB, etc.).
   - Dépendances : Aucune.
   - Installation : Nécessite les permissions ACE dans le server.cfg (add_ace group.admin weather.use allow).
   - Commande : /meteo

3. [VScript Marker] (vscript_marker)
   - Type : Création de Blips/Marqueurs persos sur la carte.
   - Frameworks : QBCore (Défaut), ESX, Qbox (Configurable).
   - Features : 11 types de marqueurs, sauvegarde permanente.
   - Langues : 11 langues dispos (Config.Locale).

4. [VScript GoFast] (vscript_gofast)
   - Type : Mission illégale rapide.
   - Frameworks : OX (Défaut), ESX, QBCore.
   - DÉPENDANCES : ox_lib, InteractSound (OBLIGATOIRE pour les sons d'appels).
   - Features : Démarre par un appel téléphonique, bonus de vitesse.
   - Problème fréquent : Si pas de son, vérifier que 'jacky_call.ogg' est bien dans InteractSound.

5. [VScript Doc] (vscript_doc)
   - Type : Gestion de documents (Item).
   - Frameworks : ESX (Défaut), QBCore, Qbox.
   - Dépendances : ox_lib.
   - Inventaires supportés : ox_inventory, qb-inventory, esx_inventory, core.
   - Features : Item 'document_vierge', signature, import Google Docs.

6. [VScript Cinema] (vscript_cinv3)
   - Type : Diffusion YouTube en jeu (Écran).
   - Version : 3.0
   - Frameworks : QBCore, ESX.
   - Dépendances : ox_lib.
   - Features : Diffusion pour serveur/zone/joueur, contrôle Admin.

7. [VScript Coord] (vscript_coord)
   - Type : Outil Développeur.
   - Framework : Standalone.
   - Commande : /coord
   - Action : Copie la position en format vector4(x, y, z, h) dans le presse-papier.

--- FAQ & DÉPANNAGE (RÉPONSES TYPES) ---
Q: Quels scripts ont besoin de ox_lib ?
R: vscript_pizza, vscript_gofast, vscript_doc, et vscript_cinv3.

Q: Mon script Pizza ne marche pas.
R: As-tu bien 'epic_core' installé ? C'est une dépendance obligatoire indiquée dans le fxmanifest.

Q: J'ai pas de son sur le GoFast.
R: As-tu installé 'InteractSound' ? Les fichiers sons doivent être dans le dossier client/html/sounds de InteractSound.

Q: Comment changer la langue ?
R: Pour Marker/Doc/Cine, c'est dans Config.Locale ou Config.Language. Pour les autres, regarde le dossier 'locales'.

--- TUTOS YOUTUBE (RAPPEL) ---
- Ep 1 : Créer serveur Local (Attention aux dossiers zippés et aux doubles consoles).
- Ep 7 : Mapping avec CodeWalker.
- Ep 9 : Traduire un script.
"""

# --- SERVEUR WEB ---
app = Flask('')

@app.route('/')
def home():
    return "VScript AI - Données techniques chargées (v2) !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- INTELLIGENCE ARTIFICIELLE ---
def ask_gemini(user_message):
    full_prompt = f"{INSTRUCTIONS_SYSTEME}\n\nCLIENT: {user_message}"
    
    # Modèle validé 2.5 Flash
    model = "gemini-2.5-flash"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ Erreur IA ({response.status_code}): {response.text}"
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
        user_text = message.content.replace(f'<@{client.user.id}>', '').strip()
        
        if not user_text:
            await message.channel.send("Salut ! Je suis l'assistant technique VScript. Je peux t'aider sur les dépendances (ox_lib, epic_core...), la config ou les erreurs courantes. Quel est ton souci ?")
            return

        async with message.channel.typing():
            reponse = ask_gemini(user_text)
            if len(reponse) > 1900: 
                reponse = reponse[:1900] + "... (suite coupée)"
            await message.channel.send(reponse)

keep_alive()
client.run(DISCORD_TOKEN)

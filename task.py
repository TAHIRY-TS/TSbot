#!/usr/bin/env python3
import sys
import os

SESSION_FILE = ".session_ts"

def check_secure_launch():
    if len(sys.argv) != 3:
        print("⛔️ Ce programme doit être lancé via start.bin (arguments manquants).")
        sys.exit(1)
    feature = sys.argv[1]
    token_expected = sys.argv[2]
    if not os.path.exists(SESSION_FILE):
        print("⛔️ Lancement direct interdit : utilisez start.bin.")
        sys.exit(1)
    with open(SESSION_FILE, "r") as f:
        token_file = f.read().strip()
    if token_file != token_expected:
        print("⛔️ Jeton de session non valide. Exécution refusée.")
        sys.exit(1)
    try: os.remove(SESSION_FILE)
    except: pass
    return feature

feature = check_secure_launch()

if feature == "ig_compte":
    # === IG_COMPTE.PY ===
    import os
    import json
    import random
    import glob
    from colorama import init, Fore, Style
    import logging
    from pathlib import Path
    import time
    import datetime
    import subprocess
    import sys

    logging.basicConfig(filename="gestion_comptes.log", level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    init(autoreset=True)

    PROJECT_DIR = Path(__file__).resolve().parent
    CONFIG_DIR = os.path.join(PROJECT_DIR, "configuration")
    SESSION_DIR = os.path.join(PROJECT_DIR, "ig_sessions")
    IG_ACCOUNTS_FILE = os.path.join(CONFIG_DIR, "ig.json")
    USER_SPACE_DIR = os.path.join(PROJECT_DIR, "utilisateurs")
    SELECTED_USER_FILE = os.path.join(USER_SPACE_DIR, "selected_user.json")

    def init_directories():
        os.makedirs(CONFIG_DIR, exist_ok=True)
        os.makedirs(SESSION_DIR, exist_ok=True)
        os.makedirs(USER_SPACE_DIR, exist_ok=True)
        if not os.path.exists(IG_ACCOUNTS_FILE):
            with open(IG_ACCOUNTS_FILE, "w") as f:
                json.dump([], f)
        if not os.path.exists(SELECTED_USER_FILE):
            with open(SELECTED_USER_FILE, "w") as f:
                json.dump({}, f)
        logging.info("Répertoires et fichiers de configuration initialisés.")

    def horloge_ts():
        now = datetime.datetime.now()
        return Fore.BLUE + f"[TS {now.strftime('%H:%M:%S')}]" + Style.RESET_ALL

    def print_colored(message, color=Fore.CYAN):
        horloge = horloge_ts()
        print(f"{horloge} {color}{message}{Style.RESET_ALL}")
        logging.info(message)
        
    def color(text, code):
        return f"\033[{code}m{text}\033[0m"

    def titre_section(titre):
        largeur = 50
        try:
            terminal_width = os.get_terminal_size().columns
        except:
            terminal_width = 80
        padding = max((terminal_width - largeur) // 2, 0)
        spaces = ' ' * padding
        print(f"\n{spaces}{color('╔' + '═' * largeur + '╗', '1;35')}")
        print(f"{spaces}{color('║ ' + titre.center(largeur - 2) + ' ║', '1;35')}")
        print(f"{spaces}{color('╚' + '═' * largeur + '╝', '1;35')}\n")

    def clear():
        if sys.stdout.isatty():
            os.system('cls' if os.name == 'nt' else 'clear')

    def load_accounts():
        if os.path.exists(IG_ACCOUNTS_FILE):
            with open(IG_ACCOUNTS_FILE, "r") as f:
                return json.load(f)
        return []

    def lister_comptes():
        clear()
        titre_section("LISTE DES COMPTES INSTAGRAM")
        accounts = load_accounts()
        if not accounts:
            print_colored("Aucun compte Instagram enregistré.", Fore.YELLOW)
            input(Fore.GREEN + "\nAppuyez sur Entrée pour revenir au menu...")
            return
        print_colored("Liste des comptes Instagram enregistrés :", Fore.LIGHTMAGENTA_EX)
        for idx, acc in enumerate(accounts, 1):
            print(Fore.YELLOW + f"{idx}" + Style.RESET_ALL + ". " + Fore.GREEN + f"{acc.get('username', '')}")
        input(Fore.GREEN + "\nAppuyez sur Entrée pour revenir au menu...")

    def supprimer_compte():
        clear()
        titre_section("SUPPRESSION DE COMPTE INSTAGRAM")
        accounts = load_accounts()
        if not accounts:
            print_colored("Aucun compte à supprimer.", Fore.YELLOW)
            input(Fore.GREEN + "\nAppuyez sur Entrée pour revenir au menu...")
            return
        print_colored("Liste des comptes Instagram enregistrés :", Fore.LIGHTMAGENTA_EX)
        for idx, acc in enumerate(accounts, 1):
            print(Fore.YELLOW + f"{idx}" + Style.RESET_ALL + ". " + Fore.GREEN + f"{acc.get('username', '')}")
        try:
            choix = input(Fore.CYAN + "Numéro(s) du/des compte(s) à supprimer (séparés par des virgules, ex: 1,3). 0 pour annuler: ").strip()
            if not choix:
                print_colored("Entrée vide, annulation.", Fore.YELLOW)
                return
            choix = choix.replace(" ", "")
            if choix == "0":
                print_colored("Suppression annulée.", Fore.YELLOW)
                return
            choix_list = []
            for part in choix.split(","):
                if not part.isdigit():
                    print_colored(f"Entrée invalide: {part}", Fore.RED)
                    return
                num = int(part)
                if num < 1 or num > len(accounts):
                    print_colored(f"Numéro de compte invalide: {num}", Fore.RED)
                    return
                if num not in choix_list:
                    choix_list.append(num)
            choix_list = sorted(set(choix_list))
            to_delete = [accounts[i-1] for i in choix_list]
            print_colored("Vous allez supprimer les comptes suivants :", Fore.LIGHTMAGENTA_EX)
            for idx, acc in zip(choix_list, to_delete):
                print(Fore.YELLOW + f"{idx}" + Style.RESET_ALL + ". " + Fore.GREEN + f"{acc.get('username','')}")
            confirm = input(Fore.RED + "Confirmez la suppression de ces comptes ? (oui/non): " + Style.RESET_ALL).strip().lower()
            if confirm not in ("oui", "o", "yes", "y"):
                print_colored("Suppression annulée.", Fore.YELLOW)
                return
            usernames_deleted = []
            for idx in sorted(choix_list, reverse=True):
                compte_suppr = accounts.pop(idx-1)
                username = compte_suppr.get('username', '')
                usernames_deleted.append(username)
                session_file = os.path.join(SESSION_DIR, f"{username}.json")
                if os.path.exists(session_file):
                    try:
                        os.remove(session_file)
                        print_colored(f"Session Instagram supprimée pour {username}.", Fore.LIGHTYELLOW_EX)
                    except Exception as e:
                        print_colored(f"Erreur suppression session : {e}", Fore.RED)
                user_file = os.path.join(USER_SPACE_DIR, f"{username}.json")
                if os.path.exists(user_file):
                    try:
                        os.remove(user_file)
                        print_colored(f"Fichier utilisateur supprimé pour {username}.", Fore.LIGHTYELLOW_EX)
                    except Exception as e:
                        print_colored(f"Erreur suppression fichier utilisateur : {e}", Fore.RED)
                try:
                    log_path = "task.log"
                    if os.path.exists(log_path):
                        with open(log_path, "r") as f:
                            lignes = f.readlines()
                        with open(log_path, "w") as f:
                            for line in lignes:
                                if username not in line:
                                    f.write(line)
                        print_colored(f"Nettoyage du log pour {username}.", Fore.LIGHTBLUE_EX)
                except Exception as e:
                    print_colored(f"Erreur nettoyage log : {e}", Fore.RED)
                if os.path.exists(SELECTED_USER_FILE):
                    try:
                        with open(SELECTED_USER_FILE, "r") as f:
                            sel = json.load(f)
                        if sel.get("username") == username:
                            with open(SELECTED_USER_FILE, "w") as f:
                                json.dump({}, f)
                            print_colored(f"Nettoyage selected_user pour {username}.", Fore.LIGHTBLUE_EX)
                    except Exception as e:
                        print_colored(f"Erreur nettoyage selected_user : {e}", Fore.RED)
            with open(IG_ACCOUNTS_FILE, "w") as f:
                json.dump(accounts, f)
            print_colored(f"Compte(s) supprimé(s) et nettoyé(s) avec succès: {', '.join(usernames_deleted)}", Fore.GREEN)
            logging.info(f"Comptes supprimés et nettoyés: {', '.join(usernames_deleted)}")
            input(Fore.GREEN + "\nAppuyez sur Entrée pour revenir au menu...")
        except Exception as e:
            print_colored(f"Erreur lors de la suppression: {e}", Fore.RED)
            input(Fore.GREEN + "\nAppuyez sur Entrée pour revenir au menu...")

    def ajouter_compte_instagram():
        clear()
        titre_section("AJOUTER UN COMPTE INSTAGRAM")
        while True:
            username = input(Fore.CYAN + "Nom d'utilisateur Instagram: ").strip()
            if not username:
                print_colored("Le nom d'utilisateur ne peut pas être vide.", Fore.RED)
                continue
            password = input(Fore.CYAN + "Mot de passe: ").strip()
            if not password:
                print_colored("Le mot de passe ne peut pas être vide.", Fore.RED)
                continue
            accounts = load_accounts()
            if any(acc.get("username", "").lower() == username.lower() for acc in accounts):
                print_colored("[❌] Ce nom d'utilisateur existe déjà.", Fore.RED)
                continue
            break
        accounts.append({"username": username, "password": password})
        with open(IG_ACCOUNTS_FILE, "w") as f:
            json.dump(accounts, f)
        print_colored("[✅] Compte ajouté avec succès.", Fore.GREEN)
        logging.info(f"Nouveau compte Instagram ajouté: {username}")
        input(Fore.GREEN + "\nAppuyez sur Entrée pour revenir au menu...")

    def menu():
        while True:
            clear()
            titre_section("MENU ESPACE COMPTE")
            print("\n1. Ajouter un compte Instagram")
            print("2. Lister les comptes Instagram")
            print("3. Supprimer un compte Instagram")
            print("0. Quitter\n")
            choice = input(Fore.GREEN + "Choix: ")
            if choice == "1":
                ajouter_compte_instagram()
            elif choice == "2":
                lister_comptes()
            elif choice == "3":
                supprimer_compte()
            elif choice == "0":
                print_colored("Arrêt du programme.", Fore.YELLOW)
                logging.info("Arrêt du programme par l'utilisateur.")
                try:
                    print_colored("Ouverture du script 'start.sh'...", Fore.LIGHTMAGENTA_EX)
                    subprocess.Popen(['bash', 'start.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
                except Exception as e:
                    print_colored(f"Erreur lors du lancement de start.sh : {e}", Fore.RED)
                sys.exit(0)
            else:
                print_colored("[❌] Choix invalide.", Fore.RED)
                logging.warning("Choix invalide au menu principal.")

    def main_ig_compte():
        try:
            init_directories()
            menu()
        except KeyboardInterrupt:
            sys.exit(0)
    main_ig_compte()

elif feature == "automatisation":
    # === AUTOMATISATION.PY ===
    import os
    import json
    import re
    import glob
    import random
    from instagrapi import Client
    from colorama import init, Fore, Style
    import logging
    from pathlib import Path
    import time
    import datetime
    import subprocess
    import sys

    init(autoreset=True)

    PROJECT_DIR = Path(__file__).resolve().parent
    CONFIG_DIR = os.path.join(PROJECT_DIR, "configuration")
    SESSION_DIR = os.path.join(PROJECT_DIR, "ig_sessions")
    IG_ACCOUNTS_FILE = os.path.join(CONFIG_DIR, "ig.json")
    USER_SPACE_DIR = os.path.join(PROJECT_DIR, "utilisateurs")
    SELECTED_USER_FILE = os.path.join(USER_SPACE_DIR, "selected_user.json")
    IMAGES_DIR = "/storage/emulated/0/TS images"
    os.makedirs(IMAGES_DIR, exist_ok=True)

    def color(text, code):
        return f"\033[{code}m{text}\033[0m"

    def horloge_ts():
        now = datetime.datetime.now()
        return Fore.BLUE + f"[TS {now.strftime('%H:%M:%S')}]" + Style.RESET_ALL

    def titre_section(titre):
        largeur = 50
        try:
            terminal_width = os.get_terminal_size().columns
        except:
            terminal_width = 80
        padding = max((terminal_width - largeur) // 2, 0)
        spaces = ' ' * padding
        print(f"\n{spaces}{color('╔' + '═' * largeur + '╗', '1;35')}")
        print(f"{spaces}{color('║ ' + titre.center(largeur - 2) + ' ║', '1;35')}")
        print(f"{spaces}{color('╚' + '═' * largeur + '╝', '1;35')}\n")

    def print_colored(message, color=Fore.CYAN):
        horloge = horloge_ts()
        print(f"{horloge} {color}{message}{Style.RESET_ALL}")
        logging.info(message)

    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    def load_accounts():
        if os.path.exists(IG_ACCOUNTS_FILE):
            with open(IG_ACCOUNTS_FILE, "r") as f:
                return json.load(f)
        return []

    def save_accounts(accounts):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(IG_ACCOUNTS_FILE, "w") as f:
            json.dump(accounts, f)

    def list_accounts():
        accounts = load_accounts()
        if not accounts:
            print_colored("Aucun compte Instagram enregistré.", Fore.YELLOW)
            return []
        print_colored("Comptes Instagram :", Fore.LIGHTMAGENTA_EX)
        for idx, acc in enumerate(accounts, 1):
            print(f"{Fore.YELLOW}{idx}{Style.RESET_ALL}. {Fore.GREEN}{acc.get('username','')}")
        return accounts

    def select_accounts():
        accounts = list_accounts()
        if not accounts:
            input("Appuyez sur Entrée pour revenir au menu...")
            return []
        choix = input(Fore.CYAN + "Sélectionnez le(s) compte(s) numéro (ex: 1 ou 1,3): ").strip()
        if not choix:
            return []
        idxs = []
        for part in choix.replace(" ", "").split(","):
            if part.isdigit():
                idx = int(part)
                if 1 <= idx <= len(accounts):
                    idxs.append(idx-1)
        selected = [accounts[i] for i in sorted(set(idxs))]
        return selected

   def list_images():
        images = []
        for ext in ("*.jpg", "*.jpeg", "*.png"):
            images.extend(glob.glob(os.path.join(IMAGES_DIR, ext)))
        if not images:
            print_colored("Aucune image trouvée dans 'images/'", Fore.YELLOW)
            return []
        print_colored("Images disponibles :", Fore.LIGHTMAGENTA_EX)
        for idx, img in enumerate(images, 1):
            print(f"{Fore.YELLOW}{idx}{Style.RESET_ALL}. {Fore.GREEN}{os.path.basename(img)}")
        return images

    def select_images():
        images = list_images()
        if not images:
            input("Appuyez sur Entrée pour revenir au menu...")
            return []
        choix = input(Fore.CYAN + "Sélectionnez image(s) par numéro ou nom (ex: 1,3 ou img1.jpg,photo2.png): ").strip()
        if not choix:
            return []
        selection = set()
        for part in choix.replace(" ", "").split(","):
            if part.isdigit():
                idx = int(part)
                if 1 <= idx <= len(images):
                    selection.add(images[idx-1])
            else:
                found = [img for img in images if os.path.basename(img) == part]
                if found:
                    selection.add(found[0])
        return list(selection)

    def follow_auto():
        clear()
        titre_section("FOLLOW AUTO")
        selected = select_accounts()
        if not selected:
            print_colored("Aucun compte sélectionné.", Fore.RED)
            input("Entrée pour revenir...")
            return
        links = input(Fore.CYAN + "Lien(s) à suivre (ex: https://instagram.com/user1,https://insta...): ").strip()
        urls = [u.strip() for u in links.replace(" ", "").split(",") if u]
        if not urls:
            print_colored("Aucun lien fourni.", Fore.RED)
            input("Entrée pour revenir...")
            return
        for acc in selected:
            cl = Client()
            cl.login(acc["username"], acc["password"])
            for url in urls:
                username = url.rstrip('/').split('/')[-1]
                print_colored(f"[{acc['username']}] → FOLLOW @{username}", Fore.LIGHTGREEN_EX)
                try:
                    user_id = cl.user_id_from_username(username)
                    cl.user_follow(user_id)
                    print_colored("→ OK", Fore.GREEN)
                except Exception as e:
                    print_colored(f"Erreur sur {username} : {e}", Fore.RED)
            cl.logout()
        input("Opération terminée. Entrée pour revenir au menu...")

    def like_auto():
        clear()
        titre_section("LIKE AUTO")
        selected = select_accounts()
        if not selected:
            print_colored("Aucun compte sélectionné.", Fore.RED)
            input("Entrée pour revenir...")
            return
        links = input(Fore.CYAN + "Lien(s) de post à liker (ex: https://instagram.com/p/xyz,...): ").strip()
        urls = [u.strip() for u in links.replace(" ", "").split(",") if u]
        if not urls:
            print_colored("Aucun lien fourni.", Fore.RED)
            input("Entrée pour revenir...")
            return
        for acc in selected:
            cl = Client()
            cl.login(acc["username"], acc["password"])
            for url in urls:
                try:
                    shortcode = url.rstrip('/').split('/')[-1]
                    print_colored(f"[{acc['username']}] → LIKE {shortcode}", Fore.LIGHTGREEN_EX)
                    media_id = cl.media_id(cl.media_pk_from_url(url))
                    cl.media_like(media_id)
                    print_colored("→ OK", Fore.GREEN)
                except Exception as e:
                    print_colored(f"Erreur sur {url} : {e}", Fore.RED)
            cl.logout()
        input("Opération terminée. Entrée pour revenir au menu...")

    def publication_auto():
        clear()
        titre_section("PUBLICATION AUTO")
        selected = select_accounts()
        if not selected:
            print_colored("Aucun compte sélectionné.", Fore.RED)
            input("Entrée pour revenir...")
            return
        imgs = select_images()
        if not imgs:
            print_colored("Aucune image sélectionnée.", Fore.RED)
            input("Entrée pour revenir...")
            return
        status = input(Fore.CYAN + "Status/Caption (laisser vide pour aucun): ").strip()
        for acc in selected:
            cl = Client()
            cl.login(acc["username"], acc["password"])
            for img in imgs:
                print_colored(f"[{acc['username']}] → PUBLIE {os.path.basename(img)}", Fore.LIGHTGREEN_EX)
                try:
                    cl.photo_upload(img, caption=status)
                    print_colored("→ OK", Fore.GREEN)
                except Exception as e:
                    print_colored(f"Erreur sur {os.path.basename(img)} : {e}", Fore.RED)
            cl.logout()
        input("Opération terminée. Entrée pour revenir au menu...")

    def main_menu():
        while True:
            clear()
            titre_section("MENU INSTAGRAM AUTOMATION TS")
            print("1. Follow auto")
            print("2. Like auto")
            print("3. Publication auto")
            print("0. Quitter\n")
            choice = input(Fore.GREEN + "Choix: ").strip()
            if choice == "1":
                follow_auto()
            elif choice == "2":
                like_auto()
            elif choice == "3":
                publication_auto()
            elif choice == "0":
                print_colored("Arrêt du programme.", Fore.YELLOW)
                logging.info("Arrêt du programme par l'utilisateur.")
                try:
                    print_colored("Ouverture du script 'start.sh'...", Fore.LIGHTMAGENTA_EX)
                    subprocess.Popen(['bash', 'start.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
                except Exception as e:
                    print_colored(f"Erreur lors du lancement de start.sh : {e}", Fore.RED)
                sys.exit(0)
            else:
                print_colored("[❌] Choix invalide.", Fore.RED)
                logging.warning("Choix invalide au menu principal.")

    main_menu()

elif feature == "task":
    # === TOUT TON SCRIPT task.py ASYNC (déjà collé plus haut, voir message précédent) ===
    # python/termux TS
import os
import json
import re
import random
import asyncio
from telethon import TelegramClient, events, errors
from instagrapi import Client
from colorama import init, Fore, Style
import logging
from pathlib import Path
import time
import datetime
import sys
from collections import deque

init(autoreset=True)

def clean_log_daily(logfile):
    """Efface le log s'il date d'hier ou avant."""
    if not os.path.exists(logfile):
        return
    try:
        # On récupère la date de la dernière modif du log
        last_modif = datetime.datetime.fromtimestamp(os.path.getmtime(logfile))
        now = datetime.datetime.now()
        # Si le log n'est pas du jour, on l'efface
        if last_modif.date() < now.date():
            with open(logfile, 'w') as f:
                pass  # Vide le fichier
            print(Fore.YELLOW + "[🧹] Log effacé car trop ancien.")
    except Exception as e:
        print(Fore.RED + f"[❌] Impossible de nettoyer le log : {e}")

clean_log_daily("task.log")

logging.basicConfig(
    filename="task.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = os.path.join(PROJECT_DIR, "configuration")
SESSION_DIR = os.path.join(PROJECT_DIR, "ig_sessions")
IG_ACCOUNTS_FILE = os.path.join(CONFIG_DIR, "ig.json")
USER_SPACE_DIR = os.path.join(PROJECT_DIR, "utilisateurs")
SELECTED_USER_FILE = os.path.join(USER_SPACE_DIR, "selected_user.json")
TELEGRAM_DIR = os.path.join(PROJECT_DIR, "telegram_user")
TELEGRAM_SESSION_FILE = os.path.join(TELEGRAM_DIR, "tg_session")
TELEGRAM_API_FILE = os.path.join(TELEGRAM_DIR, "telegram_api.json")

last_username = None
last_bot_msg_time = None
pending_comment = None
send_lock = asyncio.Lock()
last_messages_sent = deque(maxlen=2)
last_back_time = None
insta_task_queue = asyncio.Queue()
processing_insta_task = False

waiting_for_username = False  # Pour éviter les doublons Instagram/username

# Pour éviter le double "✅Completed"
last_completed_sent = None

# Ajout pour éviter les doublons username/Instagram quand les messages sont successifs
last_sent_type = None  # "instagram" ou "username" ou None
last_sent_time = 0
MIN_MSG_INTERVAL = 0.03  # secondes anti-doublon

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def titre_section(titre):
    largeur = 50
    try:
        terminal_width = os.get_terminal_size().columns
    except:
        terminal_width = 80
    padding = max((terminal_width - largeur) // 2, 0)
    spaces = ' ' * padding
    print(f"\n{spaces}{color('╔' + '═' * largeur + '╗', '1;35')}")
    print(f"{spaces}{color('║ ' + titre.center(largeur - 2) + ' ║', '1;35')}")
    print(f"{spaces}{color('╚' + '═' * largeur + '╝', '1;35')}\n")

def horloge_ts():
    now = datetime.datetime.now()
    return Fore.BLUE + f"[TS {now.strftime('%H:%M:%S')}]" + Style.RESET_ALL

def print_colored(message, color=Fore.CYAN):
    horloge = horloge_ts()
    print(f"{horloge} {color}{message}{Style.RESET_ALL}")
    logging.info(message)
def load_accounts():
    with open(IG_ACCOUNTS_FILE, "r") as f:
        return json.load(f)

def save_selected_user(account):
    with open(SELECTED_USER_FILE, "w") as f:
        json.dump(account, f)
    logging.info(f"Compte sélectionné enregistré: {account.get('username')}")

def ig_session_path(username):
    return os.path.join(SESSION_DIR, f"{username}.json")

def connect_instagram(username, password):
    cl = Client()
    session_path = ig_session_path(username)
    if os.path.exists(session_path):
        try:
            cl.load_settings(session_path)
            cl.login(username, password)
            logging.info(f"Session Instagram restaurée pour {username}.")
        except Exception as e:
            print_colored(f"[⚠️] Impossible de restaurer la session pour {username}, reconnexion...", Fore.RED)
            logging.warning(f"Restaurer session échouée pour {username} : {e}")
            try:
                cl = Client()
                cl.login(username, password)
            except Exception as e:
                print_colored(f"[❌] Erreur Instagram pour {username} : {e}", Fore.RED)
                logging.error(f"Connexion Instagram échouée pour {username} : {e}")
                return None
    else:
        try:
            cl.login(username, password)
        except Exception as e:
            print_colored(f"[❌] Erreur Instagram pour {username} : {e}", Fore.RED)
            logging.error(f"Connexion Instagram échouée pour {username} : {e}")
            return None
    try:
        cl.dump_settings(session_path)
        logging.info(f"Session Instagram sauvegardée pour {username}.")
    except Exception as e:
        print_colored(f"[⚠️] Sauvegarde session échouée pour {username} : {e}", Fore.RED)
        logging.warning(f"Sauvegarde session échouée pour {username}: {e}")
    return cl

def is_valid_phone(phone):
    return re.match(r"^\+\d{10,15}$", phone)

def load_json_file(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(Fore.RED + "[❌] Fichier de configuration invalide ou manquant.")
        return {}

def get_telegram_api():
    data = load_json_file(TELEGRAM_API_FILE)
    if all(key in data for key in ["api_id", "api_hash", "phone"]):
        return data["api_id"], data["api_hash"], data["phone"]
    try:
        titre_section("CONNECTION A TELEGRAM")
        api_id = int(input(Fore.GREEN + "API_ID Telegram : "))
        api_hash = input(Fore.GREEN + "API_HASH Telegram : ")
        while True:
            phone_number = input(Fore.GREEN + "Numéro de téléphone (+...): ")
            if is_valid_phone(phone_number):
                break
            print(Fore.RED + "Format invalide. Exemple : +261341234567")
        with open(TELEGRAM_API_FILE, "w") as f:
            json.dump({
                "api_id": api_id,
                "api_hash": api_hash,
                "phone": phone_number
            }, f)
        logging.info("Identifiants Telegram sauvegardés.")
        return api_id, api_hash, phone_number
    except Exception as e:
        print(Fore.RED + f"[❌] Erreur lors de la saisie : {e}")
        sys.exit(1)

async def send_message_with_retry(client, entity, message, max_retries=1, timeout=7):
    global last_bot_msg_time, last_messages_sent
    async with send_lock:
        if message in last_messages_sent:
            return
        for attempt in range(max_retries + 1):
            await asyncio.sleep(0.2)
            await client.send_message(entity, message)
            last_messages_sent.append(message)
            start = time.time()
            while time.time() - start < timeout:
                await asyncio.sleep(0.2)
                if last_bot_msg_time and time.time() - last_bot_msg_time < timeout:
                    return
            if attempt < max_retries:
                return
async def traiter_message(message_text, client):
    global last_username, last_bot_msg_time, pending_comment, last_messages_sent, waiting_for_username
    global last_sent_type, last_sent_time, processing_insta_task, last_completed_sent

    now = time.time()
    last_messages_sent.clear()
    last_bot_msg_time = now
    message_lower = message_text.lower().strip()

    def reset_completed_flag():
        global last_completed_sent
        last_completed_sent = None

    # Gestion du commentaire différé
    if pending_comment is not None:
        if not re.search(r'https://www\.instagram\.com/[^\s\)]+', message_text) and "action" not in message_lower:
            comment_text = message_text.strip()
            link = pending_comment['link']
            action = "leave the comment"
            reset_completed_flag()  # Nouvelle tâche = reset flag
            print_colored(f"[💬] Commentaire reçu: {comment_text}", Fore.LIGHTCYAN_EX)
            accounts = load_accounts()
            account = None
            if last_username:
                account = next((a for a in accounts if a["username"] == last_username), None)
            if account is None and accounts:
                account = random.choice(accounts)
                last_username = account["username"]
            if account is None:
                print_colored("[❌] Aucun compte Instagram valide.", Fore.RED)
                await send_message_with_retry(client, "SmmKingdomTasksBot", "Instagram")
                pending_comment = None
                return
            save_selected_user(account)
            cl = connect_instagram(account["username"], account["password"])
            if not cl:
                print_colored(f"[❌] Erreur Instagram pour {account['username']} - tâche ignorée.", Fore.RED)
                await send_message_with_retry(client, "SmmKingdomTasksBot", "Instagram")
                pending_comment = None
                return
            processing_insta_task = True
            try:
                media_id = cl.media_pk_from_url(link)
                cl.media_comment(media_id, comment_text)
                print_colored(f"[💬] Commentaire posté : {comment_text}", Fore.GREEN)
                key = f"{link}|{action}|{comment_text}"
                if last_completed_sent != key:
                    await send_message_with_retry(client, "SmmKingdomTasksBot", "✅Completed")
                    print_colored("[✅] Action Instagram réussi.", Fore.GREEN)
                    last_completed_sent = key
                key = f"{link}|{action}|{comment_text}"
                if last_completed_sent != key:
                    await send_message_with_retry(client, "SmmKingdomTasksBot", "✅Completed")
                    last_completed_sent = key
            except Exception as e:
                print_colored(f"[❌] Erreur lors du commentaire avec {account['username']} : {e} -- tâche ignorée.", Fore.RED)
            finally:
                pending_comment = None
                await asyncio.sleep(0.05)
                processing_insta_task = False
            return

    # Quand le bot demande explicitement le username → envoyer UNIQUEMENT le username,
    # mais ignorer si on vient juste d'envoyer "Instagram" (anti-doublon !)
    if "please give us your profile's username" in message_lower or \
       "choose account from the list" in message_lower or \
       "select user from list" in message_lower:
        if last_sent_type == "instagram" and (now - last_sent_time) < MIN_MSG_INTERVAL:
            print_colored("[⚠️] Username ignoré car Instagram vient d'être envoyé.", Fore.YELLOW)
            return
        accounts = load_accounts()
        if not accounts:
            print_colored("[❌] Aucun compte disponible.", Fore.RED)
            return
        selected = random.choice(accounts)
        last_username = selected["username"]
        save_selected_user(selected)
        await asyncio.sleep(0.1)
        print_colored(f"[🤵] Compte: {last_username}", Fore.YELLOW)
        await send_message_with_retry(client, "SmmKingdomTasksBot", last_username)
        waiting_for_username = False
        last_sent_type = "username"
        last_sent_time = now
        return

    # Quand on reçoit "Instagram" SEUL → on attend la demande du username ensuite, ne pas répondre
    if message_lower == "instagram":
        waiting_for_username = True
        return

    link_match = re.search(r'https://www\.instagram\.com/[^\s\)]+', message_text)
    action_match = re.search(r"action\s*:\s*([^\n\r]+)", message_text, re.IGNORECASE)
    if link_match and action_match:
        link = link_match.group(0)
        action = action_match.group(1).strip().lower()
        reset_completed_flag()  # Nouvelle tâche = reset flag
        accounts = load_accounts()
        account = None
        if last_username:
            account = next((a for a in accounts if a["username"] == last_username), None)
        if account is None and accounts:
            account = random.choice(accounts)
            last_username = account["username"]
        if account is None:
            print_colored("[❌] Aucun compte Instagram valide.", Fore.RED)
            await send_message_with_retry(client, "SmmKingdomTasksBot", "Instagram")
            return
        save_selected_user(account)
        cl = connect_instagram(account["username"], account["password"])
        if not cl:
            print_colored(f"[❌] Erreur Instagram pour {account['username']} - tâche ignorée.", Fore.RED)
            await send_message_with_retry(client, "SmmKingdomTasksBot", "Instagram")
            return
        processing_insta_task = True
        try:
            if "like" in action or "video view" in action or "view video" in action or "leave the comment" in action:
                media_id = cl.media_pk_from_url(link)
                id_to_show = media_id
            elif "follow" in action or "story view" in action or "view story" in action:
                if "stories" in link:
                    user_match = re.search(r"instagram\.com/stories/([^/?]+)", link)
                    if user_match:
                        user_story = user_match.group(1)
                        user_id = cl.user_id_from_username(user_story)
                        id_to_show = user_id
                        user = user_story
                    else:
                        target = re.search(r"instagram\.com/([^/?]+)", link).group(1)
                        user_id = cl.user_id_from_username(target)
                        id_to_show = user_id
                        user = target
                else:
                    target = re.search(r"instagram\.com/([^/?]+)", link)
                    if target:
                        user = target.group(1)
                        user_id = cl.user_id_from_username(user)
                        id_to_show = user_id
            else:
                id_to_show = "???"
            print_colored(f"[🌍] Lien : {link}", Fore.CYAN)
            print_colored(f"[🆔] Id : {id_to_show}", Fore.CYAN)
            print_colored(f"[🔧] Action : {action}", Fore.MAGENTA)

            key = f"{link}|{action}"
            # LIKE
            if "like" in action:
                cl.media_like(media_id)
                print_colored(f"[👍] Post liké par {account['username']}", Fore.GREEN)
                if last_completed_sent != key:
                    await send_message_with_retry(client, "SmmKingdomTasksBot", "✅Completed")
                    last_completed_sent = key
            # FOLLOW
            elif "follow" in action:
                cl.user_follow(user_id)
                print_colored(f"[❤️] {account['username']} suit {user}", Fore.GREEN)
                if last_completed_sent != key:
                    await send_message_with_retry(client, "SmmKingdomTasksBot", "✅Completed")
                    last_completed_sent = key
            # VIDEO VIEW
            elif "video view" in action or "view video" in action:
                cl.media_seen([media_id])
                print_colored(f"[🎬] Vidéo vue 3s par {account['username']}", Fore.GREEN)
                await asyncio.sleep(3)
                if last_completed_sent != key:
                    await send_message_with_retry(client, "SmmKingdomTasksBot", "✅Completed")
                    last_completed_sent = key
            # STORY VIEW
            elif "story view" in action or "view story" in action:
                stories = cl.user_stories(user_id)
                if stories:
                    cl.story_view(stories[0].pk)
                    print_colored(f"[👀] Story vue pour {user}", Fore.GREEN)
                if last_completed_sent != key:
                    await send_message_with_retry(client, "SmmKingdomTasksBot", "✅Completed")
                    last_completed_sent = key
            # COMMENTAIRE DIFFÉRÉ
            elif "leave the comment" in action:
                pending_comment = {"link": link}
                print_colored("[♻️] Attente du texte à commenter", Fore.LIGHTYELLOW_EX)
                processing_insta_task = False
                return
            else:
                print_colored(f"[❓] Action non reconnue : {action}", Fore.YELLOW)

            print_colored("[✅] Action Instagram réussi.", Fore.GREEN)
            logging.info(f"Action {action} faite sur {link} avec {account['username']}")
        except Exception as e:
            print_colored(f"[❌] Erreur action avec {account['username']} : {e} -- tâche ignorée.", Fore.RED)
            await send_message_with_retry(client, "SmmKingdomTasksBot", "Instagram")
        finally:
            await asyncio.sleep(0.01)
            processing_insta_task = False
        return

    # Après "all condition" ou "no active tasks", on envoie UNIQUEMENT "Instagram"
    # mais ignorer si on vient juste d'envoyer le username (anti-doublon !)
    if "no active tasks" in message_lower or "all condition" in message_lower or "choose social network" in message_lower:
        if last_sent_type == "username" and (now - last_sent_time) < MIN_MSG_INTERVAL:
            print_colored("[⚠️] Instagram ignoré car username vient d'être envoyé.", Fore.YELLOW)
            return
        if not waiting_for_username:
            await asyncio.sleep(0.01)
            await send_message_with_retry(client, "SmmKingdomTasksBot", "Instagram")
            waiting_for_username = True
            last_sent_type = "instagram"
            last_sent_time = now
        return

    if "💸 my balance" in message_lower:
        match = re.search(r"💸\s*My\s*Balance\s*[:：]?\s*\*?\*?([0-9.,kK]+)\*?\*?", message_text, re.IGNORECASE)
        montant = match.group(1) if match else "???"
        print(color("💸 My Balance : ", "1;37") + color(f"{montant}", "1;35") + color(" cashCoins", "1;37"))
        await asyncio.sleep(0.05)
        await client.send_message("SmmKingdomTasksBot", "📝Tasks📝")
        return

def is_idle():
    if pending_comment is not None:
        return False
    if last_bot_msg_time is not None and time.time() - last_bot_msg_time < 10:
        return False
    return True

def boucle_automatique(client):
    global last_back_time
    last_back_time = time.time()

    @client.on(events.NewMessage(chats="SmmKingdomTasksBot"))
    async def handler(event):
        # NOUVEAU LOGIQUE : Si le message du bot contient "thank you for completing the task"
        # alors on considère que c'est un vrai retour du bot, on met à jour last_bot_msg_time !
        if "thank you for completing the task" in event.message.message.lower():
            global last_bot_msg_time
            last_bot_msg_time = time.time()
            print_colored("[🤖] Le bot vous remercie grace à vos tâches.", Fore.LIGHTGREEN_EX)
        await insta_task_queue.put(event.message.message)

    async def boucle():
        global last_back_time, processing_insta_task, pending_comment
        while True:
            await asyncio.sleep(5)
            now = time.time()
            # NE relance QUE si aucune tâche n'est en cours et aucun commentaire différé en attente
            if not processing_insta_task and pending_comment is None:
                if last_bot_msg_time is not None and now - last_bot_msg_time > 8:
                    time_before = last_bot_msg_time
                    print_colored("[⏳] Relance rapide demande tâche Instagram.", Fore.YELLOW)
                    await asyncio.sleep(0.1)
                    # Double vérification juste avant d'envoyer
                    if last_bot_msg_time == time_before and not processing_insta_task and pending_comment is None:
                        await send_message_with_retry(client, "SmmKingdomTasksBot", "Instagram")
                    else:
                        print_colored("[🔛] Le bot déjà du retour", Fore.GREEN)
            # 🔙Back toutes les 30 minutes SI le script est "idle" (pas occupé)
            if is_idle() and (last_back_time is None or now - last_back_time > 1800):
                await send_message_with_retry(client, "SmmKingdomTasksBot", "🔙Back")
                last_back_time = now
    client.loop.create_task(boucle())

async def process_insta_tasks(client):
    global processing_insta_task
    while True:
        task_message = await insta_task_queue.get()
        try:
            await traiter_message(task_message, client)
        except Exception as e:
            print_colored(f"[❌] Erreur dans le traitement de la tâche: {e}", Fore.RED)
        insta_task_queue.task_done()
async def connect_telegram():
    titre_section("LANCEMENT DES TACHES TELEGRAM - INSTAGRAM")
    print(Fore.YELLOW + "\n[🥰] Raha hiala na hanajanona ny asa ianao dia tsindrio ny CTRL+C ")
    api_id, api_hash, phone = get_telegram_api()
    client = TelegramClient(TELEGRAM_SESSION_FILE, api_id, api_hash)
    try:
        if os.path.exists(TELEGRAM_SESSION_FILE + ".session"):
            await client.connect()
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                code = input(Fore.GREEN + "Code reçu par Telegram : ")
                await client.sign_in(phone, code)
            print(Fore.GREEN + "[✅] Session Telegram restaurée.")
            logging.info("Session Telegram restaurée.")
        else:
            await client.start(phone=lambda: phone)
            print(Fore.GREEN + "[✅] Connexion Telegram réussie !")
            logging.info("Nouvelle session Telegram connectée.")
    except errors.PhoneCodeInvalidError:
        print(Fore.RED + "[❌] Code incorrect. Réessaie.")
        sys.exit(1)
    except errors.ApiIdInvalidError:
        print(Fore.RED + "[❌] API_ID ou API_HASH invalide.")
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"[❌] Erreur de connexion : {e}")
        sys.exit(1)
    return client

async def main():
    init_directories()
    telegram_client = await connect_telegram()

    try:
        messages = await telegram_client.get_messages("SmmKingdomTasksBot", limit=1)
        if messages:
            await insta_task_queue.put(messages[0].message)
    except Exception as e:
        print_colored(f"[⚠️] Impossible de traiter le dernier message : {e}", Fore.YELLOW)
        logging.warning(f"Erreur récupération dernier message : {e}")

    boucle_automatique(telegram_client)
    telegram_client.loop.create_task(process_insta_tasks(telegram_client))
    await telegram_client.run_until_disconnected()

def init_directories():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(SESSION_DIR, exist_ok=True)
    os.makedirs(USER_SPACE_DIR, exist_ok=True)
    os.makedirs(TELEGRAM_DIR, exist_ok=True)
    if not os.path.exists(IG_ACCOUNTS_FILE):
        with open(IG_ACCOUNTS_FILE, "w") as f:
            json.dump([], f)
    if not os.path.exists(SELECTED_USER_FILE):
        with open(SELECTED_USER_FILE, "w") as f:
            json.dump({}, f)
    logging.info("Répertoires et fichiers de configuration initialisés.")

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print(Fore.CYAN + "\n📴 Arrêt manuel détecté. Retour à start.sh dans 3 secondes..." + Style.RESET_ALL)
            time.sleep(4)
            os.system("bash start.sh")
            break
        except Exception as e:
            print(Fore.YELLOW + f"⚠️ Redémarrage du bot suite à une erreur : {e}" + Style.RESET_ALL)
            time.sleep(5)

else:
    print("❌ Fonction non reconnue.")
    sys.exit(1)

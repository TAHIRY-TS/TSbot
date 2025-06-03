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
    # ...
    # (colle ici tout ton script async du mode task, exactement comme dans ton message précédent)
    # ...
    # à la fin :
    if __name__ == "__main__" or True:
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

#!/bin/bash

chmod +x ./*.sh ./*.py
clear
tput civis

ROUGE="\033[0;31m"
JAUNE="\033[0;33m"
CYAN="\033[0;36m"
BLANC="\033[1;37m"
RESET="\033[0m"
BLEU="\033[1;34m"
MAGENTA="\033[1;35m"
VERT="\033[1;32m"
BOLD="\033[1m"

USER_ID_FILE="user_id.json"
API_URL="https://your-fly-app.fly.dev/check-key"  # <-- Mets ici ton endpoint, le nom est neutre
VERSION_FILE="version.txt"
VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "1.0.0")

center_text() {
    local text="$1"
    local largeur=48
    local len=${#text}
    local padding=$(( (largeur - len) / 2 ))
    printf "%*s%s%*s" "$padding" "" "$text" "$((largeur - len - padding))" ""
}

# Vérifie la validité user_id+clé via API (ne dit rien sur la technologie ou le serveur)
is_subscription_valid() {
    local uid="$1"
    local key="$2"
    local response status

    response=$(curl -s --connect-timeout 6 "$API_URL?user_id=$uid&key=$key")
    if [[ -z "$response" ]] || ! echo "$response" | grep -q '"status"'; then
        echo ""
        return 2
    fi

    status=$(echo "$response" | grep -oE '"status"\s*:\s*"[a-zA-Z0-9_-]+"' | sed -E 's/.*"status"\s*:\s*"([^"]+)".*/\1/')
    if [[ "$status" == "valid" ]]; then
        return 0
    elif [[ "$status" == "expired" ]] || [[ "$status" == "invalid" ]]; then
        return 1
    else
        echo ""
        return 2
    fi
}

# Demande l'user id ET la clé, vérifie via l'API, enregistre dans le JSON
ask_and_save_user_id() {
    clear
    echo -e "${CYAN}=== Enregistrement de votre ID utilisateur et clé d'abonnement ===${RESET}"
    while true; do
        read -rp "Entrez votre ID (fourni par le bot Telegram) : " uid
        read -rp "Collez votre clé d'abonnement : " key
        [[ -z "$uid" || -z "$key" ]] && { echo -e "${ROUGE}Champs requis non remplis.${RESET}"; continue; }
        is_subscription_valid "$uid" "$key"
        api_status=$?
        if [[ "$api_status" == "0" ]]; then
            echo "{\"user_id\":\"$uid\",\"key\":\"$key\"}" > "$USER_ID_FILE"
            echo -e "${VERT}✅ ID et clé enregistrés et vérifiés !${RESET}"
            sleep 1
            break
        elif [[ "$api_status" == "2" ]]; then
            echo -e "${ROUGE}Erreur réseau ou serveur injoignable. Essayez plus tard.${RESET}"
            sleep 2
        else
            echo -e "${ROUGE}❌ ID ou clé invalide/expiré. Vérifiez votre abonnement sur le bot Telegram.${RESET}"
            sleep 1
        fi
    done
}

# Lit user_id et clé du JSON ou demande
get_or_ask_user_data() {
    local uid="" key=""
    if [[ -f "$USER_ID_FILE" ]]; then
        uid=$(grep -oE '"user_id"\s*:\s*"([a-zA-Z0-9_-]+)"' "$USER_ID_FILE" | sed -E 's/.*"user_id"\s*:\s*"([^"]+)".*/\1/')
        key=$(grep -oE '"key"\s*:\s*"([a-zA-Z0-9_-]+)"' "$USER_ID_FILE" | sed -E 's/.*"key"\s*:\s*"([^"]+)".*/\1/')
    fi
    is_subscription_valid "$uid" "$key"
    api_status=$?
    if [[ -z "$uid" || -z "$key" || "$api_status" == "1" || "$api_status" == "2" ]]; then
        ask_and_save_user_id
        uid=$(grep -oE '"user_id"\s*:\s*"([a-zA-Z0-9_-]+)"' "$USER_ID_FILE" | sed -E 's/.*"user_id"\s*:\s*"([^"]+)".*/\1/')
        key=$(grep -oE '"key"\s*:\s*"([a-zA-Z0-9_-]+)"' "$USER_ID_FILE" | sed -E 's/.*"key"\s*:\s*"([^"]+)".*/\1/')
    fi
    echo "$uid;$key"
}

affichage_logo() {
    local logo=(
        "████████╗███████╗"
        "╚══██╔══╝██╔════╝"
        "   ██║   ███████╗"
        "   ██║        ██║"
        "   ██║   ███████║"
        "   ╚═╝   ╚══════╝"
    )
    local colors=(31 33 32 36 34 35)
    local term_width=$(tput cols)
    local i=0
    for line in "${logo[@]}"; do
        local padding=$(( (term_width - ${#line}) / 2 ))
        local color=${colors[$((i % ${#colors[@]}))]}
        printf "%*s\e[1;${color}m%s\e[0m\n" "$padding" "" "$line"
        ((i++))
    done
}

afficher_message_animated() {
    local couleurs=("\033[1;31m" "\033[1;32m" "\033[1;33m" "\033[1;34m" "\033[1;35m" "\033[1;36m" "\033[1;37m")
    local messages=("BIENVENUE !")
    local largeur_terminal=$(tput cols)
    for texte in "${messages[@]}"; do
        local longueur=${#texte}
        local espace_gauche=$(( (largeur_terminal - longueur) / 2 ))
        printf "%*s" "$espace_gauche" ""
        for ((i=0; i<longueur; i++)); do
            local lettre="${texte:$i:1}"
            local couleur=${couleurs[$((RANDOM % ${#couleurs[@]}))]}
            echo -ne "${couleur}${lettre}${RESET}"
            sleep 0.1
        done
        echo ""
    done
}

afficher_version() {
    local largeur=55
    local texte="TS SMM AUTOCLICK - $VERSION"
    local longueur=${#texte}
    local espace_gauche=$(( ( $(tput cols) - largeur ) / 2 ))
    printf "%*s" "$espace_gauche" ""
    printf "${MAGENTA}║${RESET}"
    printf "%*s" $(( (largeur - 2 + longueur) / 2 )) "$texte"
    printf "%*s" $(( (largeur - 2 - longueur) / 2 )) ""
    echo -e "  ${MAGENTA}║${RESET}"
}

afficher_cadre() {
    local largeur=55
    local texte="MENU PRINCIPAL"
    local longueur=${#texte}
    local espace_gauche=$(( ( $(tput cols) - largeur ) / 2 ))

    printf "%*s" "$espace_gauche" ""
    echo -e "${MAGENTA}╔$(printf '═%.0s' $(seq 1 $((largeur - 2))))╗${RESET}"

    printf "%*s" "$espace_gauche" ""
    printf "${MAGENTA}║${RESET}"
    printf "%*s" $(( (largeur - 2 + longueur) / 2 )) "$texte"
    printf "%*s" $(( (largeur - 2 - longueur) / 2 )) ""
    echo -e " ${MAGENTA}║${RESET}"

    printf "%*s" "$espace_gauche" ""
    echo -e "${MAGENTA}╠$(printf '═%.0s' $(seq 1 $((largeur - 2))))╣${RESET}"
}

afficher_options() {
    local espace_gauche=$(( ( $(tput cols) - 55 ) / 2 ))
    printf "%*s" "$espace_gauche" ""; echo -e "${MAGENTA}║${RESET} ${MAGENTA}1.${RESET} ⚙ Gestion de compte Instagram                    ${MAGENTA}║${RESET}"                   
    printf "%*s" "$espace_gauche" ""; echo -e "${MAGENTA}║${RESET} ${CYAN}2.${RESET} ⛏️ Lancer l'autoclick SMM                         ${MAGENTA}║${RESET}"
    printf "%*s" "$espace_gauche" ""; echo -e "${MAGENTA}║${RESET} 3.${RESET} 🪓 Lancer une tâche manuellement                  ${MAGENTA}║${RESET}"
    printf "%*s" "$espace_gauche" ""; echo -e "${MAGENTA}║${RESET} ${VERT}4.${RESET} 📥 Mise à jour                                   ${MAGENTA}║${RESET}"
    printf "%*s" "$espace_gauche" ""; echo -e "${MAGENTA}║${RESET} ${BLEU}5.${RESET} 🛃 Infos & Aide                                  ${MAGENTA}║${RESET}"
    printf "%*s" "$espace_gauche" ""; echo -e "${MAGENTA}║${RESET} ${BLEU}6.${RESET} ❤ Follow & Pubs auto                             ${MAGENTA}║${RESET}"
    printf "%*s" "$espace_gauche" ""; echo -e "${MAGENTA}║${RESET} ${JAUNE}7.${RESET} 🔑 Abonnement                                    ${MAGENTA}║${RESET}"
    printf "%*s" "$espace_gauche" ""; echo -e "${MAGENTA}║${RESET} ${ROUGE}0.${RESET} 🔙 Quitter                                       ${MAGENTA}║${RESET}"
}

ligne_inferieure() {
    local espace_gauche=$(( ( $(tput cols) - 55 ) / 2 ))
    printf "%*s" "$espace_gauche" ""
    echo -e "${MAGENTA}╚$(printf '═%.0s' $(seq 1 53))╝${RESET}"
}

progress_bar() {
    local step=5
    local duree=2.0
    local delay=$(echo "$duree / (100 / $step)" | bc -l)
    local progress=0

    while [ $progress -le 100 ]; do
        local count=$((progress / 5))
        local bar=$(printf "%-${count}s" | tr ' ' '-')
        printf "\r${BLEU}Progression : [%-20s] %3d%%${RESET}" "$bar" "$progress"
        sleep "$delay"
        progress=$((progress + step))
    done
    echo ""
}

maj_auto() {
    local version=$(cat "$VERSION_FILE" 2>/dev/null || echo "Inconnue")
    local largeur=48

    local ligne1="┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓"
    local ligne2="┃$(center_text "MAJ Automatique   [$(date +'TS %H:%M:%S')]")┃"
    local ligne3="┃$(center_text "Version $version")┃"
    local ligne4="┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
    local largeur_term=$(tput cols)
    centrer_et_afficher() {
        local ligne="$1"
        local couleur="$2"
        local longeur_pure=48
        local gauche=$(( (largeur_term - longeur_pure) / 2 ))
        printf "%*s" "$gauche" ""
        echo -e "${couleur}${ligne}${RESET}"
    }

    clear
    centrer_et_afficher "$ligne1" "$MAGENTA"
    centrer_et_afficher "$ligne2" "$MAGENTA"
    centrer_et_afficher "$ligne3" "$MAGENTA"
    centrer_et_afficher "$ligne4" "$MAGENTA"

    echo -e "${JAUNE}\n[1] Mitahiry ireo doné rehetra...${RESET}"
    progress_bar && git stash > /dev/null

    echo -e "${JAUNE}[2] Telechargement...${RESET}"
    progress_bar && git pull > /dev/null

    echo -e "${JAUNE}[3] Mamemerina ilay donné rehetra...${RESET}"
    progress_bar && git stash pop > /dev/null

    echo -e "\n${VERT}✓ Vita tsara ! Version ampiasaina : $version${RESET}\n"
    echo -ne "${JAUNE}Appuyez sur Entrée pour revenir au menu...${RESET}"
    read -r
}

menu_abonnement() {
    clear
    echo -e "${JAUNE}╔══════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${JAUNE}║                        Abonnement                       ║${RESET}"
    echo -e "${JAUNE}╠══════════════════════════════════════════════════════════╣${RESET}"
    echo -e "${JAUNE}║ 1. Ajouter une clé d'abonnement                         ║${RESET}"
    echo -e "${JAUNE}║ 2. Faire abonnement / inscription (via Telegram)         ║${RESET}"
    echo -e "${JAUNE}║ 0. Retour au menu principal                             ║${RESET}"
    echo -e "${JAUNE}╚══════════════════════════════════════════════════════════╝${RESET}"
    echo -n "Votre choix : "
    read -r subchoix
    case "$subchoix" in
        1)
            clear
            echo -e "${CYAN}=== Ajouter votre clé d'abonnement (ID utilisateur) ===${RESET}"
            read -rp "Collez votre clé d'abonnement (ID) achetée : " key
            read -rp "Entrez votre ID utilisateur : " uid
            if [[ -z "$key" || -z "$uid" ]]; then
                echo -e "${ROUGE}Champs requis non remplis. Annulation.${RESET}"
                sleep 1
                return
            fi
            is_subscription_valid "$uid" "$key"
            api_status=$?
            if [[ "$api_status" == "0" ]]; then
                echo "{\"user_id\":\"$uid\",\"key\":\"$key\"}" > "$USER_ID_FILE"
                echo -e "${VERT}✅ Clé sauvegardée et active.${RESET}"
                echo -e "${CYAN}Votre abonnement sera surveillé automatiquement.${RESET}"
            elif [[ "$api_status" == "2" ]]; then
                echo -e "${ROUGE}Erreur réseau ou serveur injoignable.${RESET}"
            else
                echo -e "${ROUGE}Clé invalide ou expirée.${RESET}"
            fi
            sleep 2
            ;;
        2)
            clear
            echo -e "${CYAN}Vous allez être redirigé vers le bot Telegram d'abonnement...${RESET}"
            termux-open-url "https://t.me/TS_task_bot"
            sleep 2
            ;;
        0)
            ;;
        *)
            echo -e "${ROUGE}Choix invalide.${RESET}"
            sleep 1
            ;;
    esac
}

menu_principal() {
    local menu_lock=0
    local lock_message=""
    while true; do
        clear
        affichage_logo
        afficher_message_animated
        afficher_cadre
        afficher_version

        local user_id="" key=""
        if [[ -f "$USER_ID_FILE" ]]; then
            user_id=$(grep -oE '"user_id"\s*:\s*"([a-zA-Z0-9_-]+)"' "$USER_ID_FILE" | sed -E 's/.*"user_id"\s*:\s*"([^"]+)".*/\1/')
            key=$(grep -oE '"key"\s*:\s*"([a-zA-Z0-9_-]+)"' "$USER_ID_FILE" | sed -E 's/.*"key"\s*:\s*"([^"]+)".*/\1/')
        fi
        is_subscription_valid "$user_id" "$key"
        api_status=$?
        if [[ "$api_status" == "1" ]]; then
            menu_lock=2 # Abonnement expiré/invalide
        elif [[ "$api_status" == "2" ]]; then
            lock_message="${ROUGE}Erreur réseau ou serveur injoignable. Toutes les fonctions sont verrouillées.${RESET}"
            menu_lock=1 # Hors ligne
        else
            menu_lock=0
            lock_message=""
        fi

        afficher_options
        ligne_inferieure

        if [[ $menu_lock -eq 1 ]]; then
            echo -e "$lock_message"
            echo -ne "${JAUNE}Appuyez sur Entrée pour réessayer...${RESET}"
            read -r
            continue
        fi

        if [[ $menu_lock -eq 2 ]]; then
            echo -e "${ROUGE}Votre abonnement est expiré ou invalide. Seules les options 4, 5 et 7 sont disponibles.${RESET}"
        fi

        echo ""
        read -rp "Votre choix : " choix

        if [[ $menu_lock -eq 2 && ! "$choix" =~ ^(4|5|7|0)$ ]]; then
            echo -e "${ROUGE}Accès restreint. Veuillez renouveler votre abonnement pour débloquer toutes les fonctionnalités.${RESET}"
            sleep 2
            continue
        fi

        case $choix in
            1)
                clear
                JETON=$(head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16)
                echo "$JETON" > .session_ts
                ./task.bin ig_compte "$JETON"
                rm -f .session_ts
                ;;
            2)
                JETON=$(head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16)
                echo "$JETON" > .session_ts
                ./task.bin task "$JETON"
                rm -f .session_ts
                ;;
            3)
                clear
                echo -e "${CYAN}Tâche manuelle...${RESET}"
                if [[ -f main/introxt_Instagram.sh ]]; then
                    bash main/introxt_Instagram.sh
                else
                    echo -e "${ROUGE}Fichier manquant.${RESET}"
                fi
                ;;
            4)
                clear
                echo -e "${CYAN}Mise à jour...${RESET}"
                maj_auto
                ;;
            5)
                clear
                echo -e "${VERT}Développeur : TAHIRY TS"
                echo -e "\nfacebook : https://www.facebook.com/profile.php?id=61553579523412"
                echo -e "Email : tahiryandriatefy52@gmail.com"
                echo -e "Version actuelle : ${VERSION}${RESET}"
                echo -ne "${JAUNE}Appuyez sur Entrée pour revenir au menu...${RESET}"
                read -r
                ;;
            6)
                clear
                JETON=$(head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16)
                echo "$JETON" > .session_ts
                ./task.bin automatisation "$JETON"
                rm -f .session_ts
                echo -ne "${JAUNE}Appuyez sur Entrée pour revenir au menu...${RESET}"
                read -r
                ;;
            7)
                menu_abonnement
                ;;
            0)
                echo -e "${BLEU}Fermeture du programme...${RESET}"
                termux-open-url "https://www.facebook.com/profile.php?id=61556805455642"
                cd ~ || exit
                exit 0
                ;;
            *)
                echo -e "${ROUGE}Choix invalide. Veuillez réessayer.${RESET}"
                sleep 1
                ;;
        esac
    done
}

menu_principal

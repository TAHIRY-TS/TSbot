#!/bin/bash
chmod +x ./*.sh ./*.py
clear
tput civis

# === COULEURS ===
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
CODES_CSV_URL="https://raw.githubusercontent.com/tonrepo/tonprojet/main/codes.csv" # À ADAPTER

command -v python3 >/dev/null 2>&1 || { echo -e "${ROUGE}Python3 est requis mais non installé.${RESET}"; exit 1; }
command -v curl >/dev/null 2>&1 || { echo -e "${ROUGE}curl est requis mais non installé.${RESET}"; exit 1; }
command -v bc >/dev/null 2>&1 || { echo -e "${ROUGE}bc est requis mais non installé.${RESET}"; pkg install -y bc; }

VERSION_FILE="version.txt"
VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "Inconnue")

# === LOGO ===
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
    local espace_gauche=$(( ( $(tput cols) - largeur ) / 2))
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
    printf "%*s" "$espace_gauche" ""; echo -e "${MAGENTA}║${RESET} ${ROUGE}0.${RESET} 🔙 Quitter                                       ${MAGENTA}║${RESET}"
}

ligne_inferieure() {
    local espace_gauche=$(( ( $(tput cols) - 55 ) / 2 ))
    printf "%*s" "$espace_gauche" ""
    echo -e "${MAGENTA}╚$(printf '═%.0s' $(seq 1 53))╝${RESET}"
}

is_connected() {
    curl -s --connect-timeout 3 https://www.google.com > /dev/null
    return $?
}

get_user_id() {
    if [[ -f "$USER_ID_FILE" ]]; then
        cat "$USER_ID_FILE" | grep -oE "[a-zA-Z0-9_-]+" | head -1
    else
        echo ""
    fi
}

save_user_id() {
    echo "{\"user_id\":\"$1\"}" > "$USER_ID_FILE"
}

ask_user_id() {
    clear
    echo -e "${CYAN}=== Enregistrement de votre ID utilisateur ===${RESET}"
    while true; do
        read -rp "Entrez votre ID (fourni par le bot Telegram) : " uid
        [[ -z "$uid" ]] && { echo -e "${ROUGE}ID non valide.${RESET}"; continue; }
        if curl -s --connect-timeout 6 "$CODES_CSV_URL" | grep -q "^$uid,"; then
            save_user_id "$uid"
            echo -e "${VERT}✅ ID enregistré !${RESET}"
            sleep 1
            break
        else
            echo -e "${ROUGE}❌ ID introuvable. Faites d'abord l'inscription sur le bot Telegram.${RESET}"
            sleep 1
        fi
    done
}

check_code_valid() {
    local uid="$1"
    local csv
    csv=$(curl -s --connect-timeout 6 "$CODES_CSV_URL")
    [[ -z "$csv" ]] && return 1
    local now
    now=$(date +%s)
    while IFS=, read -r user_id code payment_method payment_number active timestamp _; do
        [[ "$user_id" == "$uid" && "$active" == "validated" ]] || continue
        [[ "$timestamp" =~ ^[0-9]+$ ]] || continue
        if (( now - timestamp < 2592000 )); then
            return 0
        fi
    done <<< "$csv"
    return 1
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
    local center_text() {
        local text="$1"
        local len=${#text}
        local padding=$(( (largeur - len) / 2 ))
        printf "%*s%s%*s" "$padding" "" "$text" "$((largeur - len - padding))" ""
    }

    local ligne1="┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓"
    local ligne2="┃$(center_text "MAJ Automatique   [$(date +'TS %H:%M:%S')]")┃"
    local ligne3="┃$(center_text "Version $version")┃"
    local ligne4="┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
    local largeur_term=$(tput cols)
    local centrer_et_afficher() {
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

menu_principal() {
    clear
    affichage_logo
    afficher_message_animated
    afficher_cadre
    afficher_version

    user_id=$(get_user_id)
    if [[ -z "$user_id" ]]; then
        ask_user_id
        user_id=$(get_user_id)
    fi

    if ! is_connected; then
        echo -e "${ROUGE}⛔️ Accès verrouillé : connexion internet requise.${RESET}"
        sleep 3
        menu_principal
        return
    fi

    if ! check_code_valid "$user_id"; then
        locked=1
    else
        locked=0
    fi

    afficher_options
    ligne_inferieure
    echo ""
    read -rp "Votre choix : " choix

    case $choix in
        1)
            clear
            JETON=$(head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16)
            echo "$JETON" > .session_ts
            ./task.bin ig_compte "$JETON"
            rm -f .session_ts
            menu_principal
            ;;
        2)
            JETON=$(head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16)
            echo "$JETON" > .session_ts
            ./task.bin task "$JETON"
            rm -f .session_ts
            menu_principal
            ;;
        3)
            clear
            echo -e "${CYAN}Tâche manuelle...${RESET}"
            if [[ -f main/introxt_Instagram.sh ]]; then
                bash main/introxt_Instagram.sh
            else
                echo -e "${ROUGE}Fichier manquant.${RESET}"
            fi
            menu_principal
            ;;
        4)
            clear
            echo -e "${CYAN}Mise à jour...${RESET}"
            maj_auto
            menu_principal
            ;;
        5)
            clear
            echo -e "${VERT}Développeur : TAHIRY TS"
            echo -e "\nfacebook : https://www.facebook.com/profile.php?id=61553579523412"
            echo -e "Email : tahiryandriatefy52@gmail.com"
            echo -e "Version actuelle : ${VERSION}${RESET}"
            echo -ne "${JAUNE}Appuyez sur Entrée pour revenir au menu...${RESET}"
            read -r
            menu_principal
            ;;
        6)
            clear
            JETON=$(head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16)
            echo "$JETON" > .session_ts
            ./task.bin automatisation "$JETON"
            rm -f .session_ts
            echo -ne "${JAUNE}Appuyez sur Entrée pour revenir au menu...${RESET}"
            read -r
            menu_principal
            ;;
        0)
            echo -e "${BLEU}Fermeture du programme...${RESET}"
            termux-open-url "https://www.facebook.com/profile.php?id=61556805455642"
            cd ~ || exit
            exit 0
            ;;
        *)
            if [[ "$locked" == "1" && "$choix" != "5" ]]; then
                echo -e "${ROUGE}🔒 Fonctionnalité réservée aux abonnés. Utilisez le bot Telegram pour vous abonner.${RESET}"
                sleep 2
            else
                echo -e "${ROUGE}Choix invalide. Veuillez réessayer.${RESET}"
                sleep 1
            fi
            menu_principal
            ;;
    esac
}

menu_principal

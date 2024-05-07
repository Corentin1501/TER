#!/bin/bash

# Vérifier si le répertoire est spécifié en tant que premier argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <répertoire>"
    exit 1
fi

# Définir le répertoire à décompresser
repertoire="$1"

# Vérifier si le répertoire existe
if [ -d "$repertoire" ]; then
    # Fonction pour décompresser les fichiers tar
    decompress_tar() {
        dossier_decompression="${1%.tar*}-decompressee"
        mkdir -p "$dossier_decompression" && tar -xf "$1" -C "$dossier_decompression" > /dev/null 2>&1
    }

    # Fonction pour décompresser les fichiers zip
    decompress_zip() {
        dossier_decompression="${1%.zip}-decompressee"
        mkdir -p "$dossier_decompression" && unzip -d "$dossier_decompression" "$1" > /dev/null 2>&1
    }

    # Parcourir tous les fichiers dans le répertoire et ses sous-répertoires
    while IFS= read -r -d '' fichier; do
        # Vérifier si le fichier est une archive
        if file -b --mime-type "$fichier" | grep -q 'application/'; then
            # Déterminer le type de l'archive et décompresser en conséquence
            case "$fichier" in
                *.tar.gz|*.tgz|*.tar.bz2|*.tbz|*.tar)
                    decompress_tar "$fichier" ;;
                *.zip)
                    decompress_zip "$fichier" ;;
                *.gz|*.gzip)
                    # Si c'est un fichier gzip, utiliser tar pour décompresser
                    decompress_tar <(gzip -dc "$fichier") ;;
                *)
                    echo "Type d'archive non pris en charge: $fichier" ;;
            esac
        fi
    done < <(find "$repertoire" -type f -print0)

    echo "Décompression terminée."
else
    echo "Le répertoire spécifié n'existe pas."
fi

#!/bin/bash

# Définir le répertoire à décompresser
repertoire="src/exemple/L1/depot-eleves"

# Vérifier si le répertoire existe
if [ -d "$repertoire" ]; then
    # Décompresser les fichiers zip
    find "$repertoire" -type f -name "*.zip" -exec sh -c 'dossier_decompression="${1%.zip}-decompressee"; mkdir -p "$dossier_decompression" && unzip -d "$dossier_decompression" "$1"' _ {} \;

    # Décompresser les fichiers tar
    find "$repertoire" -type f \( -name "*.tar" -o -name "*.tar.gz" -o -name "*.tgz" -o -name "*.tar.bz2" -o -name "*.tbz" \) -exec sh -c 'dossier_decompression="${1%.tar*}-decompressee"; mkdir -p "$dossier_decompression" && tar -xf "$1" -C "$dossier_decompression"' _ {} \;

    echo "Décompression terminée."
else
    echo "Le répertoire spécifié n'existe pas."
fi

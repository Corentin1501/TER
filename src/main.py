import re
import os
import cssutils

from Regles import *

#============ Lecture des fichiers ============

def read_file(filename):
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"ERREUR : Le fichier '{filename}' est introuvable.")
        return None
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier '{filename}': {e}")
        return None

def read_rules(filename):
    rules = []
    with open(filename, 'r') as f:
        for rule_line in f:
            if not rule_line.startswith('#'):
                rules.append(rule_line.strip())
    return rules

def get_css_rules_from_file(css_content):
    # Parser le fichier CSS
    sheet = cssutils.parseString(css_content)

    rules = []

    # Parcourir les règles CSS
    for index, rule in enumerate(sheet):
        if rule.type == rule.STYLE_RULE:
            selectors_string = rule.selectorText

            # Utiliser une expression régulière plus précise pour diviser les sélecteurs
            selectors = re.findall(r'[^,{]+', selectors_string)

            selectors = [s.strip() for s in selectors if s.strip()]  # Enlever les espaces vides et vides

            properties = {}
            for prop in rule.style:
                properties[prop.name] = prop.value

            new_rule = CSS_rule(selectors, properties, index)
            rules.append(new_rule)

    return rules

#============ Decoupage des regles HTML / CSS ============

def get_rules(rules):
    html_rules_in_string = []

    css_rules_in_string = ""
    in_css_rule = False

    logical_rules = []
    logical_rule_stack = []  # Utiliser une pile pour les règles logiques imbriquées
    in_css_in_logic_rule = False

    line_number = 0
    while line_number < len(rules):
        line = rules[line_number].strip()

        # print("\t###### current :", line)

        try:

            if line.startswith("html"):
                if logical_rule_stack:
                    current_html_rules = identify_html_rules([rules[line_number].replace("html ", "")])
                    for rule in current_html_rules:
                        logical_rule_stack[-1].add_rule(rule)  # Ajouter les règles HTML à la règle logique en cours de traitement
                else:
                    html_rules_in_string.append(line.replace("html ", ""))

            elif line.startswith("OR") or line.startswith("AND") or line.startswith("NOT"):

                logic_type = Logical_type.OR if line.startswith("OR") else (Logical_type.AND if line.startswith("AND") else Logical_type.NOT)
                logical_rule = Logical_rule(logic_type, [])
                if logical_rule_stack:
                    logical_rule_stack[-1].add_rule(logical_rule)  # Ajouter la règle logique à la règle logique parente
                else:
                    logical_rules.append(logical_rule)

                logical_rule_stack.append(logical_rule)  # Ajouter la règle logique à la pile

            elif line.startswith("css"):
                if logical_rule_stack:
                    logical_rule_stack[-1].add_css_rule(line[line.find(" ") + 1:])  # Ajouter la règle CSS à la règle logique en cours de traitement
                    # print("ajout de css :", line[line.find(" ") + 1:])
                    in_css_in_logic_rule = True
                else:
                    if in_css_rule:
                        css_rules_in_string += line + "\n"
                    else:
                        in_css_rule = True
                        css_rules_in_string += line[line.find(" ") + 1:] + "\n"

            elif line.startswith('}'):
                if logical_rule_stack:
                    if in_css_in_logic_rule:
                        logical_rule_stack[-1].add_css_rule(line)  # Ajouter la règle CSS à la règle logique en cours de traitement
                        # print("ajout de css :", line)
                        in_css_in_logic_rule = False
                    else:
                        logical_rule_stack.pop()  # Retirer la règle logique du sommet de la pile
                else:
                    if in_css_rule:
                        in_css_rule = False
                        css_rules_in_string += line + "\n"


            else:
                if logical_rule_stack:
                    logical_rule_stack[-1].add_css_rule(line)  # Ajouter la règle CSS à la règle logique en cours de traitement
                    # print("ajout de css :", line)
                else:
                    if in_css_rule:
                        css_rules_in_string += line + "\n"
                    else:
                        css_rules_in_string += "\n"

        except Exception as e:
            print(f"ERREUR lors de l'analyse de la règle à la ligne {line_number + 1}: {e}")

        line_number += 1

    html_rules = identify_html_rules(html_rules_in_string)
    css_rules = get_css_rules_from_file(css_rules_in_string.strip())

    set_css_rules_for_logic(logical_rules)

    return html_rules, css_rules, logical_rules

#============ Affichage des regles ============

def print_all_rules(html_rules, css_rules, logical_rules):
    print("\n=============== Règles ===============\n")
    if len(html_rules) != 0:
        print("---------- HTML ----------\n")
        for rule in html_rules:
            print(rule.to_string())
    else:
        print("---------- Aucune règle HTML ----------\n")

    if len(css_rules) != 0:
        print("---------- CSS ----------\n")
        for rule in css_rules:
            print(rule.to_string())
    else:
        print("---------- Aucune règle CSS ----------\n")

    if len(logical_rules) != 0:
        print("---------- Logique ----------\n")
        for rule in logical_rules:
            print(rule.to_string())
    else:
        print("---------- Aucune règle Logique ----------\n")

    print("\n======================================\n")

#============ Identification du type des regles HTML ============

def identify_html_rules(rules):

    rules_identified = []
    
    for rule in rules:
        current_tags = []   # on va noter chaque balise une à une
        rule_index = {}     # on va noter les règles liés aux balises

        new_rule = HTML_Rule(current_tags, rule_index, len(rules_identified))

        mots = rule.split(" ")
        i = 0
        # On parcours chaque mot pour identifier les regles 
        while i < len(mots):
            #=========== Attribut ===========

            if mots[i].startswith('['):
                attributs = {}
                isLastAttribut = False
                # On récupère les attributs et leurs valeurs
                while not isLastAttribut and i < len(mots):
                    isLastAttribut = mots[i].endswith(']')

                    mot_clean = mots[i].strip('[').strip(']')
                    attribut = mot_clean.split('=')
                    attributs[attribut[0]] = attribut[1].strip('"')
                    i += 1
    
                new_little_rule = Attribut(attributs)
                new_rule.add_secondary_rule(new_little_rule,len(current_tags)-1)

            #=========== Valeur ===========

            elif mots[i].startswith('"'):   

                value = ""
                isEndOfValue = False
                while not isEndOfValue and i < len(mots):
                    # print("\tcurrent value", mots[i])
                    isEndOfValue = mots[i].endswith('"')
                    value += " " + mots[i].strip('"')
                    i += 1

                new_little_rule = Value(value[1:]) # on enleve le premier " " de 'value'
                new_rule.add_secondary_rule(new_little_rule,len(current_tags)-1)

            #=========== Balise ===========

            else :  
                current_tags.append(mots[i])
                i += 1

        if not mots[-1].endswith(']') and not mots[-1].endswith('"') and current_tags:
            new_rule.balises = current_tags.copy()
            rules_identified.append(new_rule)
        else:
            rules_identified.append(new_rule)


    return rules_identified

def set_content_rules_for_all_rules(html_content, html_rules_identified, css_file_rules, css_rules_identified, logical_rules):
    for html_rule in html_rules_identified:
        html_rule.set_content(html_content)

    for css_rule in css_rules_identified:
        css_rule.set_content(css_file_rules)

    set_content_for_logic_rules(html_content, css_file_rules, logical_rules)

def set_content_for_logic_rules(html_content, css_file_rules, logical_rules):
    for logic_rule in logical_rules:
        for rule_concerned in logic_rule.rules_concerned:
            if isinstance(rule_concerned, HTML_Rule):
                rule_concerned.set_content(html_content)
            elif isinstance(rule_concerned, CSS_rule):
                rule_concerned.set_content(css_file_rules)
            elif isinstance(rule_concerned, Logical_rule):
                set_content_for_logic_rules(html_content, css_file_rules, [rule_concerned])

def set_css_rules_for_logic(logical_rules):
    # pour chacune des regles logiques
    for logic_rule in logical_rules:
        # si la regle a du css
        if logic_rule.css_rules_string != "":
            # on l'identifie et on lui ajoute les nouvelles regles
            for css_rule in get_css_rules_from_file(logic_rule.css_rules_string):
                logic_rule.add_rule(css_rule)
        # si elle a des regles logique en elle, on fait pareil pour elles
        for rule in logic_rule.rules_concerned:
            if isinstance(rule, Logical_rule):
                set_css_rules_for_logic([rule])

#============ Vérification des regles HTML / CSS ============

def verif_all_html_rules(regles):
    rules_not_respected = []
    for i in range(len(regles)):
        try:
            if not regles[i].verif_rule():
                rules_not_respected.append(regles[i])
        except Exception as e:
            print(f"ERREUR lors de la vérification de la règle HTML {i + 1}: {e}")
    print()
    if len(rules_not_respected) != 0:
        print("❌  --------- HTML non respectées --------- ❌ ")
        for rule in rules_not_respected:
            print(rule.to_string())
    else:
        print("✅ ---------   HTML OK   --------- ✅\n")
    return rules_not_respected

def verif_all_css_rules(css_rules):
    rules_not_respected = []
    for i in range(len(css_rules)):
        try:
            if not css_rules[i].verif_rule():
                rules_not_respected.append(css_rules[i])
        except Exception as e:
            print(f"ERREUR lors de la vérification de la règle CSS {i + 1}: {e}")
    print()
    if len(rules_not_respected) != 0:
        print("❌  --------- CSS non respectées --------- ❌ ")
        for rule in rules_not_respected:
            print(rule.to_string())
    else:
        print("✅ ---------   CSS OK    --------- ✅\n")

def verif_all_logical_rules(logical_rules):
    rules_not_respected = []
    for i in range(len(logical_rules)):
        try:
            if not logical_rules[i].verif_rule():
                rules_not_respected.append(logical_rules[i])
        except Exception as e:
            print(f"ERREUR lors de la vérification de la règle Logique {i + 1}: {e}")
    print()
    if len(rules_not_respected) != 0:
        print("❌  --------- Logique non respectées --------- ❌ ")
        for rule in rules_not_respected:
            print(rule.to_string())
    else:
        print("✅ --------- LOGIQUES OK --------- ✅\n")

def verif_all_rules(html_rules, css_rules, logical_rules):
    if len(html_rules) != 0:
        verif_all_html_rules(html_rules)
    if len(css_rules) != 0:
        verif_all_css_rules(css_rules)
    if len(logical_rules) != 0:
        verif_all_logical_rules(logical_rules)

#============ Process pair of files ============

def process_pair(html_file, css_file, rules_file):
    html_content = read_file(html_file)
    css_content = read_file(css_file)
    css_file_rules = get_css_rules_from_file(css_content)
    html_rules, css_rules, logical_rules = get_rules(read_rules(rules_file))
    set_content_rules_for_all_rules(html_content, html_rules, css_file_rules, css_rules, logical_rules)

    # verif_all_rules(html_rules, css_rules, logical_rules)
    num_respected_rules = count_respected_rules(html_rules, css_rules, logical_rules)
    return num_respected_rules

def count_respected_rules(html_rules, css_rules, logical_rules):
    total_respected_rules = 0
    for rule in html_rules:
        if rule.verif_rule():
            total_respected_rules += 1
    for rule in css_rules:
        if rule.verif_rule():
            total_respected_rules += 1
    for rule in logical_rules:
        if rule.verif_rule():
            total_respected_rules += 1
    return total_respected_rules

def get_file_pairs(folder_path):
    html_files = []
    css_files = []
    file_pairs = []

    # Parcours des fichiers dans le dossier spécifié
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)  # Chemin absolu du fichier

        # Filtrage des fichiers HTML et CSS
        if file_name.endswith(".html"):
            html_files.append(file_path)
        elif file_name.endswith(".css"):
            css_files.append(file_path)

    # Association des fichiers HTML et CSS
    for html_file in html_files:
        html_base_name = os.path.splitext(html_file)[0]  # Nom de base du fichier HTML (sans extension)
        css_file_name = html_base_name + ".css"  # Nom du fichier CSS correspondant
        css_file_path = os.path.join(folder_path, css_file_name)  # Chemin absolu du fichier CSS
        if css_file_path in css_files:
            file_pairs.append((html_file, css_file_path))  # Ajout de la paire de fichiers

    return file_pairs


#============ Main ============

def main():

    #*********** Noms des fichiers en ligne de commandes ***********

    # rules_file = input("Fichier de règles : ")
    # html_file = input("Fichier HTML : ")
    # css_file = input("Fichier CSS : ")

    #*********** Ou directement ici ***********

    rules_file = "src/exemple/regles.txt"
    html_file = "src/exemple/L1/index.html"

    # rules_file = "src/exemple/regles2.txt"
    # html_file = "src/exemple/gros_fichier_html.html"
    # css_file = "src/exemple/gros_css.css"

    css_file = "src/exemple/L1/style.css"

    folder_path = "src/fichiers/"

    #*********** Affichage des règles ***********

    display_rules = True

    #*********** Faire la vérification ***********

    verif_rules = True
    
    #*********** Lire les fichiers ***********

    files_pair = get_file_pairs(folder_path)

    print(files_pair)

    for html_file, css_file in files_pair:
        nRules = process_pair(html_file, css_file, rules_file)
        print(nRules, "règles respectées")




    # # HTML
    # html_content = read_file(html_file)

    # # CSS
    # css_content = read_file(css_file)
    # css_file_rules = get_css_rules_from_file(css_content)
    
    # # Règles
    # html_rules, css_rules, logical_rules = get_rules(read_rules(rules_file))

    # #*********** Attribution des fichiers correspondant aux règles ***********

    # set_content_rules_for_all_rules(html_content, html_rules, css_file_rules, css_rules, logical_rules)

    #*********** Affichage ***********

    # if display_rules:
    #     print_all_rules(html_rules, css_rules, logical_rules)


    # #*********** Verification ***********

    # if verif_rules:
    #     verif_all_rules(html_rules, css_rules, logical_rules)



if __name__ == "__main__":
    main()

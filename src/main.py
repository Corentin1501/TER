from Regles import *
import re
import os

import cssutils

#============ Lecture des fichiers ============

def read_file(filename):
    if os.path.isfile(filename) and (filename.endswith(".html") or filename.endswith(".css")) and os.path.getsize(filename) < 1000000000:
        with open(filename, 'r') as f:
            content = f.read()
        return content
    else:
        extension = filename.split(".")[-1]
        print("\nErreur : Les fichiers doivent être un .html ou .css (extension : ." + extension + ")")
        return ""

# Lis le fichier de règles et retourne chaque ligne dans un tableau en ignorant les commentaires
def read_rules(filename):
    if os.path.isfile(filename) and filename.endswith(".txt") and os.path.getsize(filename) < 1000000000:
        rules = []
        with open(filename, 'r') as f:
            for rule_line in f:
                if not rule_line.startswith('#'):
                    rules.append(rule_line.strip())
        return rules
    else:
        print("\nErreur : Le fichier de règle doit être un .txt (extension :",filename[-4:],")")
        return []

# Parse un fichier CSS en string et retourne chaque règles CSS dans un tableau
def get_css_rules_from_file(css_content):
    # Parser le fichier CSS
    sheet = cssutils.parseString(css_content, validate=False)  # Ignorer les erreurs de validation

    rules = []

    # Parcourir les règles CSS
    for index, rule in enumerate(sheet):
        if rule.type == rule.STYLE_RULE:
            selectors_string = rule.selectorText

            # Utiliser une expression régulière plus précise pour diviser les sélecteurs
            selectors = re.findall(r'[^,{]+', selectors_string)

            selectors = [s.strip() for s in selectors if s.strip()]  # Enlever les espaces vides

            properties = {}
            for prop in rule.style:
                properties[prop.name] = prop.value

            new_rule = CSS_rule(selectors, properties)
            rules.append(new_rule)

    return rules

#============ Decoupage des regles HTML / CSS ============

# Lis chaque règles et identifie son type pour retourner une liste de règles HTML, CSS et Logiques
def get_rules(rules):
    html_rules_in_string = []

    css_rules_in_string = ""
    in_css_rule = False

    logical_rules = []
    logical_rule_pile = []  # Utiliser une pile pour les règles logiques imbriquées
    is_in_css_in_logic_rule = False

    line_number = 0
    while line_number < len(rules):
        line = rules[line_number].strip()

        #=========== HTML ===========

        if line.startswith("html"):
            # Si on est dans une règle logique
            if logical_rule_pile:
                current_html_rules = identify_html_rules([rules[line_number].replace("html ", "")])
                logical_rule_pile[-1].add_rule(current_html_rules[0])  # Ajouter les règles HTML à la règle logique en cours de traitement
            else:
                html_rules_in_string.append(line.replace("html ", ""))

        #=========== Logique ===========

        elif line.startswith("OR") or line.startswith("AND") or line.startswith("NOT"):
            logic_type = Logical_type.OR if line.startswith("OR") else (Logical_type.AND if line.startswith("AND") else Logical_type.NOT)
            logical_rule = Logical_rule(logic_type, [])
            # Si on est dans une règle logique
            if logical_rule_pile:
                logical_rule_pile[-1].add_rule(logical_rule)  # Ajouter la règle logique à la règle logique parente
            else:
                logical_rules.append(logical_rule)

            logical_rule_pile.append(logical_rule)  # Ajouter la règle logique à la pile

        #=========== CSS ===========
        
        elif line.startswith("css"):
            # Si on est dans une règle logique
            if logical_rule_pile:
                logical_rule_pile[-1].add_css_rule(line[line.find(" ") + 1:])  # Ajouter la règle CSS à la règle logique en cours de traitement
                is_in_css_in_logic_rule = True
            else:
                if in_css_rule:
                    css_rules_in_string += line + "\n"
                else:
                    in_css_rule = True
                    css_rules_in_string += line[line.find(" ") + 1:] + "\n"

        #=========== Fin de la Logique ===========

        elif line.startswith(')'):
            if logical_rule_pile:
                logical_rule_pile.pop()  # Retirer la règle logique du sommet de la pile

        #=========== Fin du CSS ===========

        elif line.startswith('}'):
            # Si on est dans une règle logique
            if is_in_css_in_logic_rule:
                logical_rule_pile[-1].add_css_rule(line)  # Ajouter la règle CSS à la règle logique en cours de traitement
                is_in_css_in_logic_rule = False
            else:
                if in_css_rule:
                    in_css_rule = False
                    css_rules_in_string += line + "\n"

        #=========== Ligne quelconque ===========
        
        else:
            if logical_rule_pile:
                logical_rule_pile[-1].add_css_rule(line)  # Ajouter la règle CSS à la règle logique en cours de traitement
            else:
                if in_css_rule:
                    css_rules_in_string += line + "\n"
                else:
                    css_rules_in_string += "\n"

        line_number += 1

    # On identifie chaque règles pour retourner des instances de règles HTML, CSS ou Logiques
    html_rules = identify_html_rules(html_rules_in_string)
    css_rules = get_css_rules_from_file(css_rules_in_string.strip())
    set_css_rules_for_logic(logical_rules)

    return html_rules, css_rules, logical_rules

#============ Affichage des regles ============

def print_all_rules(html_rules, css_rules, logical_rules):
    print("\n=============== Règles ===============\n")
    if len(html_rules) != 0:
        print("################ HTML ################\n")
        for rule in html_rules:
            print(rule.to_string())
    else:
        print("################ Aucune règle HTML ################\n")

    if len(css_rules) != 0:
        print("################ CSS ################\n")
        for rule in css_rules:
            print(rule.to_string())
    else:
        print("################ Aucune règle CSS ################\n")

    if len(logical_rules) != 0:
        print("################ Logique ################\n")
        for rule in logical_rules:
            print(rule.to_string())
    else:
        print("################ Aucune règle Logique ################\n")

    print("\n======================================\n")

#============ Identification du type des regles HTML ============

def identify_html_rules(rules):

    rules_identified = []
    
    for rule in rules:
        current_tags = []   # on va noter chaque balise une à une
        rule_index = {}     # on va noter les règles liés aux balises

        new_rule = HTML_rule(current_tags, rule_index)

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

                    mot_clean = mots[i].strip('[]')
                    attribut = mot_clean.split('=')
                    if attribut[0] in ['class','rel','style'] and not isLastAttribut:
                        isLastClass = False
                        classes = "" + attribut[1]
                        i += 1        
                        while not isLastClass and i < len(mots):
                            isLastClass = mots[i].endswith('"')
                            classes += " " + mots[i]
                            attributs[attribut[0]] = classes.strip('"]')
                            i += 1        

                    else :
                        attributs[attribut[0]] = attribut[1].strip('"')
                        i += 1
    
                new_little_rule = Attribut(attributs)
                new_rule.add_secondary_rule(new_little_rule,len(current_tags)-1)

            #=========== Valeur ===========

            elif mots[i].startswith('"'):   

                value = ""
                isEndOfValue = False
                while not isEndOfValue and i < len(mots):
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
            if isinstance(rule_concerned, HTML_rule):
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

def verif_all_html_rules(regles, display_errors):
    rules_not_respected = []
    for i in range(len(regles)):
        if not regles[i].verif_rule():
            rules_not_respected.append(regles[i])
    if display_errors:
        print()
        if len(rules_not_respected) != 0:
            print("❌  ========= HTML non respectées ========= ❌ ")
            for rule in rules_not_respected:
                print("➡️" + rule.to_string())
        else:
            print("✅ =========   HTML OK   ========= ✅\n")
    return rules_not_respected

def verif_all_css_rules(css_rules, display_errors):
    rules_not_respected = []
    for i in range(len(css_rules)):
        if not css_rules[i].verif_rule():
            rules_not_respected.append(css_rules[i])
    if display_errors:
        print()
        if len(rules_not_respected) != 0:
            print("❌  ========= CSS non respectées ========= ❌ ")
            for rule in rules_not_respected:
                print("➡️" + rule.to_string())
        else:
            print("✅ =========   CSS OK    ========= ✅\n")
    return rules_not_respected

def verif_all_logical_rules(logical_rules, display_errors):
    rules_not_respected = []
    for i in range(len(logical_rules)):
        if not logical_rules[i].verif_rule():
            rules_not_respected.append(logical_rules[i])
    if display_errors:
        print()
        if len(rules_not_respected) != 0:
            print("❌  ========= Logique non respectées ========= ❌ ")
            for rule in rules_not_respected:
                print("➡️" + rule.to_string())
        else:
            print("✅ ========= LOGIQUES OK ========= ✅\n")
    return rules_not_respected

def verif_all_rules(html_rules, css_rules, logical_rules, display_errors):
    html_rules_not_respected = []
    css_rules_not_respected = []
    logic_rules_not_respected = []
    if len(html_rules) != 0:
        html_rules_not_respected = verif_all_html_rules(html_rules, display_errors)
    if len(css_rules) != 0:
        css_rules_not_respected = verif_all_css_rules(css_rules, display_errors)
    if len(logical_rules) != 0:
        logic_rules_not_respected = verif_all_logical_rules(logical_rules, display_errors)

    return len(html_rules_not_respected) + len(css_rules_not_respected) + len(logic_rules_not_respected)

#============ Traitement plusieurs élèves ============

def get_student_files(directory_path):
    # Dictionnaire pour stocker les liens entre élèves et fichiers HTML/CSS
    liens_eleves_fichiers = {}

    # Fonction récursive pour trouver les fichiers HTML et CSS
    def find_html_css_file(chemin_dossier):
        chemin_html = ""
        chemin_css = ""
        for racine, _, fichiers in os.walk(chemin_dossier):
            for fichier in fichiers:
                if fichier.endswith('.html'):
                    chemin_html = os.path.join(racine, fichier)
                elif fichier.endswith('.css'):
                    chemin_css = os.path.join(racine, fichier)
        return chemin_html, chemin_css

    # Obtention de la liste des dossiers d'élèves et tri par ordre alphabétique
    dossiers_eleves = sorted(os.listdir(directory_path))

    # Parcours des dossiers des élèves dans l'ordre alphabétique
    for dossier_eleve in dossiers_eleves:
        nom_prenom = dossier_eleve.split('_')[0]
        chemin_dossier_eleve = os.path.join(directory_path, dossier_eleve)

        if os.path.isdir(chemin_dossier_eleve):
            chemin_html, chemin_css = find_html_css_file(chemin_dossier_eleve)
            if chemin_html == "":
                print("Erreur : aucun fichier HTML trouvé pour", nom_prenom)
            if chemin_css == "":
                print("Erreur : aucun fichier CSS  trouvé pour", nom_prenom)
            liens_eleves_fichiers[nom_prenom] = (chemin_html, chemin_css)
        else:
            print(chemin_dossier_eleve, "n'est pas un dossier")

    return liens_eleves_fichiers

def verif_student(student_file, html_rules, css_rules, logical_rules, display_errors):
    # on récupère les fichiers 
    html_content = read_file(student_file[0])
    css_content = read_file(student_file[1])
    css_file_rules = get_css_rules_from_file(css_content)
    # on attributs leurs contenus aux règles 
    set_content_rules_for_all_rules(html_content, html_rules, css_file_rules, css_rules, logical_rules)
    # on retourne le nombre de regles valides 
    return verif_all_rules(html_rules, css_rules, logical_rules, display_errors)

def verif_all_students(students_files, html_rules, css_rules, logical_rules, display_errors):
    total_rules = len(html_rules) + len(css_rules) + len(logical_rules)

    total_note_students = 0

    for nom_prenom, fichiers in students_files.items():
        # Si le HTML et le CSS ne manque pas 
        if fichiers[0] != "" and fichiers[1] != "":
            number_of_rules_not_respected = verif_student(fichiers, html_rules, css_rules, logical_rules, display_errors)
            note = total_rules - number_of_rules_not_respected

            total_note_students += note

            # Si l'élève a 0, on le fait remarquer
            if note == 0:
                print(note, "/", total_rules, "  ⬅️ ❗ ", nom_prenom)
            else:
                print(note, "/", total_rules, "  ⬅️  ", nom_prenom)
        else:
            print("⚠️", nom_prenom, "⚠️\tfichiers HTML/CSS manquants")


    return total_note_students / len(students_files)

#============ Main ============

def main():

    #*********** Récupération des paramètres en ligne de commandes ***********
        #*********** Affichage  ***********

    display_rules_string = input("Afficher les règles (O/N) : ")
    display_rules = display_rules_string.lower() == "o"
# 
    display_errors_string = input("Afficher les erreurs des étudiants (O/N) : ")
    display_errors = display_errors_string.lower() == "o"
# 
    # display_rules = False
    # display_errors = False

    #*********** Fichiers à traiter ***********

    rules_file = "src/fichiers_a_traiter/reglesJMR_v2.txt"
    student_files_directory = "src/fichiers_a_traiter/fichiers_eleves"
    # rules_file = "src/fichiers_a_traiter/regles-test-perf.txt"
    # student_files_directory = "src/fichiers_a_traiter/test-perfs"

    #*********** Faire la vérification ***********

    verif_rules = True

    #*********** Lire les fichiers ***********
    
    # Règles
    html_rules, css_rules, logical_rules = get_rules(read_rules(rules_file))

    student_files = get_student_files(student_files_directory)

    #*********** Affichage ***********

    if display_rules:
        print_all_rules(html_rules, css_rules, logical_rules)

    #*********** Verification ***********

    if verif_rules:
        total_rules = len(html_rules) + len(css_rules) + len(logical_rules)
        moyenne = verif_all_students(student_files, html_rules, css_rules, logical_rules, display_errors)
        print("\n\nMoyenne = {0:.2f} /".format(moyenne), total_rules," \t(",len(student_files),"élève(s) )") 
        print("        = {0:.2f} / 20".format(moyenne * 20 / total_rules)) 

if __name__ == "__main__":
    main()

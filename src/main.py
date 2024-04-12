from Regles import *
import re
#============ Lecture des fichiers ============

def read_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    return content

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
    html_rules = []
    css_rules = ""

    # Variable pour garder une trace si nous sommes dans une règle CSS
    in_css_rule = False

    for line_number in range(len(rules)):
        line = rules[line_number].strip()  # Supprimer les espaces inutiles au début et à la fin de la ligne
        if line.startswith("html"):
            html_rules.append(line.replace("html ", ""))

        elif line.startswith("css"):
            # Si nous sommes déjà dans une règle CSS, cela signifie que nous devons ajouter la ligne à la règle actuelle
            if in_css_rule:
                css_rules += line + "\n"
            else:
                # Sinon, nous entrons dans une nouvelle règle CSS
                in_css_rule = True
                css_rules += line[line.find(" ") + 1:] + "\n"
        elif line.startswith('}'):
            css_rules += line + "\n"
            in_css_rule = False
        else:
            # Si nous sommes dans une règle CSS, nous ajoutons simplement la ligne à la règle en cours
            if in_css_rule:
                css_rules += line + "\n"
            else:
                css_rules += "\n"


    return html_rules, css_rules.strip()

def print_all_rules(html_rules, css_rules):
    print("\n=============== Règles ===============\n")
    if len(html_rules) != 0:
        print("---------- HTML ----------\n")
        for rule in html_rules:
            print(rule.to_string())
    else:
        print("Aucune règle HTML\n")

    if len(css_rules) != 0:
        print("---------- CSS ----------\n")
        for rule in css_rules:
            print(rule.to_string())
    else:
        print("Aucune règle CSS")

    print("\n======================================\n")

#============ Identification du type des regles HTML ============

def identify_html_rules(rules):

    rules_identified = []
    
    for rule in rules:
        current_tags = []   # on va noter chaque balise une à une
        rule_index = {}     # on va noter les règles liés aux balises

        new_rule = Rule(current_tags, rule_index, len(rules_identified))

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

#============ Vérification des regles HTML / CSS ============

def verif_all_html_rules(html_content, regles):
    rules_not_respected = []
    for i in range(len(regles)):
        if regles[i].verif_rule(html_content):
            print("Règle HTML",i,":  OK")
        else:
            print("Règle HTML",i,":  ❌")
            rules_not_respected.append(regles[i])
    print()
    if len(rules_not_respected) != 0:
        print("⚠️  Règles HTML non respectées ⚠️ ")
        for rule in rules_not_respected:
            print(" - " + rule.to_string())
    return rules_not_respected

def verif_all_css_rules(css_file_rules, css_rules):
    rules_not_respected = []
    for i in range(len(css_rules)):
        if css_rules[i].verif_rule(css_file_rules):
            print("Règle CSS",i,":  OK")
        else:
            print("Règle CSS",i,":  ❌")
            rules_not_respected.append(css_rules[i])
    print()
    if len(rules_not_respected) != 0:
        print("⚠️  Règles CSS non respectées ⚠️ ")
        for rule in rules_not_respected:
            print(" - " + rule.to_string())

#============ Main ============

def main():
    # Récupérer les noms des fichiers
    # rules_file = input("Fichier de règles : ")
    # html_file = input("Fichier HTML : ")
    # css_file = input("Fichier CSS : ")
    rules_file = "src/regles.txt"
    html_file = "src/index.html"
    css_file = "src/style.css"
    
    # Lire les contenus des fichiers
    html_content = read_file(html_file)
    css_content = read_file(css_file)
    css_file_rules = get_css_rules_from_file(css_content)


    html_rules, css_rules = get_rules(read_rules(rules_file))

    html_rules_identified = identify_html_rules(html_rules)
    css_rules_identified = get_css_rules_from_file(css_rules)

    # print_all_rules(html_rules_identified, css_rules_identified)

    verif_all_html_rules(html_content, html_rules_identified)
    verif_all_css_rules(css_file_rules, css_rules_identified)

if __name__ == "__main__":
    main()

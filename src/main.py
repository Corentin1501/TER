from Regles import *

#============ Lecture des fichiers ============

def read_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    return content

def read_rules(filename):
    regles = []
    with open(filename, 'r') as f:
        for rule_line in f:
            if not rule_line.startswith('#'):
                regles.append(rule_line.strip())
    return regles

#============ Decoupage des regles HTML / CSS ============

def get_html_rules(regles):
    regles_html = []
    for regle in regles:
        if regle.startswith("html"):
            regles_html.append(regle.replace("html ", ""))
    return regles_html

def print_all_rules(regles):
    print("\n--------------- Règles ---------------\n")
    for i in range(len(regles)):
        regles[i].print_rule()
        print("")
    print("--------------------------------------\n")

def print_all_main_rules(regles):
    print("\n--------------- Règles ---------------\n")
    for rule in regles:
        print(rule.to_string())
    print("--------------------------------------\n")

#============ Identification du type des regles HTML ============

def identify_rules(regles):
    instances_rules = []
    for regle in regles:

        mots = regle.split(" ")
        current_balises = []    # on va noter chaque balise une à une
        i = 0

        new_big_rule = Big_rule(current_balises, [], len(instances_rules))

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

                nouvelle_regle = Attribute_rule(current_balises.copy(), attributs)
                new_big_rule.add_secondary_rules(nouvelle_regle)

            #=========== Valeur ===========

            elif mots[i].startswith('"'):   

                value = ""
                isEndOfValue = False
                while not isEndOfValue and i < len(mots):
                    # print("\tcurrent value", mots[i])
                    isEndOfValue = mots[i].endswith('"')
                    value += " " + mots[i].strip('"')
                    i += 1

                nouvelle_regle = Value_rule(current_balises.copy(),value[1:]) # on enleve le premier " " de 'value'
                new_big_rule.add_secondary_rules(nouvelle_regle)

            #=========== Balise ===========

            else :  
                current_balises.append(mots[i])
                i += 1

        if not mots[-1].endswith(']') and not mots[-1].endswith('"') and current_balises:
            new_big_rule.balises = current_balises.copy()
            instances_rules.append(new_big_rule)
        else:
            instances_rules.append(new_big_rule)


    return instances_rules


def identify_main_rules(rules):

    main_rules = []
    for rule in rules:
        current_tags = []   # on va noter chaque balise une à une
        rule_index = {}     # on va noter les règles liés aux balises

        new_main_rule = Main_rule(current_tags, rule_index, len(main_rules))

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
    
                new_rule = Attribut(attributs)
                new_main_rule.add_secondary_rule(new_rule,len(current_tags)-1)

            #=========== Valeur ===========

            elif mots[i].startswith('"'):   

                value = ""
                isEndOfValue = False
                while not isEndOfValue and i < len(mots):
                    # print("\tcurrent value", mots[i])
                    isEndOfValue = mots[i].endswith('"')
                    value += " " + mots[i].strip('"')
                    i += 1

                new_rule = Value(value[1:]) # on enleve le premier " " de 'value'
                new_main_rule.add_secondary_rule(new_rule,len(current_tags)-1)

            #=========== Balise ===========

            else :  
                current_tags.append(mots[i])
                i += 1

        if not mots[-1].endswith(']') and not mots[-1].endswith('"') and current_tags:
            new_main_rule.balises = current_tags.copy()
            main_rules.append(new_main_rule)
        else:
            main_rules.append(new_main_rule)


    return main_rules

#============ Vérification des regles HTML ============

def verif_all_html_rules(html_content, regles):
    rules_not_respected = []
    for i in range(len(regles)):
        if regles[i].verif_rule(html_content):
            print("Règle ",i,":  OK")
        else:
            print("Règle ",i,":  ❌")
            rules_not_respected.append(regles[i])
    print()
    if len(rules_not_respected) != 0:
        print("⚠️  Règles non respectées ⚠️ ")
        for rule in rules_not_respected:
            print(" - " + rule.to_string())
            # rule.print_rule()

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

    regles = read_rules(rules_file)
    
    # html_rules = identify_rules(get_html_rules(regles))

    html_main_rules = identify_main_rules(get_html_rules(regles))

    # print_all_rules(html_rules)

    print_all_main_rules(html_main_rules)

    verif_all_html_rules(html_content, html_main_rules)

if __name__ == "__main__":
    main()

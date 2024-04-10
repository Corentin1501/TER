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
        print(i, end=" ")
        regles[i].print_rule()
        print("")
    print("--------------------------------------\n")

#============ Identification du type des regles HTML ============

def identify_rules(regles):
    instances_rules = []
    for regle in regles:

        mots = regle.split(" ")
        current_balises = []    # on va noter chaque balise une à une
        i = 0

        # print()

        # On parcours chaque mot pour identifier les regles 
        while i < len(mots):
            # print("Balises :", balises)

            if mots[i].startswith('['):     # ce sera des attributs
                attributs = {}
                isLastAttribut = False
                # On récupère les attributs et leurs valeurs
                while not isLastAttribut and i < len(mots):
                    # print("\tcurrent attribut", mots[i])
                    isLastAttribut = mots[i].endswith(']')

                    mot_clean = mots[i].strip('[').strip(']')
                    attribut = mot_clean.split('=')
                    attributs[attribut[0]] = attribut[1].strip('"')
                    i += 1
                # print("New Attribute rule with", attributs, ":", balises)
                nouvelle_regle = Attribute_rule(current_balises, attributs)
                instances_rules.append(nouvelle_regle)
                print("new rule added : ", end="")
                nouvelle_regle.print_rule()

            elif mots[i].startswith('"'):   # ce sera une valeur

                value = ""
                isEndOfValue = False
                while not isEndOfValue and i < len(mots):
                    # print("\tcurrent value", mots[i])
                    isEndOfValue = mots[i].endswith('"')
                    value += " " + mots[i].strip('"')
                    i += 1
                nouvelle_regle = Value_rule(current_balises,value[1:])
                instances_rules.append(nouvelle_regle) # on enleve le premier " " de 'value'
                print("new rule added : ", end="")
                nouvelle_regle.print_rule()
            else :                          # sinon c'est une balise
                # print("current balise", mots[i])
                current_balises.append(mots[i])
                i += 1

        if not mots[-1].endswith(']') and not mots[-1].endswith('"') and current_balises:
            nouvelle_regle = Balise_rule(current_balises)
            instances_rules.append(nouvelle_regle)
            print("new rule added : ", end="")
            nouvelle_regle.print_rule()

    return instances_rules

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
            print(" -", end="")
            rule.print_rule()

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
    
    html_rules = identify_rules(get_html_rules(regles))

    print_all_rules(html_rules)

    verif_all_html_rules(html_content, html_rules)

if __name__ == "__main__":
    main()

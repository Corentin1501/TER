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
        isBaliseRule = False
        isValeurRule = False
        isAttributeRule = False
        mots = regle.split(" ")

        # On parcours chaque mot pour identifier les regles 
        startsOfValue = 0
        for i in range(len(mots)):
            if mots[i].startswith('"'):     # Regle de valeur
                startsOfValue = i
                isValeurRule = True
                break
            elif mots[i].startswith('['):   # Regle d'attribut
                startsOfValue = i
                isAttributeRule = True
                break


        isBaliseRule = not isAttributeRule  # Regle de Balise si pas d'attribut

        if isValeurRule:
            value = ""
            for j in range(startsOfValue, len(mots)):
                value += " " + mots[j].strip('"')
            instances_rules.append(Value_rule(mots[0:startsOfValue],value[1:]))

        elif isBaliseRule:
            instances_rules.append(Balise_rule(mots))

        elif isAttributeRule:
            attributs = {}
            # On récupère les attributs et leurs valeurs
            for i in range(startsOfValue,len(mots)):
                mot_clean = mots[i].strip('[').strip(']')
                if mot_clean != "": # si le mot n'était pas juste '[' ou ']'
                    attribut = mot_clean.split('=')
                    attributs[attribut[0]] = attribut[1].strip('"')
            instances_rules.append(Attribute_rule(mots[0:startsOfValue], attributs))

        else:
            print("Erreur : regle non reconnue : " + regle)

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

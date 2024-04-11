from bs4 import BeautifulSoup
import re

# import cssutils

def attrs_to_string(attributs):
    out = "{"
    for att, valeur in attributs.items():
        out += "'" + str(att) + "'='" + str(valeur) + "', "
    return out[:-2] + "}"


#============ Classe mère ============

class Rule:
    pass

#============ Verification de la valeur d'une balise ============


class Value_rule(Rule):
    balises = []
    value = ""

    def __init__(self, balise, value):
        self.balises = balise
        self.value = value

    def print_rule(self):
        print(" where " + self.balises[-1] + " = '" + self.value, end="'\n")

    def verif_rule(self, html_content):
        def verif_recursive(tag, balise_index):
            if tag.name == self.balises[balise_index]:
                if balise_index == 0:
                    return True
                else:
                    return verif_recursive(tag.parent, balise_index - 1)
            else:
                return False

        parser = BeautifulSoup(html_content, 'html.parser')
        tags = parser.find_all(self.balises[-1], string=self.value)  # on cherche le tag avec cette valeur

        # Si aucun tag n'existe, alors on peut déjà retourner False
        if tags is None :
            return False
        # Sinon, on va regarder si le tag a la bonne hiérarchie
        else:
            balise_index = len(self.balises) -1
            for tag in tags:
                if verif_recursive(tag,balise_index):
                    return True
            return False


#============ Verification des valeurs des attributs d'une balise ============


class Attribute_rule(Rule):
    balises = []
    attributs = {}

    def __init__(self, balises, attributs):
        self.balises = balises
        self.attributs = attributs

    def print_rule(self):
        print(" where " + self.balises[-1] + " is", self.attributs)

    def verif_rule(self, html_content):
        def verif_recursive(tag, balise_index):
            if tag.name == self.balises[balise_index]:
                if balise_index == 0:
                    return True
                else:
                    return verif_recursive(tag.parent, balise_index - 1)
            else:
                return False

        parser = BeautifulSoup(html_content, 'html.parser')
        tags = parser.find_all(self.balises[-1],attrs=self.attributs)  # on cherche le tag avec ces attributs

        # Si aucun tag n'existe, alors on peut déjà retourner False
        if tags is None :
            return False
        # Sinon, on va regarder si le tag a la bonne hiérarchie
        else:
            balise_index = len(self.balises) -1
            for tag in tags:
                if verif_recursive(tag,balise_index):
                    return True
            return False


#============ Regle générale ============

class Value:
    valeur = ""

    def __init__(self, valeur):
        self.valeur = valeur

    def set_tag(self, tag):
        self.tag = tag

    def verif_rule(self, tag):
        if tag.string == self.valeur:
            print("\t\t" + tag.string + "   =   " + self.valeur)
        else:
            print("\t\t" + tag.string + "   =X   " + self.valeur)
        return tag.string == self.valeur
    
    def to_string(self):
        return "'" + str(self.valeur) + "'"

class Attribut:
    attributs = {}

    def __init__(self, attributs):
        self.attributs = attributs

    def set_tag(self, tag):
        self.tag = tag
    
    def verif_rule(self, tag):
        # print("\t\tverif attributs : " + str(tag.attrs))
        for att, valeur in self.attributs.items():
            if tag.get(att) is not None:
                if att == 'class':
                    if valeur not in tag.get(att):
                        print("\t\t\t" + str(att) + "   =X   " + str(valeur))
                        return False
                else:
                    if tag.get(att) != valeur:
                        print("\t\t\t" + str(att) + "   =X   " + str(valeur))
                        return False
                    else:
                        print("\t\t\t" + str(att) + "   =   " + str(valeur))
            else:
                print("\t\t\t" + str(att) + "   =X   " + str(valeur))
                return False
        print("\t\t\t" + str(att) + "   =   " + str(valeur))
        return True
        
    def to_string(self):
        return attrs_to_string(self.attributs)

class Main_rule:
    balises = []
    rule_index = {}
    numero = 0

    def __init__(self, balises, rule_index, numero):
        self.balises = balises
        self.rule_index = rule_index
        self.numero = numero

    def to_string(self):
        out = "[" + str(self.numero) + "]   "
        for balise in self.balises:
            out += str(balise) + " > "
        out = out[:-3] + "\n"

        if len(self.rule_index) != 0:
            for tag_index, rule in self.rule_index.items():
                # print("tag index =", tag_index)
                out += "\t\twhere " + str(self.balises[tag_index]) + " is " + rule.to_string() + "\n"
        return out

    def add_secondary_rule(self, rule, balise_index):
        self.rule_index[balise_index] = rule

    def verif_hierarchy(self, html_content):
        def verif_recursive(tag, balise_index):
            if tag.name == self.balises[balise_index]:
                if balise_index == 0:
                    return True
                else:
                    return verif_recursive(tag.parent, balise_index - 1)
            else:
                return False

        parser = BeautifulSoup(html_content, 'html.parser')
        tags = parser.find_all(self.balises[-1])  # on cherche tous les tag correspondant à la dernière balise
        
        # Si aucun tag n'existe, alors on peut déjà retourner False
        if tags is None :
            return False
        # Sinon, on va regarder si le tag a la bonne hiérarchie
        else:
            balise_index = len(self.balises) -1
            for tag in tags:
                if verif_recursive(tag,balise_index):
                    return True
            return False

    def verif_rule(self, html_content):
        def verif_recursive(tag, balise_index):
            # bonne balise ?
            if tag.name == self.balises[balise_index]:

                # y a t il une regle particulière sur cette balise ?
                if self.rule_index.get(balise_index) is not None:

                    
                    if not self.rule_index.get(balise_index).verif_rule(tag):
                        return False    # s'il est n'est pas respecté, on arrete

                
                # sommes nous à la dernière balise à vérifier ?
                if balise_index == 0:
                    # y a t il une regle particulière sur cette balise ?
                    if self.rule_index.get(balise_index) is not None:
                        return self.rule_index.get(balise_index).verif_rule(tag) # on retourne directement le résultat
                    else:
                        return True
                # il reste des balises à vérifier
                else:
                    return verif_recursive(tag.parent, balise_index - 1)
            else:
                return False # mauvaise balise

        # on fais une premiere verification de la hiérarchie, 
        # ça evite de vérifier les attributs ou les valeurs alors que les balises sont déjà mauvaises
        if not self.verif_hierarchy(html_content):
            print("Hiérarchie des balises n'est pas respectée")
            return False
        else:
            parser = BeautifulSoup(html_content, 'html.parser')
            tags = parser.find_all(self.balises[-1])  # on cherche tous les tag correspondant à la dernière balise
            
            # Si aucun tag n'existe, alors on peut déjà retourner False
            if tags is None :
                return False
            # Sinon, on va regarder si le tag a la bonne hiérarchie
            else:
                balise_index = len(self.balises) -1
                for tag in tags:
                    if verif_recursive(tag,balise_index):
                        return True
                return False

class Big_rule(Rule):
    balises = []
    secondary_rules = []
    numero = 0

    def __init__(self, balises, secondary_rules, numero):
        self.balises = balises
        self.secondary_rules = secondary_rules
        self.numero = numero

    def print_rule(self):
        print("[",self.numero,"]   ", end="")
        out = ""
        for balise in self.balises:
            out += balise + " > "
        print(out[:-3])

        if len(self.secondary_rules) != 0:
            for regle in self.secondary_rules:
                print("\t\t", end="")
                regle.print_rule()

    def add_secondary_rules(self, rule):
        self.secondary_rules.append(rule)

    def verif_hierarchy(self, html_content):
        def verif_recursive(tag, balise_index):
            if tag.name == self.balises[balise_index]:
                if balise_index == 0:
                    return True
                else:
                    return verif_recursive(tag.parent, balise_index - 1)
            else:
                return False

        parser = BeautifulSoup(html_content, 'html.parser')
        tags = parser.find_all(self.balises[-1])  # on cherche tous les tag correspondant à la dernière balise
        
        # Si aucun tag n'existe, alors on peut déjà retourner False
        if tags is None :
            return False
        # Sinon, on va regarder si le tag a la bonne hiérarchie
        else:
            balise_index = len(self.balises) -1
            for tag in tags:
                if verif_recursive(tag,balise_index):
                    return True
            return False
        

    def verif_rule(self, html_content):
        # on fais une premiere verification de la hiérarchie, 
        # ça evite de vérifier les attributs alors que les balises sont déjà mauvaises
        if not self.verif_hierarchy(html_content):
            print("Hiérarchie des balises n'est pas respectée")
            return False
        else:
            for regle in self.secondary_rules:
                if not regle.verif_rule(html_content):  # si une des sous règles n'est pas respéctée 
                    return False
            return True
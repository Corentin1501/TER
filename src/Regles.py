from bs4 import BeautifulSoup
# import cssutils


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
        def verif_recursive(tag, rule_index):
            if rule_index >= len(self.balises):
                return tag.string == self.value
            else:
                current_balise = self.balises[rule_index]
                next_tags = tag.find_all(current_balise)
                for next_tag in next_tags:
                    if verif_recursive(next_tag, rule_index + 1):
                        return True
                return False

        tag = BeautifulSoup(html_content, 'html.parser')
        return verif_recursive(tag, 0)


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
        tag = parser.find(attrs=self.attributs)  # on cherche tous les tag avec ces attributs
        
        # Si aucun tag n'a ces attributs, alors on peut déjà retourner False
        if tag is None :
            return False
        # Sinon, on va regarder si le tag a la bonne hiérarchie
        else:
            balise_index = len(self.balises) -1
            return verif_recursive(tag,balise_index)


#============ Regle générale ============


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
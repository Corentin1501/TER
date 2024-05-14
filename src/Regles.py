from bs4 import BeautifulSoup
from enum import Enum


class Rule:
    pass

class Logical_type(Enum):
    OR = 'OR'
    AND = 'AND'
    NOT = 'NOT'

class Logical_rule(Rule):
    logic_type = Logical_type.AND
    rules_concerned = []
    numero = 0

    css_rules_string = ""


    def __init__(self, logic_type, rules):
        self.logic_type = logic_type
        self.rules_concerned = rules

    def to_string(self):
        out = "-   " + str(self.logic_type.name) + "\n----------\n"
        for rule in self.rules_concerned:
            out += "|" + rule.to_string()
        return out + "----------\n"
    
    def add_rule(self, rule):
        self.rules_concerned.append(rule) 

    def add_css_rule(self, rule):
        self.css_rules_string += rule + "\n"

    def verif_rule(self):

        if self.logic_type == Logical_type.OR:
            for rule in self.rules_concerned:
                if rule.verif_rule():
                    return True
            # print("[Logique] Aucune règle n'est respecté dans OR")
            return False
        
        elif self.logic_type == Logical_type.AND:
            for rule in self.rules_concerned:
                if not rule.verif_rule():
                    # print("[Logique] Une règle n'est pas respecté dans AND")
                    return False
            return True
        
        elif self.logic_type == Logical_type.NOT:
            for rule in self.rules_concerned:
                if rule.verif_rule():
                    # print("[Logique] Une règle n'est pas respecté dans NOT")
                    return False
            return True

        else:
            return False

class CSS_rule:
    css_file_rules = []

    def __init__(self, selectors, properties, numero):
        self.selectors = selectors
        self.properties = properties
        self.numero = numero

    def set_content(self, content):
        self.css_file_rules = content

    def to_string(self):
        out = "-   "
        aux_out = ""
        for selector in self.selectors:
            aux_out += ", " + selector
        out += aux_out[2:] + "\n\t{"
        for prop, value in self.properties.items():
            out += prop + ":'" + value + "', "
        out = out[:-2] + "}\n"
        return out

    def verif_rule(self):
        # Vérifier la règle avec les règles du fichier CSS
        for rule in self.css_file_rules:
            if all(selector in rule.selectors for selector in self.selectors):
                if all(prop in rule.properties and rule.properties[prop] == self.properties[prop] for prop in self.properties):
                    return True

        # Si aucune correspondance n'a été trouvée, diviser la règle en sélecteurs individuels
        if len(self.selectors) > 2:
            for selector in self.selectors:
                new_rule = CSS_rule([selector], self.properties, 0)
                if new_rule.verif_rule():
                    return True

        # Si la division en sélecteurs individuels n'a pas abouti, diviser en propriétés individuelles
        if len(self.properties) > 2:
            for prop in self.properties:
                new_rule = CSS_rule(self.selectors, {prop: self.properties[prop]}, 0)
                if new_rule.verif_rule():
                    return True

        # Si la division en propriétés individuelles n'a pas abouti, diviser en sélecteurs et propriétés individuels
        if len(self.selectors) > 2 and len(self.properties) > 2:
            for selector in self.selectors:
                for prop in self.properties:
                    new_rule = CSS_rule([selector], {prop: self.properties[prop]}, 0)
                    if new_rule.verif_rule():
                        return True

        return False

#============ Précision sur la valeur d'une balise ============

class Value:
    valeur = ""

    def __init__(self, valeur):
        self.valeur = valeur

    def verif_rule(self, tag):
        """Vérifie si une balise a la bonne valeur"""

        return tag.string == self.valeur
    
    def to_string(self):
        return "\"" + str(self.valeur) + "\""
    
#============ Précision sur les attributs d'une balise ============

class Attribut:
    attributs = {}

    def __init__(self, attributs):
        self.attributs = attributs

    def verif_rule(self, tag):
        """Vérifie si une balise a tous les attributs nécessaire"""

        # pour chaque attribut nécessaire
        for att, valeur in self.attributs.items():
            # si le tag a cet attribut
            if tag.get(att) is not None:
                if att == 'class' or att =='rel':  # si c'est une classe qu'on vérifie, c'est considéré comme une liste
                    # print("\t",tag.get(att), "in?", valeur)
                    if valeur not in tag.get(att):
                        return False
                else:
                    if tag.get(att) != valeur:
                        return False
            else:
                return False
        return True
        
    def to_string(self):
        out = "{"
        for att, valeur in self.attributs.items():
            out += "'" + str(att) + "'='" + valeur + "', "
        return out[:-2] + "}"
    
#============ Règle Générale qui combine toutes les petites règles ============

class HTML_Rule(Rule):
    html_content = ""
    balises = []
    secondary_rules_index = {}  # Dictionnaire de tableaux de règles : {0 : [Attribut{class='titi'}, ...], ...}
    numero = 0  

    def __init__(self, balises, secondary_rules_index, numero):
        self.balises = balises
        self.secondary_rules_index = secondary_rules_index
        self.numero = numero

    def set_content(self, content):
        self.html_content = content

    def to_string(self):
        out = "[" + str(self.numero) + "]   "
        out = "-   "
        for balise in self.balises:
            out += str(balise) + " > "
        out = out[:-3] + "\n"

        if len(self.secondary_rules_index) != 0:
            for tag_index, secondary_rules in self.secondary_rules_index.items():
                out += "\twhere " + str(self.balises[tag_index]) + " is " + self.rules_to_string(secondary_rules) + "\n"
        return out

    def rules_to_string(self, rules):
        out = ""
        for rule in rules:
            out += rule.to_string() + "  AND  "
        return out[:-7]

    def add_secondary_rule(self, rule, balise_index):
        """Ajoute une règle secondaire (attribut/valeur) sur une balise"""

        if balise_index not in self.secondary_rules_index:
            self.secondary_rules_index[balise_index] = [rule]
        else:
            self.secondary_rules_index[balise_index].append(rule)

    def verif_rule(self):
        """Vérifie si la règle est respectée, et toutes les règles secondaires associées"""

        def verif_recursive(tag, tag_index):
            """Vérifie récursivement si toutes les règles secondaires sont respectées à partir d'un tag"""

            # est-ce la bonne balise ?
            if tag.name == self.balises[tag_index]:
                # y a-t-il des règles particulières sur cette balise ?
                if self.secondary_rules_index.get(tag_index) is not None:
                    # On vérifie le respect de chaque règle secondaire
                    for rule in self.secondary_rules_index.get(tag_index):
                        if not rule.verif_rule(tag):
                            return False    # Si l'une des règles n'est pas respectée, on arrête
                # est-ce la dernière balise à vérifier ?
                if tag_index == 0:
                    return True
                else:
                    return verif_recursive(tag.parent, tag_index - 1)
            else:
                return False # Mauvaise balise

        parser = BeautifulSoup(self.html_content, 'html.parser')
        tags = parser.find_all(self.balises[-1])  # On cherche toutes les balises correspondant à la dernière balise
        
        # Si aucune balise n'existe, alors on peut déjà retourner False
        if tags is None:
            return False
        # Sinon, on va regarder si toutes les règles sont respectées
        else:
            tag_index = len(self.balises) - 1
            for tag in tags:
                if verif_recursive(tag, tag_index):
                    return True
            return False

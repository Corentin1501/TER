from bs4 import BeautifulSoup
from enum import Enum

from Levenshtein import ratio, distance

# Vérifie la similarité entre deux chaînes de caractères
def similar(a, b, threshold=0.75):
    return ratio(a, b) >= threshold

# Vérifie la similarité entre deux propriétés de CSS
def similar_property(a, b):
    mots1 = set(a.split())
    mots2 = set(b.split())

    # Vérifier que chaque mot de mots1 a un correspondant similaire dans mots2 et vice versa
    return all(any(similar(mot1, mot2) for mot2 in mots2) for mot1 in mots1) and \
           all(any(similar(mot2, mot1) for mot1 in mots1) for mot2 in mots2)



# Définition d'un type énuméré pour les types logiques (AND, OR, NOT)
class Logical_type(Enum):
    OR = 'OR'
    AND = 'AND'
    NOT = 'NOT'

class Logical_rule:
    logic_type = Logical_type.AND
    rules_concerned = []
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
            return False
        
        elif self.logic_type == Logical_type.AND:
            for rule in self.rules_concerned:
                if not rule.verif_rule():
                    return False
            return True
        
        elif self.logic_type == Logical_type.NOT:
            for rule in self.rules_concerned:
                if rule.verif_rule():
                    return False
            return True

        else:
            return False

class CSS_rule:
    css_file_rules = []

    def __init__(self, selectors, properties):
        self.selectors = selectors
        self.properties = properties

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
        selectors_set = set(self.selectors)
        properties_items = self.properties.items()

        # Vérifier la règle avec les règles du fichier CSS
        for rule in self.css_file_rules:
            if selectors_set.issubset(rule.selectors):
                if all(prop in rule.properties and similar_property(rule.properties[prop], value)
                       for prop, value in properties_items):
                    return True

        # Si aucune correspondance n'a été trouvée, diviser la règle en sélecteurs et propriétés individuels
        if len(self.selectors) > 2:
            for selector in self.selectors:
                new_rule = CSS_rule([selector], self.properties)
                if new_rule.verif_rule():
                    return True
        # Si la division en sélecteurs individuels n'a pas abouti, diviser en propriétés individuelles
        if len(self.properties) > 2:
            for prop in self.properties:
                new_rule = CSS_rule(self.selectors, {prop: self.properties[prop]})
                if new_rule.verif_rule():
                    return True
        # Si la division en propriétés individuelles n'a pas abouti, diviser en sélecteurs et propriétés individuels
        if len(self.selectors) > 2 and len(self.properties) > 2:
            for selector in self.selectors:
                for prop in self.properties:
                    new_rule = CSS_rule([selector], {prop: self.properties[prop]})
                    if new_rule.verif_rule():
                        return True
        return False

#============ Précision sur la valeur d'une balise ============

class Value:
    valeur = ""

    def __init__(self, valeur):
        self.valeur = valeur

    def verif_rule(self, tag):
        tag_string_lower = tag.string
        if tag.string:
            tag_string_lower = tag.string.lower()
        self_string_lower = self.valeur.lower()

        return similar(tag_string_lower,self_string_lower)
    
    def to_string(self):
        return "\"" + str(self.valeur) + "\""
    
#============ Précision sur les attributs d'une balise ============

class Attribut:
    attributs = {}

    def __init__(self, attributs):
        self.attributs = attributs

    def verif_rule(self, tag):
        # pour chaque attribut nécessaire
        for att, valeur in self.attributs.items():
            # si le tag a cet attribut
            if tag.get(att) is not None:
                if att in ['class','rel','style']:  # certains cas sont considéré comme une liste
                    valeurs = valeur.split(" ")
                    return all(val in tag.get(att, []) for val in valeurs)

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

class HTML_rule:
    html_content = ""
    balises = []
    secondary_rules_index = {}  # Dictionnaire de tableaux de règles : {0 : [Attribut{class='titi'}, ...], ...}

    def __init__(self, balises, secondary_rules_index):
        self.balises = balises
        self.secondary_rules_index = secondary_rules_index

    def set_content(self, content):
        self.html_content = content

    def to_string(self):
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
        if balise_index not in self.secondary_rules_index:
            self.secondary_rules_index[balise_index] = [rule]
        else:
            self.secondary_rules_index[balise_index].append(rule)

    def verif_rule(self):

        def verif_recursive(tag, tag_index):
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
        if not tags:
            return False

        tag_index = len(self.balises) - 1
        return any(verif_recursive(tag, tag_index) for tag in tags)

from bs4 import BeautifulSoup

import cssutils


class CSS_rule:
    selectors = []
    properties = {}
    numero = 0

    def __init__(self, selectors, properties, numero):
        self.selectors = selectors
        self.properties = properties
        self.numero = numero

    def to_string(self):
        out = "[" + str(self.numero) + "]   "
        aux_out = ""
        for selector in self.selectors:
            aux_out += " , " + selector
        out += aux_out[3:] + "\n\t{'"
        for property, value in self.properties.items():
            out += property + "':'" + value + "', "
        out = out[:-2] + "}\n"
        return out

    def verif_rule(self, css_file_rules):
        # Vérifier si la règle actuelle est respectée parmi toutes les règles dans css_file_rules
        for rule in css_file_rules:
            # Vérifier si tous les sélecteurs de la règle actuelle sont présents dans les sélecteurs de la règle en cours
            if all(selector in rule.selectors for selector in self.selectors):
                # Vérifier si toutes les propriétés de la règle actuelle sont présentes dans les propriétés de la règle en cours
                if all(prop in rule.properties and rule.properties[prop] == self.properties[prop] for prop in self.properties):
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
                if att == 'class':  # si c'est une classe qu'on vérifie, c'est considéré comme une liste
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

class Rule:
    balises = []
    secondary_rules_index = {}  # dictionnaire de regles : {0 : Attribut{class='titi'}, ...}
    numero = 0  

    def __init__(self, balises, secondary_rules_index, numero):
        self.balises = balises
        self.secondary_rules_index = secondary_rules_index
        self.numero = numero


    def to_string(self):
        out = "[" + str(self.numero) + "]   "
        for balise in self.balises:
            out += str(balise) + " > "
        out = out[:-3] + "\n"

        if len(self.secondary_rules_index) != 0:
            for tag_index, secondary_rules in self.secondary_rules_index.items():
                out += "\t\twhere " + str(self.balises[tag_index]) + " is " + secondary_rules.to_string() + "\n"
        return out


    def add_secondary_rule(self, rule, balise_index):
        """Ajoute une règle secondaire (attribut/valeur) sur une balise"""

        self.secondary_rules_index[balise_index] = rule


    def verif_hierarchy(self, html_content):
        """Vérifie si la suite des balises existe dans le document HTML"""
        
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
        """Vérifie si la règle est respectée, et toutes les règles secondaires associées"""

        def verif_recursive(tag, tag_index):
            """Vérifie récursivement si toutes les règles secondaires sont respectées à partir d'un tag"""

            # est-ce la bonne balise ?
            if tag.name == self.balises[tag_index]:
                # y a t il une règle particulière sur cette balise ?
                if self.secondary_rules_index.get(tag_index) is not None:
                    # On vérifie le respect de la règle
                    if not self.secondary_rules_index.get(tag_index).verif_rule(tag):
                        return False    # s'il est n'est pas respecté, on arrête
                # est-ce la dernière balise à vérifier ?
                if tag_index == 0:
                    return True
                else:
                    return verif_recursive(tag.parent, tag_index - 1)
            else:
                # print("Balises dans le mauvais ordre")
                return False # mauvaise balise

        parser = BeautifulSoup(html_content, 'html.parser')
        tags = parser.find_all(self.balises[-1])  # on cherche toutes les balises correspondant à la dernière balise
        
        # Si aucune balise n'existe, alors on peut déjà retourner False
        if tags is None :
            return False
        # Sinon, on va regarder si toutes les règles sont respectées
        else:
            tag_index = len(self.balises) -1
            for tag in tags:
                if verif_recursive(tag,tag_index):
                    return True
            return False
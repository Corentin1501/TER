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


    def __init__(self, logic_type, rules):
        self.logic_type = logic_type
        self.rules_concerned = rules

    def to_string(self):
        out = "[" + str(self.numero) + "]   "
        out += str(self.logic_type.name) + "\n"
        for rule in self.rules_concerned:
            out += "\t" + rule.to_string()
        return out
    

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

class CSS_rule(Rule):
    css_file_rules = []

    selectors = []
    properties = {}
    numero = 0

    def __init__(self, selectors, properties, numero):
        self.selectors = selectors
        self.properties = properties
        self.numero = numero

    def set_content(self, content):
        self.css_file_rules = content

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

    def verif_rule(self):

        rules_to_test_again = []

        # on vérifie une première fois avec les règles en l'état actuel
        for rule in self.css_file_rules:
            if all(selector in rule.selectors for selector in self.selectors):
                if all(prop in rule.properties and rule.properties[prop] == self.properties[prop] for prop in self.properties):
                    return True
                
        # si on a pas trouvé de correspondance avec le fichier CSS, on divise la regle en 
        # autant de fois qu'il y a de selecteurs mais seulement s'il y a plusieurs selecteurs
        if len(self.selectors) > 1:
            for selector in self.selectors:
                rules_to_test_again.append(CSS_rule([selector], self.properties, 0))

            # et on re test avec ces nouvelles règles
            all_rules_verified = True
            for rule in rules_to_test_again:
                # print("regle à re tester : " + rule.to_string())
                if not rule.verif_rule(self.css_file_rules):
                    all_rules_verified = False
            
            return all_rules_verified

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

class HTML_Rule(Rule):
    html_content = ""

    balises = []
    secondary_rules_index = {}  # dictionnaire de regles : {0 : Attribut{class='titi'}, ...}
    numero = 0  

    def __init__(self, balises, secondary_rules_index, numero):
        self.balises = balises
        self.secondary_rules_index = secondary_rules_index
        self.numero = numero

    def set_content(self, content):
        self.html_content = content


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


    # def verif_hierarchy(self):
    #     """Vérifie si la suite des balises existe dans le document HTML"""
        
    #     def verif_recursive(tag, balise_index):
    #         if tag.name == self.balises[balise_index]:
    #             if balise_index == 0:
    #                 return True
    #             else:
    #                 return verif_recursive(tag.parent, balise_index - 1)
    #         else:
    #             return False

    #     parser = BeautifulSoup(self.html_content, 'html.parser')
    #     tags = parser.find_all(self.balises[-1])  # on cherche tous les tag correspondant à la dernière balise
        
    #     # Si aucun tag n'existe, alors on peut déjà retourner False
    #     if tags is None :
    #         return False
    #     # Sinon, on va regarder si le tag a la bonne hiérarchie
    #     else:
    #         balise_index = len(self.balises) -1
    #         for tag in tags:
    #             if verif_recursive(tag,balise_index):
    #                 return True
    #         return False        


    def verif_rule(self):
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

        parser = BeautifulSoup(self.html_content, 'html.parser')
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
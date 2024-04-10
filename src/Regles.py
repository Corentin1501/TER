from bs4 import BeautifulSoup
# import cssutils


#============ Classe mère ============

class Rule:
    pass

#============ Existence d'une balise ============


class Balise_rule(Rule):
    balises = []

    def __init__(self, balises):
        self.balises = balises
        # print("new balise rule created : balises=",self.balises)

    def print_rule(self):
        out = "\t"
        for balise in self.balises:
            out += balise + "  >  "
        print(out[:-3], end='\n')

    def verif_rule(self, html_content):
        def verif_recursive(tag, rule_index):
            if rule_index >= len(self.balises):
                return True
            else:
                current_balise = self.balises[rule_index]
                next_tags = tag.find_all(current_balise)
                for next_tag in next_tags:
                    if verif_recursive(next_tag, rule_index + 1):
                        return True
                return False

        tag = BeautifulSoup(html_content, 'html.parser')
        return verif_recursive(tag, 0)
    

#============ Verification de la valeur d'une balise ============


class Value_rule(Rule):
    balises = []
    value = ""

    def __init__(self, balise, value):
        self.balises = balise
        self.value = value
        # print("new value rule created : balises=",self.balises,",",self.value)

    def print_rule(self):
        out = "\t"
        for balise in self.balises:
            out += balise + "  >  "
        print(out[:-3] + "  ==  '" + self.value, end="'\n")

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

    def __init__(self, balise, attributs):
        self.balises = balise
        self.attributs = attributs
        # print("new attribute rule created : balises=",self.balises,",",self.attributs)

    def print_rule(self):
        out = "\t"
        for balise in self.balises:
            out += balise + "  >  "
        print(out[:-4] + " is ", self.attributs, end="\n")

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

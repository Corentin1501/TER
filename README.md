# Correction automatique de pages HTML+CSS
Professeur encadrant : *Jean-Michel Richer*

On désire corriger automatiquement des pages HTML et CSS suite à un contrôle continu donné en 
L1. Fournir un utilitaire qui prend en paramètre un fichier de règles, un fichier HTML et un fichier CSS puis vérifie que les règles sont respectées.

## Fonctionnalités voulues dans le fichier de règles
-   **HTML** :
    -   Vérification de l'**existence** d'une balise
    -   Vérification des valeurs des **attributs** d'une balise
    -   Vérification de la **valeur** d'une balise
-   **CSS** :
    -   Vérification des **propriétés** CSS

Pour chacune des règles, on vérifiera également la bonne hiérarchie des balises.

## Syntaxe

### HTML

- ### Existence d'une suite de balises :

        html balise1 balise2 ...

    #### Exemples 
        html main section form
    
    ---

- ### Valeurs des attributs d'une balise :

        html balise1 balise2 ... [attr1=val1 attr2=val2 ...]

    #### Exemples 
        html form fieldset input [type=number min=2 name=quantite]
        html table [class="client"]
    
    #### Notes supplémentaires
    Les `[` et `]` doivent être collés aux attributs.
    Les attributs et valeurs doivent être collés au `=`.

    ---

- ### Valeur d'une balise :

        html balise1 balise2 ... "valeur"

    #### Exemples 
        html table td "Marc Decafer"

    ---

### CSS

Même syntaxte que dans un fichier CSS mais il faut rajouter `css` au début des sélecteurs.

    css p {
        font-size: 14px;
        font-family: Verdana;
    }
ou 

    css table.commande th, 
    table.commande td {
        padding: 10px;
        border: 1px solid black;
        border-collapse: collapse;
    }


### Logique

Pour aller plus loin, des connecteurs logiques peuvent être ajoutés pour plus de précisions :
**AND**, **OR** et **NOT**.

#### Exemples 

	OR (
		css h1 {
			font-size: 50px;
		}
		css h2 {
			font-size: 80px;
		}
	)

#### Notes
-   **AND** : il faut que toutes les règles soient *VRAIS* 
-   **OR** : il faut qu'au moins une règle soit *VRAI* 
-   **NOT** : il faut que toutes les règles soient *FAUSSES* 

Il n'y a pas de limites au nombre de règles. Il faut juste que les règles soient comprises entre deux `(` `)` (avec la `)` fermante sur une seule ligne et pas en fin de ligne). De plus, des règles logiques peuvent aussi contenir d'autres règles logiques :

    AND (
        html table [class="client"]
        NOT (
            html header h2 "Ah! Ma Zone!"
        )
        OR (
            css h1 {
                font-size: 50px;
            }
            css h2 {
                font-size: 80px;
            }
        )
    )



## Notes générales
Toutes les chaînes de caractères, que ce soit pour les attributs, les valeurs ou les balises, sont ***sensibles à la casse et aux espaces***.

---
Il est possible d'ajouter des ***commentaires*** dans le fichier de règles, en rajoutant `#` au début de la ligne.

---
Il est aussi possible de ***combiner*** plusieurs types de règles : 

    html section [id=section_form] form h2 "Mon Formulaire"


Cependant, il n'est pas possible de mettre plusieurs règles sur une seule balise : 

    html h2 "Mon Formulaire" [class=bold]               = IMPOSSIBLE

---
Dans le CSS, deux règles peuvent être ***séparés*** ou ***combinés*** : Si dans le *fichier CSS* deux règles sont séparés (`h1 {...} h2 {...}`) et que dans le *fichier de règles* les deux sont combinés (`h1, h2 {...}`), l'utilitaire saura valider la règle. Et ce même si c'est l'inverse, que les règles soients séparés et dans le CSS combinées.

---
Par défaut, toutes les règles dans le fichier de règles sont considérés comme un **AND** : si une des règles n'est pas vérifiée, alors il y a une erreur.


## Librairies utilisées

-   **[BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) :**
        Bibliothèque Python d'analyse syntaxique de documents HTML et XML créée par Leonard Richardson. 
        Elle produit un arbre syntaxique qui peut être utilisé pour chercher des éléments ou les modifier.

-   **[CSSutils](https://cthedot.de/cssutils/) :**
        A Python package to parse and build CSS Cascading Style Sheets. Currently a DOM only, no rendering options.
        
## Manipulation nécessaire

### Installer CSSUtils 

Dans un terminal :

    pip install cssutils

## Exemples de règles "complexes" à tester

    html section [id=section_form] form h2 "Mon Formulaire"

    html form [method=post] fieldset select [name=produit] option "Clavier"

    AND (
        html table [class="client"]
        NOT (
            html header h2 "Ah! Ma Zone!"
        )
        OR (
            css h1 {
                font-size: 50px;
            }
            css h2 {
                font-size: 80px;
            }
        )
    )

## Notions importantes à implémenter 

-   Si un attribut de style dans une balise n'est pas respecté, on doit vérifier cette prorpiété dans le fichier CSS.
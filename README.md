# Correction automatique de pages HTML+CSS
Encadrant: *Jean-Michel Richer*

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

1. ### Existence d'une suite de balises :

    `html balise1 balise2 ...`

    #### Exemples 
    -   `html main section form`

2. ### Valeurs des attributs d'une balise :

    `html balise1 balise2 ... [attr1=val1 attr2=val2 ...]`

    #### Exemples 
    -   `html form fieldset input [type=number min=2 name=quantite]`
    -   `html table [class="client"]`
    
    #### Notes supplémentaires
    Les `[` et `]` doivent être collés aux attributs.
    Les attributs et valeurs doivent être collés au `=`

3. ### Valeur d'une balise :

    `html balise1 balise2 ... "valeur"`

    #### Exemples 
    -   `html table td "Marc Decafer"`

### CSS

Même syntaxte que dans un fichier CSS mais il faut rajouter `css` au début de la première ligne 

    css p {
        font-size: 14px;
        font-family: Verdana;
    }

## Notes générales
Toutes les chaînes de caractères, que ce soit pour les attributs, les valeurs ou les balises, sont ***sensibles à la casse et aux espaces***. 

Il est possible d'ajouter des ***commentaires*** dans le fichier de règles, en rajoutant `#` au début de la ligne.

Il est aussi possible de ***combiner*** plusieurs types de règles, exemple : `html section [id=section_form] form h2 "Mon Formulaire"`

Cependant, il n'est pas possible de mettre plusieurs règles sur une seule balise. Exemple : `html h2 "Mon Formulaire" [class=bold]` ***= IMPOSSIBLE***


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

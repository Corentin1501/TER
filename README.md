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

1. ### Hiérarchie ET existence d'une balise dans le fichier HTML :

    `html balise1 balise2 ...`

    #### Exemples 
    -   `html main section form`
    -   `html table tbody`
    -   `html header img`

2. ### Hiérarchie ET Valeurs des attributs d'une balise dans le fichier HTML :

    `html balise1 balise2 ... [attr1=val1 attr2=val2 ...]`

    #### Exemples 
    -   `html form fieldset input [type=number min=2 name=quantite]`
    -   `html table [class="client"]`
    
    #### Notes supplémentaires
    Les `[` et `]` doivent être collés aux attributs.
    Les attributs et valeurs doivent être collés au `=`

3. ### Hiérarchie ET valeur d'une balise dans le fichier HTML :

    `html balise1 balise2 ... "valeur"`

    #### Exemples 
    -   `html table td "Marc Decafer"`
    -   `html header h2 "Ma Page Web"`


## Notes générales
Toutes les valeurs, que ce soit pour les attributs ou les balises, sont ***sensibles à la casse et aux espaces***. 

Il est possible d'ajouter des ***commentaires*** dans le fichier de règles, en rajoutant `#` au début de la ligne.



## Librairies utilisées

-   **[BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) :**
        Bibliothèque Python d'analyse syntaxique de documents HTML et XML créée par Leonard Richardson. 
        Elle produit un arbre syntaxique qui peut être utilisé pour chercher des éléments ou les modifier.

-   **[CSSutils](https://cthedot.de/cssutils/) :**
        A Python package to parse and build CSS Cascading Style Sheets. Currently a DOM only, no rendering options.
        

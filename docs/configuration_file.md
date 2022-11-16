# Sections

## additional_classes

Classes additionnelles rattachées aux tables, les entrées sont créées
automatiquement dès qu’une object property est créée depuis une colonne
d’une table ou lors d’une analyse récursive automatique d’un document
JSON par l’usage du type CT_JSON_STRUCT.

Une table de type TT_CLASS définit une classe, les paramètres de cette
classe sont dans les paramètres de la table, ce n’est pas une classe
additionnelle.

## additional_datatypes_properties

Datatype properties créées automatiquement lors d’une analyse récursive
automatique d’un document JSON par l’usage du type CT_JSON_STRUCT.

Leurs paramètres peuvent être modifiés à la main à l’exception du nom du
prédicat qui est automatique. Modifier le nom du prédicat provoquera la
suppression de l’entrée et une nouvelle création avec le nom d’origine
mais aussi des paramètres par défaut. Les anciens paramètres seront donc
perdus.

Les entrées inutilisées sont nettoyées automatiquement.

Transformer une datatype property en classe additionnelle est possible,
voir le tuto dédié à cette opération.

## additional_object_properties

Object properties créées automatiquement lors d’une analyse récursive
automatique d’un document JSON par l’usage du type CT_JSON_STRUCT.

Leurs paramètres peuvent être modifiés à la main à l’exception du nom du
prédicat qui est automatique. Modifier le nom du prédicat provoquera la
suppression de l’entrée et une nouvelle création avec le nom d’origine
mais aussi des paramètres par défaut. Les anciens paramètres seront donc
perdus.

Les entrées inutilisées sont nettoyées automatiquement.

## kb_params

Paramètres de la future KB

Renseigner a minima :

- l’URI ou le basemane, l’autre entrée sera renseignée automatiquement.

- Le nom de la kb sans espace ni accent

## ontology_params

Paramètres de la future ontologie

Renseigner a minima :

- l’URI ou le basemane, l’autre entrée sera renseignée automatiquement.

- Le nom de l’ontologie sans espace ni accent

## sources_files

Liste des fichiers sources de données : types acceptés .CSV ou .JSON

Attention les chemins relatifs sont à donner relativement au path de
l’appel de l’application et non du fichier de paramétrage

Usage recommandé :

- Créer un dossier par projet

- Y placer le fichier de configuration

- Appeler l’application depuis ce dossier

- Dans le fichier de configuration, donner des chemins relatifs à ce
  dossier

## tables

Entrées sous forme de dictionnaire : la clé est le nom du fichier
source, la valeur est la structure des informations

Attention, s’il faut modifier le nom d’un fichier source de données, le
modifier aux deux endroits identiquement :

1.  En tant que clé de la section « tables »

2.  En tant que fichier source dans la section « source_files »

A défaut une seconde entrée de « tables » sera créée.

# Sous-sections

## additional_classes

{  
"ac_conversions_pipe": \[\],  
"ac_extra_uri_mask":
"https://www.allocine.fr/film/fichefilm_gen_cfilm={ID}.html",  
"ac_labels": { "en": "Allocine Movie ID", “fr": "ID Film Allocine" },  
"ac_subclass_of": \["pmcore:Entity"\]  
}

<table>
<colgroup>
<col style="width: 62%" />
<col style="width: 37%" />
</colgroup>
<thead>
<tr class="header">
<th>"ac_conversions_pipe": []</th>
<th><p>Pipe de conversions pour la création des labels des entités. Les
labels sont construits dans la colonne source CT_OBJECT_PROPERTY_KEY ou
automatiquement par les valeurs rencontrées dans une analyse de type
CT_JSON_STRUCT</p>
<p>Le pipe permet de modifier le format des labels (majuscules,
minuscules, underscores, etc.)</p></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>"ac_extra_uri_mask":
"https://www.allocine.fr/film/fichefilm_gen_cfilm={ID}.html"</td>
<td>OPTION: s’il est renseigné chaque entité de la classe aura une
datatype property URL avec l’URL construite sur la base de l’ID de
l’entité</td>
</tr>
<tr class="even">
<td><p>"ac_labels":</p>
<p>{ "en": "Allocine Movie ID", "fr": "ID Film Allocine" }</p></td>
<td>Label de la classe à créer</td>
</tr>
<tr class="odd">
<td>"ac_subclass_of": ["pmcore:Entity"]</td>
<td>Liens de parenté de la classe à créer, ici la classe sera une
subclass_of de la classe pmcore :Entity</td>
</tr>
</tbody>
</table>

## additional_datatypes_properties

## additional_object_properties

## kb_params

## ontology_params

## sources_files

## tables

# Conversions pipe
Les données scannées peuvent être modifiées via un pipe de conversions afin de personnaliser les labels ou le rendu des datatype_properties
Par exemple :
"conversions_pipe": [ "LOWER_STR", "REMOVE_UNDERSCORE_STR", " CAPITALIZE_SENTENCE_STR " ]
Va appliquer la série de modifications ordonnée de la façon suivante :
1.	LOWER_STR: toutes les lettres sont transformées en minuscules
2.	REMOVE_UNDERSCORE_STR: Transforme tous les ‘_’ en ‘ ‘, supprime les espaces en doublons ou en bordures de chaîne 
3.	CAPITALIZE_SENTENCE_STR: Met la première lettre de la chaîne en majuscule
La chaîne « TELEPHONE_CLIENT » deviendra donc « telephone_client » puis « telephone client » et finalement « Telephone client »
Les autres opérations possibles sont les suivantes :

<table>
<colgroup>
<col style="width: 29%" />
<col style="width: 19%" />
<col style="width: 16%" />
<col style="width: 34%" />
</colgroup>
<thead>
<tr class="header">
<th>Nom</th>
<th>Type de données scannées (python)</th>
<th>XSD type de la colonne</th>
<th>Usage</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>"STR_TO_FLOAT"</td>
<td>str, float, int</td>
<td>xsd:float</td>
<td><p>Convertit une valeur de type numérique ou chaîne de caractères en
type float.</p>
<p>Fonction robuste qui traite les cas du type "3,230,000.20$" ou
"3 230 000,20$" pour retourner 3230000.2</p></td>
</tr>
<tr class="even">
<td>"STR_TO_INTEGER"</td>
<td>str, float, int</td>
<td>xsd:integer</td>
<td>Utilise l’opération STR_TO_FLOAT puis cast en entier</td>
</tr>
<tr class="odd">
<td>"EXTRACT_INTEGERS"</td>
<td>str, float, int</td>
<td>xsd:string</td>
<td>Utilise l’opération STR_TO_ INTEGER puis cast en chaîne</td>
</tr>
<tr class="even">
<td>"CAPITALIZE_WORDS_STR"</td>
<td>str</td>
<td>xsd:string</td>
<td>Met la première lettre de chaque mot en majuscule sans modifier les
autres lettres.</td>
</tr>
<tr class="odd">
<td>"REMOVE_PUNCT_STR"</td>
<td>str</td>
<td>xsd:string</td>
<td>Retire les ponctuations puis les espaces en doublons ou en bordures
de chaîne</td>
</tr>
<tr class="even">
<td>"UPPER_STR"</td>
<td>str</td>
<td>xsd:string</td>
<td>Toutes les lettres sont transformées en minuscules</td>
</tr>
</tbody>
</table>

# Reprendre ou étendre l'emploi du temps

Le `README.md` dit ce que ce projet **est**. Ce fichier dit comment on y
touche sans le casser. Les deux se lisent avant d'écrire une ligne ; le
second surtout, parce que la moitié de ce qu'il contient ne se devine pas
et a été payée une fois.

## 1. La commande

Faire d'un planning de collège photocopié quelque chose qu'une enfant de
onze ans lit d'un coup d'œil : trois affiches A4 paysage à punaiser, et une
page à mettre sur son iPad. Présentation intuitive, couleurs par matière,
semaines A et B distinguées.

Tout le reste — la source unique, les harnais, la chaîne de publication —
découle d'une seule exigence : **ces documents ne se relisent pas à l'œil**.
Quatorze matières, quarante et un cours, deux semaines, quatre sorties. Une
relecture humaine en laisse passer, et personne ne s'en aperçoit avant que
l'enfant ne se trompe de salle.

## 2. La chaîne, dans l'ordre

```bash
python3 generer_planning.py && python3 verifier_planning.py \
  && python3 generer_app.py && python3 verifier_app.py \
  && python3 verifier_readme.py
```

Engendrer **puis** vérifier, pour chaque sortie. Jamais l'inverse, jamais
l'un sans l'autre. Le `&&` n'est pas décoratif : un harnais qui échoue doit
arrêter la chaîne, et non défiler au milieu d'un journal que personne ne
lit.

Ensuite `git commit` et `git push` : la chaîne GitHub relance les trois
harnais et ne publie que s'ils passent.

## 3. La source unique, et le seul maillon qui ne se vérifie pas

**Tout part de `donnees_planning.py`.** Les matières, leurs couleurs, leurs
familles, les créneaux, les quarante et un cours. Les trois PDF et la page
en découlent ; ils ne peuvent donc pas se contredire.

**Ce fichier est le seul maillon non vérifié du projet.** Le planning
officiel, `PLANNING_CHLOE_ETIENNE_6EC.pdf`, est un scan sans couche texte :
aucun programme ne peut le relire. Chaque case a été lue à l'écran,
agrandie, les marqueurs A / B vérifiés un par un.

**Conséquence pratique** : si le collège publie une correction, c'est là
qu'on reprend, à l'œil, et c'est le seul endroit du projet où une relecture
humaine attentive est la seule garantie. Tout le reste s'ensuit
mécaniquement — et se vérifie.

## 4. Ce que chaque harnais prend, et ce qu'il ne prend pas

`verifier_planning.py` ouvre les trois PDF **aux coordonnées où
`generer_planning.py` dit avoir posé ses cases**. Il ne recalcule pas la
géométrie de son côté : le générateur tient un registre (`POSEES`,
`VIDES`), le harnais le suit. Deux calculs de la même géométrie seraient
deux copies, et une copie finit par diverger.

Il prend : une case hors de son créneau, un bloc de deux heures qui n'en
couvre qu'une, un cours de la semaine B composé sur la feuille A, une
légende qui titre une famille absente. Aucune de ces fautes ne lève
d'erreur à la compilation.

`verifier_app.py` relit le bloc JSON **depuis la page composée**, et non
depuis le générateur : c'est ce que le navigateur lira. Il mesure aussi le
contraste des quatorze matières, de jour comme de nuit.

Ce qu'il **ne fait pas**, et qu'il faut savoir : ouvrir un navigateur pour
regarder le rendu. Cette vérification-là est manuelle, et elle est à
refaire **à chaque changement d'allure**. Ne pas s'en dispenser sous
prétexte que les harnais passent.

`verifier_readme.py` relit les affirmations du `README.md` et de ce
fichier-ci : compteurs, chemins, adresses, chiffres tirés des données.

## 5. Les conventions qui ne se devinent pas

### La couleur est une information

Une teinte par matière, toutes sur la même plage de clarté, rangées par
famille — et la famille « vie scolaire » volontairement désaturée, parce
que le CDI et les devoirs faits ne sont pas des disciplines.

**Le contraste se mesure, il ne s'apprécie pas.** Toute couleur forte vaut
au moins 4,5:1 sur sa couleur claire. Pour corriger une couleur trop pâle,
on baisse la **clarté** à teinte constante : la teinte identifie la
matière, elle n'est pas négociable. Ajouter une matière, c'est ajouter ses
deux couleurs **et** lancer `verifier_app.py`, qui dira si elles tiennent.

### La typographie

Une seule famille, Avenir Next, mais toute son amplitude : Ultra Light,
Medium, Demi Bold, et la coupe Condensed pour les détails de case. Ne pas
ajouter une seconde police pour créer une hiérarchie — elle se fait par la
graisse et par la chasse.

Avenir Next est une police du système macOS et iOS, ce qui donne le même
caractère sur l'affiche et sur l'iPad — mais impose **lualatex**, jamais
pdflatex.

### La page publiée

Elle s'écrit en **ASCII pur** : entités numériques dans le balisage,
`\uXXXX` dans le script, translittération dans les commentaires CSS. Ne
jamais y remettre d'UTF-8 brut, même si « ça marche » : voir les incidents
du README. Elle n'appelle **aucune ressource extérieure** — ni police, ni
script, ni feuille de style.

### La prose se relit comme les chiffres

Un compteur se **recalcule**, jamais ne se recopie, et le total est une
somme. Un chemin entre dos-d'âne est une affirmation d'existence — sauf
pour ce que `.gitignore` écarte, où l'affirmation à relire est « il en est
bien tenu dehors ».

Et **le récit n'est pas une promesse** : la section « Les incidents » du
README raconte des états passés, et `verifier_readme.py` l'écarte
nommément. Y écrire les erreurs corrigées ; n'écrire ailleurs rien de
vérifiable qui ne soit relu.

## 6. Étendre

**Changer un cours, une salle, un professeur** → `donnees_planning.py`,
puis la chaîne du §2. Rien d'autre à toucher.

**Ajouter une matière** → une entrée dans `MATIERES` avec sa famille et ses
deux couleurs, puis `verifier_app.py` pour le contraste. Si la famille est
nouvelle, l'ajouter à `FAMILLES` — l'ordre y est celui de la légende, et il
n'est pas alphabétique.

**Changer d'année scolaire** → `ELEVE`, `CLASSE`, `ANNEE`, `SOURCE` en bas
de `donnees_planning.py`, et le scan de référence à côté. Les chiffres du
README (heures par semaine, nombre de matières) sont relus par
`verifier_readme.py` : il dira lesquels mettre à jour.

**Toucher à la mise en page** → les mesures sont en tête de
`generer_planning.py`, en millimètres, en coordonnées absolues. Après quoi
il faut **regarder la page** : le harnais vérifie que le contenu est au bon
endroit, pas qu'il est beau.

**Ajouter un contrôle** → dans le harnais concerné, puis relancer
`verifier_readme.py`, qui refusera tant que le compteur du README n'aura
pas suivi. C'est voulu.

## 7. Deux choses à ne pas défaire sans en parler

**Le dépôt est public**, avec le nom de l'élève, son établissement, ses
professeurs et l'endroit où elle se trouve à chaque heure. Ce choix a été
fait en connaissance de cause, après que la question a été posée. Ne pas le
rouvrir de sa propre initiative — et ne pas l'aggraver non plus.

**Le planning officiel du collège n'est pas versionné.** C'est le document
de l'établissement. Il reste sur la machine.

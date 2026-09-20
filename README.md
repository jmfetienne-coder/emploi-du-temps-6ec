# L'emploi du temps de Chloé — 6ᵉ C, 2026-2027

Trois affiches A4 paysage à imprimer, et une application web pour l'iPad.
Toutes les quatre sortent du **même fichier de données** : corriger une
erreur une fois la corrige partout, et le papier ne peut pas contredire
l'écran.

| Ce que c'est | Où | Pour quoi faire |
|---|---|---|
| `PLANNING_SEMAINE_A.pdf` | papier | l'affiche de la semaine en cours |
| `PLANNING_SEMAINE_B.pdf` | papier | l'affiche de la semaine en cours |
| `PLANNING_A_ET_B.pdf` | papier | la vue d'ensemble, pour le cartable |
| `docs/index.html` | écran | l'application, publiée en ligne |

Les trois PDF font une page, au format A4 paysage (842 × 595 pt).

**L'application est en ligne ici :**

> ### <https://jmfetienne-coder.github.io/emploi-du-temps-6ec/>

C'est l'adresse à ouvrir sur l'iPad. Elle ne demande aucun compte.

---

## L'application

**<https://jmfetienne-coder.github.io/emploi-du-temps-6ec/>**

**Pour la mettre sur l'iPad** : ouvrir cette adresse dans Safari, puis
*Partager → Sur l'écran d'accueil*. Elle s'ouvre ensuite comme une
application, sans barre d'adresse et sans qu'aucun compte soit demandé.
Elle fonctionne **hors connexion** : elle n'appelle aucune ressource
extérieure.

La même page existe aussi comme artefact Claude, à l'adresse
<https://claude.ai/artifact/DCs9k1Ggyc2cES7kP8HzeL>. Celle-là est
**privée** — elle ne s'ouvre que depuis le compte qui l'a publiée — et
c'est précisément pourquoi le site GitHub existe : une enfant n'a pas de
compte Claude.

Elle fait quatre choses que le papier ne peut pas faire.

1. **Elle sait quel jour on est**, et ouvre sur la journée en cours. C'est
   toute sa raison d'être : sur l'affiche, il faut chercher sa colonne ;
   ici, la bonne journée est déjà là. Le samedi et le dimanche, elle ouvre
   sur le lundi qui vient.
2. **Elle sait l'heure.** Le cours en cours est mis en avant, ceux qui sont
   passés s'effacent, et un bandeau annonce ce qui vient — « Anglais, E26,
   dans 12 minutes ». Un enfant de onze ans ne calcule pas « il est 10h12,
   donc… ».
3. **Elle déduit la semaine A ou B.** On lui dit une fois laquelle est en
   cours ; elle retient la parité de la semaine et se débrouille ensuite
   toute seule, y compris après les vacances. La pastille en haut à droite
   permet de basculer à la main.
4. **Elle connaît le groupe de Chloé.** Une fois son groupe renseigné,
   **l'autre groupe disparaît** : elle ne lit plus qu'un cours là où
   l'affiche en montre deux. Tant que le groupe n'est pas renseigné, les
   deux restent affichés — on ne choisit pas à sa place.

Deux vues : **Ma journée** (la liste des cours, avec les horaires) et **Ma
semaine** (la grille des cinq jours). Le thème clair et le thème sombre sont
dessinés tous les deux.

### Le site GitHub Pages

| | |
|---|---|
| **Site** | <https://jmfetienne-coder.github.io/emploi-du-temps-6ec/> |
| **Dépôt** | <https://github.com/jmfetienne-coder/emploi-du-temps-6ec> |
| **Servi depuis** | `docs/`, branche `main`, par `.github/workflows/publier.yml` |

Le fichier servi, `docs/index.html`, est **exactement la page de
l'artefact** et non une copie : le harnais vérifie qu'il enveloppe le même
contenu, si bien que les deux adresses ne peuvent pas se contredire.

**Le dépôt refuse de publier ce qui ne tient pas ses promesses.** À chaque
`push`, GitHub relance **les trois harnais avant le déploiement** — la
page, les PDF et ce README. Une retouche à la main dans le HTML, un emploi
du temps corrigé sans réengendrer, une adresse morte dans ce fichier : la
construction casse, et l'iPad de Chloé continue d'afficher la version
d'avant.

`verifier_planning.py` y tourne sans LaTeX : il ne **compile** rien, il
ouvre les trois PDF versionnés. PyMuPDF suffit.

Ce qui **n'est pas** publié, et pourquoi :

- `PLANNING_CHLOE_ETIENNE_6EC.pdf`, le planning officiel du collège. C'est
  le document de l'établissement et non le nôtre. Il n'est d'ailleurs pas
  nécessaire pour reconstruire quoi que ce soit : tout ce qu'il contient a
  été transcrit dans `donnees_planning.py`.
- Les trois `.tex`, qui sont engendrés : les versionner reviendrait à
  versionner deux fois la même chose, et à risquer qu'ils se contredisent.

**Ce qui est publié l'est publiquement.** Un site GitHub Pages est
accessible à qui en a l'adresse et indexé par les moteurs de recherche, y
compris depuis un dépôt privé. Cette page porte le nom de l'élève, son
établissement, ses professeurs et l'endroit où elle se trouve à chaque
heure de la semaine. Le choix a été fait en connaissance de cause ; il se
défait en rendant le dépôt privé et en désactivant Pages, ou en retirant
ces champs de `donnees_planning.py`.

---

## Comment ça se lit

Tout est fait pour qu'on lise **la couleur avant le mot**. Chaque matière a
la sienne, toujours la même sur l'affiche et sur l'écran, et chaque case
porte à gauche un bandeau de couleur franche — lisible même imprimé en noir
et blanc, où il devient un gris plus ou moins soutenu.

**La couleur est une information, pas une décoration.** Trois décisions :

- Une teinte par matière, pour qu'on la repère sans lire le mot.
- Toutes les teintes fortes sur la même plage de clarté, toutes les claires
  sur une autre : la feuille se tient comme une palette et non comme une
  boîte de crayons. C'est à cela que tient son allure.
- Les matières sont **rangées par famille**, et la légende le montre :
  langues, sciences, humanités, arts et sport, vie scolaire. La famille
  « vie scolaire » est volontairement désaturée : CDI, pastorale, devoirs
  faits et vie de classe ne sont pas des disciplines, et la grille doit le
  dire sans qu'on l'explique.

Le reste des conventions :

- **Le bandeau en haut à droite** dit de quelle semaine il s'agit : vert
  pour A, prune pour B.
- **L'heure de début est en gros**, l'heure de fin en petit dessous. C'est
  l'heure de début qu'on cherche quand on regarde sa montre.
- **Une bande grise en travers** marque la pause déjeuner.
- **Un créneau, une heure.** Le planning du collège fusionne les cases
  quand la même matière occupe deux heures de suite — l'EPS du lundi et du
  jeudi, le français du jeudi matin y sont des cases hautes. Ici, ce sont
  **deux cours d'une heure**, l'un sous l'autre. L'heure est l'unité que
  l'élève manipule : elle regarde sa montre, pas la durée du bloc ; et
  chaque ligne porte alors son propre libellé, au lieu d'une case vide sous
  une case haute qu'il faut relier des yeux.
- **Quand la classe se partage en deux groupes**, la case se partage aussi,
  avec « Groupe 1 » et « Groupe 2 ». Chloé n'en suit qu'un — et sur
  l'application, où l'on peut dire lequel, l'autre ne s'affiche pas.
- **La légende ne liste que les matières présentes sur cette feuille-là.**
  Sur la feuille de la semaine A, pas de CDI : il n'y en a pas cette
  semaine-là, et une couleur qu'on chercherait en vain n'apprend rien.

Sur la feuille commune `PLANNING_A_ET_B.pdf`, **une case n'est coupée en
deux que lorsque les deux semaines diffèrent.** Le lundi à 9h30, l'anglais
est le même en A et en B : la case reste entière. Le mardi à 8h30 en
revanche, c'est histoire-géo en A et SVT/CDI en B : la case se coupe, A en
haut, B en bas, chacune marquée de sa lettre. Couper systématiquement aurait
doublé le nombre de cases à lire pour ne rien apprendre de plus.

En chiffres : **28 heures de cours en semaine A**, **30 en semaine B**,
14 matières, du lundi au vendredi, 8h30 à 17h30 — et pas de cours le
mercredi après-midi.

## La typographie

**Une seule famille de caractères, Avenir Next, mais toute son amplitude** :
Ultra Light pour le titre, Medium pour les heures, Demi Bold pour les
matières, et la coupe **Condensed** pour les détails de case. Empiler deux
ou trois polices aurait été plus rapide et moins tenu ; la hiérarchie se
fait ici par la graisse et par la chasse.

La coupe condensée n'est pas un pis-aller : une case de demi-groupe fait
vingt-cinq millimètres, et c'est la réponse juste au problème de place —
elle garde à « Physique-Chimie » sa ligne unique là où la coupe normale le
casserait en deux.

Avenir Next est une police du système **macOS et iOS**. L'affiche punaisée
au mur et l'écran de l'iPad se composent donc dans le même caractère, sans
rien télécharger. En contrepartie, les PDF se composent avec **lualatex**
et `fontspec`, et non avec pdflatex.

## Les fichiers

```
PLANNING/
├── PLANNING_CHLOE_ETIENNE_6EC.pdf   le planning officiel du collège (la source)
├── donnees_planning.py              LA SOURCE UNIQUE : matières, couleurs, créneaux, cours
├── generer_planning.py              engendre les trois .tex et les compile
├── verifier_planning.py             ouvre les PDF et vérifie ce qui y est composé
├── generer_app.py                   engendre la page de l'iPad, dans ses deux formes
├── verifier_app.py                  vérifie les données, la palette et les contrastes
├── verifier_readme.py               relit les affirmations du README et du PROMPT
├── PROMPT-planning.md               comment étendre ce projet sans le casser
├── planning_ipad.html               l'application, au format attendu par l'artefact
├── docs/index.html                  la MÊME page, autonome : le site GitHub Pages
├── .github/workflows/publier.yml    lance les trois harnais, puis publie sur Pages
├── PLANNING_SEMAINE_A.pdf / .tex
├── PLANNING_SEMAINE_B.pdf / .tex
└── PLANNING_A_ET_B.pdf  / .tex
```

Pour tout refaire après une correction, et la mettre en ligne :

```bash
python3 generer_planning.py && python3 verifier_planning.py && python3 generer_app.py && python3 verifier_app.py && git commit -am "mise à jour de l'emploi du temps" && git push
```

Les trois affiches, l'artefact Claude et le site GitHub se remettent à jour
ensemble : ils lisent le même fichier, et 710 contrôles interdisent qu'ils
divergent. Le `push` déclenche la publication, qui relance les contrôles de
la page avant de déployer.

Pour regarder l'application sur cette machine :

```bash
python3 -m http.server 8777
```

puis ouvrir `http://localhost:8777/docs/`. Un fichier ouvert directement —
sans serveur — ne verra pas son JavaScript s'exécuter.

Les `.tex`, `planning_ipad.html` et `docs/index.html` sont **engendrés** : les
modifier à la main serait perdre la modification à la prochaine exécution.
Tout se corrige dans `donnees_planning.py`.

---

## Ce qui est vérifié, et ce qui ne l'est pas

**Ce qui ne l'est pas, et qu'il faut savoir.** Le planning officiel du
collège est un **scan sans couche texte** : aucun programme ne peut le
relire. Chaque case a été lue à l'écran, agrandie, et les marqueurs A / B
vérifiés un par un. C'est le seul maillon de ce projet qui repose sur une
lecture humaine. **Si le collège publie une version corrigée, c'est
`donnees_planning.py` qu'il faut reprendre**, à l'œil, comme la première
fois.

**Tout le reste se vérifie : 864 contrôles**, 602 pour le papier, 216 pour
l'écran et 46 pour ce README.

### Le papier — `verifier_planning.py`, 602 contrôles

Composer trois feuilles depuis une même source ne garantit rien par
soi-même : une case peut se poser hors de son créneau, un cours de la
semaine B se glisser dans la feuille A, une case s'étendre sur deux lignes
au lieu d'une — et LaTeX ne dira rien, puisqu'il compose aussi volontiers au
mauvais endroit qu'au bon.

Le harnais ouvre donc les trois PDF **aux coordonnées où le générateur dit
avoir posé ses cases**, et lit ce qui s'y trouve :

1. **Le format** — une page, A4 paysage, bandeau de semaine composé.
2. **Ce qui doit être là** — chaque cours se retrouve dans son rectangle,
   avec sa salle, son groupe, son professeur, sa lettre de semaine, et
   chaque case tient sur exactement une ligne.
   S'y ajoute **la règle du projet, épinglée** : aucun cours ne dure plus
   d'une heure, et deux heures de suite de la même matière s'écrivent en
   deux cours. Le champ `duree` reste dans le modèle pour le jour où un
   vrai bloc indivisible s'imposerait ; le contrôle interdit qu'on s'en
   serve sans l'avoir décidé.
3. **Ce qui ne doit pas y être** — les créneaux libres de la semaine sont
   vides. C'est ce contrôle qui prendrait un cours de la semaine B composé
   sur la feuille A.
4. **La légende** — elle porte exactement les matières présentes, et ne
   titre que les familles qui ont au moins une matière à l'affiche.

Le harnais ne recalcule pas la géométrie de son côté. `generer_planning.py`
tient le registre de ce qu'il pose (`POSEES`, `VIDES`) et le harnais suit ce
registre : deux calculs de la même géométrie seraient deux copies, et une
copie finit par diverger de l'autre sans prévenir.

### L'écran — `verifier_app.py`, 216 contrôles

La page dessine sa grille dans le navigateur, à partir d'un bloc JSON que le
générateur y dépose. Le harnais vérifie ce bloc et la palette, c'est-à-dire
tout ce dont la page se sert pour dessiner :

1. **L'idempotence** — la page du disque est bien celle qu'engendre le
   générateur, et `docs/index.html` enveloppe la même page sans la
   recopier. Le site publié et l'artefact ne peuvent donc pas diverger.
2. **Les données** — mêmes cours, mêmes salles, mêmes professeurs, mêmes
   groupes, mêmes semaines que `donnees_planning.py` ; et rien en trop.
3. **La palette** — le ton de jour de chaque matière est celui du papier,
   au caractère près. C'est ce qui interdit à l'affiche et à l'écran de
   diverger.
4. **La lisibilité** — le contraste de chaque nom de matière sur son fond
   est **mesuré**, de jour comme de nuit, et doit valoir au moins 4,5:1,
   le seuil des WCAG pour du texte courant.
5. **Les demi-groupes** — un créneau partagé porte bien un cours pour
   **chaque** groupe. C'est l'invariant dont dépend le filtrage : s'il n'en
   portait qu'un, l'élève de l'autre groupe verrait « Pas de cours ». Rien
   dans les données n'impose cette symétrie — c'est un fait du planning, et
   c'est pourquoi il est épinglé plutôt que supposé.
6. **Les horaires** — la pause déjeuner n'est pas saisie : elle se déduit
   de ce qui l'entoure, et le harnais vérifie qu'elle tombe juste.
7. **L'autonomie** — le site n'appelle **aucune** ressource extérieure :
   ni police, ni script, ni feuille de style. C'est ce qui le rend
   consultable hors connexion, et ce qui garantit qu'aucun tiers ne voit
   passer les horaires d'une enfant.
8. **L'encodage** — la page ne porte aucun caractère non-ASCII, et ses
   accents reviennent bien une fois les échappements résolus. Voir
   l'incident ci-dessous : c'est le contrôle qui interdit au mojibake de
   revenir.

Ce que ce harnais **ne fait pas**, et il faut le dire : ouvrir un navigateur
pour regarder le rendu. Cette vérification-là a été faite à l'écran, en
clair et en sombre, et elle est à refaire à chaque changement d'allure.
`verifier_planning.py` est plus exigeant parce qu'il le peut : un PDF se
relit sans navigateur.

### Le README et le PROMPT — `verifier_readme.py`, 46 contrôles

Un README vieillit plus vite que ce qu'il décrit. Ses compteurs restent à
leur valeur de la veille, ses chemins survivent aux fichiers qu'ils
nomment, ses adresses cessent de répondre — et le lecteur suivant fait
confiance sans que rien ne le détrompe. C'est la règle des valeurs
imprimées, appliquée à la prose : **une affirmation qu'aucun programme ne
relit finit par être fausse.**

Il relit **deux** fichiers : ce README, qui dit ce que le projet est, et
`PROMPT-planning.md`, qui dit comment on l'étend. Les chemins et les
adresses sont vérifiés dans les deux ; les compteurs et les chiffres ne
vivent que dans ce README, et c'est délibéré — une valeur écrite à deux
endroits est une valeur qui va diverger. Un contrôle refuse d'ailleurs
qu'un compteur apparaisse dans le PROMPT.

Les affirmations relues :

1. **Les compteurs**, obtenus en relançant chaque harnais — jamais recopiés.
   Le total est calculé comme une somme, et non écrit à côté des autres :
   c'est par là qu'un README se met à se contredire lui-même.
2. **Les chemins entre dos-d'âne**, cherchés sur le disque. Un chemin cité
   est une affirmation d'existence — sauf pour les fichiers que
   `.gitignore` tient hors du dépôt, où l'affirmation à relire n'est pas
   « il existe » mais « il en est bien écarté ». Confondre les deux faisait
   échouer la chaîne GitHub, qui travaille sur un clone frais.
3. **Les adresses**, interrogées. Deux sont déclarées non testables, et le
   sont nommément : `localhost`, qui n'est pas un service publié, et
   l'artefact Claude, qui exige une authentification. L'exemption est
   écrite dans le harnais, pas devinée à l'exécution — une exception
   silencieuse passerait pour un succès.
4. **Le format des trois PDF**, obtenu en les ouvrant.
5. **Les chiffres tirés des données** : les heures par semaine, le nombre
   de matières.
6. **Le contraste le plus faible**, remesuré sur les quatorze matières.
7. **Son propre compteur.** Un harnais qui vérifie les compteurs des autres
   et pas le sien serait la seule affirmation de ce fichier que personne ne
   relit.

Ce qu'il ne relit **pas** : la section « Les incidents » ci-dessous. Elle
raconte des états passés — « Histoire-Géo tombait à 3,6:1 » — et ces
nombres ne décrivent plus rien. Les tenir pour des affirmations présentes
obligerait à réécrire le récit pour satisfaire le harnais, c'est-à-dire à
le falsifier.

```bash
python3 verifier_readme.py
```

L'option `--sans-reseau` laisse les adresses de côté. Elle ne les **saute**
pas : elle pose le contrôle en disant qu'il n'a pas été vérifié, et le
nombre de contrôles ne change pas d'un mode à l'autre. Sans quoi ce
harnais, qui compte les siens, se serait mis en échec tout seul — c'est
arrivé, et c'est ce qui a fait écrire cette ligne.

### Les contrôles ont été mis à l'épreuve

Un harnais qui n'échoue jamais peut aussi bien ne rien lire. Deux fautes ont
été introduites volontairement dans les données, sans réengendrer les PDF :

- une salle changée (E25 → E31) : **3 contrôles en échec** ;
- un cours de la semaine A déclaré aussi en semaine B : **5 contrôles en
  échec**, dont la légende de la feuille B.

Les deux fautes ont ensuite été retirées. C'est la preuve que le harnais lit
bien le PDF, et non les données une seconde fois.

---

## Les incidents, pour qui reprendra ce projet

- **Quatre couleurs étaient trop pâles**, et personne ne l'avait vu :
  Histoire-Géo tombait à 3,6:1 sur son fond, EMC à 3,8:1, Vie de classe à
  3,7:1, SVT à 4,4:1. Le contrôle de contraste les a trouvées le jour où il
  a été écrit. Elles ont été foncées à teinte constante — seule la clarté
  est négociable, la teinte identifie la matière. Le plus faible contraste
  vaut désormais 4,6:1.
- **Les accents se sont affichés en mojibake.** Publiée en UTF-8, la page a
  été relue en Latin-1 par l'hébergeur : « CHLOÉ ÉTIENNE · 6ᵉ C » devenait
  « CHLOÃ© Ã‰TIENNE Â· 6ÁΜ‰ C ». Le fichier était pourtant de l'UTF-8
  parfaitement valide — c'est la déclaration de jeu de caractères, côté
  hébergeur, qui manquait, et sur quoi ce projet n'a aucune prise. Plutôt
  que d'espérer, la page a cessé d'en dépendre : **elle est désormais
  écrite en ASCII pur**, entités numériques dans le balisage et `\uXXXX`
  dans le script. Aucun décodeur ne peut plus se tromper, quel que soit
  l'hébergeur.
- **L'application se croyait lundi le dimanche.** La date de référence
  bascule sur le lundi qui vient dès le samedi, pour ouvrir sur la semaine
  qui commence ; mais « aujourd'hui » en héritait, et la page annonçait un
  cours « en ce moment » un dimanche après-midi. La référence sert à
  choisir la journée, pas à dire quel jour on est.
- **Le scan était à l'envers.** Rendu puis tourné de −90°, il sortait la
  tête en bas ; c'est une rotation de 180° qu'il fallait.
- **L'espace-mot d'Avenir Next**, tirée du `.ttc` par `fontspec`, est très
  large : « Arts plastiques » se lisait « Arts  plastiques » dans toutes
  les cases. Et sur les familles interlettrées, c'est l'inverse : le
  crénage mange l'espace et « SEMAINE A » se composait « SEMAINEA ».
  Aucune erreur n'est levée ni dans un cas ni dans l'autre.
- **`.gr-case span { display: block }`** attrapait aussi le séparateur
  « · », qui passait à la ligne : « E26 », puis un point tout seul, puis
  « Groupe 1 ». Il a fallu une règle plus sélective pour le ramener en
  ligne.
- **Le nom du fichier source porte des `_`.** Non échappés, LaTeX les prend
  pour des indices mathématiques et s'arrête sur « Missing $ inserted ».
- **Une seule passe de compilation donnait une page blanche.** Le dessin
  est posé par rapport à `current page` avec `remember picture, overlay` :
  la position n'est connue qu'à la passe suivante, et la première compose
  une page vide sans lever d'erreur. Le générateur compile donc deux fois.
- **Un libellé peut être coupé en fin de ligne** dans une demi-case :
  « Physique-Chimie » s'y compose parfois sur deux lignes. Le harnais ôte
  les blancs avant de chercher, sinon il déclarerait muette une case qui
  dit exactement ce qu'on attend d'elle.

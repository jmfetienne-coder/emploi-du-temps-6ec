#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L'emploi du temps de Chloé, 6ᵉ C — la source unique.

Relevé sur `PLANNING_CHLOE_ETIENNE_6EC.pdf`, l'emploi du temps officiel du
collège Pastre-Grande Bastide (édition du 28/08/2026). Ce PDF est un scan :
il n'a pas de couche texte, et rien ne pouvait en être extrait
automatiquement. Chaque case a donc été lue à l'écran, agrandie, et les
marqueurs A / B vérifiés un par un — c'est la seule partie de ce projet qui
ne se vérifie pas toute seule.

TOUT LE RESTE EN DÉCOULE. Les trois PDF sont engendrés depuis ce fichier :
corriger une erreur ici la corrige dans les trois.

Conventions
-----------
`semaines` vaut "AB" quand le cours a lieu les deux semaines, "A" ou "B"
sinon. Un créneau peut porter deux cours différents selon la semaine, ou
deux cours en même temps pour les deux demi-groupes (Gr1 et Gr2).
"""

# --------------------------------------------------------------------------
#  Les matières : nom court, couleur forte, couleur claire, famille
#
#  LA COULEUR EST UNE INFORMATION, PAS UNE DÉCORATION. Trois décisions :
#
#  1. Une teinte par matière, pour qu'on la repère sans lire le mot — c'est
#     ainsi qu'un enfant de onze ans lit une grille.
#  2. Toutes les teintes fortes sur la même plage de clarté, toutes les
#     claires sur une autre : la feuille se tient comme une palette, et non
#     comme une boîte de crayons. C'est à cela que tient l'élégance ici.
#  3. Les matières sont rangées par famille, et la légende le montre. La
#     famille « vie scolaire » est volontairement désaturée : CDI, pastorale,
#     devoirs faits et vie de classe ne sont pas des disciplines, et la
#     grille doit le dire sans qu'on l'explique.
#
#  La couleur forte porte le bandeau et le nom ; elle reste lisible imprimée
#  en noir et blanc, où elle devient un gris franc.
#
#  CONTRAINTE MESURÉE, ET NON APPRÉCIÉE À L'ŒIL : le contraste de chaque
#  couleur forte sur sa couleur claire vaut au moins 4,5:1, le seuil des
#  WCAG pour du texte courant. `verifier_app.py` le mesure pour les
#  quatorze matières, de jour comme de nuit. Quatre couleurs ont dû être
#  foncées quand ce contrôle a été posé — Histoire-Géo tombait à 3,6:1,
#  et personne ne l'avait vu.
# --------------------------------------------------------------------------
MATIERES = {
    # Langues
    "FRANCAIS":   ("Français",        "2F5C8F", "E4ECF5", "Langues"),
    "ANGLAIS":    ("Anglais",         "5B4B9E", "E9E6F5", "Langues"),
    # Sciences
    "MATHS":      ("Maths",           "B23A2E", "F7E4E1", "Sciences"),
    "PHYSIQUE":   ("Physique-Chimie", "17726F", "DCEFEC", "Sciences"),
    "SVT":        ("SVT",             "3C7539", "E3F0DF", "Sciences"),
    # Humanités
    "HIST":       ("Histoire-Géo",    "975B13", "F8E9D4", "Humanités"),
    "EMC":        ("EMC",             "7F6712", "F3EDD3", "Humanités"),
    # Arts et sport
    "ARTS":       ("Arts plastiques", "A8336B", "F7E1EB", "Arts et sport"),
    "MUSIQUE":    ("Musique",         "7A4B86", "F0E5F3", "Arts et sport"),
    "EPS":        ("EPS",             "5C6B22", "EBEFD8", "Arts et sport"),
    # Vie scolaire — en retrait, volontairement
    "CDI":        ("CDI",             "6E5B48", "EEE8E1", "Vie scolaire"),
    "PASTORALE":  ("Pastorale",       "4E5F73", "E5EAEF", "Vie scolaire"),
    "DEVOIRS":    ("Devoirs faits",   "6B665E", "EBE9E5", "Vie scolaire"),
    "VIECLASSE":  ("Vie de classe",   "6C6760", "EDEBE8", "Vie scolaire"),
}

#  L'ordre des familles dans la légende. Il n'est pas alphabétique : il va
#  des disciplines fondamentales à la vie de l'établissement.
FAMILLES = ["Langues", "Sciences", "Humanités", "Arts et sport", "Vie scolaire"]

#  Les gris de la page. Chauds, tirés vers l'ocre des humanités : un gris
#  neutre à côté de ces teintes-là a l'air d'avoir été subi, pas choisi.
ENCRE = "23262B"        # le texte, presque noir
GRIS = "8B8479"         # les détails de case, les mentions
FILET = "D8D4CC"        # les filets de structure
PAPIER = "FFFFFF"

# --------------------------------------------------------------------------
#  Les créneaux de la journée
# --------------------------------------------------------------------------
CRENEAUX = [
    ("8h30", "9h30"),
    ("9h30", "10h30"),
    ("10h30", "11h30"),
    ("11h30", "12h30"),
    ("REPAS", ""),
    ("13h30", "14h30"),
    ("14h30", "15h30"),
    ("15h30", "16h30"),
    ("16h30", "17h30"),
]

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]


def cours(matiere, prof, salle="E26", semaines="AB", groupe=None, duree=1):
    return {"matiere": matiere, "prof": prof, "salle": salle,
            "semaines": semaines, "groupe": groupe, "duree": duree}


# --------------------------------------------------------------------------
#  L'emploi du temps. Une entrée par case du planning officiel.
#  Clé : (jour, heure de début). Valeur : la liste des cours de ce créneau.
# --------------------------------------------------------------------------
SEMAINE = {
    # ------------------------------------------------------------- lundi
    ("lundi", "8h30"): [
        cours("CDI", "Chassaigne", "CDI", "B", "Groupe 1"),
        cours("SVT", "Criado", "Labo", "B", "Groupe 2"),
    ],
    ("lundi", "9h30"): [cours("ANGLAIS", "Cuesta Roe")],
    ("lundi", "10h30"): [
        cours("FRANCAIS", "Dubois", "E26", "AB", "Groupe 1"),
        cours("MATHS", "Spriet", "E26", "AB", "Groupe 2"),
    ],
    ("lundi", "11h30"): [
        cours("MATHS", "Spriet", "E26", "AB", "Groupe 1"),
        cours("FRANCAIS", "Dubois", "E26", "AB", "Groupe 2"),
    ],
    ("lundi", "13h30"): [cours("EPS", "Jullien", "EPS2", "AB", None, 2)],
    ("lundi", "15h30"): [cours("MUSIQUE", "Faure", "E25")],

    # ------------------------------------------------------------- mardi
    ("mardi", "8h30"): [
        cours("HIST", "Halimi", "E26", "A"),
        cours("SVT", "Criado", "Labo", "B", "Groupe 1"),
        cours("CDI", "Chassaigne", "CDI", "B", "Groupe 2"),
    ],
    ("mardi", "9h30"): [cours("MATHS", "Spriet")],
    ("mardi", "10h30"): [
        cours("ARTS", "Adjeroud", "E26", "A"),
        cours("MATHS", "Spriet", "E26", "B"),
    ],
    ("mardi", "11h30"): [cours("FRANCAIS", "Dubois")],
    ("mardi", "13h30"): [
        cours("ANGLAIS", "Cuesta Roe", "E26", "A"),
        cours("ARTS", "Adjeroud", "E26", "B"),
    ],
    ("mardi", "14h30"): [cours("MATHS", "Spriet")],
    ("mardi", "15h30"): [cours("PHYSIQUE", "Guipert")],
    ("mardi", "16h30"): [cours("DEVOIRS", "Mathurin", "—", "A")],

    # ---------------------------------------------------------- mercredi
    ("mercredi", "8h30"): [
        cours("MATHS", "Spriet", "E26", "A"),
        cours("PASTORALE", "Aps, Rios", "E26", "B"),
    ],
    ("mercredi", "9h30"): [
        cours("PHYSIQUE", "Guipert", "E26", "A"),
        cours("MATHS", "Spriet", "E26", "B"),
    ],
    ("mercredi", "10h30"): [
        cours("PASTORALE", "Aps, Rios", "E26", "A"),
        cours("ANGLAIS", "Cuesta Roe", "E26", "B"),
    ],
    ("mercredi", "11h30"): [cours("MATHS", "Spriet", "E26", "B")],

    # ------------------------------------------------------------- jeudi
    ("jeudi", "8h30"): [cours("FRANCAIS", "Dubois", "E26", "AB", None, 2)],
    ("jeudi", "10h30"): [
        cours("SVT", "Criado", "E26", "A"),
        cours("ANGLAIS", "Cuesta Roe", "E26", "B"),
    ],
    ("jeudi", "11h30"): [cours("HIST", "Halimi")],
    ("jeudi", "13h30"): [cours("EPS", "Jullien", "EPS2", "AB", None, 2)],
    ("jeudi", "15h30"): [cours("ANGLAIS", "Cuesta Roe", "E26", "B")],
    ("jeudi", "16h30"): [cours("DEVOIRS", "Cuesta Roe", "—", "B")],

    # ---------------------------------------------------------- vendredi
    ("vendredi", "9h30"): [cours("EMC", "Halimi", "E26", "A")],
    ("vendredi", "10h30"): [cours("ANGLAIS", "Cuesta Roe")],
    ("vendredi", "11h30"): [cours("HIST", "Halimi")],
    ("vendredi", "13h30"): [cours("FRANCAIS", "Dubois")],
    ("vendredi", "14h30"): [
        cours("SVT", "Criado", "E26", "A"),
        cours("VIECLASSE", "Dubois", "E26", "B"),
    ],
}

ELEVE = "Chloé Étienne"
CLASSE = "6\\textsuperscript{e} C"
ETABLISSEMENT = "Collège Pastre-Grande Bastide"
ANNEE = "2026-2027"
SOURCE = "PLANNING_CHLOE_ETIENNE_6EC.pdf, édition du 28/08/2026"


def pour_semaine(lettre):
    """L'emploi du temps d'une semaine : A, B, ou les deux si lettre vaut None."""
    sortie = {}
    for (jour, heure), liste in SEMAINE.items():
        gardes = [c for c in liste
                  if lettre is None or lettre in c["semaines"]]
        if gardes:
            sortie[(jour, heure)] = gardes
    return sortie

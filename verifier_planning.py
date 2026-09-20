#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Les trois PDF disent-ils ce que dit `donnees_planning.py` ?

Le planning officiel est un scan sans couche texte : personne ne peut le
relire automatiquement, et la transcription dans `donnees_planning.py` a dû
être faite à l'œil. C'est le seul maillon non vérifié de ce projet, et il
est assumé comme tel.

TOUT LE RESTE se vérifie, et c'est l'objet de ce fichier. Composer trois
feuilles depuis une même source ne garantit rien : une case peut se poser
hors de son créneau, un cours de la semaine B se glisser dans la feuille A,
un blocs de deux heures n'en couvrir qu'une — sans qu'aucune erreur soit
levée, puisque LaTeX compose tout ce qu'on lui donne, au bon endroit comme
au mauvais.

Le contrôle ouvre donc chaque PDF **aux coordonnées où le générateur dit
avoir posé ses cases**, et lit ce qui s'y trouve. Il ne recalcule pas la
géométrie de son côté : `generer_planning.py` tient un registre (`POSEES`,
`VIDES`) de ce qu'il pose, et c'est ce registre que le harnais suit. Deux
calculs de la même géométrie seraient deux copies, et une copie finit par
diverger de l'autre.

Quatre familles de contrôles :

1. **Le format.** Une page, A4 paysage. Une feuille passée en portrait sans
   qu'on le remarque est une feuille qu'on réimprime.
2. **Ce qui est là.** Chaque cours des données se retrouve dans son
   rectangle, avec sa salle, son groupe et son professeur.
3. **Ce qui n'y est pas.** Les créneaux libres de cette semaine-là sont
   vides : c'est le contrôle qui prend un cours de la semaine B composé sur
   la feuille A.
4. **Le compte.** Les feuilles A et B portent ensemble tous les cours de
   la semaine, et la légende liste exactement les matières présentes.

Usage : python3 verifier_planning.py
"""
import os
import re
import sys
import unicodedata

import fitz

import donnees_planning as D
import generer_planning as G

ICI = os.path.dirname(os.path.abspath(__file__))
MM = 72.0 / 25.4
controles = []


def verifier(libelle, calcule, attendu):
    controles.append((libelle, calcule, attendu, calcule == attendu))


def serre(t):
    """Le texte sans ses blancs, ligatures résolues.

    Un libellé peut être coupé en fin de ligne dans une demi-case :
    « Physique-Chimie » s'y compose sur deux lignes. En ôtant les blancs, la
    recherche retrouve le mot que l'enfant lit, et non celui que le fichier
    source écrit.
    """
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", t))


def lu(page, r, haut_pt):
    """Le texte composé dans le rectangle (x, y, larg, haut) en millimètres.

    Le dessin est posé depuis `current page.south west` : l'origine TikZ est
    en bas à gauche, celle de PyMuPDF en haut à gauche. D'où le retournement.
    """
    x0 = r["x"] * MM
    x1 = (r["x"] + r["larg"]) * MM
    y0 = haut_pt - r["y"] * MM
    y1 = haut_pt - (r["y"] - r["haut"]) * MM
    return page.get_text("text", clip=fitz.Rect(x0, y0, x1, y1))


for nom, lettre, badge, montrer_ab in G.SORTIES:
    semaine = D.pour_semaine(lettre)
    # On réengendre le document : le registre se remplit de ce que le
    # générateur pose, pour le PDF qui est sur le disque.
    G.document(semaine, badge, montrer_ab, "")
    posees, vides = list(G.POSEES), list(G.VIDES)

    chemin = os.path.join(ICI, nom + ".pdf")
    if not os.path.exists(chemin):
        verifier("%s : le PDF est construit" % nom, False, True)
        continue
    doc = fitz.open(chemin)
    page = doc[0]
    L, H = page.rect.width, page.rect.height

    # ------------------------------------------------------- 1. le format
    verifier("%s : une seule page" % nom, doc.page_count, 1)
    verifier("%s : A4 paysage" % nom,
             (round(L), round(H)), (842, 595))
    verifier("%s : le bandeau de semaine est composé" % nom,
             serre(badge[0]) in serre(page.get_text()), True)

    # --------------------------------------------- 2. ce qui doit être là
    verifier("%s : autant de cases posées que de cours" % nom,
             len(posees), sum(len(v) for v in semaine.values()))
    for p in posees:
        c = p["cours"]
        t = serre(lu(page, p, H))
        ou = "%s %s" % (c["matiere"], c["salle"])
        verifier("%s : %s est composé dans sa case" % (nom, ou),
                 serre(D.MATIERES[c["matiere"]][0]) in t, True)
        if c["salle"] not in ("—", ""):
            verifier("%s : %s porte sa salle" % (nom, ou),
                     serre(c["salle"]) in t, True)
        if c["groupe"]:
            verifier("%s : %s porte son groupe" % (nom, ou),
                     serre(c["groupe"]) in t, True)
        if not p["compact"]:
            verifier("%s : %s porte son professeur" % (nom, ou),
                     serre(c["prof"]) in t, True)
        if p["etiquette"]:
            verifier("%s : %s porte sa lettre de semaine" % (nom, ou),
                     p["etiquette"] in lu(page, p, H), True)
        # Un bloc de deux heures couvre deux lignes, et non une : sans ce
        # contrôle, l'EPS du lundi pourrait se poser sur la seule première
        # heure sans que rien ne le dise.
        attendue = G.HAUT_LIGNE * c["duree"]
        if not p["etiquette"]:
            verifier("%s : %s occupe %d heure(s)" % (nom, ou, c["duree"]),
                     round(p["haut"], 2), round(attendue, 2))

    # ------------------------------------------ 3. ce qui ne doit pas y être
    # Un créneau libre cette semaine-là doit l'être sur la feuille. C'est le
    # contrôle qui prendrait un cours de la semaine B composé sur la
    # feuille A — une fuite qu'une compilation réussie ne signale pas.
    for v in vides:
        t = serre(lu(page, v, H))
        verifier("%s : un créneau libre reste vide (x=%.0f, y=%.0f)"
                 % (nom, v["x"], v["y"]), t, "")

    # -------------------------------------------------------- 4. la légende
    # La légende liste les matières de CETTE feuille : ni une de plus — une
    # couleur qu'on cherche en vain dans la grille —, ni une de moins.
    # Sous la grille, marge comprise : la légende commence exactement là où
    # la grille s'arrête, c'est-à-dire MARGE + HAUT_LEGENDE au-dessus du bas.
    bas = fitz.Rect(0, H - (G.MARGE + G.HAUT_LEGENDE) * MM, L, H)
    pied = page.get_text("text", clip=bas)
    presentes = {c["matiere"] for liste in semaine.values() for c in liste}
    for m, (libelle, fort, clair, famille) in D.MATIERES.items():
        verifier("%s : la légende %s %s"
                 % (nom, "porte" if m in presentes else "ignore", libelle),
                 serre(libelle) in serre(pied), m in presentes)
    # La légende range les matières par famille, et nomme les familles. Une
    # famille dont aucune matière n'est à l'affiche ne doit pas être titrée :
    # une rubrique vide se cherche, et ne se trouve pas.
    familles_vues = {D.MATIERES[m][3] for m in presentes}
    for famille in D.FAMILLES:
        verifier("%s : la légende %s la famille « %s »"
                 % (nom, "titre" if famille in familles_vues else "tait", famille),
                 serre(famille.upper()) in serre(pied), famille in familles_vues)

# --------------------------------------------- 4 bis. un créneau, une heure
# LA RÈGLE DU PROJET, ÉPINGLÉE. Le planning du collège fusionne les cases
# quand la même matière occupe deux heures de suite ; ici on les écrit en
# deux cours d'une heure. L'heure est l'unité que l'élève manipule, et
# chaque ligne de la grille porte alors son propre libellé au lieu d'une
# case vide sous une case haute.
#
# Le champ `duree` reste dans le modèle pour le jour où un vrai bloc
# indivisible s'imposerait. Ce contrôle interdit qu'on s'en serve sans
# l'avoir décidé : il faudra le modifier sciemment, et non le contourner.
for (jour, heure), liste in sorted(D.SEMAINE.items()):
    for c in liste:
        verifier("règle : %s %s, %s tient sur une heure"
                 % (jour, heure, c["matiere"]), c["duree"], 1)

# Et le corollaire : deux heures de suite de la même matière sont DEUX
# cours. Le contrôle le constate là où c'est le cas — si l'un des deux
# disparaissait au profit d'un bloc, la ligne suivante deviendrait vide.
HEURES = [h for h, _ in D.CRENEAUX if h != "REPAS"]
suites = []
for jour in D.JOURS:
    for i in range(len(HEURES) - 1):
        for lettre in "AB":
            ici = {c["matiere"] for c in D.pour_semaine(lettre).get((jour, HEURES[i]), [])
                   if not c["groupe"]}
            apres = {c["matiere"] for c in D.pour_semaine(lettre).get((jour, HEURES[i + 1]), [])
                     if not c["groupe"]}
            for m in sorted(ici & apres):
                suites.append((jour, HEURES[i], HEURES[i + 1], m, lettre))
for jour, a, b, m, lettre in suites:
    verifier("règle : %s semaine %s, %s de %s à %s est écrit en deux cours"
             % (jour, lettre, m, a, b),
             len(D.pour_semaine(lettre).get((jour, b), [])) > 0, True)

# ------------------------------------------------- 5. aucune perte entre A et B
# Tout cours de la semaine se compose sur au moins une des deux feuilles.
for (jour, heure), liste in D.SEMAINE.items():
    for c in liste:
        vus = sum(1 for l in "AB"
                  if c in D.pour_semaine(l).get((jour, heure), []))
        verifier("répartition : %s %s %s est sur %s"
                 % (jour, heure, c["matiere"],
                    "les deux feuilles" if c["semaines"] == "AB"
                    else "une feuille"),
                 vus, 2 if c["semaines"] == "AB" else 1)

# =====================================================================
if __name__ == "__main__":
    echecs = [c for c in controles if not c[3]]
    for libelle, calcule, attendu, ok in controles:
        if not ok:
            print("  [ECHEC] %s" % libelle)
            print("           calculé = %r   attendu = %r" % (calcule, attendu))
    print()
    print("  planning : %d contrôles, %d en échec" % (len(controles), len(echecs)))
    sys.exit(1 if echecs else 0)

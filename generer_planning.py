#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Engendre les trois plannings de Chloé, en A4 paysage.

    PLANNING_SEMAINE_A.pdf    la semaine A seule
    PLANNING_SEMAINE_B.pdf    la semaine B seule
    PLANNING_A_ET_B.pdf       les deux sur la même feuille

Tous les trois sortent de `donnees_planning.py` : une correction portée là
se retrouve dans les trois, et ils ne peuvent pas diverger.

LE PARTI PRIS TYPOGRAPHIQUE

Une seule famille de caractères, Avenir Next, mais toute son amplitude :
Ultra Light pour le titre, Medium pour les heures, Demi Bold pour les
matières, et la coupe **Condensed** pour les détails de case. Empiler deux
ou trois polices aurait été plus rapide et moins tenu ; la hiérarchie se
fait ici par la graisse et par la chasse, ce qui est le métier.

La coupe condensée n'est pas un pis-aller : une case de demi-groupe fait
vingt-cinq millimètres, et c'est la réponse juste au problème de place —
elle garde à « Physique-Chimie » sa ligne unique là où la coupe normale le
casserait en deux.

Avenir Next est une police du système macOS. Le document se compose donc
avec **lualatex** et `fontspec`, et non avec pdflatex.

LE PARTI PRIS DE LA FEUILLE « A ET B »

Sur les quarante-cinq créneaux de la semaine, la plupart ne changent pas
d'une semaine à l'autre. Couper toutes les cases en deux pour montrer deux
fois la même chose doublerait la densité sans rien apprendre. La case n'est
donc coupée que **lorsque les deux semaines diffèrent** : partout ailleurs
elle reste entière, et l'œil tombe tout de suite sur les quelques cases qui
changent.

Usage : python3 generer_planning.py
"""
import os
import subprocess
import sys

import donnees_planning as D

ICI = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ mesures
# A4 paysage, en millimètres. Tout est posé en coordonnées absolues : c'est
# le seul moyen de garantir qu'un bloc de deux heures couvre exactement deux
# lignes, et qu'une case coupée en deux tombe juste au milieu.
PAGE_L, PAGE_H = 297.0, 210.0
MARGE = 11.0
COL_HEURE = 17.0
HAUT_ENTETE = 31.0
HAUT_LEGENDE = 28.0

LARGEUR = PAGE_L - 2 * MARGE
LARG_JOUR = (LARGEUR - COL_HEURE) / len(D.JOURS)
HAUT_GRILLE = PAGE_H - 2 * MARGE - HAUT_ENTETE - HAUT_LEGENDE

# Le repas prend une bande mince : c'est une respiration, pas un cours.
HAUT_REPAS = 6.0
LIGNES_COURS = len(D.CRENEAUX) - 1
HAUT_LIGNE = (HAUT_GRILLE - HAUT_REPAS) / LIGNES_COURS

# Le dessin de la case. Le bandeau de couleur est le seul ornement de la
# feuille, et il porte une information : c'est lui qu'on voit avant le mot.
RAYON = 0.7          # coins, en mm — assez pour adoucir, pas assez pour amuser
BANDEAU = 1.5        # largeur du bandeau de couleur
GOUTTIERE = 0.5      # l'air entre deux cases voisines

# Ce que la page pose réellement. Le harnais lit CE registre plutôt que de
# recalculer les coordonnées de son côté : deux calculs de la même géométrie,
# c'est déjà une copie, et une copie finit par diverger. `verifier_planning.py`
# ouvre le PDF à ces rectangles-là et regarde ce qui s'y trouve.
POSEES = []      # les cases de cours : rectangle + cours + mode d'affichage
VIDES = []       # les créneaux sans aucun cours cette semaine-là


def y_de_ligne(i):
    """Le haut de la ligne i, compté depuis le bas de la page."""
    y = MARGE + HAUT_LEGENDE + HAUT_GRILLE
    for k in range(i):
        y -= HAUT_REPAS if D.CRENEAUX[k][0] == "REPAS" else HAUT_LIGNE
    return y


def echappe(t):
    return (t.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
             .replace("#", r"\#"))


def filet(x0, y, x1, couleur="filet", epaisseur=0.18):
    return (r"\draw[color=%s, line width=%.2fmm] (%.2f,%.2f) -- (%.2f,%.2f);"
            % (couleur, epaisseur, x0, y, x1, y))


def case(x, y, larg, haut, c, compact=False, etiquette=None):
    """Une case de cours : fond clair, bandeau de couleur à gauche, texte."""
    nom, fort, clair, famille = D.MATIERES[c["matiere"]]
    POSEES.append({"x": x, "y": y, "larg": larg, "haut": haut,
                   "cours": c, "compact": compact, "etiquette": etiquette})
    m = GOUTTIERE
    L = []
    L.append(r"\fill[rounded corners=%.2fmm, fill=c%s] (%.2f,%.2f) rectangle (%.2f,%.2f);"
             % (RAYON, c["matiere"], x + m, y - haut + m, x + larg - m, y - m))
    # Le bandeau : la couleur forte, sur toute la hauteur de la case. Il
    # aligne les cases entre elles et donne à la colonne son ossature.
    L.append(r"\fill[rounded corners=%.2fmm, fill=f%s] (%.2f,%.2f) rectangle (%.2f,%.2f);"
             % (RAYON * 0.6, c["matiere"], x + m, y - haut + m,
                x + m + BANDEAU, y - m))
    cx = x + m + BANDEAU + 2.0
    larg_texte = larg - (m + BANDEAU + 2.0) - m - 1.0
    # La graisse porte la hiérarchie : Demi Bold pour la matière, coupe
    # condensée et gris chaud pour ce qui la précise.
    t_nom = 7.4 if not compact else 6.2
    t_det = 5.6 if not compact else 5.0
    lignes = [r"{\avDemi\fontsize{%.1f}{%.1f}\selectfont\color{f%s} %s}"
              % (t_nom, t_nom + 1.2, c["matiere"], echappe(nom))]
    detail = c["salle"] if c["salle"] not in ("—", "") else ""
    if c["groupe"]:
        detail = (detail + r" \textbf{·} " + c["groupe"]) if detail else c["groupe"]
    if not compact:
        detail = ((detail + r" \textbf{·} " + echappe(c["prof"]))
                  if detail else echappe(c["prof"]))
    if detail:
        lignes.append(r"{\cdReg\fontsize{%.1f}{%.1f}\selectfont\color{gris} %s}"
                      % (t_det, t_det + 1.0, echappe(detail)))
    L.append(r"\node[anchor=west, align=left, text width=%.2fmm, inner sep=0] "
             r"at (%.2f,%.2f) {%s};"
             % (larg_texte, cx, y - haut / 2.0, r"\\[1.6pt]".join(lignes)))
    if etiquette:
        # La lettre de semaine, en pastille pleine : sur la feuille commune
        # c'est elle qui dit laquelle des deux moitiés on est en train de lire.
        rx, ry = x + larg - m - 2.6, y - m - 2.4
        L.append(r"\fill[fill=f%s, rounded corners=0.5mm] (%.2f,%.2f) "
                 r"rectangle (%.2f,%.2f);"
                 % (c["matiere"], rx - 1.7, ry - 1.7, rx + 1.7, ry + 1.7))
        L.append(r"\node[anchor=center, inner sep=0] at (%.2f,%.2f) "
                 r"{\avDemi\fontsize{5}{5}\selectfont\color{white} %s};"
                 % (rx, ry, etiquette))
    return L


def entete(titre_semaine):
    """Le haut de la feuille : le titre, l'identité, le bandeau de semaine."""
    L = []
    haut = PAGE_H - MARGE
    # Le titre en Ultra Light et en grand : la légèreté du trait fait tout le
    # calme de la page, là où une graisse forte l'aurait rendue scolaire.
    L.append(r"\node[anchor=north west, inner sep=0] at (%.2f,%.2f) "
             r"{\avUltra\fontsize{25}{27}\selectfont\color{encre} %s};"
             % (MARGE, haut, "Emploi du temps"))
    L.append(r"\node[anchor=north west, inner sep=0] at (%.2f,%.2f) "
             r"{\espace\fontsize{7.4}{9}\selectfont\color{encre} %s};"
             % (MARGE, haut - 11.4, D.ELEVE.upper()))
    L.append(r"\node[anchor=north west, inner sep=0] at (%.2f,%.2f) "
             r"{\cdReg\fontsize{7}{8.4}\selectfont\color{gris} "
             r"%s \textbf{·} %s \textbf{·} %s};"
             % (MARGE, haut - 16.4, D.CLASSE, D.ETABLISSEMENT, D.ANNEE))

    # Le bandeau de semaine : la première chose à voir sur la feuille.
    bl, bh = 54.0, 12.6
    bx = PAGE_L - MARGE - bl
    L.append(r"\fill[rounded corners=1.4mm, fill=%s] (%.2f,%.2f) rectangle (%.2f,%.2f);"
             % (titre_semaine[1], bx, haut - bh, bx + bl, haut))
    L.append(r"\node[anchor=center, inner sep=0] at (%.2f,%.2f) "
             r"{\espace\fontsize{9.5}{11}\selectfont\color{white} %s};"
             % (bx + bl / 2.0, haut - bh / 2.0, titre_semaine[0]))
    return L


def grille(semaine, titre_semaine, montrer_ab):
    """Le corps de la page : l'en-tête, la grille, les cases."""
    L = [r"\begin{tikzpicture}[x=1mm, y=1mm]"]
    L += entete(titre_semaine)

    x0 = MARGE
    y_haut = MARGE + HAUT_LEGENDE + HAUT_GRILLE

    # Les noms de jours, interlettrés : une ligne de titres, et non des mots
    # simplement posés là.
    for j, jour in enumerate(D.JOURS):
        jx = x0 + COL_HEURE + j * LARG_JOUR
        L.append(r"\node[anchor=center, inner sep=0] at (%.2f,%.2f) "
                 r"{\espace\fontsize{8}{9}\selectfont\color{encre} %s};"
                 % (jx + LARG_JOUR / 2.0, y_haut + 4.6, jour.upper()))
    L.append(filet(x0, y_haut + 1.4, x0 + LARGEUR))

    # Les filets verticaux entre les jours. Très pâles : ils structurent
    # l'œil sans concurrencer les cases, qui sont le contenu.
    for j in range(1, len(D.JOURS)):
        jx = x0 + COL_HEURE + j * LARG_JOUR
        L.append(r"\draw[color=filet!80, line width=0.15mm] (%.2f,%.2f) -- (%.2f,%.2f);"
                 % (jx, y_haut + 0.5, jx, MARGE + HAUT_LEGENDE))

    occupees = set()
    for i, (debut, fin) in enumerate(D.CRENEAUX):
        y = y_de_ligne(i)
        h = HAUT_REPAS if debut == "REPAS" else HAUT_LIGNE
        if debut == "REPAS":
            L.append(r"\fill[rounded corners=%.2fmm, fill=filet!30] (%.2f,%.2f) "
                     r"rectangle (%.2f,%.2f);"
                     % (RAYON, x0, y - h + GOUTTIERE, x0 + LARGEUR, y - GOUTTIERE))
            L.append(r"\node[anchor=center, inner sep=0] at (%.2f,%.2f) "
                     r"{\espacePetit\fontsize{6}{7}\selectfont\color{gris} "
                     r"PAUSE DÉJEUNER};"
                     % (x0 + LARGEUR / 2.0, y - h / 2.0))
            continue
        # L'heure de début en Medium, l'heure de fin bien plus pâle : c'est
        # l'heure de début qu'on cherche quand on regarde sa montre.
        L.append(r"\node[anchor=east, inner sep=0] at (%.2f,%.2f) "
                 r"{\avMed\fontsize{8.4}{9}\selectfont\color{encre} %s};"
                 % (x0 + COL_HEURE - 4.0, y - h / 2.0 + 1.5, debut))
        L.append(r"\node[anchor=east, inner sep=0] at (%.2f,%.2f) "
                 r"{\cdReg\fontsize{6}{7}\selectfont\color{gris!75} %s};"
                 % (x0 + COL_HEURE - 4.0, y - h / 2.0 - 2.4, fin))

        for j, jour in enumerate(D.JOURS):
            if (jour, i) in occupees:
                continue
            jx = x0 + COL_HEURE + j * LARG_JOUR
            liste = semaine.get((jour, debut), [])
            if not liste:
                # Presque rien : un creux dans la journée doit se lire comme
                # un creux, et non comme une case de plus à déchiffrer.
                VIDES.append({"x": jx, "y": y, "larg": LARG_JOUR, "haut": h})
                L.append(r"\fill[rounded corners=%.2fmm, fill=filet!22] "
                         r"(%.2f,%.2f) rectangle (%.2f,%.2f);"
                         % (RAYON, jx + GOUTTIERE, y - h + GOUTTIERE,
                            jx + LARG_JOUR - GOUTTIERE, y - GOUTTIERE))
                continue
            duree = max(c["duree"] for c in liste)
            hh = h
            if duree == 2:
                hh = h + HAUT_LIGNE
                occupees.add((jour, i + 1))
            if montrer_ab:
                L += case_ab(jx, y, hh, jour, debut)
            else:
                n = len(liste)
                for k, c in enumerate(liste):
                    L += case(jx + k * LARG_JOUR / n, y, LARG_JOUR / n, hh,
                              c, compact=(n > 1))
    L.append(filet(x0, MARGE + HAUT_LEGENDE - 0.6, x0 + LARGEUR))
    L.append(r"\end{tikzpicture}")
    return L


def case_ab(jx, y, hh, jour, debut):
    """Sur la feuille commune : entière si les deux semaines s'accordent."""
    a = D.pour_semaine("A").get((jour, debut), [])
    b = D.pour_semaine("B").get((jour, debut), [])

    def signature(liste):
        return [(c["matiere"], c["groupe"], c["salle"]) for c in liste]

    if a and signature(a) == signature(b):
        n = len(a)
        out = []
        for k, c in enumerate(a):
            out += case(jx + k * LARG_JOUR / n, y, LARG_JOUR / n, hh, c,
                        compact=(n > 1))
        return out

    out = []
    for lettre, liste, dy in (("A", a, 0.0), ("B", b, hh / 2.0)):
        if not liste:
            out.append(r"\node[anchor=center, inner sep=0] at (%.2f,%.2f) "
                       r"{\cdReg\fontsize{5.6}{6}\selectfont\color{gris!55} "
                       r"%s : libre};"
                       % (jx + LARG_JOUR / 2.0, y - dy - hh / 4.0, lettre))
            continue
        n = len(liste)
        for k, c in enumerate(liste):
            out += case(jx + k * LARG_JOUR / n, y - dy, LARG_JOUR / n, hh / 2.0,
                        c, compact=True, etiquette=lettre)
    return out


def legende(semaine):
    """Les matières de CETTE feuille, rangées par famille.

    Rangées, et non alignées dans l'ordre alphabétique : la légende dit du
    même coup à quoi sert chaque couleur et comment les matières se
    regroupent. C'est une information de plus pour le même encombrement.
    """
    presentes = [c["matiere"] for liste in semaine.values() for c in liste]
    colonnes = []
    for famille in D.FAMILLES:
        membres = [m for m, v in D.MATIERES.items()
                   if v[3] == famille and m in presentes]
        if membres:
            colonnes.append((famille, membres))

    L = [r"\begin{tikzpicture}[x=1mm, y=1mm]"]
    y = MARGE + HAUT_LEGENDE - 7.0
    lx = LARGEUR / len(colonnes)
    for k, (famille, membres) in enumerate(colonnes):
        cx = MARGE + k * lx
        L.append(r"\node[anchor=north west, inner sep=0] at (%.2f,%.2f) "
                 r"{\espacePetit\fontsize{5.6}{6.4}\selectfont\color{gris} %s};"
                 % (cx, y + 6.4, echappe(famille.upper())))
        for r, m in enumerate(membres):
            nom, fort, clair, _ = D.MATIERES[m]
            cy = y - r * 4.9
            L.append(r"\fill[rounded corners=0.5mm, fill=c%s] (%.2f,%.2f) "
                     r"rectangle (%.2f,%.2f);" % (m, cx, cy - 3.0, cx + 7.0, cy))
            L.append(r"\fill[rounded corners=0.35mm, fill=f%s] (%.2f,%.2f) "
                     r"rectangle (%.2f,%.2f);" % (m, cx, cy - 3.0, cx + 1.4, cy))
            L.append(r"\node[anchor=west, inner sep=0] at (%.2f,%.2f) "
                     r"{\avReg\fontsize{6.4}{7.4}\selectfont\color{encre} %s};"
                     % (cx + 8.6, cy - 1.5, echappe(nom)))
    L.append(r"\end{tikzpicture}")
    return L


PREAMBULE = r"""\documentclass{article}
\usepackage{fontspec}
\usepackage[a4paper,landscape,margin=0mm]{geometry}
\usepackage{tikz}
\usepackage{xcolor}

%% Une seule famille, toute son amplitude. Avenir Next est une police du
%% système macOS : ce document se compose avec lualatex, pas avec pdflatex.
%%
%% L'ESPACE-MOT. Tirée du .ttc par fontspec, Avenir Next arrive avec une
%% espace-mot très large : « Arts plastiques » se lisait « Arts  plastiques »
%% dans toutes les cases. Elle est donc resserrée à 0,76. Et sur les familles
%% interlettrées, c'est l'inverse : le crénage mange l'espace, et « SEMAINE A »
%% se composait « SEMAINEA ». Aucune erreur n'est levée ni dans un cas ni dans
%% l'autre — c'est de la typographie, pas de la syntaxe.
\defaultfontfeatures{WordSpace=0.76}
\setmainfont{Avenir Next}[UprightFont={* Regular}, BoldFont={* Demi Bold}]
\newfontfamily\avUltra{Avenir Next Ultra Light}
\newfontfamily\avReg{Avenir Next}[UprightFont={* Regular}, BoldFont={* Demi Bold}]
\newfontfamily\avMed{Avenir Next Medium}
\newfontfamily\avDemi{Avenir Next Demi Bold}
\newfontfamily\cdReg{Avenir Next Condensed}[UprightFont={* Regular}, BoldFont={* Demi Bold}]
%% Les titres et les mentions sont interlettrés : c'est ce qui distingue une
%% ligne de titres de mots simplement posés là.
\newfontfamily\espace{Avenir Next Demi Bold}[LetterSpace=11.0, WordSpace=2.6]
\newfontfamily\espacePetit{Avenir Next Condensed Demi Bold}[LetterSpace=13.0, WordSpace=3.0]

\pagestyle{empty}
\setlength{\parindent}{0pt}
\definecolor{encre}{HTML}{%(encre)s}
\definecolor{gris}{HTML}{%(gris)s}
\definecolor{filet}{HTML}{%(filet)s}
\definecolor{semA}{HTML}{1F5E54}
\definecolor{semB}{HTML}{6E3A63}
%(couleurs)s
\begin{document}
"""


def document(semaine, badge, montrer_ab, note):
    del POSEES[:], VIDES[:]
    couleurs = "\n".join(
        r"\definecolor{f%s}{HTML}{%s}\definecolor{c%s}{HTML}{%s}" % (k, v[1], k, v[2])
        for k, v in D.MATIERES.items())
    L = [PREAMBULE % {"couleurs": couleurs, "encre": D.ENCRE,
                      "gris": D.GRIS, "filet": D.FILET}]
    L.append(r"\begin{tikzpicture}[remember picture, overlay, x=1mm, y=1mm, "
             r"shift={(current page.south west)}]")
    L += grille(semaine, badge, montrer_ab)[1:-1]
    L += legende(semaine)[1:-1]
    L.append(r"\node[anchor=south east, inner sep=0] at (%.2f,%.2f) "
             r"{\cdReg\fontsize{5.4}{6}\selectfont\color{gris!70} %s};"
             % (PAGE_L - MARGE, MARGE - 6.0, note))
    L.append(r"\end{tikzpicture}")
    L.append(r"\end{document}")
    return "\n".join(L)


SORTIES = [
    ("PLANNING_SEMAINE_A", "A", ("SEMAINE A", "semA"), False),
    ("PLANNING_SEMAINE_B", "B", ("SEMAINE B", "semB"), False),
    ("PLANNING_A_ET_B", None, ("SEMAINES A + B", "encre"), True),
]


def main():
    # Le nom du fichier source porte des « _ » : non échappés, LaTeX les
    # prend pour des indices mathématiques et s'arrête.
    note = echappe("Source : " + D.SOURCE + " — " + D.ETABLISSEMENT)
    for nom, lettre, badge, ab in SORTIES:
        semaine = D.pour_semaine(lettre)
        tex = os.path.join(ICI, nom + ".tex")
        with open(tex, "w", encoding="utf-8") as f:
            f.write(document(semaine, badge, ab, note))
        # Deux passes : le dessin est posé par rapport à `current page` avec
        # `remember picture, overlay`, dont la position n'est connue qu'à la
        # passe suivante. La première passe compose une page BLANCHE sans
        # lever la moindre erreur.
        for passe in (1, 2):
            r = subprocess.run(["lualatex", "-interaction=nonstopmode",
                                "-halt-on-error", nom + ".tex"],
                               cwd=ICI, capture_output=True, text=True)
            if r.returncode != 0:
                print(r.stdout[-2000:])
                raise SystemExit("échec de compilation : " + nom)
        import fitz
        d = fitz.open(os.path.join(ICI, nom + ".pdf"))
        larg, haut = d[0].rect.width, d[0].rect.height
        print("  %-22s %d page, %.0f x %.0f pt (%s)"
              % (nom + ".pdf", d.page_count, larg, haut,
                 "A4 paysage" if larg > haut else "PORTRAIT — anomalie"))
    for reste in os.listdir(ICI):
        if reste.endswith((".aux", ".log", ".out")):
            os.remove(os.path.join(ICI, reste))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`planning_ipad.html` dit-il la même chose que `donnees_planning.py` ?

La page dessine sa grille dans le navigateur, à partir d'un bloc JSON que le
générateur y dépose. Ce harnais vérifie **ce bloc et la palette**, c'est-à-
dire tout ce dont la page se sert pour dessiner. Ce qu'il ne fait pas — et
il faut le dire — c'est ouvrir un navigateur pour regarder le rendu : cette
vérification-là a été faite à l'écran, une fois, et elle est refaite à
chaque changement d'allure. `verifier_planning.py` est plus exigeant parce
qu'il le peut : un PDF se relit sans navigateur.

Cinq familles de contrôles :

1. **L'idempotence.** On réengendre la page et on compare à celle du
   disque. Une retouche portée à la main dans le HTML se voit ici — et elle
   serait perdue à la prochaine exécution du générateur.
2. **Les données.** Le JSON de la page est exactement celui que
   `donnees_planning.py` produit : mêmes cours, mêmes salles, mêmes
   professeurs, mêmes groupes, mêmes semaines.
3. **La palette.** Chaque matière porte ses quatre tons, et le ton de jour
   est bien celui du papier : l'affiche et l'écran ne peuvent pas diverger.
4. **La lisibilité.** Le contraste de chaque nom de matière sur son fond est
   mesuré, de jour comme de nuit. C'est le contrôle que le papier n'exigeait
   pas : une teinte éclaircie pour le mode sombre peut très bien devenir
   illisible sans que rien ne le signale, et personne ne relit quatorze
   couleurs × deux thèmes à l'œil.
5. **Les horaires.** La pause déjeuner n'est pas saisie : elle se déduit de
   ce qui l'entoure, et le harnais vérifie qu'elle tombe juste.

Usage : python3 verifier_app.py
"""
import json
import os
import re
import sys

import donnees_planning as D
import generer_app as G

ICI = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ICI, "planning_ipad.html")

# Le seuil. 4,5:1 est l'exigence des WCAG pour du texte courant ; les noms de
# matière sont composés en demi-gras et plutôt gros, mais on ne s'accorde pas
# la tolérance « grand texte » : cette page est lue par une enfant, parfois
# sur un écran en plein soleil.
SEUIL = 4.5
controles = []


def verifier(libelle, calcule, attendu):
    controles.append((libelle, calcule, attendu, calcule == attendu))


def luminance(couleur):
    def canal(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    h = couleur.lstrip("#")
    r, v, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * canal(r) + 0.7152 * canal(v) + 0.0722 * canal(b)


def contraste(a, b):
    la, lb = luminance(a), luminance(b)
    clair, sombre = max(la, lb), min(la, lb)
    return (clair + 0.05) / (sombre + 0.05)


# ------------------------------------------------------------ 1. idempotence
sortie, sys.stdout = sys.stdout, open(os.devnull, "w")
try:
    reengendree = G.main()
finally:
    sys.stdout.close()
    sys.stdout = sortie

sur_disque = open(PAGE, encoding="utf-8").read() if os.path.exists(PAGE) else None
verifier("app : la page du disque est bien celle qu'engendre le générateur",
         sur_disque == reengendree, True)
verifier("app : aucun marqueur de gabarit ne subsiste",
         "@DONNEES@" in reengendree, False)
# `apercu.html` enveloppe la MÊME page, il ne la recopie pas. S'il s'en
# écartait, on regarderait sur cette machine autre chose que ce qui est
# publié — c'est-à-dire qu'on ne vérifierait rien.
apercu = (open(G.APERCU, encoding="utf-8").read()
          if os.path.exists(G.APERCU) else "")
verifier("app : docs/index.html enveloppe la page publiée, sans la recopier",
         apercu.count(reengendree), 1)
verifier("app : le fichier autonome porte le viewport et le jeu de caractères",
         "viewport-fit=cover" in apercu and "charset=\"utf-8\"" in apercu
         or "charset=utf-8" in apercu, True)
# Un site public ne doit tirer AUCUNE ressource d'ailleurs : ni police, ni
# script, ni feuille de style. C'est ce qui le rend consultable hors
# connexion, et ce qui garantit qu'aucun tiers ne voit passer les horaires
# d'une enfant.
verifier("app : le fichier autonome n'appelle aucune ressource externe",
         re.findall(r"https?://", apercu), [])

# L'ENCODAGE. Publiée en UTF-8, la page a été relue en Latin-1 par l'hôte :
# « CHLOÉ ÉTIENNE · 6ᵉ C » s'affichait « CHLOÃ© Ã‰TIENNE Â· 6ÁΜ‰ C ». Le
# fichier était pourtant de l'UTF-8 valide — c'est la déclaration de jeu de
# caractères, côté hôte, qui manquait, et sur quoi ce projet n'a pas prise.
# La page n'en dépend donc plus : entités numériques dans le balisage,
# \uXXXX dans le script, et pas un octet au-dessus de 127. Ces deux
# contrôles interdisent au problème de revenir.
for nom, texte in (("la page publiée", reengendree), ("le fichier autonome", apercu)):
    durs = sorted({c for c in texte if ord(c) > 127})
    verifier("app : %s ne porte aucun caractère non-ASCII" % nom, durs, [])
# Et les accents sont bien là, une fois les échappements résolus : une page
# dont on aurait simplement retiré les accents passerait le contrôle
# précédent sans rien valoir.
import html as _html
verifier("app : le titre porte bien son accent, une fois l'entité résolue",
         "Chloé" in _html.unescape(re.search(r"<title>(.*?)</title>",
                                             reengendree).group(1)), True)

# Le bloc JSON, relu depuis la page composée — et non depuis le générateur :
# c'est ce que le navigateur de l'iPad lira, et rien d'autre.
brut = re.search(r"const DONNEES = (\{.*?\n\});", reengendree, re.S)
verifier("app : le bloc de données est présent dans la page", bool(brut), True)
J = json.loads(brut.group(1)) if brut else {}

# --------------------------------------------------------------- 2. données
verifier("app : l'élève", J.get("eleve"), D.ELEVE)
verifier("app : l'établissement", J.get("etablissement"), D.ETABLISSEMENT)
verifier("app : l'année", J.get("annee"), D.ANNEE)
verifier("app : les cinq jours", J.get("jours"), D.JOURS)
verifier("app : les familles", J.get("familles"), D.FAMILLES)

total = 0
for (jour, heure), liste in D.SEMAINE.items():
    porte = (J.get("semaine", {}).get(jour, {}) or {}).get(heure)
    verifier("app : %s %s est dans les données" % (jour, heure),
             bool(porte) and len(porte) == len(liste), True)
    for attendu, ecrit in zip(liste, porte or []):
        total += 1
        verifier("app : %s %s %s" % (jour, heure, attendu["matiere"]),
                 {k: ecrit.get(k) for k in ("m", "prof", "salle", "sem", "gr", "duree")},
                 {"m": attendu["matiere"], "prof": attendu["prof"],
                  "salle": attendu["salle"], "sem": attendu["semaines"],
                  "gr": attendu["groupe"], "duree": attendu["duree"]})
verifier("app : tous les cours de la semaine sont portés", total,
         sum(len(v) for v in D.SEMAINE.values()))

# Rien de plus, non plus : une matière ou un jour en trop se verrait ici.
verifier("app : aucun jour en trop", sorted(J.get("semaine", {})),
         sorted({j for (j, h) in D.SEMAINE}))
verifier("app : aucune matière en trop", sorted(J.get("matieres", {})),
         sorted(D.MATIERES))

# --------------------------------------------------------------- 3. palette
for cle, (nom, fort, clair, famille) in D.MATIERES.items():
    m = J.get("matieres", {}).get(cle, {})
    verifier("app : %s porte son nom" % cle, m.get("nom"), nom)
    verifier("app : %s porte sa famille" % cle, m.get("famille"), famille)
    # Le ton de jour est celui du papier, au caractère près : c'est ce qui
    # garantit que l'affiche au mur et l'écran ne se contredisent pas.
    verifier("app : %s a la couleur forte du papier" % cle,
             (m.get("fort") or "").upper(), "#" + fort.upper())
    verifier("app : %s a la couleur claire du papier" % cle,
             (m.get("clair") or "").upper(), "#" + clair.upper())
    verifier("app : %s a ses deux tons de nuit" % cle,
             bool(re.fullmatch(r"#[0-9A-F]{6}", m.get("fortNuit", "")))
             and bool(re.fullmatch(r"#[0-9A-F]{6}", m.get("clairNuit", ""))), True)

# ------------------------------------------------------------ 4. lisibilité
for cle, m in sorted(J.get("matieres", {}).items()):
    for quand, texte, fond in (("de jour", m["fort"], m["clair"]),
                               ("de nuit", m["fortNuit"], m["clairNuit"])):
        r = contraste(texte, fond)
        verifier("app : %s se lit %s (contraste %.1f:1, seuil %.1f)"
                 % (m["nom"], quand, r, SEUIL), r >= SEUIL, True)

# --------------------------------------------------------------- 5. horaires
cr = J.get("creneaux", [])
verifier("app : autant de créneaux que dans les données", len(cr), len(D.CRENEAUX))
repas = [c for c in cr if c.get("repas")]
verifier("app : une seule pause déjeuner", len(repas), 1)
if repas and len(cr) > 2:
    i = cr.index(repas[0])
    # La pause se déduit de ses voisins : elle commence quand finit le
    # dernier cours du matin et finit quand commence le premier de l'après-
    # midi. Saisie à la main, elle aurait vieilli à la première retouche.
    verifier("app : la pause commence à la fin du dernier cours du matin",
             repas[0]["min"], cr[i - 1]["max"])
    verifier("app : la pause finit au début du premier cours de l'après-midi",
             repas[0]["max"], cr[i + 1]["min"])
for c in cr:
    verifier("app : le créneau %s finit après avoir commencé" % c.get("debut"),
             c["max"] > c["min"], True)

# =====================================================================
if __name__ == "__main__":
    echecs = [c for c in controles if not c[3]]
    for libelle, calcule, attendu, ok in controles:
        if not ok:
            print("  [ECHEC] %s" % libelle)
            print("           calculé = %r   attendu = %r" % (calcule, attendu))
    print()
    print("  app : %d contrôles, %d en échec" % (len(controles), len(echecs)))
    sys.exit(1 if echecs else 0)

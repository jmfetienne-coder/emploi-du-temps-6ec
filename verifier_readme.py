#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le README dit-il encore la vérité ?

Un README vieillit plus vite que ce qu'il décrit. Ses compteurs restent à
leur valeur de la veille, ses chemins survivent aux fichiers qu'ils nomment,
ses adresses cessent de répondre — et le lecteur suivant fait confiance sans
que rien ne le détrompe. C'est la même règle que pour les valeurs imprimées
sur les affiches, appliquée à la prose : **une affirmation qu'aucun
programme ne relit finit par être fausse.**

Ce harnais relit donc chaque affirmation vérifiable du README :

1. **Les compteurs par harnais.** « `verifier_app.py`, 198 contrôles » n'est
   pas une phrase, c'est une mesure : on relance le harnais et on lit son
   résultat. Le total est recalculé comme somme, et non recopié.
2. **Les chemins entre dos-d'âne.** Un chemin cité est une affirmation
   d'existence. Le citer sans son répertoire est exact pour qui connaît le
   projet et introuvable pour qui le découvre.
3. **Les adresses.** Le site et le dépôt doivent répondre. Une adresse qui
   cesse de répondre est exactement le genre d'affirmation qui pourrit sans
   que personne ne le voie. Deux sont déclarées non testables, et le sont
   nommément : `localhost`, qui n'est pas une adresse publique, et
   l'artefact Claude, qui exige une authentification.
4. **Le format des PDF.** « Une page, A4 paysage (842 × 595 pt) » s'obtient
   en ouvrant les trois fichiers.
5. **Les chiffres tirés des données.** Les heures de cours par semaine et
   le nombre de matières se recalculent depuis `donnees_planning.py`.
6. **Le contraste le plus faible.** Le README annonce un plancher mesuré ;
   on le remesure. Les valeurs citées dans la section « Les incidents » sont
   le récit d'un état passé, et ne sont pas relues comme des affirmations
   présentes — c'est ce qui distingue une histoire d'une promesse.

Usage : python3 verifier_readme.py
        python3 verifier_readme.py --sans-reseau   (sauter les adresses)
"""
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(ICI, "README.md")

# Ces adresses ne peuvent pas être interrogées, et la raison est écrite ici
# plutôt que devinée à l'exécution : une exception silencieuse passerait pour
# un succès.
INTESTABLES = {
    "localhost": "adresse locale, pas un service publié",
    "claude.ai/artifact": "artefact privé, une authentification est exigée",
}

controles = []


def verifier(libelle, calcule, attendu):
    controles.append((libelle, calcule, attendu, calcule == attendu))


def lire():
    return open(README, encoding="utf-8").read()


def sans_incidents(texte):
    """Le README privé de sa section « Les incidents ».

    Cette section raconte des états passés — « Histoire-Géo tombait à
    3,6:1 » — et ces nombres ne décrivent plus rien. Les relire comme des
    affirmations présentes obligerait à les réécrire à chaque correction,
    c'est-à-dire à falsifier le récit pour satisfaire le harnais.
    """
    i = texte.find("## Les incidents")
    return texte if i < 0 else texte[:i]


# ------------------------------------------------- 1. les compteurs par harnais
def compteur(harnais):
    """Le nombre de contrôles qu'annonce un harnais, en le relançant."""
    r = subprocess.run([sys.executable, harnais], cwd=ICI,
                       capture_output=True, text=True)
    m = re.search(r"(\d+) contrôles, (\d+) en échec", r.stdout)
    if not m:
        return None, None, (r.stdout + r.stderr)[-400:]
    return int(m.group(1)), int(m.group(2)), None


def plat(texte):
    """Le texte aux blancs normalisés, apostrophes droites.

    Une affirmation traverse les retours à la ligne : « 198 pour
    l'écran » est la même phrase que « 198 pour l'écran », et un motif qui
    l'ignore déclare manquante une affirmation qui est là. C'est la
    convention des autres harnais de ce projet, appliquée à la prose.
    """
    return re.sub(r"\s+", " ", texte).replace("\u2019", "'")


R = lire()
HORS_RECIT = sans_incidents(R)
PLAT = plat(HORS_RECIT)
total_mesure = 0
HARNAIS = ["verifier_planning.py", "verifier_app.py"]

for h in HARNAIS:
    n, echecs, souci = compteur(h)
    if n is None:
        verifier("readme : %s s'exécute" % h, souci, None)
        continue
    total_mesure += n
    verifier("readme : %s ne signale aucun échec" % h, echecs, 0)
    # Le compteur doit être cité AVEC son harnais, dans la même phrase : un
    # nombre seul, perdu dans la prose, ne dit pas ce qu'il compte.
    cite = re.search(r"`%s`[^.]{0,60}?(\d[\d  ]*) contrôles"
                     % re.escape(h), PLAT)
    verifier("readme : `%s` est cité avec son compteur" % h, bool(cite), True)
    if cite:
        verifier("readme : le compteur de %s est à jour" % h,
                 int(re.sub(r"\D", "", cite.group(1))), n)

# ------------------------------------------------------------ 2. les chemins
for chemin in sorted(set(re.findall(
        r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:py|pdf|tex|html|md|yml|json))`", R))):
    verifier("readme : le chemin `%s` existe" % chemin,
             os.path.exists(os.path.join(ICI, chemin)), True)

# ------------------------------------------------------------ 3. les adresses
def joignable(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "verifier-readme"})
        return urllib.request.urlopen(req, timeout=20).getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return repr(e)[:80]


sans_reseau = "--sans-reseau" in sys.argv
for url in sorted(set(re.findall(r"https?://[^\s>)*`]+", R))):
    motif = next((v for k, v in INTESTABLES.items() if k in url), None)
    if motif:
        # On ne saute pas en silence : l'exemption est nommée, et c'est
        # elle-même une affirmation qu'on vérifie.
        verifier("readme : %s est déclarée non testable (%s)" % (url, motif),
                 True, True)
        continue
    if sans_reseau:
        # On ne saute PAS le contrôle : on le pose en disant qu'il n'a pas
        # été vérifié. Sauter changerait le nombre de contrôles d'un mode à
        # l'autre — et ce harnais compte les siens, si bien qu'il se serait
        # mis en échec tout seul. Une affirmation non vérifiée doit se voir,
        # pas s'effacer.
        verifier("readme : %s n'a pas été interrogée (--sans-reseau)" % url,
                 True, True)
        continue
    verifier("readme : %s répond" % url, joignable(url), 200)

# ------------------------------------------------------- 4. le format des PDF
import donnees_planning as D                                      # noqa: E402
import generer_planning as G                                      # noqa: E402

dims = re.search(r"(\d+) × (\d+) pt", PLAT)
verifier("readme : les dimensions des PDF sont annoncées", bool(dims), True)
try:
    import fitz
except ImportError:
    fitz = None
    verifier("readme : PyMuPDF est disponible pour relire les PDF", False, True)
if fitz and dims:
    for nom, _, _, _ in G.SORTIES:
        chemin = os.path.join(ICI, nom + ".pdf")
        if not os.path.exists(chemin):
            verifier("readme : %s.pdf existe" % nom, False, True)
            continue
        d = fitz.open(chemin)
        verifier("readme : %s.pdf fait bien une page" % nom, d.page_count, 1)
        verifier("readme : %s.pdf fait bien %s × %s pt"
                 % (nom, dims.group(1), dims.group(2)),
                 (round(d[0].rect.width), round(d[0].rect.height)),
                 (int(dims.group(1)), int(dims.group(2))))

# -------------------------------------------- 5. les chiffres tirés des données
heures = {l: sum(max(c["duree"] for c in v)
                 for v in D.pour_semaine(l).values()) for l in "AB"}
m = re.search(r"\*\*(\d+) heures de cours en semaine A\*\*, \*\*(\d+) en semaine B\*\*, "
              r"(\d+) matières", PLAT)
verifier("readme : les chiffres de la semaine sont annoncés", bool(m), True)
if m:
    verifier("readme : les heures de la semaine A", int(m.group(1)), heures["A"])
    verifier("readme : les heures de la semaine B", int(m.group(2)), heures["B"])
    verifier("readme : le nombre de matières", int(m.group(3)), len(D.MATIERES))

# ------------------------------------------------------------ 6. le contraste
import verifier_app as VA                                         # noqa: E402

plancher = min(VA.contraste("#" + fort, "#" + clair)
               for _, fort, clair, _ in D.MATIERES.values())
seuil = re.search(r"au moins (\d),(\d):1", PLAT)
verifier("readme : le seuil de contraste est annoncé", bool(seuil), True)
if seuil:
    exige = float("%s.%s" % seuil.groups())
    verifier("readme : le seuil annoncé est celui du harnais", exige, VA.SEUIL)
    verifier("readme : aucune matière ne descend sous le seuil annoncé",
             plancher >= exige, True)
# Le plancher effectif, qui vit dans le récit mais qui est une mesure d'AUJOURD'HUI.
dit = re.search(r"Le plus faible contraste vaut désormais (\d),(\d):1", plat(R))
verifier("readme : le plus faible contraste est annoncé", bool(dit), True)
if dit:
    verifier("readme : le plus faible contraste annoncé est celui qu'on mesure",
             float("%s.%s" % dit.groups()), round(plancher, 1))

# -------------------------------------------- 7. ce harnais se compte lui-même
# Un harnais qui vérifie les compteurs des autres et pas le sien serait la
# seule affirmation du README que personne ne relit. Il se compte donc — ce
# qui ne peut se faire qu'ici, une fois tous ses autres contrôles posés.
#
# FINALS est le nombre de contrôles que ce bloc ajoute, lui-même compris.
# L'assertion de la dernière ligne le tient à jour : se tromper d'un cran
# arrête le programme au lieu d'annoncer un chiffre faux.
FINALS = 5
n_moi = len(controles) + FINALS
total_mesure += n_moi

moi = re.search(r"`verifier_readme.py`[^.]{0,60}?(\d[\d\u202f ]*) contrôles",
                PLAT)
verifier("readme : `verifier_readme.py` est cité avec son compteur", bool(moi), True)
verifier("readme : le compteur de verifier_readme.py est à jour",
         int(re.sub(r"\D", "", moi.group(1))) if moi else None, n_moi)

# Le total est une SOMME, et non un quatrième nombre écrit à côté des trois
# autres. C'est par là qu'un README se met à se contredire lui-même.
tot = re.search(r"(\d[\d\u202f ]*) contrôles\*\*, (\d[\d\u202f ]*) pour le papier, "
                r"(\d[\d\u202f ]*) pour l'écran et (\d[\d\u202f ]*) pour", PLAT)
verifier("readme : le total des contrôles est annoncé", bool(tot), True)
if tot:
    a, b, c, d_ = (int(re.sub(r"\D", "", g)) for g in tot.groups())
    verifier("readme : le total annoncé est la somme des trois harnais", a, b + c + d_)
    verifier("readme : le total annoncé est celui qu'on mesure", a, total_mesure)
else:
    verifier("readme : le total annoncé est la somme des trois harnais", None, True)
    verifier("readme : le total annoncé est celui qu'on mesure", None, True)

assert len(controles) == n_moi, (
    "FINALS vaut %d, mais ce bloc a posé %d contrôles"
    % (FINALS, len(controles) - (n_moi - FINALS)))

# =====================================================================
if __name__ == "__main__":
    echecs = [c for c in controles if not c[3]]
    for libelle, calcule, attendu, ok in controles:
        if not ok:
            print("  [ECHEC] %s" % libelle)
            print("           calculé = %r   attendu = %r" % (calcule, attendu))
    print()
    print("  readme : %d contrôles, %d en échec" % (len(controles), len(echecs)))
    sys.exit(1 if echecs else 0)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Engendre `planning_ipad.html`, l'emploi du temps de Chloé sur son iPad.

MÊME SOURCE QUE LES TROIS PDF. Les matières, les couleurs, les familles, les
créneaux et les cours viennent de `donnees_planning.py` et de nulle part
ailleurs : ils sont sérialisés en JSON dans la page. Une correction portée
dans les données se retrouve du même coup sur le papier et sur l'écran, et
les deux ne peuvent pas se contredire.

CE QUE LA PAGE AJOUTE, QUE LE PAPIER NE PEUT PAS FAIRE

1. **Elle sait quel jour on est**, et ouvre sur la journée en cours. C'est
   la vraie raison d'avoir une application : sur le papier, il faut chercher
   sa colonne ; ici, la bonne journée est déjà là.
2. **Elle sait l'heure**, met en avant le cours en cours et annonce le
   suivant. Un enfant de onze ans ne calcule pas « il est 10h12, donc… ».
3. **Elle déduit la semaine A ou B.** On lui dit une fois laquelle est en
   cours, elle en retient la parité et se débrouille ensuite toute seule.
4. **Elle connaît le groupe de Chloé.** Les cours en demi-groupe restent
   tous les deux affichés — rien n'est caché —, mais le sien est mis en
   avant et l'autre s'efface.

LA TYPOGRAPHIE EST CELLE DU PAPIER. Avenir Next est une police du système
iOS comme elle l'est de macOS : l'affiche punaisée au mur et l'écran de
l'iPad se composent dans le même caractère, sans qu'il faille télécharger
quoi que ce soit.

Usage : python3 generer_app.py
"""
import colorsys
import json
import os

import donnees_planning as D

ICI = os.path.dirname(os.path.abspath(__file__))
CIBLE = os.path.join(ICI, "planning_ipad.html")
# Le même fichier sert à deux choses : le regarder sur cette machine, et le
# publier comme site. C'est donc UN seul fichier, et non deux qui
# divergeraient. Il s'appelle `docs/index.html` parce que GitHub Pages
# n'accepte que deux emplacements — la racine du dépôt, ou `docs/` — et que
# la racine est déjà prise par les générateurs.
APERCU = os.path.join(ICI, "docs", "index.html")

# `planning_ipad.html` est écrit pour être PUBLIÉ : il commence à <title>, et
# l'hébergeur l'enveloppe lui-même dans un squelette (jeu de caractères,
# viewport, marges de sécurité de l'écran). Pour le regarder sur cette
# machine, il lui faut cette enveloppe. Elle est donc engendrée ici, à partir
# de la même page — et non recopiée à côté, où elle vieillirait aussitôt.
ENVELOPPE = """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
  :root { color-scheme: light dark;
          padding-top: env(safe-area-inset-top, 0px);
          padding-bottom: env(safe-area-inset-bottom, 0px); }
  body { margin: 0; }
  img { max-width: 100%; }
  [hidden] { display: none !important; }
</style>
</head><body>
<!--@PAGE@-->
</body></html>
"""


# --------------------------------------------------------------- les couleurs
def rvb(h):
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def hexa(r, v, b):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c * 255)))
                                   for c in (r, v, b))


def eclaircir(couleur, clarte):
    """La même teinte, portée à la clarté demandée.

    Les couleurs fortes du papier sont sombres : posées sur le fond noir du
    mode nuit, elles deviennent illisibles. On garde la teinte — c'est elle
    qui identifie la matière — et on remonte la clarté.
    """
    r, v, b = rvb(couleur)
    h, l, s = colorsys.rgb_to_hls(r, v, b)
    return hexa(*colorsys.hls_to_rgb(h, clarte, min(1.0, s * 0.92)))


def melanger(couleur, fond, part):
    a, b_ = rvb(couleur), rvb(fond)
    return hexa(*(a[i] * part + b_[i] * (1 - part) for i in range(3)))


NUIT_SURFACE = "212327"


def palette():
    """Les quatre tons de chaque matière : jour et nuit, fond et texte."""
    out = {}
    for cle, (nom, fort, clair, famille) in D.MATIERES.items():
        out[cle] = {
            "nom": nom, "famille": famille,
            "fort": "#" + fort,          # le bandeau et le nom, en plein jour
            "clair": "#" + clair,        # le fond de case, en plein jour
            "fortNuit": eclaircir(fort, 0.72),
            "clairNuit": melanger(fort, NUIT_SURFACE, 0.20),
        }
    return out


# ------------------------------------------------------------- les horaires
def minutes(h):
    """« 13h30 » vaut 810."""
    a, b = h.split("h")
    return int(a) * 60 + int(b or 0)


def creneaux():
    out = []
    for debut, fin in D.CRENEAUX:
        if debut == "REPAS":
            # La pause n'a pas d'horaire propre dans les données : elle
            # occupe ce qui sépare le dernier cours du matin du premier de
            # l'après-midi. On le déduit plutôt que de le ressaisir.
            out.append({"repas": True})
        else:
            out.append({"repas": False, "debut": debut, "fin": fin,
                        "min": minutes(debut), "max": minutes(fin)})
    for i, c in enumerate(out):
        if c["repas"]:
            c["min"] = out[i - 1]["max"]
            c["max"] = out[i + 1]["min"]
            c["debut"], c["fin"] = out[i - 1]["fin"], out[i + 1]["debut"]
    return out


def semaine_json():
    """Les cours, par jour et par créneau, prêts à être lus par la page."""
    out = {}
    for (jour, heure), liste in D.SEMAINE.items():
        out.setdefault(jour, {})[heure] = [
            {"m": c["matiere"], "prof": c["prof"], "salle": c["salle"],
             "sem": c["semaines"], "gr": c["groupe"], "duree": c["duree"]}
            for c in liste]
    return out


def donnees():
    return {
        "eleve": D.ELEVE,
        "classe": "6ᵉ C",
        "etablissement": D.ETABLISSEMENT,
        "annee": D.ANNEE,
        "source": D.SOURCE,
        "jours": D.JOURS,
        "familles": D.FAMILLES,
        "matieres": palette(),
        "creneaux": creneaux(),
        "semaine": semaine_json(),
    }


# ------------------------------------------------------- l'encodage
# LA PAGE EST ECRITE EN ASCII PUR, et ce n'est pas un raffinement.
#
# Publiee telle quelle en UTF-8, elle a ete relue en Latin-1 par l'hote :
# « CHLOE ETIENNE . 6e C » s'affichait « CHLOÃ© Ã‰TIENNE Â· 6ÁΜ‰ C ». Le
# fichier etait pourtant de l'UTF-8 valide — c'est la declaration de jeu de
# caracteres, cote hote, qui manquait ou qui a ete ignoree, et sur quoi ce
# projet n'a aucune prise.
#
# On cesse donc d'en dependre : plus un seul octet au-dessus de 127 ne sort
# d'ici. Trois zones, trois echappements, parce qu'une entite HTML placee
# dans un textContent s'afficherait telle quelle, et un \uXXXX pose dans du
# balisage aussi :
#
#   - dans <script>  : \uXXXX, valable en chaine comme en gabarit ;
#   - dans <style>   : le non-ASCII n'y est QUE dans des commentaires, et on
#                      le translittere ; s'il en apparaissait ailleurs, on
#                      s'arrete plutot que d'alterer une declaration ;
#   - ailleurs       : entites numeriques &#xXXXX;.
#
# `verifier_app.py` mesure le resultat : zero caractere non-ASCII. C'est ce
# controle qui interdit au probleme de revenir.
TRANSLIT = {"\u00ab": '"', "\u00bb": '"', "\u2014": "--", "\u2013": "-",
            "\u00b7": ".", "\u2019": "'", "\u00a0": " ", "\u2026": "..."}


def _translitterer(t):
    """Le meme texte, sans accent ni signe typographique. Commentaires seuls."""
    import unicodedata
    out = []
    for c in t:
        if ord(c) < 128:
            out.append(c)
        elif c in TRANSLIT:
            out.append(TRANSLIT[c])
        else:
            d = unicodedata.normalize("NFKD", c)
            out.append("".join(x for x in d if not unicodedata.combining(x))
                       or "?")
    return "".join(out)


def _zone_style(t):
    """Le bloc CSS, translittere dans ses commentaires et nulle part ailleurs."""
    morceaux, i = [], 0
    while True:
        d = t.find("/*", i)
        if d < 0:
            morceaux.append((t[i:], False))
            break
        f = t.find("*/", d)
        f = len(t) if f < 0 else f + 2
        morceaux.append((t[i:d], False))
        morceaux.append((t[d:f], True))
        i = f
    out = []
    for bout, commentaire in morceaux:
        if commentaire:
            out.append(_translitterer(bout))
        else:
            dur = [c for c in bout if ord(c) > 127]
            if dur:
                raise SystemExit(
                    "du non-ASCII hors commentaire dans le CSS : %r. "
                    "Le translitterer changerait ce qui s'affiche ; "
                    "l'ecrire en \\XXXX CSS, ou en entite dans le balisage."
                    % dur[:5])
            out.append(bout)
    return "".join(out)


def ascii_seul(page):
    """La page, sans un seul octet au-dessus de 127."""
    def borne(ouvrant, fermant, depuis=0):
        d = page.index(ouvrant, depuis)
        return d, page.index(fermant, d) + len(fermant)

    ds, fs = borne("<style>", "</style>")
    dj, fj = borne("<script>", "</script>", fs)
    entites = lambda t: "".join(
        c if ord(c) < 128 else "&#x%04X;" % ord(c) for c in t)
    echappe_js = lambda t: "".join(
        c if ord(c) < 128 else "\\u%04X" % ord(c) for c in t)
    sortie = (entites(page[:ds]) + _zone_style(page[ds:fs])
              + entites(page[fs:dj]) + echappe_js(page[dj:fj])
              + entites(page[fj:]))
    reste = [c for c in sortie if ord(c) > 127]
    assert not reste, reste[:5]
    return sortie


# --------------------------------------------------------------- la page
PAGE = """<title>L'emploi du temps de Chloé</title>
<style>
/* ---------------------------------------------------------------- jetons
   Palette chaude : les gris tirent vers l'ocre des humanités. Un gris
   parfaitement neutre, à côté de ces teintes-là, a l'air subi et non choisi.
   Tout est défini ici, sur :root nu — une couleur qui n'existerait que dans
   le bloc « nuit » ne s'appliquerait jamais chez qui n'a rien réglé. */
:root {
  --papier:   #F7F5F1;
  --surface:  #FFFFFF;
  --encre:    #23262B;
  --gris:     #857E73;
  --gris-pale:#A9A296;
  --filet:    #E4E0D7;
  --ombre:    0 1px 2px rgba(35,38,43,.05), 0 6px 18px rgba(35,38,43,.05);
  --ombre-nette: 0 2px 6px rgba(35,38,43,.09), 0 10px 28px rgba(35,38,43,.09);
  --semA:     #1F5E54;
  --semB:     #6E3A63;
  --r:        14px;
  --nuit:     0;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --papier:   #141517;
    --surface:  #212327;
    --encre:    #EFEDE8;
    --gris:     #9A9389;
    --gris-pale:#6E6962;
    --filet:    #33363B;
    --ombre:    0 1px 2px rgba(0,0,0,.4), 0 6px 18px rgba(0,0,0,.3);
    --ombre-nette: 0 2px 6px rgba(0,0,0,.5), 0 10px 28px rgba(0,0,0,.45);
    --semA:     #4FA392;
    --semB:     #B77BA8;
    --nuit:     1;
  }
}
:root[data-theme="dark"] {
  --papier:   #141517;
  --surface:  #212327;
  --encre:    #EFEDE8;
  --gris:     #9A9389;
  --gris-pale:#6E6962;
  --filet:    #33363B;
  --ombre:    0 1px 2px rgba(0,0,0,.4), 0 6px 18px rgba(0,0,0,.3);
  --ombre-nette: 0 2px 6px rgba(0,0,0,.5), 0 10px 28px rgba(0,0,0,.45);
  --semA:     #4FA392;
  --semB:     #B77BA8;
  --nuit:     1;
}

/* Avenir Next est une police du systeme iOS et macOS : l'ecran de l'iPad et
   l'affiche punaisee au mur se composent dans le meme caractere. */
body {
  margin: 0;
  background: var(--papier);
  color: var(--encre);
  font-family: "Avenir Next", "Avenir", -apple-system, BlinkMacSystemFont,
               "Segoe UI", system-ui, sans-serif;
  font-size: 16px;
  line-height: 1.45;
  -webkit-text-size-adjust: 100%;
  -webkit-tap-highlight-color: transparent;
}
* { box-sizing: border-box; }
button { font: inherit; color: inherit; cursor: pointer; }
:focus-visible { outline: 2px solid var(--encre); outline-offset: 2px; border-radius: 6px; }

.enveloppe { max-width: 1120px; margin: 0 auto; padding: 0 18px 44px; }

/* ------------------------------------------------------------- l'en-tete */
.chapeau {
  position: sticky; top: env(safe-area-inset-top, 0px); z-index: 20;
  background: color-mix(in srgb, var(--papier) 88%, transparent);
  -webkit-backdrop-filter: saturate(180%) blur(14px);
  backdrop-filter: saturate(180%) blur(14px);
  border-bottom: 1px solid var(--filet);
  padding-block: 14px 12px;
}
.chapeau-i {
  max-width: 1120px; margin: 0 auto; padding: 0 18px;
  display: flex; align-items: flex-start; gap: 14px; flex-wrap: wrap;
}
h1 {
  margin: 0; font-weight: 200; font-size: clamp(25px, 5.4vw, 34px);
  letter-spacing: -.012em; line-height: 1.08; text-wrap: balance;
}
.qui {
  margin: 5px 0 0; font-size: 11px; font-weight: 600;
  letter-spacing: .13em; color: var(--gris); text-transform: uppercase;
}
.pilule {
  margin-left: auto; border: 0; border-radius: 999px;
  padding: 10px 17px; background: var(--semA); color: #fff;
  font-weight: 600; font-size: 13px; letter-spacing: .13em;
  display: inline-flex; align-items: center; gap: 9px;
  box-shadow: var(--ombre);
}
.pilule[data-sem="B"] { background: var(--semB); }
.pilule .permuter { opacity: .72; font-size: 15px; line-height: 1; }

/* --------------------------------------------------------------- onglets */
.onglets {
  display: flex; gap: 4px; margin: 18px 0 4px; padding: 4px;
  background: var(--surface); border: 1px solid var(--filet);
  border-radius: 999px; width: fit-content; box-shadow: var(--ombre);
}
.onglets button {
  border: 0; background: transparent; border-radius: 999px;
  padding: 9px 20px; font-size: 14px; font-weight: 500; color: var(--gris);
  transition: background .18s, color .18s;
}
.onglets button[aria-selected="true"] { background: var(--encre); color: var(--papier); }

/* ------------------------------------------------- la barre des journees */
.jours { display: flex; gap: 8px; margin: 16px 0 20px; overflow-x: auto;
         padding-bottom: 4px; scrollbar-width: none; }
.jours::-webkit-scrollbar { display: none; }
.jour-chip {
  flex: 0 0 auto; border: 1px solid var(--filet); background: var(--surface);
  border-radius: var(--r); padding: 9px 15px; text-align: center;
  min-width: 78px; transition: border-color .18s, background .18s;
}
.jour-chip b { display: block; font-size: 12px; font-weight: 600;
               letter-spacing: .1em; text-transform: uppercase; }
.jour-chip span { display: block; font-size: 11px; color: var(--gris); margin-top: 2px; }
.jour-chip[aria-pressed="true"] { background: var(--encre); border-color: var(--encre); }
.jour-chip[aria-pressed="true"] b,
.jour-chip[aria-pressed="true"] span { color: var(--papier); }
.jour-chip.aujourdhui:not([aria-pressed="true"]) { border-color: var(--encre); }

/* ------------------------------------------------------ la journee, en liste */
.titre-jour { display: flex; align-items: baseline; gap: 12px;
              margin: 0 0 14px; flex-wrap: wrap; }
.titre-jour h2 { margin: 0; font-size: 21px; font-weight: 500; letter-spacing: -.01em; }
.titre-jour .compte { font-size: 13px; color: var(--gris); }

.annonce {
  display: flex; align-items: center; gap: 13px; margin-bottom: 16px;
  padding: 14px 16px; border-radius: var(--r); background: var(--surface);
  border: 1px solid var(--filet); box-shadow: var(--ombre);
}
.annonce .pastille { width: 9px; height: 9px; border-radius: 50%; flex: 0 0 auto; }
.annonce .txt { font-size: 14px; }
.annonce .txt b { font-weight: 600; }
.annonce .quand { display: block; font-size: 12px; color: var(--gris); margin-top: 1px; }

.liste { display: flex; flex-direction: column; gap: 9px; }
.creneau { display: grid; grid-template-columns: 62px 1fr; gap: 13px; align-items: stretch; }
.heure { text-align: right; padding-top: 12px; font-variant-numeric: tabular-nums; }
.heure b { display: block; font-size: 15px; font-weight: 500; }
.heure span { display: block; font-size: 11px; color: var(--gris-pale); margin-top: 1px; }

.cours {
  position: relative; border-radius: var(--r); padding: 13px 15px 13px 19px;
  background: var(--fond); overflow: hidden; box-shadow: var(--ombre);
}
.cours::before { content: ""; position: absolute; inset: 0 auto 0 0;
                 width: 5px; background: var(--teinte); }
.cours h3 { margin: 0; font-size: 16px; font-weight: 600; color: var(--teinte);
            letter-spacing: -.005em; }
.cours .detail { margin: 3px 0 0; font-size: 13px; color: var(--gris); }
.cours .detail .sep { opacity: .45; padding: 0 4px; }
.cours.autre-groupe { opacity: .46; }
.cours.passe { opacity: .5; }
.cours.maintenant { box-shadow: var(--ombre-nette); outline: 2px solid var(--teinte); }
.cours .maintenant-tag {
  display: inline-block; margin-top: 8px; padding: 3px 9px; border-radius: 999px;
  background: var(--teinte); color: #fff; font-size: 10px; font-weight: 600;
  letter-spacing: .12em; text-transform: uppercase;
}
.cours .lettre {
  position: absolute; top: 11px; right: 12px; width: 19px; height: 19px;
  border-radius: 6px; background: var(--teinte); color: #fff;
  font-size: 11px; font-weight: 600; display: grid; place-items: center;
}
.repas {
  grid-column: 2; border-radius: var(--r); background: var(--filet);
  color: var(--gris); font-size: 11px; font-weight: 600; letter-spacing: .14em;
  text-transform: uppercase; padding: 9px 15px;
}
.vide { grid-column: 2; border-radius: var(--r); border: 1px dashed var(--filet);
        color: var(--gris-pale); font-size: 13px; padding: 12px 15px; }

/* ----------------------------------------------------- la semaine, en grille */
.cadre { overflow-x: auto; -webkit-overflow-scrolling: touch;
         border-radius: var(--r); }
.grille { display: grid; gap: 5px; min-width: 760px;
          grid-template-columns: 52px repeat(5, 1fr); }
.gr-jour { font-size: 11px; font-weight: 600; letter-spacing: .12em;
           text-transform: uppercase; text-align: center; padding: 4px 0 8px;
           border-bottom: 1px solid var(--filet); margin-bottom: 3px; }
.gr-jour.aujourdhui { color: var(--encre); }
.gr-jour:not(.aujourdhui) { color: var(--gris); }
.gr-heure { font-size: 11px; color: var(--gris); text-align: right;
            padding: 8px 8px 0 0; font-variant-numeric: tabular-nums; }
.gr-heure b { display: block; font-size: 13px; font-weight: 500; color: var(--encre); }
.gr-case { position: relative; border-radius: 9px; background: var(--fond);
           padding: 7px 8px 7px 12px; overflow: hidden; min-height: 50px; }
.gr-case::before { content: ""; position: absolute; inset: 0 auto 0 0;
                   width: 4px; background: var(--teinte); }
.gr-case b { display: block; font-size: 12px; font-weight: 600; color: var(--teinte);
             line-height: 1.2; }
.gr-case span { display: block; font-size: 10px; color: var(--gris); margin-top: 2px; }
/* Le separateur est un span, et « .gr-case span { display:block } » le
   passait a la ligne : « E26 » puis un point tout seul, puis « Groupe 1 ».
   Il faut une selectivite superieure pour le ramener en ligne. */
.gr-case .sep { display: inline; margin: 0; opacity: .45; padding: 0 3px; }
.gr-case .lettre { position: absolute; top: 5px; right: 5px; width: 15px; height: 15px;
                   border-radius: 4px; background: var(--teinte); color: #fff;
                   font-size: 9px; font-weight: 600; display: grid; place-items: center; }
.gr-case.autre-groupe { opacity: .5; }
.gr-vide { border-radius: 9px; background: var(--filet); opacity: .35; }
.gr-repas { grid-column: 1 / -1; border-radius: 9px; background: var(--filet);
            color: var(--gris); font-size: 10px; font-weight: 600;
            letter-spacing: .14em; text-transform: uppercase; text-align: center;
            padding: 5px; }
.paire { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; }
.empile { display: grid; gap: 3px; }

/* ------------------------------------------------------------- la legende */
.pied { margin-top: 34px; border-top: 1px solid var(--filet); padding-top: 22px; }
.pied h4 { margin: 0 0 16px; font-size: 11px; font-weight: 600; letter-spacing: .14em;
           text-transform: uppercase; color: var(--gris); }
.familles { display: grid; gap: 20px;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }
.famille h5 { margin: 0 0 9px; font-size: 10px; font-weight: 600; letter-spacing: .14em;
              text-transform: uppercase; color: var(--gris-pale); }
.famille ul { margin: 0; padding: 0; list-style: none; display: grid; gap: 7px; }
.famille li { display: flex; align-items: center; gap: 9px; font-size: 13px; }
.puce { width: 26px; height: 15px; border-radius: 5px; background: var(--fond);
        position: relative; flex: 0 0 auto; }
.puce::before { content: ""; position: absolute; inset: 0 auto 0 0; width: 5px;
                border-radius: 5px 0 0 5px; background: var(--teinte); }

/* ------------------------------------------------------------- les reglages */
.reglages { margin-top: 26px; display: grid; gap: 14px; }
.reglage { display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
           font-size: 13px; color: var(--gris); }
.reglage .choix { display: flex; gap: 4px; padding: 3px; border-radius: 999px;
                  background: var(--surface); border: 1px solid var(--filet); }
.reglage .choix button { border: 0; background: transparent; border-radius: 999px;
                         padding: 6px 14px; font-size: 13px; color: var(--gris); }
.reglage .choix button[aria-pressed="true"] { background: var(--encre); color: var(--papier); }
.source { margin-top: 24px; font-size: 11px; color: var(--gris-pale); line-height: 1.6; }

@media (max-width: 560px) {
  .creneau { grid-template-columns: 52px 1fr; gap: 10px; }
  .enveloppe, .chapeau-i { padding-inline: 16px; }
}
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
</style>

<header class="chapeau">
  <div class="chapeau-i">
    <div>
      <h1>Emploi du temps</h1>
      <p class="qui" id="qui"></p>
    </div>
    <button class="pilule" id="pilule" type="button" aria-live="polite">
      <span id="pilule-txt">SEMAINE A</span><span class="permuter" aria-hidden="true">&#8646;</span>
    </button>
  </div>
</header>

<div class="enveloppe">
  <div class="onglets" role="tablist">
    <button role="tab" id="t-jour" data-vue="jour" aria-selected="true">Ma journée</button>
    <button role="tab" id="t-semaine" data-vue="semaine" aria-selected="false">Ma semaine</button>
  </div>

  <section id="vue-jour" role="tabpanel" aria-labelledby="t-jour">
    <div class="jours" id="jours"></div>
    <div class="titre-jour"><h2 id="titre-jour"></h2><span class="compte" id="compte"></span></div>
    <div id="annonce"></div>
    <div class="liste" id="liste"></div>
  </section>

  <section id="vue-semaine" role="tabpanel" aria-labelledby="t-semaine" hidden>
    <div class="cadre"><div class="grille" id="grille"></div></div>
  </section>

  <div class="pied">
    <h4>Les couleurs des matières</h4>
    <div class="familles" id="familles"></div>
    <div class="reglages">
      <div class="reglage">
        <span>Le groupe de Chloé&nbsp;:</span>
        <div class="choix" id="choix-groupe">
          <button type="button" data-gr="Groupe 1">Groupe&nbsp;1</button>
          <button type="button" data-gr="Groupe 2">Groupe&nbsp;2</button>
          <button type="button" data-gr="">Les deux</button>
        </div>
      </div>
      <div class="reglage" id="reglage-ancre"></div>
    </div>
    <p class="source" id="source"></p>
  </div>
</div>

<script>
const DONNEES = /*@DONNEES@*/null;

/* ====================================================================
   L'ETAT. Trois reglages, gardes dans le navigateur de l'iPad : la
   semaine en cours, le groupe de Chloe, le jour regarde. Rien ne part
   ailleurs, et la page s'ouvre exactement comme on l'a laissee.

   localStorage peut lever (navigation privee, donnees de site bloquees).
   Tout passe donc par un try/catch, et la page se dessine correctement
   meme quand rien ne peut etre ni lu ni ecrit.
   ==================================================================== */
const CLE = "planning-chloe-6ec";
function lire() {
  try { return JSON.parse(localStorage.getItem(CLE) || "{}") || {}; }
  catch (e) { return {}; }
}
function ecrire(o) {
  try { localStorage.setItem(CLE, JSON.stringify(o)); } catch (e) { /* tant pis */ }
}
let etat = lire();

/* La semaine ISO : c'est elle qui fait tourner A et B.
   On retient une seule fois « telle semaine etait une A », et la parite
   des semaines ISO donne toutes les autres — passees comme a venir. */
function semaineISO(d) {
  const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  t.setUTCDate(t.getUTCDate() + 4 - (t.getUTCDay() || 7));
  const jan1 = new Date(Date.UTC(t.getUTCFullYear(), 0, 1));
  return Math.round(((t - jan1) / 86400000 + 1) / 7);
}
function numeroAbsolu(d) {
  /* Un numero qui ne repart pas a 1 au nouvel an : sinon la parite se
     casserait au 31 decembre, et l'application se tromperait de semaine
     pile au retour des vacances de Noel. */
  return Math.floor((Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())
                     - Date.UTC(2020, 0, 6)) / 604800000);
}
function semaineDe(d) {
  if (!etat.ancre) return etat.semaine || "A";
  const ecart = numeroAbsolu(d) - etat.ancre.n;
  const pair = ((ecart % 2) + 2) % 2 === 0;
  return pair ? etat.ancre.lettre : (etat.ancre.lettre === "A" ? "B" : "A");
}

const MAINTENANT = () => new Date();

/* LA DATE DE REFERENCE, qui n'est pas toujours aujourd'hui.
   Le samedi et le dimanche, l'eleve ne cherche pas la semaine qui s'acheve
   mais celle qui commence : la reference bascule alors sur le lundi qui
   vient. Sans cela, l'application ouvrirait le dimanche soir sur le lundi
   d'il y a six jours — et sur la mauvaise lettre une semaine sur deux. */
function reference() {
  const d = MAINTENANT();
  const j = d.getDay();
  if (j === 0) d.setDate(d.getDate() + 1);        /* dimanche -> lundi */
  else if (j === 6) d.setDate(d.getDate() + 2);   /* samedi  -> lundi */
  return d;
}
const NOMS_JOURS = ["dimanche", "lundi", "mardi", "mercredi", "jeudi",
                    "vendredi", "samedi"];
const MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
              "août", "septembre", "octobre", "novembre", "décembre"];

function dateDuJour(nomJour, ref) {
  /* La date de ce jour-la dans la semaine de `ref` (lundi premier). */
  const i = DONNEES.jours.indexOf(nomJour);
  const d = new Date(ref);
  const decalage = (d.getDay() === 0 ? -6 : 1 - d.getDay());
  d.setDate(d.getDate() + decalage + i);
  return d;
}

/* Le jour ouvre sur aujourd'hui — c'est toute la raison d'etre de
   l'application. Le week-end, sur le lundi qui vient. */
function jourDepart() {
  const j = NOMS_JOURS[MAINTENANT().getDay()];
  return DONNEES.jours.includes(j) ? j : "lundi";
}
let jourVu = jourDepart();
let semaineVue = semaineDe(reference());
let vue = "jour";

/* ==================================================================== */
function teintes(cle) {
  const m = DONNEES.matieres[cle];
  const nuit = getComputedStyle(document.documentElement)
                 .getPropertyValue("--nuit").trim() === "1";
  return { teinte: nuit ? m.fortNuit : m.fort,
           fond: nuit ? m.clairNuit : m.clair, nom: m.nom };
}
function coursDe(jour, heure, lettre) {
  const l = (DONNEES.semaine[jour] || {})[heure] || [];
  return l.filter(c => c.sem.includes(lettre));
}
function estSien(c) {
  return !c.gr || !etat.groupe || c.gr === etat.groupe;
}
function detail(c, court) {
  const bouts = [];
  if (c.salle && c.salle !== "\\u2014") bouts.push(c.salle);
  if (c.gr) bouts.push(c.gr);
  if (!court) bouts.push(c.prof);
  return bouts.join('<span class="sep">·</span>');
}

/* ------------------------------------------------------------ la journee */
function dessinerJours() {
  const ref = reference();
  const auj = NOMS_JOURS[MAINTENANT().getDay()];
  document.getElementById("jours").innerHTML = DONNEES.jours.map(j => {
    const d = dateDuJour(j, ref);
    return `<button type="button" class="jour-chip${j === auj ? " aujourdhui" : ""}"
      data-jour="${j}" aria-pressed="${j === jourVu}">
      <b>${j.slice(0, 3)}</b><span>${d.getDate()} ${MOIS[d.getMonth()].slice(0, 4)}</span>
    </button>`;
  }).join("");
}

function dessinerJournee() {
  const ref = reference();
  const d = dateDuJour(jourVu, ref);
  // Le vrai jour, et non la reference : `reference()` vaut lundi des le
  // samedi, et « en ce moment » se serait declenche pendant le week-end.
  const estAuj = NOMS_JOURS[MAINTENANT().getDay()] === jourVu;
  document.getElementById("titre-jour").textContent =
    jourVu[0].toUpperCase() + jourVu.slice(1) + " " + d.getDate() + " " + MOIS[d.getMonth()];

  const mnt = estAuj ? ref.getHours() * 60 + ref.getMinutes() : -1;
  let heures = 0, courant = null, suivant = null;
  const morceaux = [];

  DONNEES.creneaux.forEach(cr => {
    if (cr.repas) {
      morceaux.push(`<div class="creneau"><div class="heure"></div>
        <div class="repas">Pause déjeuner</div></div>`);
      return;
    }
    const liste = coursDe(jourVu, cr.debut, semaineVue);
    const enCours = mnt >= cr.min && mnt < cr.max;
    let cases;
    if (!liste.length) {
      cases = `<div class="vide">Pas de cours</div>`;
    } else {
      heures += Math.max(...liste.map(c => c.duree));
      cases = liste.map(c => {
        const t = teintes(c.m);
        const sien = estSien(c);
        if (sien && enCours && !courant) courant = { c, cr, t };
        if (sien && mnt >= 0 && cr.min > mnt && !suivant) suivant = { c, cr, t };
        const cl = ["cours"];
        if (!sien) cl.push("autre-groupe");
        if (mnt >= 0 && cr.max <= mnt) cl.push("passe");
        if (sien && enCours) cl.push("maintenant");
        const duree = c.duree > 1
          ? `<span class="sep">·</span>${c.duree}\\u00a0h` : "";
        return `<div class="${cl.join(" ")}" style="--teinte:${t.teinte};--fond:${t.fond}">
          <h3>${t.nom}</h3>
          <p class="detail">${detail(c, false)}${duree}</p>
          ${sien && enCours ? '<span class="maintenant-tag">en ce moment</span>' : ""}
        </div>`;
      }).join("");
      if (liste.length > 1) cases = `<div class="empile">${cases}</div>`;
    }
    morceaux.push(`<div class="creneau">
      <div class="heure"><b>${cr.debut}</b><span>${cr.fin}</span></div>
      <div>${cases}</div></div>`);
  });

  document.getElementById("liste").innerHTML = morceaux.join("");
  document.getElementById("compte").textContent =
    heures ? heures + (heures > 1 ? " heures de cours" : " heure de cours")
           : "pas de cours";

  /* L'annonce : ce qui se passe maintenant, ou ce qui vient. C'est la
     seule chose qu'un enfant regarde entre deux sonneries. */
  const zone = document.getElementById("annonce");
  const quoi = courant || suivant;
  if (!estAuj || !quoi) { zone.innerHTML = ""; return; }
  const reste = courant ? quoi.cr.max - mnt : quoi.cr.min - mnt;
  const quand = courant
    ? `en cours, jusqu'à ${quoi.cr.fin}`
    : (reste <= 60 ? `dans ${reste} minute${reste > 1 ? "s" : ""}, à ${quoi.cr.debut}`
                   : `à ${quoi.cr.debut}`);
  zone.innerHTML = `<div class="annonce">
    <span class="pastille" style="background:${quoi.t.teinte}"></span>
    <span class="txt"><b>${courant ? "" : "Ensuite : "}${quoi.t.nom}</b>
    ${detail(quoi.c, true) ? `<span class="sep">·</span>${detail(quoi.c, true)}` : ""}
    <span class="quand">${quand}</span></span></div>`;
}

/* ------------------------------------------------------------- la semaine */
function dessinerSemaine() {
  const auj = NOMS_JOURS[MAINTENANT().getDay()];   // le vrai jour, pas la reference
  const out = [`<div></div>`];
  DONNEES.jours.forEach(j => out.push(
    `<div class="gr-jour${j === auj ? " aujourdhui" : ""}">${j}</div>`));

  const occupe = {};
  DONNEES.creneaux.forEach((cr, i) => {
    if (cr.repas) { out.push(`<div class="gr-repas">Pause déjeuner</div>`); return; }
    out.push(`<div class="gr-heure"><b>${cr.debut}</b>${cr.fin}</div>`);
    DONNEES.jours.forEach(j => {
      if (occupe[j + i]) { out.push(""); return; }
      const liste = coursDe(j, cr.debut, semaineVue);
      if (!liste.length) { out.push(`<div class="gr-vide"></div>`); return; }
      const duree = Math.max(...liste.map(c => c.duree));
      if (duree > 1) occupe[j + (i + 1)] = true;
      const cases = liste.map(c => {
        const t = teintes(c.m);
        const cl = "gr-case" + (estSien(c) ? "" : " autre-groupe");
        const lettre = c.sem.length === 1
          ? `<span class="lettre">${c.sem}</span>` : "";
        return `<div class="${cl}" style="--teinte:${t.teinte};--fond:${t.fond}">
          ${lettre}<b>${t.nom}</b><span>${detail(c, true)}</span></div>`;
      }).join("");
      out.push(liste.length > 1
        ? `<div class="paire">${cases}</div>`
        : `<div style="display:grid;grid-row:span ${duree}">${cases}</div>`);
    });
  });
  document.getElementById("grille").innerHTML = out.join("");
}

/* ------------------------------------------------------------- la legende */
function dessinerLegende() {
  document.getElementById("familles").innerHTML = DONNEES.familles.map(f => {
    const membres = Object.keys(DONNEES.matieres)
      .filter(k => DONNEES.matieres[k].famille === f);
    return `<div class="famille"><h5>${f}</h5><ul>` + membres.map(k => {
      const t = teintes(k);
      return `<li><span class="puce" style="--teinte:${t.teinte};--fond:${t.fond}"></span>
        ${t.nom}</li>`;
    }).join("") + `</ul></div>`;
  }).join("");
}

function dessinerReglages() {
  document.querySelectorAll("#choix-groupe button").forEach(b =>
    b.setAttribute("aria-pressed", (etat.groupe || "") === b.dataset.gr));
  const d = reference();
  document.getElementById("reglage-ancre").innerHTML = etat.ancre
    ? `<span>Cette semaine est une <b>semaine ${semaineDe(d)}</b>, et
       l'application suit toute seule.</span>
       <div class="choix"><button type="button" data-ancre="">Corriger</button></div>`
    : `<span>Quelle semaine est-ce, en ce moment&nbsp;?</span>
       <div class="choix">
         <button type="button" data-ancre="A">Semaine A</button>
         <button type="button" data-ancre="B">Semaine B</button>
       </div>`;
}

/* ==================================================================== */
function tout() {
  document.getElementById("pilule-txt").textContent = "SEMAINE " + semaineVue;
  document.getElementById("pilule").dataset.sem = semaineVue;
  dessinerJours();
  if (vue === "jour") dessinerJournee(); else dessinerSemaine();
  dessinerLegende();
  dessinerReglages();
}

document.addEventListener("click", e => {
  const chip = e.target.closest(".jour-chip");
  if (chip) { jourVu = chip.dataset.jour; tout(); return; }

  const onglet = e.target.closest(".onglets button");
  if (onglet) {
    vue = onglet.dataset.vue;
    document.querySelectorAll(".onglets button").forEach(b =>
      b.setAttribute("aria-selected", b.dataset.vue === vue));
    document.getElementById("vue-jour").hidden = vue !== "jour";
    document.getElementById("vue-semaine").hidden = vue === "jour";
    tout();
    return;
  }

  if (e.target.closest("#pilule")) {
    semaineVue = semaineVue === "A" ? "B" : "A";
    etat.semaine = semaineVue; ecrire(etat); tout(); return;
  }

  const gr = e.target.closest("#choix-groupe button");
  if (gr) { etat.groupe = gr.dataset.gr; ecrire(etat); tout(); return; }

  const ancre = e.target.closest("[data-ancre]");
  if (ancre) {
    const v = ancre.dataset.ancre;
    etat.ancre = v ? { n: numeroAbsolu(MAINTENANT()), lettre: v } : null;
    if (v) semaineVue = v;
    ecrire(etat); tout();
  }
});

/* La page reste ouverte des jours sur un iPad posé sur un bureau : sans
   cela, « en ce moment » désignerait le cours d'avant-hier. */
setInterval(() => { if (vue === "jour") dessinerJournee(); }, 60000);
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) { jourVu = jourDepart(); semaineVue = semaineDe(reference()); tout(); }
});
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", tout);

document.getElementById("qui").textContent =
  DONNEES.eleve + " · " + DONNEES.classe + " · " + DONNEES.annee;
document.getElementById("source").textContent =
  DONNEES.etablissement + " · Source : " + DONNEES.source;
tout();
</script>
"""


def main():
    page = PAGE.replace("/*@DONNEES@*/null",
                        json.dumps(donnees(), ensure_ascii=True,
                                   sort_keys=True, indent=1))
    page = ascii_seul(page)
    with open(CIBLE, "w", encoding="utf-8") as f:
        f.write(page)
    os.makedirs(os.path.dirname(APERCU), exist_ok=True)
    with open(APERCU, "w", encoding="utf-8") as f:
        f.write(ENVELOPPE.replace("<!--@PAGE@-->", page))
    print("  planning_ipad.html + docs/index.html : %d matières, %d jours, "
          "%d créneaux, %d Ko" % (len(D.MATIERES), len(D.JOURS),
                                  len(D.CRENEAUX),
                                  round(len(page.encode("utf-8")) / 1024)))
    return page


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Palmares PEA + portefeuille : recupere 6 mois de cours et ecrit data.json a la
racine du depot. Lance par GitHub Actions (voir .github/workflows/update.yml).
Dependance : yfinance.

Deux familles de series dans data.json :

  - mk = true  : valeur de l'univers classe (liste UNIVERS ci-dessous). La page
                 calcule elle-meme les 5 plus fortes hausses et les 5 plus fortes
                 baisses sur la fenetre choisie au curseur (1 a 6 mois).
  - pf = "PEG" / "PEA" / "AV" : ligne du portefeuille. Ces lignes ne sont PAS
                 ecrites ici : elles sont lues a chaque passage dans le catalogue
                 supports.txt du depot mes-actions. Ajouter une valeur au
                 portefeuille se fait donc la-bas, et nulle part ailleurs.
                 Seul le catalogue est lu (intitule, identifiant, enveloppe) :
                 jamais les quantites ni les apports.

Une meme valeur peut etre les deux a la fois (ex. Airbus, Air Liquide).

Sources de cours :
  - src = "yahoo" : Yahoo Finance, cours ajustes des dividendes (auto_adjust).
  - src = "vl"    : fonds non cotes (epargne salariale, assurance vie). Leur
                    historique de valeurs liquidatives est lu dans history.json
                    du depot mes-actions. Il ne commence que le 18/06/2026 : sur
                    une fenetre plus profonde, la page fait partir ces courbes de
                    100 a leur premiere date connue et le signale dans la legende.

Chaque serie est normalisee base 100 sur son premier point ; la page la rebase
ensuite sur le debut de la fenetre affichee.
"""

import calendar
import json
import os
import urllib.request
from datetime import date, datetime, timedelta, timezone

import yfinance as yf

# ----------------------------------------------------------------------------
# UNIVERS CLASSE
# Trois blocs, tous eligibles au PEA :
#   1. Grandes et moyennes valeurs de la Bourse de Paris : le SBF 120 hors
#      foncieres cotees (les SIIC ne sont pas eligibles au PEA).
#   2. Quelques valeurs francaises hors SBF 120 connues pour la regularite de
#      leur dividende.
#   3. Une selection de valeurs europeennes a dividende regulier ou croissant
#      (siege dans l'Union europeenne). Celles cotees a Amsterdam et Bruxelles
#      suivent le tarif Euronext habituel ; pour les autres places, la brochure
#      BoursoBank impose un ordre minimal de 2 500 EUR dans un PEA, et la page le
#      rappelle dans la legende. Les deux valeurs danoises cotent en couronnes,
#      monnaie arrimee a l'euro.
# LISTE FIGEE, ecrite a la main le 03/10/2026 : la composition de l'indice est
# revue chaque trimestre (mars, juin, septembre, decembre), il faut donc la
# relire de temps en temps. Elle n'a pas besoin d'etre exacte a la valeur pres :
# elle sert de vivier pour le classement.
# Un ticker que Yahoo ne reconnait plus est signale dans data.json (cle
# "echecs") et dans la barre d'etat de la page, sans bloquer le reste.
# (ticker Yahoo, nom affiche)
# ----------------------------------------------------------------------------
UNIVERS = [
    ("AC.PA",    "Accor"),
    ("ADP.PA",   "Aéroports de Paris"),
    ("AF.PA",    "Air France-KLM"),
    ("AI.PA",    "Air Liquide"),
    ("AIR.PA",   "Airbus"),
    ("ALO.PA",   "Alstom"),
    ("ATE.PA",   "Alten"),
    ("AMUN.PA",  "Amundi"),
    ("ANTIN.PA", "Antin Infrastructure"),
    ("APAM.AS",  "Aperam"),                 # Amsterdam, droit luxembourgeois
    ("MT.AS",    "ArcelorMittal"),          # Amsterdam, droit luxembourgeois
    ("AKE.PA",   "Arkema"),
    ("ATO.PA",   "Atos"),
    ("CS.PA",    "AXA"),
    ("AYV.PA",   "Ayvens"),
    ("BB.PA",    "Bic"),
    ("BIM.PA",   "bioMérieux"),
    ("BNP.PA",   "BNP Paribas"),
    ("BOL.PA",   "Bolloré"),
    ("EN.PA",    "Bouygues"),
    ("BVI.PA",   "Bureau Veritas"),
    ("CAP.PA",   "Capgemini"),
    ("CA.PA",    "Carrefour"),
    ("CLARI.PA", "Clariane"),
    ("COFA.PA",  "Coface"),
    ("ACA.PA",   "Crédit Agricole"),
    ("BN.PA",    "Danone"),
    ("AM.PA",    "Dassault Aviation"),
    ("DSY.PA",   "Dassault Systèmes"),
    ("DBG.PA",   "Derichebourg"),
    ("EDEN.PA",  "Edenred"),
    ("FGR.PA",   "Eiffage"),
    ("ELIOR.PA", "Elior"),
    ("ELIS.PA",  "Elis"),
    ("EMEIS.PA", "Emeis"),
    ("ENGI.PA",  "Engie"),
    ("ERA.PA",   "Eramet"),
    ("EL.PA",    "EssilorLuxottica"),
    ("RF.PA",    "Eurazeo"),
    ("ERF.PA",   "Eurofins Scientific"),
    ("ENX.PA",   "Euronext"),
    ("ETL.PA",   "Eutelsat"),
    ("EXA.PA",   "Exail Technologies"),
    ("EXENS.PA", "Exosens"),
    ("FDJU.PA",  "FDJ United"),
    ("FRVIA.PA", "Forvia"),
    ("GTT.PA",   "GTT"),
    ("GNFT.PA",  "Genfit"),
    ("GET.PA",   "Getlink"),
    ("RMS.PA",   "Hermès"),
    ("IDL.PA",   "ID Logistics"),
    ("NK.PA",    "Imerys"),
    ("ITP.PA",   "Interparfums"),
    ("IPN.PA",   "Ipsen"),
    ("IPS.PA",   "Ipsos"),
    ("DEC.PA",   "JCDecaux"),
    ("KER.PA",   "Kering"),
    ("OR.PA",    "L'Oréal"),
    ("LSS.PA",   "Lectra"),
    ("LR.PA",    "Legrand"),
    ("FII.PA",   "Lisi"),
    ("MC.PA",    "LVMH"),
    ("MMT.PA",   "M6 Métropole TV"),
    ("MAU.PA",   "Maurel & Prom"),
    ("MEDCL.PA", "Medincell"),
    ("MRN.PA",   "Mersen"),
    ("ML.PA",    "Michelin"),
    ("NANO.PA",  "Nanobiotix"),
    ("NEX.PA",   "Nexans"),
    ("NXI.PA",   "Nexity"),
    ("OPM.PA",   "OPmobility"),
    ("ORA.PA",   "Orange"),
    ("OVH.PA",   "OVHcloud"),
    ("RI.PA",    "Pernod Ricard"),
    ("PLNW.PA",  "Planisware"),
    ("PLX.PA",   "Pluxee"),
    ("PUB.PA",   "Publicis"),
    ("RCO.PA",   "Rémy Cointreau"),
    ("RNO.PA",   "Renault"),
    ("RXL.PA",   "Rexel"),
    ("RUI.PA",   "Rubis"),
    ("SAF.PA",   "Safran"),
    ("SGO.PA",   "Saint-Gobain"),
    ("SAN.PA",   "Sanofi"),
    ("DIM.PA",   "Sartorius Stedim"),
    ("SU.PA",    "Schneider Electric"),
    ("SCR.PA",   "Scor"),
    ("SK.PA",    "SEB"),
    ("SESG.PA",  "SES"),
    ("GLE.PA",   "Société Générale"),
    ("SW.PA",    "Sodexo"),
    ("SOI.PA",   "Soitec"),
    ("SOLB.BR",  "Solvay"),                 # Bruxelles
    ("SOP.PA",   "Sopra Steria"),
    ("SPIE.PA",  "Spie"),
    ("STLAP.PA", "Stellantis"),
    ("STMPA.PA", "STMicroelectronics"),
    ("TE.PA",    "Technip Energies"),
    ("TEP.PA",   "Teleperformance"),
    ("TFI.PA",   "TF1"),
    ("HO.PA",    "Thales"),
    ("TKO.PA",   "Tikehau Capital"),
    ("TTE.PA",   "TotalEnergies"),
    ("TRI.PA",   "Trigano"),
    ("UBI.PA",   "Ubisoft"),
    ("FR.PA",    "Valeo"),
    ("VK.PA",    "Vallourec"),
    ("VLA.PA",   "Valneva"),
    ("VIE.PA",   "Veolia"),
    ("VRLA.PA",  "Verallia"),
    ("VCT.PA",   "Vicat"),
    ("DG.PA",    "Vinci"),
    ("VIRP.PA",  "Virbac"),
    ("VIRI.PA",  "Viridien"),
    ("VIV.PA",   "Vivendi"),
    ("VU.PA",    "VusionGroup"),
    ("MF.PA",    "Wendel"),
    ("WLN.PA",   "Worldline"),
    ("XFAB.PA",  "X-Fab"),
    ("ABVX.PA",  "Abivax"),
    # --- bloc 2 : valeurs francaises hors SBF 120, dividende regulier (ajout 03/10/2026) ---
    ("EQS.PA",   "Equasens"),
    ("RBT.PA",   "Robertet"),
    ("LOUP.PA",  "LDC"),
    ("THEP.PA",  "Thermador"),
    ("VETO.PA",  "Vetoquinol"),
    ("NRO.PA",   "Neurones"),
    ("STF.PA",   "Stef"),
    # --- bloc 3 : valeurs europeennes, Euronext Amsterdam et Bruxelles (ajout 03/10/2026) ---
    ("WKL.AS",   "Wolters Kluwer"),
    ("ASML.AS",  "ASML"),
    ("AD.AS",    "Ahold Delhaize"),
    ("HEIA.AS",  "Heineken"),
    ("ASRNL.AS", "ASR Nederland"),
    ("UCB.BR",   "UCB"),
    ("KBC.BR",   "KBC"),
    ("ACKB.BR",  "Ackermans & van Haaren"),
    ("SOF.BR",   "Sofina"),
    ("AGS.BR",   "Ageas"),
    ("DIE.BR",   "D'Ieteren"),
    # --- bloc 3 : valeurs europeennes hors Euronext, ordre minimal de 2 500 EUR en PEA ---
    ("MUV2.DE",  "Munich Re"),              # Francfort
    ("ALV.DE",   "Allianz"),
    ("SAP.DE",   "SAP"),
    ("HNR1.DE",  "Hannover Re"),
    ("DB1.DE",   "Deutsche Börse"),
    ("SIE.DE",   "Siemens"),
    ("FPE3.DE",  "Fuchs"),
    ("SY1.DE",   "Symrise"),
    ("NOVO-B.CO", "Novo Nordisk"),          # Copenhague, en couronnes danoises
    ("COLO-B.CO", "Coloplast"),             # Copenhague, en couronnes danoises
    ("ITX.MC",   "Inditex"),                # Madrid
    ("IBE.MC",   "Iberdrola"),
    ("G.MI",     "Generali"),               # Milan
    ("TRN.MI",   "Terna"),
    ("KNEBV.HE", "Kone"),                   # Helsinki
    ("SAMPO.HE", "Sampo"),
    ("KRZ.IR",   "Kerry Group"),            # Dublin
]
UNIVERS_LIBELLE = "SBF 120 hors foncières et sélection européenne à dividende régulier, liste figée au 03/10/2026"

# ----------------------------------------------------------------------------
# PORTEFEUILLE : lu dans le depot mes-actions (public).
# Si ce depot passe un jour en prive, ces deux adresses ne repondront plus : la
# page continuera d'afficher le palmares, sans les lignes du portefeuille, et
# l'erreur sera visible dans la barre d'etat.
# ----------------------------------------------------------------------------
BRUT = "https://raw.githubusercontent.com/guermeurdaniel-cpu/mes-actions/main/"
URL_SUPPORTS = BRUT + "supports.txt"
URL_HISTORIQUE = BRUT + "history.json"

PERIOD = "6mo"
JOURS_VL = 190          # profondeur gardee pour les valeurs liquidatives
OUT = os.path.join(os.path.dirname(__file__), "..", "data.json")


def ms_du_jour(d):
    """Minuit UTC du jour de cotation, en millisecondes."""
    return calendar.timegm(d.timetuple()) * 1000


def lire_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "telemesure-zone-euro"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def lire_catalogue(texte):
    """Blocs [Intitule] suivis de lignes cle = valeur. Renvoie une liste de dict."""
    blocs, courant = [], None
    for brute in texte.splitlines():
        ligne = brute.strip()
        if not ligne or ligne.startswith("#"):
            continue
        if ligne.startswith("[") and ligne.endswith("]"):
            courant = {"intitule": ligne[1:-1].strip()}
            blocs.append(courant)
            continue
        if courant is not None and "=" in ligne:
            nom, valeur = ligne.split("=", 1)
            courant[nom.strip().lower()] = valeur.strip()
    return [b for b in blocs if b.get("cle")]


def part_actions(ligne, defaut):
    try:
        return float(ligne.get("actions", defaut))
    except (TypeError, ValueError):
        return defaut


def portefeuille():
    """Lignes du portefeuille : (lignes, historique des VL, message d'erreur)."""
    try:
        lignes = lire_catalogue(lire_url(URL_SUPPORTS))
    except Exception as e:
        return [], {}, "catalogue du portefeuille illisible (%s)" % e
    try:
        vl = json.loads(lire_url(URL_HISTORIQUE))
    except Exception as e:
        return lignes, {}, "historique des fonds illisible (%s)" % e
    return lignes, vl, None


def telecharge(tickers):
    """Cours de cloture ajustes par ticker : un appel groupe, puis rattrapage unitaire."""
    cours = {}
    try:
        df = yf.download(tickers, period=PERIOD, interval="1d", auto_adjust=True,
                         group_by="ticker", threads=True, progress=False)
        for tk in tickers:
            try:
                s = df[tk]["Close"].dropna()
                if len(s) >= 2:
                    cours[tk] = s
            except Exception:
                pass
    except Exception as e:
        print("  appel groupe en echec (%s), passage en unitaire" % e)
    for tk in tickers:
        if tk in cours:
            continue
        try:
            s = yf.Ticker(tk).history(period=PERIOD, auto_adjust=True)["Close"].dropna()
            if len(s) >= 2:
                cours[tk] = s
        except Exception as e:
            print("  rattrapage en echec %-10s (%s)" % (tk, e))
    return cours


def serie_base100(points):
    """points : liste de (date, valeur) triee. Renvoie x (ms) et y (base 100)."""
    base = float(points[0][1])
    x = [ms_du_jour(d) for d, _ in points]
    y = [round(float(v) / base * 100.0, 3) for _, v in points]
    return x, y


def build():
    lignes, vl, erreur_pf = portefeuille()
    if erreur_pf:
        print("  PORTEFEUILLE : " + erreur_pf)

    noms = dict(UNIVERS)
    cotes = [tk for tk, _ in UNIVERS]
    for l in lignes:
        if l.get("source") == "yahoo" and l["cle"] not in noms:
            cotes.append(l["cle"])

    cours = telecharge(cotes)
    en_pf = {l["cle"]: l for l in lignes}
    rang = {l["cle"]: i for i, l in enumerate(lignes)}     # ordre du catalogue
    series, echecs = [], []

    def ajoute_cotee(tk, nom, mk):
        s = cours.get(tk)
        if s is None:
            echecs.append(tk)
            print("  FAIL %-10s %s" % (tk, nom))
            return
        points = [(ts.date(), v) for ts, v in zip(s.index, s.values)]
        x, y = serie_base100(points)
        l = en_pf.get(tk)
        series.append(dict(
            tk=tk, name=nom, mk=mk,
            pf=(l.get("enveloppe") if l else None), src="yahoo",
            on=(part_actions(l, 1.0) > 0 if l else True),
            ord=rang.get(tk), x=x, y=y))
        print("  ok   %-10s %-22s %+6.1f%%" % (tk, nom, y[-1] - 100.0))

    for tk, nom in UNIVERS:
        ajoute_cotee(tk, nom, True)

    limite = date.today() - timedelta(days=JOURS_VL)
    for l in lignes:
        cle, nom = l["cle"], l["intitule"]
        if l.get("source") == "yahoo":
            if cle not in noms:
                ajoute_cotee(cle, nom, False)
            continue
        points = []
        for p in vl.get(cle, []):
            try:
                d = datetime.strptime(p["date"], "%Y-%m-%d").date()
                if d >= limite:
                    points.append((d, float(p["value"])))
            except Exception:
                pass
        points.sort()
        if len(points) < 2:
            echecs.append(cle)
            print("  FAIL %-12s %s (pas d'historique de VL)" % (cle, nom))
            continue
        x, y = serie_base100(points)
        series.append(dict(
            tk=cle, name=nom, mk=False, pf=l.get("enveloppe"), src="vl",
            on=(part_actions(l, 0.0) > 0), ord=rang.get(cle), x=x, y=y))
        print("  ok   %-12s %-22s %+6.1f%%  (VL, %d points)" % (cle, nom, y[-1] - 100.0, len(points)))

    return series, echecs, erreur_pf


def main():
    print("Recuperation des cours (Yahoo Finance) et du portefeuille (mes-actions)...")
    series, echecs, erreur_pf = build()
    payload = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "period": PERIOD,
        "univers": UNIVERS_LIBELLE,
        "echecs": echecs,
        "erreur_pf": erreur_pf,
        "series": series,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print("Ecrit %s (%d series, %d echec(s))" % (os.path.normpath(OUT), len(series), len(echecs)))


if __name__ == "__main__":
    main()

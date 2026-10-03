#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Historique long pour les etudes hors ligne (essais de strategies).

Ce script ne sert PAS a la page : il est lance a la main (onglet Actions >
Analyse historique > Run workflow) ou a chaque modification de ce fichier, et
ecrit deux fichiers dans le dossier analyse/ :

  - historique.json   : cours quotidiens depuis 2010, ajustes des dividendes et
                        des divisions, plus l'historique des dividendes verses, pour
                        toutes les valeurs de l'univers (liste UNIVERS de
                        fetch_data.py) et quelques temoins.
                        Par ticker : d = jours (nombre de jours depuis 1970),
                        c = cours ajustes, div = [[jour, montant], ...].
  - fondamentaux.json : quelques donnees de bilan et de resultat lues chez Yahoo
                        (capitalisation, dette, tresorerie, marges, secteur).
                        ATTENTION : ce sont les valeurs du jour, pas celles du
                        passe. Les utiliser pour juger une decision passee
                        revient a connaitre l'avenir.
"""

import calendar
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import yfinance as yf

sys.path.insert(0, os.path.dirname(__file__))
from fetch_data import UNIVERS  # noqa: E402

TEMOINS = [
    ("CW8.PA",  "ETF MSCI World (CW8)"),
    ("WPEA.PA", "ETF MSCI World (WPEA)"),
    ("^FCHI",   "CAC 40"),
]
DEBUT = "2010-01-01"       # profondeur de l'historique
DOSSIER = os.path.join(os.path.dirname(__file__), "..", "analyse")
CLES = [
    "shortName", "sector", "industry", "currency", "marketCap",
    "totalDebt", "totalCash", "ebitda", "freeCashflow", "operatingCashflow",
    "totalRevenue", "profitMargins", "operatingMargins", "returnOnEquity",
    "trailingEps", "forwardEps", "trailingPE", "forwardPE", "priceToBook",
    "payoutRatio", "dividendYield", "dividendRate", "fiveYearAvgDividendYield",
    "debtToEquity", "currentRatio", "beta",
    "regularMarketPrice", "fiftyTwoWeekLow", "fiftyTwoWeekHigh",
]


def jour(ts):
    """Nombre de jours depuis le 01/01/1970 pour une date de cotation."""
    return calendar.timegm(ts.date().timetuple()) // 86400


def cours(tickers):
    out = {}
    df = yf.download(tickers, start=DEBUT, interval="1d", auto_adjust=True,
                     actions=True, group_by="ticker", threads=True, progress=False)
    for tk in tickers:
        try:
            sub = df[tk]
            c = sub["Close"].dropna()
            if len(c) < 50:
                raise ValueError("serie trop courte")
            div = sub["Dividends"].dropna()
            div = div[div > 0]
            out[tk] = {
                "d": [jour(t) for t in c.index],
                "c": [round(float(v), 4) for v in c.values],
                "div": [[jour(t), round(float(v), 4)] for t, v in div.items()],
            }
            print("  ok   %-10s %5d seances, %2d dividendes" % (tk, len(c), len(div)))
        except Exception as e:
            print("  FAIL %-10s (%s)" % (tk, e))
    return out


def fiche(tk):
    try:
        info = yf.Ticker(tk).info or {}
        return tk, {k: info.get(k) for k in CLES}
    except Exception as e:
        return tk, {"erreur": str(e)[:120]}


def main():
    noms = dict(UNIVERS)
    noms.update(dict(TEMOINS))
    tickers = list(noms)
    os.makedirs(DOSSIER, exist_ok=True)
    horodatage = datetime.now(timezone.utc).isoformat(timespec="seconds")

    print("Cours depuis le %s pour %d tickers..." % (DEBUT, len(tickers)))
    series = cours(tickers)
    with open(os.path.join(DOSSIER, "historique.json"), "w", encoding="utf-8") as f:
        json.dump({"generated": horodatage, "debut": DEBUT, "noms": noms,
                   "temoins": [t for t, _ in TEMOINS], "series": series},
                  f, ensure_ascii=False, separators=(",", ":"))
    print("historique.json : %d series" % len(series))

    print("Fondamentaux (valeurs du jour)...")
    with ThreadPoolExecutor(max_workers=6) as ex:
        fiches = dict(ex.map(fiche, [t for t, _ in UNIVERS]))
    ko = [t for t, v in fiches.items() if "erreur" in v or not v.get("marketCap")]
    with open(os.path.join(DOSSIER, "fondamentaux.json"), "w", encoding="utf-8") as f:
        json.dump({"generated": horodatage, "fiches": fiches, "incompletes": ko},
                  f, ensure_ascii=False, indent=0)
    print("fondamentaux.json : %d fiches, %d incompletes" % (len(fiches), len(ko)))


if __name__ == "__main__":
    main()

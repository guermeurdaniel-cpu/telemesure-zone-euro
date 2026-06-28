#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recupere 6 mois de cours, normalise base 100 et ecrit data.json a la racine du repo.
Lance par GitHub Actions (voir .github/workflows/update.yml).
Dependance : yfinance.

Deux onglets :
  - tab="panier" : agregats deja constitues (indices zone euro). Voir README pour
                   la correspondance indice -> ETF eligible PEA (ISIN).
  - tab="valeur" : titres individuels que l'on allume/eteint dans la legende.
                   Pour en ajouter/retirer un, edite simplement la liste VALEURS.
"""

import json
import os
from datetime import datetime, timezone
import yfinance as yf

# ----------------------------------------------------------------------------
# ONGLET 1 — PANIERS (agregats zone euro / Europe, base 100)
# (ticker Yahoo, nom, groupe, couleur, repere gras)
# Deux natures melangees :
#   - indices "^..." (CAC, DAX...) : cours prix, toujours resolus par Yahoo.
#   - ETF accumulants (CEMU.AS, PCEU.PA, MEUD.PA) : cours total return (dividendes
#     reinvestis) -> ces lignes derivent legerement vers le haut vs les indices prix
#     (~rendement du dividende). Voir la note "methodologie" dans le README.
# ----------------------------------------------------------------------------
PANIERS = [
    # --- agregats larges ---
    ("^STOXX50E",  "EuroStoxx 50",     "panier", "#00E5C7", True),   # indice zone euro, 50 leaders
    ("CEMU.AS",    "MSCI EMU",         "panier", "#E36BE0", False),  # ETF iShares Core MSCI EMU, zone euro ~225 (physique)
    ("PCEU.PA",    "MSCI Europe (PEA)","panier", "#C98BFF", False),  # ETF Amundi PEA MSCI Europe, Europe large (synthetique)
    ("MEUD.PA",    "Stoxx Europe 600", "panier", "#5BD1E6", False),  # ETF Amundi Core Stoxx Europe 600, Europe 600 (TER 0,07%)
    # --- indices nationaux zone euro ---
    ("^FCHI",      "CAC 40",           "panier", "#FFB000", False),  # France
    ("^GDAXI",     "DAX",              "panier", "#4DA3FF", False),  # Allemagne (indice total return)
    ("FTSEMIB.MI", "FTSE MIB",         "panier", "#FF5470", False),  # Italie
    ("^IBEX",      "IBEX 35",          "panier", "#9D7CFF", False),  # Espagne
    ("^AEX",       "AEX",              "panier", "#6FE26F", False),  # Pays-Bas
    # --- emergents (hors zone euro, ETF Amundi PEA synthetiques, pour comparaison) ---
    ("PAEEM.PA",   "PAEEM - Emergents","panier", "#FF8C42", False),  # Amundi PEA MSCI Emerging (monde) FR0013412020, TER 0,30%
    ("PAASI.PA",   "PAASI - Asie em.", "panier", "#B7E04B", False),  # Amundi PEA MSCI Emerging Asia FR0013412012, TER ~0,30%
]

# ----------------------------------------------------------------------------
# ONGLET 2 — VALEURS (titres individuels zone euro, eligibles PEA, base 100)
# Amorce demandee : Air Liquide, Sanofi, Pernod Ricard.
# Le reste est un fond de panier que tu peux retirer librement.
# ----------------------------------------------------------------------------
VALEURS = [
    ("AI.PA",   "Air Liquide",    "valeur", "#5BD1E6", False),  # demande
    ("SAN.PA",  "Sanofi",         "valeur", "#54E0A0", False),  # demande
    ("RI.PA",   "Pernod Ricard",  "valeur", "#FFD23F", False),  # demande
    # --- fond de panier (retirable) ---
    ("MC.PA",   "LVMH",           "valeur", "#E36BE0", False),
    ("OR.PA",   "L'Oreal",        "valeur", "#FF8C42", False),
    ("TTE.PA",  "TotalEnergies",  "valeur", "#FF9E5B", False),
    ("AIR.PA",  "Airbus",         "valeur", "#7AA5FF", False),
    ("SU.PA",   "Schneider El.",  "valeur", "#C9D14B", False),
    ("ASML.AS", "ASML",           "valeur", "#C98BFF", False),
    ("SAP.DE",  "SAP",            "valeur", "#FF6FA5", False),
    ("BNP.PA",  "BNP Paribas",    "valeur", "#8FE388", False),
]

SERIES = PANIERS + VALEURS

PERIOD = "6mo"
OUT = os.path.join(os.path.dirname(__file__), "..", "data.json")


def build():
    series = []
    for tk, name, grp, col, hero in SERIES:
        try:
            df = yf.Ticker(tk).history(period=PERIOD, auto_adjust=True)
            s = df["Close"].dropna()
            if len(s) < 2:
                raise ValueError("serie vide")
            base = float(s.iloc[0])
            x = [int(ts.timestamp() * 1000) for ts in s.index]
            y = [round(float(v) / base * 100.0, 3) for v in s.values]
            pct = round(float(s.iloc[-1]) / base * 100.0 - 100.0, 2)
            series.append(dict(tk=tk, name=name, tab=grp, col=col,
                               hero=hero, pct=pct, x=x, y=y))
            print("  ok   %-11s %-15s %+6.1f%%" % (tk, name, pct))
        except Exception as e:
            print("  FAIL %-11s %-15s (%s)" % (tk, name, e))
    return series


def main():
    print("Recuperation des cours (Yahoo Finance)...")
    series = build()
    payload = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "period": PERIOD,
        "series": series,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print("Ecrit %s (%d valeurs)" % (os.path.normpath(OUT), len(series)))


if __name__ == "__main__":
    main()

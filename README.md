# telemesure-zone-euro

Telemesure boursiere — zone euro / PEA. Meme moteur que `telemesure-boursiere`
(canvas base 100 + scraper yfinance + GitHub Actions quotidien), avec deux onglets :

- **Paniers** : indices zone euro (agregats deja constitues).
- **Valeurs** : titres individuels eligibles PEA, allumables/eteignables.

## Onglet Paniers — agregats traces

| Ligne (chart) | Ticker Yahoo | Nature | Support PEA / ISIN | TER |
|---|---|---|---|---|
| EuroStoxx 50 | `^STOXX50E` | indice (prix) | iShares Core / HSBC EURO STOXX 50 — IE00B53L3W79 / IE000MWUQBJ0 | 0,10 % / 0,05 % |
| MSCI EMU | `CEMU.AS` | **ETF** (physique) | iShares Core MSCI EMU — IE00B53QG562 | 0,12 % |
| MSCI Europe (PEA) | `PCEU.PA` | **ETF** (synthetique) | Amundi PEA MSCI Europe — part ~37 EUR | 0,25 % |
| Stoxx Europe 600 | `MEUD.PA` | **ETF** (physique) | Amundi Core Stoxx Europe 600 — LU0908500753 | 0,07 % |
| CAC 40 | `^FCHI` | indice (prix) | Amundi CAC 40 — FR0007052782 | 0,25 % |
| DAX | `^GDAXI` | indice (total return) | iShares Core DAX — DE0005933931 | ~0,16 % |
| FTSE MIB | `FTSEMIB.MI` | indice (prix) | Amundi FTSE MIB | ~0,35 % |
| IBEX 35 | `^IBEX` | indice (prix) | Amundi IBEX 35 | ~0,30 % |
| AEX | `^AEX` | indice (prix) | iShares AEX — IE00B0M62Y33 | ~0,30 % |
| PAEEM · Emergents | `PAEEM.PA` | **ETF** (synthetique) | Amundi PEA MSCI Emerging — FR0013412020 | 0,30 % |
| PAASI · Asie em. | `PAASI.PA` | **ETF** (synthetique) | Amundi PEA MSCI Emerging Asia — FR0013412012 | 0,30 % |
| WPEA · MSCI World | `WPEA.PA` | **ETF** (synthetique) | iShares MSCI World Swap PEA — IE0002XZSHO1 | 0,20 % |
| PUST · Nasdaq 100 | `PUST.PA` | **ETF** (synthetique) | Amundi PEA Nasdaq-100 — FR0011871110 | 0,30 % |

Les quatre dernieres lignes (PAEEM, PAASI, WPEA, PUST) sont **hors zone euro**, ajoutees
comme reperes de comparaison : emergents monde, Asie emergente, le MSCI World (coeur de
portefeuille) et le Nasdaq 100 (techno US). Eteins-les dans la legende pour revenir au
seul perimetre zone euro.

Le Nasdaq 100 est suivi par l'ETF **PUST.PA** (cote en euros) et non par l'indice
`^NDX` (cote en dollars) : ainsi la ligne integre l'effet de change EUR/USD, comme
WPEA.PA, et la comparaison avec les lignes zone euro reste homogene. C'est aussi un ETF
accumulant, donc en total return (voir la note methodologie ci-dessous).

Lecture des trois crans zone euro -> Europe : **EuroStoxx 50** (50 leaders, concentre)
< **MSCI EMU** (~225 valeurs, toujours zone euro, moins concentre) < **MSCI Europe /
Stoxx 600** (Europe large, incluant Royaume-Uni et Suisse pour le Stoxx 600, d'ou la
replication synthetique cote PCEU).

## Curseur de profondeur — 1 a 6 mois

Sous les onglets, un curseur regle la **fenetre affichee**, de **1 a 6 mois**.
`data.json` contient toujours 6 mois : le curseur ne relance aucune requete, il
retaille et **rebase les courbes a 100 sur la premiere seance de la fenetre**. Les
pourcentages de la legende sont recalcules sur cette meme fenetre — le classement a
1 mois n'a donc rien a voir avec celui a 6 mois. Sous ~2,5 mois, l'axe des dates passe
d'un pas mensuel a un pas hebdomadaire (etiquettes `jj/mm`).

Le curseur est masque dans la vue **Journee**, qui ne couvre qu'une seance.

### Note methodologie — prix vs total return

Les lignes ne sont pas toutes calculees pareil :
- Les **indices prix** (`^STOXX50E`, `^FCHI`, `FTSEMIB.MI`, `^IBEX`, `^AEX`)
  excluent les dividendes.
- Les **ETF accumulants** (`CEMU.AS`, `PCEU.PA`, `MEUD.PA`, `PUST.PA`) et le **DAX**
  sont en total return (dividendes reinvestis).

En base 100, les lignes total return derivent donc vers le haut d'environ le rendement
du dividende (~1,5 a 2 % sur 6 mois pour la zone euro) par rapport aux indices prix.
Pour un comparatif strictement homogene, deux options : passer toutes les lignes en
ETF accumulants, ou remplacer `^STOXX50E` par sa version *Net/Gross Return*. Dis-le si
tu veux que je bascule tout le panier en ETF total return.

Pour suivre l'ETF reel d'une ligne encore en indice, remplace son ticker dans `PANIERS`
par le mnemonique Euronext correspondant ; si Yahoo renvoie FAIL, garde l'indice.

Autres elargissements possibles (a ajouter dans `PANIERS`) :
- **Sectoriels zone euro** (banques, defense, energie...) via ETF sectoriels eligibles PEA.
- **MSCI EMU Value / Small Cap** pour un biais factoriel.

## Onglet Valeurs

Amorce : Air Liquide (`AI.PA`), Sanofi (`SAN.PA`), Pernod Ricard (`RI.PA`), complete d'un
fond de grandes capi zone euro (LVMH, L'Oreal, TotalEnergies, Airbus, Schneider, ASML, SAP,
BNP). Pour ajouter/retirer un titre, edite la liste `VALEURS` dans `scripts/fetch_data.py`
(un tuple par ligne : ticker, nom, "valeur", couleur, gras).

## Vue Gain net — retiree

La vue **Gain net** (aller-retour achat/revente net des frais PEA : courtage plafonne,
TTF, fiscalite au retrait) a ete **supprimee le 07/09/2026**, jugee sans interet a
l'usage. Le courtage decalait toutes les lignes du meme pourcentage et ne changeait pas
le classement. Le code est recuperable dans l'historique git (avant le commit
« Retire la vue Gain net »).

## Mise en route

1. Active **GitHub Pages** (Settings > Pages > branche `main`, dossier `/root`).
2. Onglet **Actions** > *Mise a jour des cours* > **Run workflow** pour generer
   `data.json` une premiere fois. Le scraper imprime `ok` / `FAIL` par ligne :
   remplace tout ticker en FAIL.
3. Ensuite, mise a jour automatique chaque jour ouvre a 06:00 UTC.

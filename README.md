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

Les trois dernieres lignes (PAEEM, PAASI, WPEA) sont **hors zone euro**, ajoutees comme
reperes de comparaison : emergents monde, Asie emergente, et le MSCI World (coeur de
portefeuille). Eteins-les dans la legende pour revenir au seul perimetre zone euro.

Lecture des trois crans zone euro -> Europe : **EuroStoxx 50** (50 leaders, concentre)
< **MSCI EMU** (~225 valeurs, toujours zone euro, moins concentre) < **MSCI Europe /
Stoxx 600** (Europe large, incluant Royaume-Uni et Suisse pour le Stoxx 600, d'ou la
replication synthetique cote PCEU).

### Note methodologie — prix vs total return

Les lignes ne sont pas toutes calculees pareil :
- Les **indices prix** (`^STOXX50E`, `^FCHI`, `FTSEMIB.MI`, `^IBEX`, `^AEX`)
  excluent les dividendes.
- Les **ETF accumulants** (`CEMU.AS`, `PCEU.PA`, `MEUD.PA`) et le **DAX** sont en
  total return (dividendes reinvestis).

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

## Vue Gain net — aller-retour net de frais PEA

La vue **Gain net** (bouton *Gain net* a cote de *Courbes*) simule, pour chaque ligne
de l'onglet courant, un **achat puis revente** sur la fenetre, et affiche le gain reel
en euros et en %, classe du meilleur au moins bon. Tu saisis le **montant par ligne**,
le **scenario de courtage** et la **fiscalite**.

Frais modelises (PEA BoursoBank) :
- **Courtage** plafonne au max legal **0,50 % par ordre** sur PEA (forfait Decouverte :
  1,99 EUR < 500 EUR, 0,60 % au-dela, le tout plafonne a 0,50 %). Soit **~1 % aller-retour**.
- **0 EUR** de droits de garde / frais de tenue / inactivite.
- **BoursoMarkets** : certains ETF (iShares, Amundi, Xtrackers) sont a **0 % de courtage
  a l'achat** — mais la **revente reste a 0,50 %**. D'ou ~0,5 % A/R sur ces ETF.
- **TTF 0,40 % a l'achat** sur les **actions francaises > 1 Md EUR** (Air Liquide, Sanofi,
  Pernod Ricard, LVMH, TotalEnergies, Airbus, Schneider, L'Oreal, BNP...). **Jamais** sur
  ETF, indices, ni titres etrangers (ASML `.AS`, SAP `.DE`). Detectee par `tab=valeur` + `.PA`.
- **TER de l'ETF** : non ajoute, il est **deja dans le cours** (lignes ETF en total return).
- **Fiscalite** : par defaut **arbitrage interne = 0 impot** (l'impot ne se declenche qu'au
  *retrait* du PEA, pas sur une revente interne). Le selecteur simule un retrait : **17,2 %**
  de prelevements sociaux sur le gain si PEA > 5 ans, **30 %** (PFU, cloture) si < 5 ans.

Les taux sont des constantes en haut du `<script>` de `index.html`
(`COURTAGE_PLAFOND`, `TTF`...) : ajuste-les si ton forfait differe.

> Limite : le courtage est identique quel que soit l'instrument a montant egal, donc il
> decale toutes les lignes du meme pourcentage et ne change pas le classement ; ce qui
> rebat les cartes entre lignes, c'est la **TTF** (actions FR vs etrangeres/ETF) et la
> gratuite **BoursoMarkets** a l'achat.

## Mise en route

1. Active **GitHub Pages** (Settings > Pages > branche `main`, dossier `/root`).
2. Onglet **Actions** > *Mise a jour des cours* > **Run workflow** pour generer
   `data.json` une premiere fois. Le scraper imprime `ok` / `FAIL` par ligne :
   remplace tout ticker en FAIL.
3. Ensuite, mise a jour automatique chaque jour ouvre a 06:00 UTC.

# telemesure-zone-euro

Palmarès PEA et portefeuille, en performance relative base 100.
Page refondue le 3 octobre 2026 : les anciens onglets Paniers et Valeurs ont disparu.

## Ce que montre la page

- **Les cinq plus fortes hausses et les cinq plus fortes baisses** parmi environ
  270 valeurs françaises et européennes éligibles au PEA, sur une fenêtre de
  **1 à 6 mois** réglée au curseur. Le classement est recalculé dans la page à chaque
  position du curseur : les dix valeurs affichées changent avec la fenêtre.
- **Les lignes du portefeuille**, tracées en trait plus épais.
- Toutes les courbes sont ramenées à **100 au début de la fenêtre**.

Deux vues, par le sélecteur du haut :

- **Courbes** : l'historique sur la fenêtre choisie.
- **Journée** : la séance en direct (Yahoo Finance, pas de 5 min, par le relais
  Cloudflare), sur les mêmes lignes. Mode Base 100 (toutes les lignes, 100 = clôture
  de la veille) ou Cours réel (une seule valeur).

## Lecture au doigt

- **Un doigt** : le niveau de chaque courbe à la date visée. La lecture s'efface
  quand on lève le doigt.
- **Deux doigts** : la variation en pourcentage de chaque courbe entre les deux
  dates. La lecture reste affichée quand on lève les doigts ; un nouvel appui
  l'efface. « n.d. » signale une courbe qui ne couvre pas les deux dates.
- Un appui sur une ligne de la légende allume ou éteint sa courbe.

## D'où viennent les données

Un seul script, `scripts/fetch_data.py`, lancé par le workflow
`.github/workflows/update.yml` : chaque jour ouvré à 06:00 UTC, à la main (Run
workflow), et à chaque modification du script ou de `univers.txt`. Il écrit `data.json` (environ
750 ko : six mois de cours pour chaque série).

### L'univers classé

Environ 270 valeurs, toutes éligibles au PEA, listées dans le fichier **`univers.txt`**
à la racine du dépôt (une ligne par valeur : `TICKER ; Nom`). C'est le seul endroit à
modifier pour ajouter ou retirer une valeur ; `fetch_data.py` et `historique.py` le
lisent tous les deux. Une modification de `univers.txt` relance aussitôt la mise à
jour des cours.

Cinq blocs, décrits dans l'en-tête du fichier :

1. **Le SBF 120 hors foncières cotées** (les SIIC ne sont pas éligibles au PEA).
2. **Quelques valeurs françaises hors SBF 120** à dividende régulier : Equasens,
   Robertet, LDC, Thermador, Vetoquinol, Neurones, Stef.
3. **Valeurs étrangères cotées à Paris, Amsterdam ou Bruxelles** (tarif Euronext
   normal) : la sélection du 3 octobre 2026, élargie le 20 novembre 2026 aux grandes
   valeurs d'Amsterdam et Bruxelles (ASM International, BESI, Adyen, ING, Philips,
   Prosus, AB InBev, argenx…) et à Nokia, cotée à Paris.
4. **Grandes valeurs européennes hors Euronext** (ordre minimal de 2 500 €) : la
   sélection du 3 octobre 2026, élargie le 20 novembre 2026 au reste de l'Euro
   Stoxx 50 et à de grandes valeurs voisines (Infineon, Rheinmetall, Deutsche
   Telekom, Enel, Intesa Sanpaolo, Ferrari, Santander, Nordea, Kingspan, EDP…).
5. **Petites et moyennes valeurs françaises hors SBF 120**, ajoutées le
   20 novembre 2026 (Wavestone, Lumibird, Manitou, Bénéteau, Aubay, Boiron…).

La liste est écrite à la main. Le SBF 120 étant revu chaque trimestre, elle est à
relire de temps en temps. Elle n'a pas besoin d'être exacte à la valeur près : elle
sert de vivier.

Règles d'éligibilité à respecter pour tout ajout : siège dans l'Union européenne ou
l'EEE, société soumise à l'impôt sur les sociétés. Donc ni foncières (SIIC, SIR
belges…), ni sociétés au siège hors UE même cotées à Paris ou Amsterdam (Shell,
Unilever, Aegon…).

Suffixes Yahoo : `.PA` Paris, `.AS` Amsterdam, `.BR` Bruxelles, `.DE` Francfort,
`.CO` Copenhague, `.MC` Madrid, `.MI` Milan, `.HE` Helsinki, `.IR` Dublin,
`.LS` Lisbonne.

Deux points propres aux valeurs européennes :

- **Ordre minimal.** Hors Paris, Amsterdam et Bruxelles, la brochure BoursoBank
  impose un ordre minimal de 2 500 € dans un PEA. La page l'indique dans la légende
  par la mention « min. 2 500 € », déduite du suffixe du ticker.
- **Devise.** Les valeurs danoises cotent en couronnes, monnaie arrimée à
  l'euro : leur variation est donnée en couronnes. Aucune valeur en couronnes
  suédoises ou norvégiennes n'a été retenue, pour ne pas mélanger un effet de change.

Un ticker que Yahoo ne reconnaît plus n'arrête pas le script : il est rangé dans la
clé `echecs` de `data.json` et affiché en rouge dans la barre d'état de la page.

### Le portefeuille

Les lignes ne sont **pas écrites dans ce dépôt**. Elles sont lues à chaque passage
dans le catalogue `supports.txt` du dépôt `mes-actions` : ajouter une valeur là-bas la
fait apparaître ici au passage suivant. Seul le catalogue est lu (intitulé,
identifiant, enveloppe, part d'actions) ; jamais les quantités ni les apports.

- Support coté (`source = yahoo`) : cours Yahoo, comme l'univers classé.
- Fonds non coté : valeurs liquidatives lues dans `history.json` de `mes-actions`.
  Cet historique ne commence que le **18 juin 2026** : sur une fenêtre plus profonde,
  la courbe part de 100 à sa première date connue et la légende affiche « depuis ».
  Le défaut se résorbe de lui-même, l'historique s'allongeant chaque jour.
- Un support dont la part d'actions est nulle (monétaire, obligataire) est éteint au
  chargement ; un appui dans la légende l'allume.
- Une valeur à la fois détenue et classée dans le palmarès apparaît une seule fois,
  dans le palmarès, avec la mention « portefeuille ».

Si `mes-actions` passe un jour en privé, ces deux lectures échoueront : la page
affichera le palmarès sans le portefeuille, avec l'erreur dans la barre d'état.

## Règles du classement

- Variation entre la première séance de la fenêtre et la dernière séance connue.
- Cours **ajustés des dividendes** (dividendes réinvestis) : les chiffres diffèrent
  légèrement des variations de cours brutes affichées par un courtier.
- Une valeur sans historique sur toute la fenêtre (introduction récente), ou dont la
  cotation s'est arrêtée depuis plus de dix jours, est écartée du classement.

## Études hors ligne (dossier analyse)

La page n'utilise pas ce dossier. Il sert aux essais de stratégies menés à part.

- `scripts/historique.py`, lancé par `.github/workflows/analyse.yml` : **uniquement à
  la main** (Actions > Analyse historique > Run workflow) ou quand ce script est
  modifié. Jamais de passage automatique. Après un ajout dans `univers.txt`, le
  relancer à la main pour que les nouvelles valeurs entrent dans ces fichiers.
- `analyse/historique.json` (environ 8,6 Mo) : cours quotidiens ajustés depuis 2010 et
  historique des dividendes versés, pour tout l'univers et trois témoins (deux ETF
  MSCI World et le CAC 40). La profondeur se règle par la constante `DEBUT` du script.
- `analyse/fondamentaux.json` : capitalisation, dette, trésorerie, marges et secteur
  lus chez Yahoo. Ce sont les **valeurs du jour**, pas celles du passé : s'en servir
  pour juger une décision passée revient à connaître l'avenir.

Limites à garder en tête pour tout essai sur ces fichiers :

- L'univers est celui d'aujourd'hui. Les sociétés sorties de la cote ou de l'indice
  n'y figurent pas, ce qui embellit les stratégies d'achat de valeurs en baisse, et
  de plus en plus à mesure qu'on remonte dans le temps.
- Deux séries sont faussées par des opérations sur titres que Yahoo corrige mal :
  Atos (regroupement d'actions fin 2024, variation mensuelle de +14 666 % puis
  -100 %) et Vivendi (scission de décembre 2024, lue comme une chute de 70 %). Les
  écarter de tout essai.
- Une règle trouvée sur une période doit être jugée sur une autre période. Essai du
  3 octobre 2026 : une règle construite sur 2022-2024 (dividende, faible volatilité,
  élan) battait la valeur médiane sur 2024-2026, mais faisait moins bien qu'elle sur
  2011-2022.

## Limites connues

- Yahoo peut avoir une séance de retard ou un trou dans une série.
- La liste de l'univers vieillit : voir plus haut.
- La sélection européenne est un choix éditorial, pas un indice : elle ne couvre pas
  toutes les valeurs européennes éligibles au PEA.
- Le fichier `.github/workflows/palmares.yml` est un reste d'essai du 3 octobre 2026
  (vérification du droit d'écriture du connecteur). Il ne se lance qu'à la main et ne
  fait rien : il peut être supprimé.

## Mise en route

1. GitHub Pages actif sur la branche `main`, dossier racine.
2. Onglet Actions > Mise a jour des cours > Run workflow pour régénérer `data.json`.
   Le script imprime `ok` ou `FAIL` par ligne.

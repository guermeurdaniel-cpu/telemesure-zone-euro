# telemesure-zone-euro

Palmarès PEA et portefeuille, en performance relative base 100.
Page refondue le 3 octobre 2026 : les anciens onglets Paniers et Valeurs ont disparu.

## Ce que montre la page

- **Les cinq plus fortes hausses et les cinq plus fortes baisses** parmi environ
  150 valeurs françaises et européennes éligibles au PEA, sur une fenêtre de
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
workflow), et à chaque modification du script. Il écrit `data.json` (environ
460 ko : six mois de cours pour chaque série).

### L'univers classé

Trois blocs, tous éligibles au PEA, dans la liste `UNIVERS` en tête du script :

1. **Le SBF 120 hors foncières cotées** (les SIIC ne sont pas éligibles au PEA).
2. **Quelques valeurs françaises hors SBF 120** connues pour la régularité de leur
   dividende : Equasens, Robertet, LDC, Thermador, Vetoquinol, Neurones, Stef.
3. **Une sélection européenne** à dividende régulier ou croissant, ajoutée le
   3 octobre 2026 : Wolters Kluwer, ASML, Ahold Delhaize, Heineken, ASR Nederland,
   UCB, KBC, Ackermans & van Haaren, Sofina, Ageas, D'Ieteren (Amsterdam et
   Bruxelles), puis Munich Re, Allianz, SAP, Hannover Re, Deutsche Börse, Siemens,
   Fuchs, Symrise, Novo Nordisk, Coloplast, Inditex, Iberdrola, Generali, Terna,
   Kone, Sampo et Kerry Group.

La liste est **figée à la main** à la date du 3 octobre 2026. Le SBF 120 étant revu
chaque trimestre, elle est à relire de temps en temps. Elle n'a pas besoin d'être
exacte à la valeur près : elle sert de vivier.

Pour ajouter ou retirer une valeur : une ligne `("TICKER.PA", "Nom")` dans `UNIVERS`.
Suffixes Yahoo : `.PA` Paris, `.AS` Amsterdam, `.BR` Bruxelles, `.DE` Francfort,
`.CO` Copenhague, `.MC` Madrid, `.MI` Milan, `.HE` Helsinki, `.IR` Dublin.

Deux points propres aux valeurs européennes :

- **Ordre minimal.** Hors Paris, Amsterdam et Bruxelles, la brochure BoursoBank
  impose un ordre minimal de 2 500 € dans un PEA. La page l'indique dans la légende
  par la mention « min. 2 500 € », déduite du suffixe du ticker.
- **Devise.** Les deux valeurs danoises cotent en couronnes, monnaie arrimée à
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
  modifié. Jamais de passage automatique.
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

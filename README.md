# telemesure-zone-euro

Palmarès PEA et portefeuille, en performance relative base 100.
Page refondue le 3 octobre 2026 : les anciens onglets Paniers et Valeurs ont disparu.

## Ce que montre la page

- **Les cinq plus fortes hausses et les cinq plus fortes baisses** parmi environ
  120 grandes et moyennes valeurs françaises éligibles au PEA, sur une fenêtre de
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
370 ko : six mois de cours pour chaque série).

### L'univers classé

Le SBF 120 hors foncières cotées (les SIIC ne sont pas éligibles au PEA). La liste
est **figée à la main** dans `UNIVERS`, en tête du script, à la date du
3 octobre 2026. L'indice étant revu chaque trimestre, elle est à relire de temps en
temps. Elle n'a pas besoin d'être exacte à la valeur près : elle sert de vivier.

Pour ajouter ou retirer une valeur : une ligne `("TICKER.PA", "Nom")` dans `UNIVERS`.
Attention aux suffixes Yahoo : `.PA` pour Paris, `.AS` pour Amsterdam
(ArcelorMittal, Aperam), `.BR` pour Bruxelles (Solvay).

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

## Limites connues

- Yahoo peut avoir une séance de retard ou un trou dans une série.
- La liste de l'univers vieillit : voir plus haut.
- Le fichier `.github/workflows/palmares.yml` est un reste d'essai du 3 octobre 2026
  (vérification du droit d'écriture du connecteur). Il ne se lance qu'à la main et ne
  fait rien : il peut être supprimé.

## Mise en route

1. GitHub Pages actif sur la branche `main`, dossier racine.
2. Onglet Actions > Mise a jour des cours > Run workflow pour régénérer `data.json`.
   Le script imprime `ok` ou `FAIL` par ligne.

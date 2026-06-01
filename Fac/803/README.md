# INFO0803 — Visualisation des données

Analyse boursière du CAC40 et cartes de France (`Projet/analyse_cac40.R`,
`Dashboard_ModeleDeRegression.Rmd`, `CM3_Construction_de_Cartes.R`, `tp4.R`, `tp5.R`).

## Datasets non versionnés

Les données volumineuses ne sont pas dans le dépôt (voir `.gitignore`).
Pour exécuter le projet, recrée l'arborescence suivante et télécharge les fichiers :

### `Projet/data/` — cours du CAC40
- `CAC40_stocks_2010_2021.csv`, `CAC40_stocks_2021_2023.csv`, `preprocessed_CAC40.csv`
- **Source :** dataset Kaggle *CAC40 stocks dataset* (bryanb)
  → https://www.kaggle.com/datasets/bryanb/cac40-stocks-dataset
  (le `archive (1).zip` est l'archive téléchargée depuis Kaggle)

### `Data/` et `Data-20260402/Data.zip` — fonds de carte France
- Shapefiles régions / départements (`regions-20180101-shp`, `regions-metropole-complet`, `dpt`)
- **Source :** contours administratifs issus d'OpenStreetMap, sur data.gouv.fr
  → https://www.data.gouv.fr/fr/datasets/contours-des-regions-francaises-sur-openstreetmap/
  → https://www.data.gouv.fr/fr/datasets/contours-des-departements-francais-issus-d-openstreetmap/

### `taches_solaires_date.csv` (TP2) — nombre de taches solaires
- **Source :** WDC-SILSO, Observatoire royal de Belgique
  → https://www.sidc.be/SILSO/datafiles

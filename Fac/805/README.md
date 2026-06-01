# INFO0805 — Gestion de projet : couverture réseau 4G/5G

Recherche de zones blanches et placement optimal de nouvelles antennes
(Set Cover glouton). Code dans `Projet/code/`, rapport dans `Projet/rapport/`.

## Données d'entrée (téléchargées automatiquement)

- **Limites administratives France** (départements / régions) : téléchargées par
  `analyse_zones_blanches.py` depuis l'IGN Géoplateforme (WFS) et mises en cache
  dans `admin_france.gpkg`.
  → https://data.geopf.fr/ (couche `LIMITES_ADMINISTRATIVES_EXPRESS.LATEST`)
- **Réseau routier** : OpenStreetMap → https://www.openstreetmap.org/
- **Installations radioélectriques / antennes** (ANFR / Cartoradio) :
  → https://data.anfr.fr/ • https://www.cartoradio.fr/

## Résultats volumineux non versionnés

Régénérés en exécutant les scripts de `Projet/code/` :

- `Projet/resultats/routes_couvertes.gpkg` (~174 Mo) — sortie de `routes_couvertes.py`
- `Projet/resultats/resultats_zones_blanches.zip` (~68 Mo) — export agrégé

Les résultats légers (`stats_departements.csv`, `stats_regions.csv`,
`rapport_antennes.csv`, `nouvelles_antennes.gpkg`, `routes_non_couvertes.gpkg`)
restent versionnés.

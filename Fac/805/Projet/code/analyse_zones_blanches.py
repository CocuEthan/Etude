#!/usr/bin/env python3
"""
analyse_zones_blanches.py

Analyse les zones de couverture 4G en France :
  1. Statistiques (moyenne, médiane, %) par département et région → CSV
  2. Placement optimal de nouvelles antennes (greedy Set Cover) → GPKG + CSV
"""

import sys
import time
import logging
import json
import urllib.request
from pathlib import Path
from contextlib import contextmanager

import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
from shapely import STRtree


# === CONFIG ===

DATA_DIR             = Path("Dead_area/gpkg/data")
ADMIN_CACHE_GPKG     = DATA_DIR / "admin_france.gpkg"

ROUTES_NON_COUVERTES = Path("routes_non_couvertes.gpkg")
ROUTES_COUVERTES     = Path("routes_couvertes.gpkg")

OUT_STATS_DEPT       = Path("stats_departements.csv")
OUT_STATS_REG        = Path("stats_regions.csv")
OUT_RAPPORT          = Path("rapport_antennes.csv")
OUT_ANTENNES_GPKG    = Path("nouvelles_antennes.gpkg")
LOG_FILE             = Path("analyse_zones_blanches.log")

ANTENNA_RADIUS_M = 1500   # rayon d'une antenne en mètres (EPSG:2154)
TARGET_CRS       = "EPSG:2154"

_WFS_BASE = (
    "https://data.geopf.fr/wfs/ows"
    "?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature"
    "&OUTPUTFORMAT=application/json&SRSNAME=EPSG:2154&COUNT=500"
)
URL_DEPT = _WFS_BASE + "&TYPENAMES=LIMITES_ADMINISTRATIVES_EXPRESS.LATEST:departement"
URL_REG  = _WFS_BASE + "&TYPENAMES=LIMITES_ADMINISTRATIVES_EXPRESS.LATEST:region"

DOM_TOM_DEPT = {"971", "972", "973", "974", "976"}
DOM_TOM_REG  = {"01", "02", "03", "04", "06"}


# === UTILITAIRES ===

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


@contextmanager
def timed_step(label: str):
    t0 = time.perf_counter()
    logging.info("▶ %s — START", label)
    try:
        yield
    finally:
        logging.info("■ %s — END (%.1fs)", label, time.perf_counter() - t0)


def human_eta(seconds: float) -> str:
    if seconds < 0:
        return "?"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h{m:02d}m"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


# === SECTION D — CONTOURS ADMINISTRATIFS IGN ===

def _fetch_wfs(url: str, label: str) -> gpd.GeoDataFrame:
    logging.info("Téléchargement WFS %s…", label)
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            raw = json.loads(resp.read())
    except Exception as exc:
        logging.error("Téléchargement WFS échoué (%s): %s", label, exc)
        logging.error(
            "Solution manuelle : placer admin_france.gpkg dans %s "
            "(couches 'departements' et 'regions')", ADMIN_CACHE_GPKG
        )
        sys.exit(1)
    return gpd.GeoDataFrame.from_features(raw["features"], crs=TARGET_CRS)


def download_admin_boundaries():
    """Télécharge ou charge depuis le cache les contours département + région IGN."""
    if ADMIN_CACHE_GPKG.exists():
        logging.info("Cache admin trouvé → %s", ADMIN_CACHE_GPKG)
        dept = gpd.read_file(ADMIN_CACHE_GPKG, layer="departements", engine="pyogrio")
        reg  = gpd.read_file(ADMIN_CACHE_GPKG, layer="regions",      engine="pyogrio")
        logging.info("Admin chargé: %d départements, %d régions", len(dept), len(reg))
        return dept, reg

    with timed_step("Téléchargement contours administratifs IGN WFS"):
        dept_raw = _fetch_wfs(URL_DEPT, "départements")
        reg_raw  = _fetch_wfs(URL_REG,  "régions")

    # --- Départements ---
    dept = dept_raw.rename(columns={
        "code_insee":              "code_dept",
        "nom_officiel":            "nom_dept",
        "code_insee_de_la_region": "code_region",
    })
    keep = [c for c in ["code_dept", "nom_dept", "code_region", "geometry"] if c in dept.columns]
    dept = dept[keep].copy()
    dept = dept[~dept["code_dept"].isin(DOM_TOM_DEPT)].reset_index(drop=True)

    # --- Régions ---
    reg = reg_raw.rename(columns={
        "code_insee":   "code_region",
        "nom_officiel": "nom_region",
    })
    keep = [c for c in ["code_region", "nom_region", "geometry"] if c in reg.columns]
    reg = reg[keep].copy()
    reg = reg[~reg["code_region"].isin(DOM_TOM_REG)].reset_index(drop=True)

    logging.info("Départements métropole: %d | Régions métropole: %d", len(dept), len(reg))

    with timed_step("Écriture cache admin"):
        dept.to_file(ADMIN_CACHE_GPKG, layer="departements", driver="GPKG")
        reg.to_file( ADMIN_CACHE_GPKG, layer="regions",      driver="GPKG")

    return dept, reg


# === HELPERS GÉOSPATIAUX ===

def _to_centroids(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Retourne un GeoDataFrame de points (centroids) en conservant les attributs."""
    geom_arr  = np.array(gdf.geometry)
    centroids = shapely.centroid(geom_arr)
    pts = gdf.drop(columns=["geometry"]).copy().reset_index(drop=True)
    pts = gpd.GeoDataFrame(pts, geometry=list(centroids), crs=TARGET_CRS)
    return pts


def _sjoin_with_fallback(
    pts: gpd.GeoDataFrame,
    admin: gpd.GeoDataFrame,
    admin_cols: list,
    label: str,
) -> gpd.GeoDataFrame:
    """sjoin 'within' avec fallback sjoin_nearest (5 km) pour les points sur frontière."""
    joined = gpd.sjoin(
        pts,
        admin[admin_cols + ["geometry"]],
        how="left",
        predicate="within",
    ).drop(columns=["index_right"], errors="ignore")

    mask_na = joined[admin_cols[0]].isna()
    if mask_na.any():
        n = int(mask_na.sum())
        logging.warning("%s: %d points hors polygone → sjoin_nearest (max 5 km)", label, n)
        fallback = gpd.sjoin_nearest(
            pts[mask_na][["geometry"]],
            admin[admin_cols + ["geometry"]],
            how="left",
            max_distance=5000,
        ).drop(columns=["index_right"], errors="ignore")

        for col in admin_cols:
            src = fallback[col].values if col in fallback.columns else "INCONNU"
            joined.loc[mask_na, col] = src

        still_na = joined[admin_cols[0]].isna()
        if still_na.any():
            logging.warning("%s: %d points définitivement non assignés → INCONNU", label, int(still_na.sum()))
            for col in admin_cols:
                joined[col] = joined[col].fillna("INCONNU")

    return joined


# === SECTION E — STATISTIQUES ===

def _total_couvert_par_dept(dept: gpd.GeoDataFrame) -> pd.Series:
    """Longueur totale des routes COUVERTES par département (km)."""
    logging.info("Lecture routes_couvertes.gpkg…")
    cov = gpd.read_file(ROUTES_COUVERTES, engine="pyogrio")
    pts_cov = _to_centroids(cov)
    del cov

    joined_cov = _sjoin_with_fallback(
        pts_cov, dept, ["code_dept"], "routes_couvertes"
    )
    return joined_cov.groupby("code_dept")["len_m"].sum() / 1000  # km


def run_stats(nc_gdf: gpd.GeoDataFrame, dept: gpd.GeoDataFrame, reg: gpd.GeoDataFrame):
    with timed_step("Jointure routes non-couvertes → départements"):
        pts_nc = _to_centroids(nc_gdf)
        joined = _sjoin_with_fallback(
            pts_nc, dept, ["code_dept", "nom_dept", "code_region"], "routes_nc"
        )
        joined = joined.merge(reg[["code_region", "nom_region"]], on="code_region", how="left")
        joined["nom_region"] = joined["nom_region"].fillna("INCONNU")

    with timed_step("Calcul longueurs totales couvertes par département"):
        cov_par_dept_km = _total_couvert_par_dept(dept)

    with timed_step("Agrégation statistiques par département"):
        grp = joined.groupby(["code_dept", "nom_dept", "code_region", "nom_region"])
        stats_dept = grp["len_m"].agg(
            nb_segments_nc="count",
            longueur_nc_km=lambda x: round(x.sum() / 1000, 2),
            longueur_moy_m=lambda x: round(x.mean(), 1),
            longueur_med_m=lambda x: round(x.median(), 1),
        ).reset_index()

        # Longueur totale = couverte + non-couverte, % non-couvert
        stats_dept = stats_dept.join(
            cov_par_dept_km.rename("cov_km"), on="code_dept"
        )
        stats_dept["longueur_total_km"] = (
            stats_dept["longueur_nc_km"] + stats_dept["cov_km"].fillna(0)
        ).round(2)
        stats_dept["pct_non_couvert"] = (
            stats_dept["longueur_nc_km"]
            / stats_dept["longueur_total_km"].replace(0, np.nan)
            * 100
        ).round(2)
        stats_dept = stats_dept.drop(columns=["cov_km"])
        stats_dept = stats_dept.sort_values("code_dept").reset_index(drop=True)

        stats_dept.to_csv(OUT_STATS_DEPT, index=False, sep=";", encoding="utf-8-sig")
        logging.info("Écrit: %s (%d départements)", OUT_STATS_DEPT, len(stats_dept))

    with timed_step("Agrégation statistiques par région"):
        grp_reg = joined.groupby(["code_region", "nom_region"])
        stats_reg = grp_reg["len_m"].agg(
            nb_segments_nc="count",
            longueur_nc_km=lambda x: round(x.sum() / 1000, 2),
            longueur_moy_m=lambda x: round(x.mean(), 1),
            longueur_med_m=lambda x: round(x.median(), 1),
        ).reset_index()

        nb_dept_par_reg = (
            dept[~dept["code_dept"].isin(["INCONNU"])]
            .groupby("code_region")["code_dept"]
            .nunique()
            .rename("nb_departements")
        )
        stats_reg = stats_reg.join(nb_dept_par_reg, on="code_region")

        # Longueur totale par région = somme des totaux dept
        total_reg = (
            stats_dept.groupby("code_region")["longueur_total_km"].sum().round(2)
        )
        stats_reg = stats_reg.join(total_reg, on="code_region")

        stats_reg["pct_non_couvert"] = (
            stats_reg["longueur_nc_km"]
            / stats_reg["longueur_total_km"].replace(0, np.nan)
            * 100
        ).round(2)

        col_order = [
            "code_region", "nom_region", "nb_departements",
            "nb_segments_nc", "longueur_nc_km", "longueur_moy_m", "longueur_med_m",
            "longueur_total_km", "pct_non_couvert",
        ]
        stats_reg = stats_reg[[c for c in col_order if c in stats_reg.columns]]
        stats_reg = stats_reg.sort_values("code_region").reset_index(drop=True)

        stats_reg.to_csv(OUT_STATS_REG, index=False, sep=";", encoding="utf-8-sig")
        logging.info("Écrit: %s (%d régions)", OUT_STATS_REG, len(stats_reg))


# === SECTION F — GREEDY SET COVER ===

def run_set_cover(
    nc_gdf: gpd.GeoDataFrame,
    dept: gpd.GeoDataFrame,
    reg: gpd.GeoDataFrame,
):
    with timed_step(f"Greedy Set Cover (rayon={ANTENNA_RADIUS_M} m)"):
        geom_arr  = np.array(nc_gdf.geometry)
        centroids = shapely.centroid(geom_arr)
        lengths   = nc_gdf["len_m"].values.astype(float)

        positive = lengths[lengths > 0]
        if positive.size > 0 and ANTENNA_RADIUS_M < positive.min() / 2:
            logging.warning(
                "ANTENNA_RADIUS_M=%d m < demi-longueur min segment (%.1f m): "
                "risque d'une antenne par segment",
                ANTENNA_RADIUS_M, positive.min() / 2,
            )

        tree    = STRtree(centroids)
        covered = np.zeros(len(nc_gdf), dtype=bool)
        antenna_indices: list[int] = []

        while not covered.all():
            masked = np.where(covered, -1.0, lengths)
            best   = int(np.argmax(masked))
            hits   = tree.query(
                centroids[best],
                predicate="dwithin",
                distance=ANTENNA_RADIUS_M,
            )
            covered[hits] = True
            antenna_indices.append(best)

        logging.info(
            "Set Cover terminé: %d antennes pour %d segments",
            len(antenna_indices), len(nc_gdf),
        )

    with timed_step("Attribution département/région aux antennes"):
        ant_geoms = [centroids[i] for i in antenna_indices]
        ant_gdf = gpd.GeoDataFrame(
            {"antenna_id": range(len(antenna_indices))},
            geometry=ant_geoms,
            crs=TARGET_CRS,
        )
        ant_gdf = _sjoin_with_fallback(
            ant_gdf, dept, ["code_dept", "nom_dept", "code_region"], "antennes"
        )
        ant_gdf = ant_gdf.merge(
            reg[["code_region", "nom_region"]], on="code_region", how="left"
        )
        ant_gdf["nom_region"] = ant_gdf["nom_region"].fillna("INCONNU")

    with timed_step("Écriture nouvelles_antennes.gpkg"):
        if OUT_ANTENNES_GPKG.exists():
            OUT_ANTENNES_GPKG.unlink()
        cols = [
            c for c in
            ["antenna_id", "code_dept", "nom_dept", "code_region", "nom_region", "geometry"]
            if c in ant_gdf.columns
        ]
        ant_gdf[cols].to_file(OUT_ANTENNES_GPKG, layer="antennes", driver="GPKG")
        logging.info("Écrit: %s (%d antennes)", OUT_ANTENNES_GPKG, len(ant_gdf))

    with timed_step("Rapport antennes par niveau géographique"):
        rows = [{
            "niveau": "national",
            "code": "FR",
            "nom": "France métropolitaine",
            "nb_antennes": len(ant_gdf),
        }]
        for code_r, g_r in ant_gdf.groupby("code_region"):
            rows.append({
                "niveau": "region",
                "code": code_r,
                "nom": g_r["nom_region"].iloc[0],
                "nb_antennes": len(g_r),
            })
        for code_d, g_d in ant_gdf.groupby("code_dept"):
            rows.append({
                "niveau": "departement",
                "code": code_d,
                "nom": g_d["nom_dept"].iloc[0],
                "nb_antennes": len(g_d),
            })

        pd.DataFrame(rows).to_csv(OUT_RAPPORT, index=False, sep=";", encoding="utf-8-sig")
        logging.info("Écrit: %s", OUT_RAPPORT)


# === MAIN ===

def main():
    setup_logger()
    t0 = time.perf_counter()
    logging.info("=== analyse_zones_blanches.py | rayon=%d m ===", ANTENNA_RADIUS_M)

    for p in [ROUTES_NON_COUVERTES, ROUTES_COUVERTES]:
        if not p.exists():
            logging.error("Fichier introuvable: %s", p)
            sys.exit(1)

    with timed_step("Lecture routes_non_couvertes.gpkg"):
        nc_gdf = gpd.read_file(ROUTES_NON_COUVERTES, engine="pyogrio")
        logging.info("Segments non-couverts: %d", len(nc_gdf))

    dept, reg = download_admin_boundaries()

    run_stats(nc_gdf, dept, reg)

    run_set_cover(nc_gdf, dept, reg)

    logging.info("✅ Terminé — temps total: %s", human_eta(time.perf_counter() - t0))
    logging.info("Sorties:")
    for p in [OUT_STATS_DEPT, OUT_STATS_REG, OUT_RAPPORT, OUT_ANTENNES_GPKG]:
        if p.exists():
            logging.info("  %s (%.1f KB)", p, p.stat().st_size / 1024)


if __name__ == "__main__":
    main()

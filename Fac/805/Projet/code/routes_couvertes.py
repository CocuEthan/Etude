#!/usr/bin/env python3
import logging
import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import shapely
import geopandas as gpd

# ---- FICHIERS --------------------------------------------------------------
DATA_DIR   = "Dead_area/gpkg/data"
ROADS_GPKG = f"{DATA_DIR}/grand_axe_2154.gpkg"
COV_GPKG   = f"{DATA_DIR}/coverage_4G_france.gpkg"

OUT_COVERED     = "routes_couvertes.gpkg"
OUT_NOT_COVERED = "routes_non_couvertes.gpkg"
LOG_FILE        = "routes_couvertes.log"

TARGET_CRS = "EPSG:2154"

# ---- PARAMÈTRES ------------------------------------------------------------
N_WORKERS    = os.cpu_count() or 4   # threads parallèles = nb cœurs
TILE_K       = 8                      # grille 8×8 = 64 tuiles
SIMPLIFY_TOL = 200.0                  # tolérance simplification locale (m)


def safe_delete(path: str):
    p = Path(path)
    if p.exists():
        p.unlink()


def looks_like_lonlat(bounds) -> bool:
    minx, miny, maxx, maxy = bounds
    return (-180 <= minx <= 180 and -180 <= maxx <= 180 and -90 <= miny <= 90 and -90 <= maxy <= 90)


# ---- FIX GEOM VECTORISÉ + PARALLÈLE ---------------------------------------

def fix_geom_chunk(geom_arr: np.ndarray) -> np.ndarray:
    """
    Équivalent vectorisé de fix_geom() sur un array numpy de géométries.
    Shapely 2 relâche le GIL dans GEOS → vrai parallélisme avec ThreadPoolExecutor.
    """
    fixed = shapely.buffer(geom_arr, 0)

    bad = ~shapely.is_valid(fixed) | shapely.is_empty(fixed)
    if bad.any():
        fixed[bad] = shapely.make_valid(geom_arr[bad])

    # keep_polygonal : type_id 3=Polygon, 6=MultiPolygon
    not_poly = ~np.isin(shapely.get_type_id(fixed), [3, 6])
    if not_poly.any():
        fixed[not_poly] = shapely.buffer(geom_arr[not_poly], 0)

    return fixed


def parallel_fix_geom(cov: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Remplace cov["geometry"].apply(fix_geom) par fix vectorisé + threadé."""
    logging.info("Fixing invalid coverage geometries (vectorized, %d threads)…", N_WORKERS)
    geom_arr = np.array(cov.geometry)
    chunks = np.array_split(geom_arr, N_WORKERS)

    with ThreadPoolExecutor(max_workers=N_WORKERS) as ex:
        results = list(ex.map(fix_geom_chunk, chunks))

    cov = cov.copy()
    cov["geometry"] = np.concatenate(results)
    cov = cov[~shapely.is_empty(np.array(cov.geometry))].copy()

    if len(cov) == 0:
        logging.error("Coverage layer is empty after fixing. (Likely wrong CRS assignment.)")
        sys.exit(1)

    return cov


# ---- TILING + OVERLAY PARALLÈLE -------------------------------------------

def build_tile_grid(bounds: tuple, k: int) -> list:
    """Crée une grille k×k de boîtes couvrant bounds."""
    minx, miny, maxx, maxy = bounds
    tw = (maxx - minx) / k
    th = (maxy - miny) / k
    return [
        shapely.box(minx + c * tw, miny + r * th,
                    minx + (c + 1) * tw, miny + (r + 1) * th)
        for r in range(k) for c in range(k)
    ]


def process_one_tile(
    tile_box,
    roads_gdf: gpd.GeoDataFrame,
    cov_arr: np.ndarray,
    cov_tree: shapely.STRtree,
    simplify_tol: float,
):
    """
    Pour une tuile : filtre routes + couverture, union local, intersection + différence.
    Retourne (covered_gdf | None, notcov_gdf | None).
    """
    # 1. Routes dont la bbox touche la tuile (filtrage numpy, pas de boucle Python)
    rb = shapely.bounds(np.array(roads_gdf.geometry))
    tb = shapely.bounds(np.array([tile_box]))[0]
    mask = (
        (rb[:, 0] < tb[2]) & (rb[:, 2] > tb[0]) &
        (rb[:, 1] < tb[3]) & (rb[:, 3] > tb[1])
    )
    if not mask.any():
        return None, None
    tile_roads = roads_gdf.iloc[np.where(mask)[0]].copy()

    # 2. Clip routes à la tuile
    road_arr = shapely.intersection(np.array(tile_roads.geometry), tile_box)
    empty_mask = shapely.is_empty(road_arr)
    tile_roads = tile_roads[~empty_mask].copy()
    road_arr = road_arr[~empty_mask]
    if len(road_arr) == 0:
        return None, None
    tile_roads = tile_roads.copy()
    tile_roads["geometry"] = road_arr

    # 3. Polygones de couverture touchant la tuile (STRtree query, thread-safe en lecture)
    cov_idx = cov_tree.query(tile_box, predicate="intersects")
    if len(cov_idx) == 0:
        nc = tile_roads.copy()
        nc["covered"] = 0
        nc["len_m"] = shapely.length(road_arr)
        return None, nc

    # 4. Union local (bien moins de sommets que l'union globale)
    local_cov = shapely.union_all(cov_arr[cov_idx])
    if simplify_tol > 0:
        local_cov = shapely.simplify(local_cov, simplify_tol, preserve_topology=True)

    # 5. Intersection + différence vectorisées (GIL relâché dans GEOS)
    inter_arr = shapely.intersection(road_arr, local_cov)
    diff_arr  = shapely.difference(road_arr,  local_cov)

    LINEAR = [1, 5]  # LineString=1, MultiLineString=5
    inter_ok = np.isin(shapely.get_type_id(inter_arr), LINEAR) & ~shapely.is_empty(inter_arr)
    diff_ok  = np.isin(shapely.get_type_id(diff_arr),  LINEAR) & ~shapely.is_empty(diff_arr)

    covered = notcov = None

    if inter_ok.any():
        covered = tile_roads.iloc[np.where(inter_ok)[0]].copy()
        covered["geometry"] = inter_arr[inter_ok]
        covered["covered"] = 1
        covered["len_m"] = shapely.length(inter_arr[inter_ok])

    if diff_ok.any():
        notcov = tile_roads.iloc[np.where(diff_ok)[0]].copy()
        notcov["geometry"] = diff_arr[diff_ok]
        notcov["covered"] = 0
        notcov["len_m"] = shapely.length(diff_arr[diff_ok])

    return covered, notcov


def parallel_overlay(roads: gpd.GeoDataFrame, cov: gpd.GeoDataFrame):
    """
    Remplace unary_union + gpd.overlay × 2 par tiling spatial + ThreadPoolExecutor.
    Évite de construire le polygone union global (cause des 19 jours originaux).
    """
    logging.info("Building tile grid (%d×%d=%d tiles)…", TILE_K, TILE_K, TILE_K**2)
    tiles = build_tile_grid(roads.total_bounds, TILE_K)

    cov_arr  = np.array(cov.geometry)
    # STRtree construit dans le thread principal, lu en read-only dans les workers
    cov_tree = shapely.STRtree(cov_arr)

    logging.info("Dispatching %d tiles to %d threads…", len(tiles), N_WORKERS)
    tile_args = [(t, roads, cov_arr, cov_tree, SIMPLIFY_TOL) for t in tiles]

    with ThreadPoolExecutor(max_workers=N_WORKERS) as ex:
        results = list(ex.map(lambda a: process_one_tile(*a), tile_args))

    cv_parts = [r[0] for r in results if r[0] is not None]
    nc_parts = [r[1] for r in results if r[1] is not None]

    logging.info("Concatenating results (%d + %d tile chunks)…", len(cv_parts), len(nc_parts))
    empty_gdf = gpd.GeoDataFrame(
        columns=list(roads.columns) + ["covered", "len_m"],
        geometry="geometry", crs=TARGET_CRS
    )
    covered = gpd.GeoDataFrame(
        pd.concat(cv_parts, ignore_index=True), crs=TARGET_CRS
    ) if cv_parts else empty_gdf.copy()
    notcov = gpd.GeoDataFrame(
        pd.concat(nc_parts, ignore_index=True), crs=TARGET_CRS
    ) if nc_parts else empty_gdf.copy()

    return covered, notcov


# ---- MAIN ------------------------------------------------------------------

def main():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("Start (workers=%d, tiles=%d×%d)", N_WORKERS, TILE_K, TILE_K)

    # ---- READ ----------------------------------------------------------------
    logging.info("Reading roads: %s", ROADS_GPKG)
    roads = gpd.read_file(ROADS_GPKG, engine="pyogrio")

    logging.info("Reading coverage: %s", COV_GPKG)
    cov = gpd.read_file(COV_GPKG, engine="pyogrio")

    # ---- CRS ROADS -----------------------------------------------------------
    if roads.crs is None:
        logging.warning("roads CRS is None -> forcing %s", TARGET_CRS)
        roads = roads.set_crs(TARGET_CRS, allow_override=True)

    if str(roads.crs) != TARGET_CRS:
        logging.info("Reproject roads %s -> %s", roads.crs, TARGET_CRS)
        roads = roads.to_crs(TARGET_CRS)

    # ---- CRS COVERAGE --------------------------------------------------------
    cov_bounds = cov.total_bounds
    logging.info("Coverage bounds: %s", cov_bounds)

    if cov.crs is None:
        if looks_like_lonlat(cov_bounds):
            logging.info("Coverage looks like lon/lat -> set CRS EPSG:4326 then reproject to %s", TARGET_CRS)
            cov = cov.set_crs("EPSG:4326", allow_override=True).to_crs(TARGET_CRS)
        else:
            logging.info("Coverage looks projected -> forcing CRS %s (override, no transform)", TARGET_CRS)
            cov = cov.set_crs(TARGET_CRS, allow_override=True)
    else:
        crs_str = str(cov.crs)
        if looks_like_lonlat(cov_bounds):
            if crs_str != TARGET_CRS:
                logging.info("Coverage looks lon/lat -> reproject %s -> %s", cov.crs, TARGET_CRS)
                cov = cov.to_crs(TARGET_CRS)
        else:
            if crs_str != TARGET_CRS:
                logging.info("Coverage looks projected but CRS is '%s' -> forcing %s (override)", crs_str, TARGET_CRS)
                cov = cov.set_crs(TARGET_CRS, allow_override=True)
            else:
                logging.info("Coverage CRS already %s", TARGET_CRS)

    # ---- FIX GEOM (vectorisé + parallèle) ------------------------------------
    cov = parallel_fix_geom(cov)

    # ---- OVERLAY PARALLÈLE (remplace unary_union + 2×gpd.overlay) -----------
    covered, notcov = parallel_overlay(roads, cov)
    del cov

    # ---- WRITE ---------------------------------------------------------------
    logging.info("Writing outputs… (close QGIS if you get locks)")
    safe_delete(OUT_COVERED)
    safe_delete(OUT_NOT_COVERED)

    covered.to_file(OUT_COVERED,     layer="covered",     driver="GPKG")
    notcov.to_file(OUT_NOT_COVERED,  layer="not_covered", driver="GPKG")

    # ---- STATS ---------------------------------------------------------------
    total_len = roads.length.sum()
    cov_len = covered["len_m"].sum() if "len_m" in covered.columns else 0.0
    pct = (cov_len / total_len * 100) if total_len > 0 else 0.0

    logging.info("Done")
    logging.info("  Roads total:       %s", f"{len(roads):,}")
    logging.info("  Covered segments:  %s", f"{len(covered):,}")
    logging.info("  Not covered segs:  %s", f"{len(notcov):,}")
    logging.info("  Covered length:    %s km", f"{cov_len/1000:,.1f}")
    logging.info("  Total length:      %s km", f"{total_len/1000:,.1f}")
    logging.info("  Coverage rate:     %s %%", f"{pct:,.2f}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
merge_coverage_optimized_progress.py

Fusionne 4 cartes de couverture (GeoPackage) en une couverture globale.
Optimisé RAM: dissolve par fichier + écriture intermédiaire + union finale.

✅ Ajouts:
- logs avec timestamps + durée par étape
- pourcentage d’avancement (fichier i/N)
- estimation simple du temps restant (ETA) basée sur la moyenne des étapes finies
- checkpoints (skip si sortie intermédiaire déjà calculée)
- option pour simplifier (souvent indispensable sur gros jeux)

Usage:
  python3 merge_coverage_optimized_progress.py
"""

import sys
import time
import logging
from pathlib import Path
from contextlib import contextmanager

import geopandas as gpd


# --- Réglages ---------------------------------------------------------------

INPUT_FILES = [
    "2025_T3_couv_Metropole_BOUY_4G_data.gpkg",
    "2025_T3_couv_Metropole_FREE_4G_data.gpkg",
    "2025_T3_couv_Metropole_OF_4G_data.gpkg",
    "2025_T3_couv_Metropole_SFR0_4G_data.gpkg",
]

OUT_DIR = Path(".")
TMP_DIR = OUT_DIR / "_tmp_union"
TMP_DIR.mkdir(exist_ok=True)

# Sorties
FINAL_OUT = OUT_DIR / "couverture_4G_totale.gpkg"

# Si True: écrit 1 gpkg dissous par opérateur (recommandé)
OUT_PER_OPERATOR = True

# Checkpoint: si True et que *_diss.gpkg existe déjà, on saute le dissolve
RESUME_IF_EXISTS = True

# Accélération / réduction complexité (mètres car EPSG:2154)
# 0 = pas de simplification (plus précis, plus lent)
SIMPLIFY_TOLERANCE_METERS = 50  # ex: 20, 50, 100 pour aller plus vite
PRESERVE_TOPOLOGY = True

# Nettoyage géométries invalides
FIX_INVALID_GEOMS = True

# ---------------------------------------------------------------------------


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@contextmanager
def timed_step(label: str):
    """Context manager pour mesurer et logger la durée d’une étape."""
    t0 = time.perf_counter()
    logging.info(f"▶ {label} — START")
    try:
        yield
    finally:
        dt = time.perf_counter() - t0
        logging.info(f"■ {label} — END ({dt:.1f}s)")


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


def pick_layer_name(gpkg_path: str) -> str | None:
    """Choisit une couche à lire (souvent une seule couche dans tes GPKG)."""
    layers = gpd.list_layers(gpkg_path)
    if layers is None or len(layers) == 0:
        return None
    return layers.loc[0, "name"]


def read_geometries(gpkg_path: str, layer: str | None) -> gpd.GeoDataFrame:
    """Lit le fichier et garde seulement la géométrie pour limiter la RAM."""
    if layer:
        gdf = gpd.read_file(gpkg_path, layer=layer)
    else:
        gdf = gpd.read_file(gpkg_path)
    return gdf[[gdf.geometry.name]].copy()


def fix_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Nettoie null/empty + tente de réparer les invalides."""
    geom_col = gdf.geometry.name
    g = gdf[geom_col]

    # enlève null/empty
    gdf = gdf[g.notna() & ~g.is_empty].copy()

    if FIX_INVALID_GEOMS:
        invalid = ~gdf.is_valid
        if invalid.any():
            # buffer(0) sur invalides seulement (coût limité)
            gdf.loc[invalid, geom_col] = gdf.loc[invalid, geom_col].buffer(0)

    return gdf


def simplify_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if SIMPLIFY_TOLERANCE_METERS and SIMPLIFY_TOLERANCE_METERS > 0:
        gdf[gdf.geometry.name] = gdf.geometry.simplify(
            SIMPLIFY_TOLERANCE_METERS,
            preserve_topology=PRESERVE_TOPOLOGY,
        )
    return gdf


def dissolve_to_single_geometry(gdf: gpd.GeoDataFrame):
    """Union shapely 2: union_all(); fallback unary_union."""
    try:
        return gdf.geometry.union_all()
    except Exception:
        return gdf.unary_union


def write_single_geom(path: Path, geom, crs):
    out = gpd.GeoDataFrame(geometry=[geom], crs=crs)
    out.to_file(path, driver="GPKG")


def main():
    setup_logger()
    global_t0 = time.perf_counter()

    # Vérifs fichiers
    for f in INPUT_FILES:
        if not Path(f).exists():
            logging.error(f"Fichier introuvable: {f}")
            sys.exit(1)

    n = len(INPUT_FILES)
    per_file_times = []
    dissolved_paths = []

    logging.info(f"Plan: {n} fichiers → dissolve/opérateur → union finale")
    logging.info(f"Simplify: {SIMPLIFY_TOLERANCE_METERS}m | Resume: {RESUME_IF_EXISTS} | Out: {FINAL_OUT}")

    for idx, f in enumerate(INPUT_FILES, start=1):
        op_name = Path(f).stem.replace("_data", "")
        tmp_out = TMP_DIR / f"{op_name}_diss.gpkg"

        pct = (idx - 1) / n * 100
        # ETA basée sur la moyenne des temps déjà observés (très simple)
        if per_file_times:
            avg = sum(per_file_times) / len(per_file_times)
            remaining = (n - (idx - 1)) * avg
            eta = human_eta(remaining)
        else:
            eta = "?"

        logging.info(f"=== [{idx}/{n}] {op_name} — avancement {pct:.0f}% — ETA ~ {eta} ===")

        # Checkpoint
        if OUT_PER_OPERATOR and RESUME_IF_EXISTS and tmp_out.exists() and tmp_out.stat().st_size > 0:
            logging.info(f"[{op_name}] Checkpoint trouvé → skip dissolve (utilise {tmp_out})")
            dissolved_paths.append(tmp_out)
            continue

        t_file = time.perf_counter()

        with timed_step(f"[{op_name}] lecture + préparation"):
            layer = pick_layer_name(f)
            if layer:
                logging.info(f"[{op_name}] layer sélectionné: {layer}")
            else:
                logging.info(f"[{op_name}] layer non détecté (lecture par défaut)")

            gdf = read_geometries(f, layer)
            crs = gdf.crs
            logging.info(f"[{op_name}] features: {len(gdf):,} | CRS: {crs}")

            gdf = fix_geometries(gdf)

            if SIMPLIFY_TOLERANCE_METERS and SIMPLIFY_TOLERANCE_METERS > 0:
                logging.info(f"[{op_name}] simplification: tol={SIMPLIFY_TOLERANCE_METERS}m")
                gdf = simplify_geometries(gdf)

        with timed_step(f"[{op_name}] union (dissolve)"):
            geom = dissolve_to_single_geometry(gdf)

        # libère RAM dès que possible
        del gdf

        if OUT_PER_OPERATOR:
            with timed_step(f"[{op_name}] écriture intermédiaire"):
                write_single_geom(tmp_out, geom, crs)
                dissolved_paths.append(tmp_out)
                logging.info(f"[{op_name}] écrit: {tmp_out} ({tmp_out.stat().st_size/1e6:.1f} MB)")
        else:
            dissolved_paths.append((geom, crs))

        dt_file = time.perf_counter() - t_file
        per_file_times.append(dt_file)
        logging.info(f"[{op_name}] total opérateur: {dt_file:.1f}s")

    # Union finale
    with timed_step("UNION FINALE (4 opérateurs)"):
        if OUT_PER_OPERATOR:
            geoms = []
            crs_final = None
            for p in dissolved_paths:
                gd = gpd.read_file(p)
                crs_final = gd.crs if crs_final is None else crs_final
                geoms.append(gd.geometry.iloc[0])

            gtmp = gpd.GeoSeries(geoms, crs=crs_final)
            try:
                final_geom = gtmp.union_all()
            except Exception:
                final_geom = gtmp.unary_union
        else:
            geoms = [x[0] for x in dissolved_paths]
            crs_final = dissolved_paths[0][1]
            gtmp = gpd.GeoSeries(geoms, crs=crs_final)
            try:
                final_geom = gtmp.union_all()
            except Exception:
                final_geom = gtmp.unary_union

    with timed_step("ÉCRITURE FINALE"):
        write_single_geom(FINAL_OUT, final_geom, crs_final)

    total_dt = time.perf_counter() - global_t0
    logging.info(f"✅ Terminé — temps total: {human_eta(total_dt)}")
    logging.info(f"📦 Sortie: {FINAL_OUT.resolve()}")

    if OUT_PER_OPERATOR:
        logging.info(f"🧩 Intermédiaires dans: {TMP_DIR.resolve()}")


if __name__ == "__main__":
    main()
"""
Clip habitat input layers to a study area (results saved, not loaded).
Run in QGIS: Plugins > Python Console > Show Editor > paste > Run.
"""
import processing
from qgis.core import QgsProject, QgsVectorLayer

# ---- settings: change these for another district ----
OUT_DIR = r"D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/M 01 - Urban Green for Heat Reduction/Python"
OVERLAY_NAME = "00_innenstadt_ost_boundary_25832"
TAG = "innenstadt_ost"
LOAD_LAYERS = False   # True = add results to the Layers panel

# input layer name in the Layers panel : output file name (without .gpkg)
JOBS = {
    "baumkataster — Layer1": f"H09_{TAG}_trees_4326",
    "H02a_dortmund_landuse_25832": f"H03_{TAG}_habitat_class",
    "H10b_dortmund_species_gbif_25832": f"H10a_{TAG}_species_gbif_25832",
    "ql_gbtpoint protected biotopes as points": f"H07d_{TAG}_protected_biotopes_point_25832",
    "ql_gbtpolygon protected biotopes as areas": f"H07d_{TAG}_protected_biotopes_polygon_25832",
    "ql_gbtpolyline protected biotopes as lines": f"H07d_{TAG}_protected_biotopes_line_25832",
    "vw_btpointproved Biotope types points": f"H07e_{TAG}_biotope_types_point_25832",
    "vw_btpolygonproved Biotope types (areas)": f"H07e_{TAG}_biotope_types_polygon_25832",
    "vw_btpolylineproved Biotope types (lines)": f"H07e_{TAG}_biotope_types_line_25832",
    "vw_lsgpolygonproved Landscape protection area less strict": f"H07b_{TAG}_landscape_protection_LSG_25832",
    "vw_nsgpolygonproved Nature reserve more strict": f"H07a_{TAG}_nature_reserves_NSG_25832",
    "water_gsk3e_gewkz_line_name": f"H08_{TAG}_streams_25832",
}

project = QgsProject.instance()


def get_layer(name):
    """Return the first layer with this name in the Layers panel, or None."""
    found = project.mapLayersByName(name)
    if not found:
        print(f"NOT FOUND  {name}")
        return None
    return found[0]


def report(path, name):
    """Open the saved file, print its feature count, load it only if LOAD_LAYERS."""
    lyr = QgsVectorLayer(path, name, "ogr")
    if not lyr.isValid():
        print(f"FAILED  {name}")
        return
    print(f"OK  {name}: {lyr.featureCount()} features")
    if LOAD_LAYERS:
        project.addMapLayer(lyr)


overlay = get_layer(OVERLAY_NAME)
if overlay is None:
    raise SystemExit("Boundary layer missing, nothing clipped.")

# 1. clip every input
for in_name, out_name in JOBS.items():
    src = get_layer(in_name)
    if src is None:
        continue
    result = processing.run("native:clip", {
        "INPUT": src,
        "OVERLAY": overlay,
        "OUTPUT": f"{OUT_DIR}/{out_name}.gpkg",
    })
    report(result["OUTPUT"], out_name)

# 2. reproject the trees from EPSG:4326 to EPSG:25832
result = processing.run("native:reprojectlayer", {
    "INPUT": f"{OUT_DIR}/H09_{TAG}_trees_4326.gpkg",
    "TARGET_CRS": "EPSG:25832",
    "OUTPUT": f"{OUT_DIR}/H09_{TAG}_trees_25832.gpkg",
})
report(result["OUTPUT"], f"H09_{TAG}_trees_25832")

print("Done.")
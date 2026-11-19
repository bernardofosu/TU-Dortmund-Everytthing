"""
Named OSM places in Innenstadt-Ost, grouped into the 7 M01 themes.
Run in QGIS: Plugins > Python Console > Show Editor > paste > Run.
"""
import processing
from collections import defaultdict
from qgis.core import QgsProject, QgsVectorLayer

# ---- settings ----
OUT_DIR = r"D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/M 01 - Urban Green for Heat Reduction/Habitat Map Innenstadt-Ost"
OSM_LAYER = "Dortmund_Multipolygons_Fixed"
BOUNDARY = "00_innenstadt_ost_boundary_25832"
LOAD_RESULT = True

FILTER = """
"name" IS NOT NULL AND (
  "amenity" IN ('hospital','clinic','doctors','nursing_home','social_facility','pharmacy',
                'place_of_worship','theatre','library','community_centre','arts_centre',
                'school','kindergarten','fountain')
  OR "leisure" IN ('park','garden','nature_reserve','sports_centre','pitch','playground',
                   'stadium','swimming_pool')
  OR "landuse" IN ('cemetery','allotments','forest','meadow','brownfield','construction',
                   'greenfield','railway','industrial','commercial','basin')
  OR "natural" IN ('wood','water','wetland')
  OR "tourism" IN ('museum','attraction')
  OR "historic" IS NOT NULL
)
"""

THEME = """
CASE
 WHEN "amenity" IN ('hospital','clinic','doctors','nursing_home','social_facility','pharmacy')
   OR "leisure" IN ('sports_centre','pitch','playground','stadium','swimming_pool') THEN 'Human Health'
 WHEN "leisure" IN ('park','garden') OR "landuse" IN ('cemetery','allotments') THEN 'Climate'
 WHEN "leisure" = 'nature_reserve' OR "natural" IN ('wood','wetland')
   OR "landuse" IN ('forest','meadow') THEN 'Species and Habitats'
 WHEN "natural" = 'water' OR "landuse" = 'basin' OR "amenity" = 'fountain' THEN 'Water'
 WHEN "landuse" IN ('brownfield','construction','greenfield') THEN 'Soil'
 WHEN "landuse" IN ('railway','industrial','commercial') THEN 'Human Infrastructures'
 WHEN "amenity" IN ('place_of_worship','theatre','library','community_centre','arts_centre',
                    'school','kindergarten')
   OR "tourism" IN ('museum','attraction') OR "historic" IS NOT NULL THEN 'Culture and Justice'
END
"""

project = QgsProject.instance()
osm = project.mapLayersByName(OSM_LAYER)[0]
boundary = project.mapLayersByName(BOUNDARY)[0]

# 1. clip to the district (in memory, the large step)
print("Clipping ... this can take a few minutes.")
clipped = processing.run("native:clip", {
    "INPUT": osm, "OVERLAY": boundary, "OUTPUT": "TEMPORARY_OUTPUT"})["OUTPUT"]

# 2. keep named places with a theme use
named = processing.run("native:extractbyexpression", {
    "INPUT": clipped, "EXPRESSION": FILTER, "OUTPUT": "TEMPORARY_OUTPUT"})["OUTPUT"]

# 3. add theme7 and save to file
out_path = f"{OUT_DIR}/H15b_innenstadt_ost_named_places_25832.gpkg"
result = processing.run("native:fieldcalculator", {
    "INPUT": named, "FIELD_NAME": "theme7", "FIELD_TYPE": 2, "FIELD_LENGTH": 40,
    "FORMULA": THEME, "OUTPUT": out_path})["OUTPUT"]

layer = QgsVectorLayer(result, "H15b_innenstadt_ost_named_places_25832", "ogr")
if LOAD_RESULT:
    project.addMapLayer(layer)

# 4. print names per theme (unique, sorted, with OSM type and area)
groups = defaultdict(dict)
for f in layer.getFeatures():
    theme = f["theme7"] or "(no theme)"
    kind = next((f[k] for k in ("amenity", "leisure", "landuse", "natural",
                                "tourism", "historic") if f[k]), "")
    area_ha = f.geometry().area() / 10000
    name = f["name"]
    # keep the largest piece if a name appears several times
    if name not in groups[theme] or area_ha > groups[theme][name][1]:
        groups[theme][name] = (kind, area_ha)

order = ["Climate", "Species and Habitats", "Water", "Soil", "Human Health",
         "Culture and Justice", "Human Infrastructures", "(no theme)"]
for theme in order:
    if theme not in groups:
        continue
    print(f"\n=== {theme} ({len(groups[theme])}) ===")
    for name, (kind, area_ha) in sorted(groups[theme].items()):
        print(f"  {name}  [{kind}, {area_ha:.2f} ha]")

print(f"\nSaved: {out_path}")
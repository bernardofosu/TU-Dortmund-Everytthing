# Check whether water and energy infrastructure exists in the OSM export
# for Innenstadt-Ost, and save what is found as I06 (energy) and I07 (water).
# Run: Plugins > Python Console > Show Editor > open > Run

import processing
from qgis.core import QgsProject, QgsVectorLayer

FOLDER = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/"
          "M 01 - Urban Green for Heat Reduction/Infrastructure Map Innenstadt-Ost/02_data_clipped")
BOUNDARY = "00_innenstadt_ost_boundary_25832"
OSM = ["Dortmund_Points_Fixed", "Dortmund_Lines_Fixed", "Dortmund_Multipolygons_Fixed"]

WATER = ["water_works", "pumping_station", "water_tower", "storage_tank",
         "wastewater_plant", "reservoir_covered", "water_well"]

def lyr(name):
    l = QgsProject.instance().mapLayersByName(name)
    if not l:
        raise Exception("Layer not found: " + name)
    return l[0]

def has(layer, field):
    return layer.fields().indexOf(field) >= 0

def water_expr(layer):
    parts = ['"other_tags" LIKE \'%"man_made"=>"{}"%\''.format(v) for v in WATER]
    if has(layer, "man_made"):
        parts.insert(0, '"man_made" IN ({})'.format(",".join("'%s'" % v for v in WATER)))
    return " OR ".join(parts)

def energy_expr(layer):
    parts = ['"other_tags" LIKE \'%"power"=>%\'',
             '"other_tags" LIKE \'%"generator:source"=>%\'']
    if has(layer, "power"):
        parts.insert(0, '"power" IS NOT NULL')
    return " OR ".join(parts)

import os
os.makedirs(FOLDER, exist_ok=True)   # creates 02_data_clipped if missing

boundary = lyr(BOUNDARY)
results = {}
for kind, make in (("I07_innenstadt_ost_water_infra_osm", water_expr),
                   ("I06_innenstadt_ost_energy_osm", energy_expr)):
    for name in OSM:
        src = lyr(name)
        geom = name.split("_")[1].lower()          # points / lines / multipolygons
        ext = processing.run("native:extractbyexpression",
                             {"INPUT": src, "EXPRESSION": make(src), "OUTPUT": "memory:"})["OUTPUT"]
        if ext.featureCount() == 0:
            print(kind, geom, ": 0 in Dortmund")
            continue
        rep = processing.run("native:reprojectlayer",
                             {"INPUT": ext, "TARGET_CRS": "EPSG:25832", "OUTPUT": "memory:"})["OUTPUT"]
        clip = processing.run("native:clip",
                              {"INPUT": rep, "OVERLAY": boundary, "OUTPUT": "memory:"})["OUTPUT"]
        n = clip.featureCount()
        print(kind, geom, ": %d in Dortmund, %d in Innenstadt-Ost" % (ext.featureCount(), n))
        if n:
            path = "%s/%s_%s_25832.gpkg" % (FOLDER, kind, geom)
            processing.run("native:savefeatures", {"INPUT": clip, "OUTPUT": path})
            QgsProject.instance().addMapLayer(QgsVectorLayer(path, "%s_%s_25832" % (kind, geom), "ogr"))
            for f in clip.getFeatures():
                tags = f["other_tags"] if has(clip, "other_tags") else ""
                print("   ", f["name"] if has(clip, "name") else "", "|", str(tags)[:120])

print("\nDone. Anything with 0 in Innenstadt-Ost: download with QuickOSM (steps in chat).")
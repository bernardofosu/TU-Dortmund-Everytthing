# Infrastructure map Innenstadt-Ost: build ALL data layers (no styling)
# I00 land use full, I01 roads+paths, I02 rail/tram, I03 parking, I04 stops (+300 m walk),
# I05 conflict with cold air paths, I08 buildings, I09 waste sites
# Run: Plugins > Python Console > Show Editor > open > Run
# Missing input layers are skipped with a message (copy them in, run again).

import os, processing
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes

FOLDER = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/"
          "M 01 - Urban Green for Heat Reduction/Infrastructure Map Innenstadt-Ost/02_data_clipped")
os.makedirs(FOLDER, exist_ok=True)

def find(part):
    for l in QgsProject.instance().mapLayers().values():
        if part.lower() in l.name().lower():
            return l
    return None

def has(layer, field):
    return layer.fields().indexOf(field) >= 0

def tagexpr(layer, key, values=None):
    """OSM key (=value) from its own column or from other_tags."""
    if values:
        ot = " OR ".join('"other_tags" LIKE \'%%"%s"=>"%s"%%\'' % (key, v) for v in values)
        if has(layer, key):
            ot = '"%s" IN (%s) OR ' % (key, ",".join("'%s'" % v for v in values)) + ot
    else:
        ot = '"other_tags" LIKE \'%%"%s"=>%%\'' % key
        if has(layer, key):
            ot = '"%s" IS NOT NULL OR ' % key + ot
    return ot

def run(alg, params):
    return processing.run(alg, params)["OUTPUT"]

def prep(layer, expr=None, polygons=False):
    """extract -> (fix) -> reproject 25832 -> clip to boundary, in memory"""
    x = run("native:extractbyexpression", {"INPUT": layer, "EXPRESSION": expr, "OUTPUT": "memory:"}) if expr else layer
    if polygons:
        x = run("native:fixgeometries", {"INPUT": x, "OUTPUT": "memory:"})
    x = run("native:reprojectlayer", {"INPUT": x, "TARGET_CRS": "EPSG:25832", "OUTPUT": "memory:"})
    return run("native:clip", {"INPUT": x, "OVERLAY": boundary, "OUTPUT": "memory:"})

def save(layer, name):
    path = "%s/%s.gpkg" % (FOLDER, name)
    run("native:savefeatures", {"INPUT": layer, "OUTPUT": path})
    QgsProject.instance().addMapLayer(QgsVectorLayer(path, name, "ogr"))
    return QgsProject.instance().mapLayersByName(name)[-1]

def km(l):  return round(sum(f.geometry().length() for f in l.getFeatures()) / 1000, 2)
def ha(l):  return round(sum(f.geometry().area() for f in l.getFeatures()) / 10000, 1)

boundary = find("00_innenstadt_ost_boundary_25832")
lines, points, polys = find("Dortmund_Lines_Fixed"), find("Dortmund_Points_Fixed"), find("Dortmund_Multipolygons_Fixed")
if not (boundary and lines and points and polys):
    raise Exception("Need boundary + Dortmund_Lines/Points/Multipolygons_Fixed in the project")
report = []

# I00 land use full (original ALKIS, nothing merged)
alkis = find("liegenschaftskataster")
if alkis:
    i00 = save(prep(alkis, polygons=True), "I00_innenstadt_ost_landuse_full_25832")
    report.append("I00 land use: %d parcels, %s ha" % (i00.featureCount(), ha(i00)))
else:
    report.append("I00 SKIPPED: copy 'liegenschaftskataster-nutzart' from the Habitat project")

# I01 roads + footpaths, with road_group
i01 = prep(lines, '"highway" IS NOT NULL')
i01 = run("native:fieldcalculator", {"INPUT": i01, "FIELD_NAME": "road_group", "FIELD_TYPE": 2, "FIELD_LENGTH": 30,
    "FORMULA": """CASE
 WHEN "highway" IN ('motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link') THEN 'Main road'
 WHEN "highway" IN ('tertiary','tertiary_link','residential','unclassified','service','road') THEN 'Local road'
 WHEN "highway" IN ('footway','pedestrian','path','steps','living_street','corridor') THEN 'Footpath'
 WHEN "highway" = 'cycleway' THEN 'Cycleway'
 WHEN "highway" IN ('track','bridleway') THEN 'Track'
 ELSE 'Other' END""", "OUTPUT": "memory:"})
i01 = save(i01, "I01_innenstadt_ost_roads_paths_25832")
for g in ("Main road", "Local road", "Footpath", "Cycleway", "Track"):
    sub = run("native:extractbyattribute", {"INPUT": i01, "FIELD": "road_group", "OPERATOR": 0, "VALUE": g, "OUTPUT": "memory:"})
    report.append("I01 %s: %s km" % (g, km(sub)))

# I02 rail + tram
i02 = save(prep(lines, tagexpr(lines, "railway", ["rail", "tram", "light_rail", "subway", "narrow_gauge"])),
           "I02_innenstadt_ost_rail_tram_25832")
report.append("I02 rail/tram: %s km" % km(i02))

# I03 parking areas
i03 = save(prep(polys, tagexpr(polys, "amenity", ["parking"]), polygons=True), "I03_innenstadt_ost_parking_25832")
report.append("I03 parking: %d areas, %s ha" % (i03.featureCount(), ha(i03)))

# I04 public transport stops + 300 m walking buffer
stop_expr = ("(" + tagexpr(points, "highway", ["bus_stop"]) + ") OR (" +
             tagexpr(points, "railway", ["tram_stop", "station", "halt"]) + ") OR (" +
             tagexpr(points, "public_transport", ["platform", "stop_position", "station"]) + ")")
i04 = save(prep(points, stop_expr), "I04_innenstadt_ost_stops_25832")
buf = run("native:buffer", {"INPUT": i04, "DISTANCE": 300, "SEGMENTS": 12, "DISSOLVE": True, "OUTPUT": "memory:"})
buf = run("native:clip", {"INPUT": buf, "OVERLAY": boundary, "OUTPUT": "memory:"})
i04b = save(buf, "I04b_innenstadt_ost_stop_walk_300m_25832")
report.append("I04 stops: %d; area within 300 m: %s ha" % (i04.featureCount(), ha(i04b)))

# I05 conflict: main roads + rail inside / crossing LANUK cold air paths
leit = find("PL_KY_KL_Leitbahn")
if leit:
    main = run("native:extractbyattribute", {"INPUT": i01, "FIELD": "road_group", "OPERATOR": 0, "VALUE": "Main road", "OUTPUT": "memory:"})
    grey = run("native:mergevectorlayers", {"LAYERS": [main, i02], "CRS": "EPSG:25832", "OUTPUT": "memory:"})
    lr = run("native:reprojectlayer", {"INPUT": leit, "TARGET_CRS": "EPSG:25832", "OUTPUT": "memory:"})
    if QgsWkbTypes.geometryType(lr.wkbType()) == QgsWkbTypes.PolygonGeometry:
        seg = run("native:clip", {"INPUT": grey, "OVERLAY": run("native:fixgeometries", {"INPUT": lr, "OUTPUT": "memory:"}), "OUTPUT": "memory:"})
        i05 = save(seg, "I05_innenstadt_ost_conflict_segments_25832")
        report.append("I05 main road/rail inside cold air paths: %s km" % km(i05))
    else:
        pts = run("native:lineintersections", {"INPUT": grey, "INTERSECT": lr, "OUTPUT": "memory:"})
        pts = run("native:clip", {"INPUT": pts, "OVERLAY": boundary, "OUTPUT": "memory:"})
        i05 = save(pts, "I05_innenstadt_ost_conflict_points_25832")
        report.append("I05 conflict points (main road/rail x cold air path): %d" % i05.featureCount())
else:
    report.append("I05 Leitbahn: not in project (no cold air paths in the district)")

# I05b conflict: main roads / rail within 100 m of LANUK air exchange points
aus = find("PL_KY_KL_Austausch") or find("Klimaanalyse-Planungshinweiskarte")
if aus and QgsWkbTypes.geometryType(aus.wkbType()) == QgsWkbTypes.PointGeometry:
    main = run("native:extractbyattribute", {"INPUT": i01, "FIELD": "road_group", "OPERATOR": 0, "VALUE": "Main road", "OUTPUT": "memory:"})
    grey = run("native:mergevectorlayers", {"LAYERS": [main, i02], "CRS": "EPSG:25832", "OUTPUT": "memory:"})
    ar = run("native:reprojectlayer", {"INPUT": aus, "TARGET_CRS": "EPSG:25832", "OUTPUT": "memory:"})
    ar = run("native:clip", {"INPUT": ar, "OVERLAY": run("native:buffer", {"INPUT": boundary, "DISTANCE": 100, "OUTPUT": "memory:"}), "OUTPUT": "memory:"})
    zone = run("native:buffer", {"INPUT": ar, "DISTANCE": 100, "SEGMENTS": 12, "DISSOLVE": True, "OUTPUT": "memory:"})
    seg = run("native:clip", {"INPUT": grey, "OVERLAY": zone, "OUTPUT": "memory:"})
    seg = run("native:clip", {"INPUT": seg, "OVERLAY": boundary, "OUTPUT": "memory:"})
    hit = run("native:extractbylocation", {"INPUT": ar, "PREDICATE": [0], "INTERSECT":
              run("native:buffer", {"INPUT": grey, "DISTANCE": 100, "OUTPUT": "memory:"}), "OUTPUT": "memory:"})
    i05b = save(seg, "I05b_innenstadt_ost_roads_at_air_exchange_25832")
    report.append("I05b air exchange points: %d; with main road/rail within 100 m: %d; road/rail length there: %s km"
                  % (ar.featureCount(), hit.featureCount(), km(i05b)))
else:
    report.append("I05b SKIPPED: copy 'PL_KY_KL_Austausch' (points) from the Climate project")

# I08 buildings
i08 = save(prep(polys, tagexpr(polys, "building"), polygons=True), "I08_innenstadt_ost_buildings_osm_25832")
report.append("I08 buildings: %d, footprint %s ha" % (i08.featureCount(), ha(i08)))

# I09 waste sites (EDG)
edg = find("edg-abfallentsorgung")
if edg:
    i09 = save(prep(edg), "I09_innenstadt_ost_waste_sites_25832")
    report.append("I09 waste sites: %d" % i09.featureCount())
else:
    report.append("I09 SKIPPED: 'edg-abfallentsorgung' not in project")

print("\n".join(["", "=== Infrastructure data, Innenstadt-Ost ==="] + report))
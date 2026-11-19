# Health map Innenstadt-Ost: heat-sensitive places + walking access to cool green (network analysis)
# Needs in project: 00_innenstadt_ost_boundary_25832, I00_innenstadt_ost_landuse_full_25832,
#                   I01_innenstadt_ost_roads_paths_25832, Dortmund_Points_Fixed, Dortmund_Multipolygons_Fixed
# Makes (in Health Map .../02_data_clipped):
#   HH01 heat-sensitive places (field place_type, walk_green)
#   HH02 cool green destinations (green >= 1 ha)
#   HH02b green entrances (where paths/roads meet the green edge)
#   HH03a walk 5 min (400 m) / HH03b walk 10 min (800 m) to green, along the network
#   HH04 main road exposure zone (50 m, assumption)
# Walking speed 4.8 km/h = 80 m per minute (assumption, state it on the map).
# Run: Plugins > Python Console > Show Editor > open > Run. Usually 1-3 minutes (one network run for all entrances).

import os, processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsField, QgsGeometry,
                       QgsFeatureRequest)
from qgis.PyQt.QtCore import QVariant

FOLDER = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/"
          "M 01 - Urban Green for Heat Reduction/Health Map Innenstadt-Ost/02_data_clipped")
os.makedirs(FOLDER, exist_ok=True)
MIN_GREEN_HA = 1.0
WALK = {"5min": 400, "10min": 800}
ROAD_BUFFER = 50

def find(part):
    for l in QgsProject.instance().mapLayers().values():
        if part.lower() in l.name().lower():
            return l
    raise Exception("Layer not found in project: " + part)

def run(alg, p):
    return processing.run(alg, p)["OUTPUT"]

def save(layer, name):
    path = "%s/%s.gpkg" % (FOLDER, name)
    # drop old fid values (duplicates after split/merge break the GeoPackage UNIQUE rule)
    drop = [f.name() for f in layer.fields() if f.name().lower() in ("fid", "ogc_fid")]
    if drop:
        layer = run("native:deletecolumn", {"INPUT": layer, "COLUMN": drop, "OUTPUT": "memory:"})
    if os.path.exists(path):
        try:
            for ext in ("", "-wal", "-shm"):
                if os.path.exists(path + ext):
                    os.remove(path + ext)
        except OSError:                      # file still locked by QGIS: write a new copy
            import time
            name = name + "_" + time.strftime("%H%M%S")
            path = "%s/%s.gpkg" % (FOLDER, name)
            report.append("NOTE: old file locked, saved as " + name)
    run("native:savefeatures", {"INPUT": layer, "OUTPUT": path})
    l = QgsVectorLayer(path, name, "ogr")
    QgsProject.instance().addMapLayer(l)
    return l

def has(l, f):
    return l.fields().indexOf(f) >= 0

def tag(l, key, vals):
    e = " OR ".join('"other_tags" LIKE \'%%"%s"=>"%s"%%\'' % (key, v) for v in vals)
    if has(l, key):
        e = '"%s" IN (%s) OR ' % (key, ",".join("'%s'" % v for v in vals)) + e
    return "(" + e + ")"

# remove earlier HH outputs (from a stopped run) so files can be rewritten
for l in list(QgsProject.instance().mapLayers().values()):
    if l.name().startswith(("HH01","HH02","HH03","HH04")):
        QgsProject.instance().removeMapLayer(l.id())
for fn in os.listdir(FOLDER):
    if fn.startswith(("HH01","HH02","HH03","HH04")):
        try:
            os.remove(os.path.join(FOLDER, fn))
        except OSError:
            pass

boundary = find("00_innenstadt_ost_boundary_25832")
i00 = find("I00_innenstadt_ost_landuse_full")
i01 = find("I01_innenstadt_ost_roads_paths")
pts = find("Dortmund_Points_Fixed")
polys = find("Dortmund_Multipolygons_Fixed")
report = []

# ---------- HH01 heat-sensitive places ----------
AMEN = ["hospital", "clinic", "doctors", "pharmacy", "nursing_home", "social_facility",
        "kindergarten", "childcare", "school"]
def places(layer, is_poly):
    e = tag(layer, "amenity", AMEN) + " OR " + tag(layer, "social_facility", ["nursing_home", "assisted_living"]) \
        + " OR " + tag(layer, "healthcare", ["hospital", "clinic", "doctor", "pharmacy"])
    x = run("native:extractbyexpression", {"INPUT": layer, "EXPRESSION": e, "OUTPUT": "memory:"})
    if is_poly:
        x = run("native:fixgeometries", {"INPUT": x, "OUTPUT": "memory:"})
        x = run("native:pointonsurface", {"INPUT": x, "ALL_PARTS": False, "OUTPUT": "memory:"})
    x = run("native:reprojectlayer", {"INPUT": x, "TARGET_CRS": "EPSG:25832", "OUTPUT": "memory:"})
    return run("native:clip", {"INPUT": x, "OVERLAY": boundary, "OUTPUT": "memory:"})

hh01 = run("native:mergevectorlayers", {"LAYERS": [places(pts, False), places(polys, True)],
                                        "CRS": "EPSG:25832", "OUTPUT": "memory:"})
TYPE = """CASE
 WHEN "other_tags" LIKE '%"nursing_home"%' OR "other_tags" LIKE '%"assisted_living"%' OR "other_tags" LIKE '%"social_facility"=>%' THEN 'Care home / social facility'
 WHEN "other_tags" LIKE '%"amenity"=>"hospital"%' OR "other_tags" LIKE '%"amenity"=>"clinic"%' OR "other_tags" LIKE '%"healthcare"=>"hospital"%' THEN 'Hospital / clinic'
 WHEN "other_tags" LIKE '%"amenity"=>"doctors"%' OR "other_tags" LIKE '%"healthcare"=>"doctor"%' THEN 'Doctor'
 WHEN "other_tags" LIKE '%"amenity"=>"pharmacy"%' OR "other_tags" LIKE '%"healthcare"=>"pharmacy"%' THEN 'Pharmacy'
 WHEN "other_tags" LIKE '%"amenity"=>"kindergarten"%' OR "other_tags" LIKE '%"amenity"=>"childcare"%' THEN 'Kindergarten / childcare'
 WHEN "other_tags" LIKE '%"amenity"=>"school"%' THEN 'School'
 ELSE 'Other health / care' END"""
if has(hh01, "amenity"):
    TYPE = TYPE.replace("CASE", """CASE
 WHEN "amenity" IN ('nursing_home','social_facility') THEN 'Care home / social facility'
 WHEN "amenity" IN ('hospital','clinic') THEN 'Hospital / clinic'
 WHEN "amenity" = 'doctors' THEN 'Doctor'
 WHEN "amenity" = 'pharmacy' THEN 'Pharmacy'
 WHEN "amenity" IN ('kindergarten','childcare') THEN 'Kindergarten / childcare'
 WHEN "amenity" = 'school' THEN 'School'""", 1)
hh01 = run("native:fieldcalculator", {"INPUT": hh01, "FIELD_NAME": "place_type", "FIELD_TYPE": 2,
                                      "FIELD_LENGTH": 40, "FORMULA": TYPE, "OUTPUT": "memory:"})

# ---------- HH02 cool green destinations (>= 1 ha) ----------
N = '"nutzart"'
GREEN = (N + " ILIKE '%Sport%' OR " + N + " ILIKE '%Erholung%' OR " + N + " ILIKE '%Friedhof%' OR "
         + N + " ILIKE '%Wald%' OR " + N + " ILIKE '%Gehoelz%' OR " + N + " ILIKE '%Gewaess%'")
g = run("native:extractbyexpression", {"INPUT": i00, "EXPRESSION": GREEN, "OUTPUT": "memory:"})
g = run("native:dissolve", {"INPUT": g, "OUTPUT": "memory:"})
g = run("native:multiparttosingleparts", {"INPUT": g, "OUTPUT": "memory:"})
g = run("native:fieldcalculator", {"INPUT": g, "FIELD_NAME": "area_ha", "FIELD_TYPE": 0, "FIELD_PRECISION": 2,
                                   "FORMULA": "round($area/10000,2)", "OUTPUT": "memory:"})
g = run("native:extractbyexpression", {"INPUT": g, "EXPRESSION": '"area_ha" >= %s' % MIN_GREEN_HA, "OUTPUT": "memory:"})
hh02 = save(g, "HH02_innenstadt_ost_cool_green_destinations_25832")
report.append("HH02 cool green areas >= %s ha: %d (%.1f ha)" % (MIN_GREEN_HA, hh02.featureCount(),
              sum(f["area_ha"] for f in hh02.getFeatures())))

# ---------- walking network (everything except motorways / trunk roads) ----------
net = run("native:extractbyexpression", {"INPUT": i01,
          "EXPRESSION": "\"highway\" NOT IN ('motorway','motorway_link','trunk','trunk_link')", "OUTPUT": "memory:"})

# ---------- access: paid / private green from HH06 (OSM fee / access tags) ----------
from qgis.analysis import (QgsVectorLayerDirector, QgsNetworkDistanceStrategy,
                           QgsGraphBuilder, QgsGraphAnalyzer)
from qgis.core import QgsFeature, QgsPointXY

def union_geom(l):
    gs = [f.geometry() for f in l.getFeatures()]
    return QgsGeometry.unaryUnion(gs) if gs else QgsGeometry()

paid_g = priv_g = QgsGeometry()
try:
    hh06 = run("native:reprojectlayer", {"INPUT": find("HH06_innenstadt_ost_paid_private_green"),
                                         "TARGET_CRS": "EPSG:25832", "OUTPUT": "memory:"})
    hh06 = run("native:fixgeometries", {"INPUT": hh06, "OUTPUT": "memory:"})
    paid = run("native:extractbyexpression", {"INPUT": hh06, "EXPRESSION": "\"other_tags\" LIKE '%\"fee\"=>\"yes\"%'", "OUTPUT": "memory:"})
    priv = run("native:extractbyexpression", {"INPUT": hh06, "EXPRESSION": "NOT (\"other_tags\" LIKE '%\"fee\"=>\"yes\"%')", "OUTPUT": "memory:"})
    paid_g, priv_g = union_geom(paid), union_geom(priv)
    report.append("HH06 paid areas: %d, private areas: %d" % (paid.featureCount(), priv.featureCount()))
except Exception as e:
    report.append("HH06 not used (%s): all green treated as free" % e)

# field 'access' on HH02: paid if mostly inside a fee area, else free (private parts cut out below)
hh02.startEditing()
hh02.addAttribute(QgsField("access", QVariant.String, len=10))
hh02.updateFields()
ia = hh02.fields().indexOf("access")
for f in hh02.getFeatures():
    g = f.geometry()
    share = g.intersection(paid_g).area() / g.area() if not paid_g.isEmpty() and g.area() else 0
    hh02.changeAttributeValue(f.id(), ia, "paid" if share > 0.5 else "free")
hh02.commitChanges()

# free green = green minus paid and private areas, still >= MIN_GREEN_HA
block = QgsGeometry.unaryUnion([x for x in (paid_g, priv_g) if not x.isEmpty()]) if not (paid_g.isEmpty() and priv_g.isEmpty()) else QgsGeometry()
free = QgsVectorLayer("Polygon?crs=EPSG:25832", "free", "memory")
fp = free.dataProvider()
fp.addAttributes([QgsField("area_ha", QVariant.Double)]); free.updateFields()
for f in hh02.getFeatures():
    g = f.geometry().difference(block) if not block.isEmpty() else f.geometry()
    for part in (g.asGeometryCollection() if g.isMultipart() else [g]):
        if part.area() / 10000 >= MIN_GREEN_HA:
            nf = QgsFeature(free.fields()); nf.setGeometry(part); nf.setAttributes([round(part.area()/10000, 2)])
            fp.addFeature(nf)
hh02f = save(free, "HH02c_innenstadt_ost_free_green_destinations_25832")
report.append("HH02c FREE green areas >= %s ha: %d (%.1f ha)" % (MIN_GREEN_HA, hh02f.featureCount(),
              sum(f["area_ha"] for f in hh02f.getFeatures())))

# ---------- walking network (everything except motorways / trunk roads) ----------
net = run("native:extractbyexpression", {"INPUT": i01,
          "EXPRESSION": "\"highway\" NOT IN ('motorway','motorway_link','trunk','trunk_link')", "OUTPUT": "memory:"})
director = QgsVectorLayerDirector(net, -1, "", "", "", QgsVectorLayerDirector.DirectionBoth)
director.addStrategy(QgsNetworkDistanceStrategy())

def walk_zones(green, tag, label):
    """entrances of 'green' -> one multi-source Dijkstra -> 5 / 10 min zones"""
    edge = run("native:polygonstolines", {"INPUT": green, "OUTPUT": "memory:"})
    ent = run("native:lineintersections", {"INPUT": net, "INTERSECT": edge, "OUTPUT": "memory:"})
    ent = run("native:deleteduplicategeometries", {"INPUT": ent, "OUTPUT": "memory:"})
    ents = save(ent, "HH02b%s_innenstadt_ost_%s_entrances_25832" % (tag, label))
    report.append("Entrances (%s green): %d" % (label, ents.featureCount()))
    builder = QgsGraphBuilder(net.crs(), True, 1.0)
    tied = director.makeGraph(builder, [f.geometry().asPoint() for f in ents.getFeatures()])
    graph = builder.graph()
    src = graph.addVertex(QgsPointXY(0, 0))
    for t in tied:
        vi = graph.findVertex(t)
        if vi >= 0:
            graph.addEdge(src, vi, [0.0])
    tree, cost = QgsGraphAnalyzer.dijkstra(graph, src, 0)
    out = {}
    for key, dist in WALK.items():
        mem = QgsVectorLayer("LineString?crs=EPSG:25832", "tmp", "memory")
        feats = []
        for e in range(graph.edgeCount()):
            ed = graph.edge(e); a, b = ed.fromVertex(), ed.toVertex()
            if a != src and b != src and 0 <= cost[a] <= dist and 0 <= cost[b] <= dist:
                ft = QgsFeature()
                ft.setGeometry(QgsGeometry.fromPolylineXY([graph.vertex(a).point(), graph.vertex(b).point()]))
                feats.append(ft)
        mem.dataProvider().addFeatures(feats)
        z = run("native:buffer", {"INPUT": mem, "DISTANCE": 30, "SEGMENTS": 3, "DISSOLVE": True, "OUTPUT": "memory:"})
        z = run("native:clip", {"INPUT": z, "OVERLAY": boundary, "OUTPUT": "memory:"})
        out[key] = save(z, "HH03%s_innenstadt_ost_walk_%s_to_%s_green_25832" % (tag + ("a" if key == "5min" else "b"), key, label))
        report.append("HH03 %s green, within %s (%d m): %.1f ha" % (label, key, dist,
                      sum(f.geometry().area() for f in out[key].getFeatures()) / 10000))
    return out

zones_all = walk_zones(hh02, "", "all")
zones_free = walk_zones(hh02f, "f", "free")

# ---------- tag each place: walk to ANY green and to FREE green ----------
def klass(p, ginside, z):
    return ("inside green" if p.intersects(ginside) else
            "<= 5 min" if p.intersects(z["5min"]) else
            "5-10 min" if p.intersects(z["10min"]) else "> 10 min")
ga = {k: union_geom(v) for k, v in zones_all.items()}
gf = {k: union_geom(v) for k, v in zones_free.items()}
g_all, g_free = union_geom(hh02), union_geom(hh02f)
hh01.startEditing()
for fld in ("walk_green", "walk_free"):
    hh01.addAttribute(QgsField(fld, QVariant.String, len=20))
hh01.updateFields()
i1, i2 = hh01.fields().indexOf("walk_green"), hh01.fields().indexOf("walk_free")
counts = {}
for f in hh01.getFeatures():
    p = f.geometry()
    v1, v2 = klass(p, g_all, ga), klass(p, g_free, gf)
    hh01.changeAttributeValue(f.id(), i1, v1)
    hh01.changeAttributeValue(f.id(), i2, v2)
    k = (f["place_type"], v1, v2)
    counts[k] = counts.get(k, 0) + 1
hh01.commitChanges()
# add the heat class (from 07_innenstadt_ost_climate_cat) to each place, prefix heat_
try:
    heat = find("07_innenstadt_ost_climate_cat")
    hh01 = run("native:joinattributesbylocation", {"INPUT": hh01, "PREDICATE": [0], "JOIN": heat,
               "JOIN_FIELDS": [], "METHOD": 2, "DISCARD_NONMATCHING": False, "PREFIX": "heat_",
               "OUTPUT": "memory:"})
    report.append("Heat class fields added to HH01: " +
                  ", ".join(f.name() for f in hh01.fields() if f.name().startswith("heat_")))
except Exception as e:
    report.append("Heat class not joined: %s" % e)
hh01s = save(hh01, "HH01_innenstadt_ost_heat_sensitive_places_25832")
report.append("HH01 heat-sensitive places: %d" % hh01s.featureCount())
report.append("   %-28s %-14s %-14s %s" % ("place type", "any green", "free green", "n"))
for (t, v1, v2), n in sorted(counts.items()):
    report.append("   %-28s %-14s %-14s %d" % (t, v1, v2, n))

# ---------- HH04 main road exposure zone ----------
main = run("native:extractbyexpression", {"INPUT": i01, "EXPRESSION": "\"road_group\" = 'Main road'", "OUTPUT": "memory:"})
mb = run("native:buffer", {"INPUT": main, "DISTANCE": ROAD_BUFFER, "SEGMENTS": 5, "DISSOLVE": True, "OUTPUT": "memory:"})
mb = run("native:clip", {"INPUT": mb, "OVERLAY": boundary, "OUTPUT": "memory:"})
hh04 = save(mb, "HH04_innenstadt_ost_main_road_zone_50m_25832")
report.append("HH04 area within %d m of a main road: %.1f ha" % (ROAD_BUFFER,
              sum(f.geometry().area() for f in hh04.getFeatures()) / 10000))

print("\n".join(["", "=== Health data, Innenstadt-Ost ==="] + report))
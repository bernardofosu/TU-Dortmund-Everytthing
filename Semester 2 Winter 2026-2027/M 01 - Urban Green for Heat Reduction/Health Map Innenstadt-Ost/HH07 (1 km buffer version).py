# HH07 (1 km buffer version): walking distance from HOMES inside Innenstadt-Ost to
#   (A) free green >= 1 ha, (B) any free cool place, (C) doctor / clinic, (D) pharmacy,
# with destinations AND streets taken from the district PLUS 1 km around it
# (so homes near the edge can use parks, doctors and pharmacies just outside the boundary).
# Homes, population and heat stay inside the district.
#
# Needs in the Health project:
#   00_innenstadt_ost_boundary_25832, I00_innenstadt_ost_landuse_full_25832 (homes),
#   I08_innenstadt_ost_buildings_osm_25832, liegenschaftskataster-nutzart (ALKIS for ALL Dortmund,
#   copy from the Habitat project), Dortmund_Lines_Fixed, Dortmund_Points_Fixed, Dortmund_Multipolygons_Fixed,
#   HH05 population, 07_innenstadt_ost_climate_cat
# Output: replaces HH07_innenstadt_ost_homes_walk_to_free_green_25832.gpkg (same fields as before).
#   The old district-only file is kept as ..._district_only.gpkg for comparison.
# After this: run HH07_show_A_and_B.py (views), then HH07_print_numbers.py (numbers).
# Run: Plugins > Python Console > Show Editor > open > Run (a few minutes).

import os, time, shutil, processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry,
                       QgsPointXY, QgsSpatialIndex, QgsRenderContext, QgsExpressionContext,
                       QgsExpressionContextUtils)
from qgis.analysis import (QgsVectorLayerDirector, QgsNetworkDistanceStrategy,
                           QgsGraphBuilder, QgsGraphAnalyzer)
from qgis.PyQt.QtCore import QVariant

FOLDER = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/"
          "M 01 - Urban Green for Heat Reduction/Health Map Innenstadt-Ost/02_data_clipped")
BUFFER_M = 1000
M_PER_MIN = 57.0           # 0.95 m/s, older people (Crabtree et al., 2014)
CLASS_M = (300, 500)      # WHO 300 m; BfN/UBA 500 m walk (Grunewald et al. 2025)
prj = QgsProject.instance()

def find(part, need=True, exact=False):
    for l in prj.mapLayers().values():
        if (l.name() == part) if exact else (part.lower() in l.name().lower()):
            return l
    if need:
        raise Exception("Layer not found in project: " + part)
    return None

def run(alg, p):
    p["OUTPUT"] = "memory:"
    return processing.run(alg, p)["OUTPUT"]

def has(l, f):
    return l.fields().indexOf(f) >= 0

def tag(l, key, vals):
    e = " OR ".join('"other_tags" LIKE \'%%"%s"=>"%s"%%\'' % (key, v) for v in vals)
    if has(l, key):
        e = '"%s" IN (%s) OR ' % (key, ",".join("'%s'" % v for v in vals)) + e
    return "(" + e + ")"

boundary = find("00_innenstadt_ost_boundary_25832")
i00 = find("I00_innenstadt_ost_landuse_full")
bld = find("I08_innenstadt_ost_buildings")
alkis = None
for l in prj.mapLayers().values():
    if "liegenschaftskataster" in l.name().lower() and not l.name().startswith("I00"):
        alkis = l
        break
if alkis is None:
    # not in the project: look for the ALKIS file anywhere in the M 01 folder and load it
    M01 = os.path.dirname(os.path.dirname(FOLDER))
    for root, _, files in os.walk(M01):
        for fn in files:
            if "liegenschaftskataster" in fn.lower() and fn.lower().endswith((".fgb", ".gpkg", ".shp", ".geojson")):
                alkis = QgsVectorLayer(os.path.join(root, fn), "liegenschaftskataster-nutzart", "ogr")
                print("ALKIS loaded from:", os.path.join(root, fn))
                break
        if alkis:
            break
if alkis is None or not alkis.isValid():
    raise Exception("ALKIS file (liegenschaftskataster...) not found in the M 01 folder. "
                    "Drag it into the Health project from the Browser panel, then run again.")
lines = find("Dortmund_Lines_Fixed")
pts = find("Dortmund_Points_Fixed")
polys = find("Dortmund_Multipolygons_Fixed")
pop = find("HH05_innenstadt_ost_population", need=False)
heat = find("07_innenstadt_ost_climate_cat", need=False, exact=True) or find("07_innenstadt_ost_climate_cat", need=False)
report = []

# ---------- study area + 1 km ----------
b25 = run("native:reprojectlayer", {"INPUT": boundary, "TARGET_CRS": "EPSG:25832"})
buf = run("native:buffer", {"INPUT": b25, "DISTANCE": BUFFER_M, "SEGMENTS": 16, "DISSOLVE": True})

def inbuf(layer, expr=None, poly=False):
    x = run("native:extractbyexpression", {"INPUT": layer, "EXPRESSION": expr}) if expr else layer
    if poly:
        x = run("native:fixgeometries", {"INPUT": x})
    x = run("native:reprojectlayer", {"INPUT": x, "TARGET_CRS": "EPSG:25832"})
    return run("native:clip", {"INPUT": x, "OVERLAY": buf})

# ---------- homes (inside the district only, as before) ----------
N = '"nutzart"'
housing = run("native:extractbyexpression", {"INPUT": i00, "EXPRESSION": N + " ILIKE '%Wohnbau%' OR " + N + " ILIKE '%gemischt%'"})
b = run("native:reprojectlayer", {"INPUT": bld, "TARGET_CRS": "EPSG:25832"})
b = run("native:fixgeometries", {"INPUT": b})
b = run("native:fieldcalculator", {"INPUT": b, "FIELD_NAME": "foot_m2", "FIELD_TYPE": 0, "FIELD_PRECISION": 1,
                                   "FORMULA": "round($area,1)"})
c = run("native:pointonsurface", {"INPUT": b, "ALL_PARTS": False})
homes = run("native:extractbylocation", {"INPUT": c, "PREDICATE": [0], "INTERSECT": housing})
report.append("Homes (inside district): %d" % homes.featureCount())

# ---------- walking network: district + 1 km, no motorways / trunk roads ----------
net = inbuf(lines, "\"highway\" IS NOT NULL AND \"highway\" NOT IN ('motorway','motorway_link','trunk','trunk_link')")
director = QgsVectorLayerDirector(net, -1, "", "", "", QgsVectorLayerDirector.DirectionBoth)
director.addStrategy(QgsNetworkDistanceStrategy())
report.append("Street network (district + %d m): %.0f km" % (BUFFER_M, sum(f.geometry().length() for f in net.getFeatures()) / 1000))

# ---------- green: ALKIS (all Dortmund) within buffer, minus OSM paid / private ----------
GREEN = (N + " ILIKE '%Sport%' OR " + N + " ILIKE '%Erholung%' OR " + N + " ILIKE '%Friedhof%' OR "
         + N + " ILIKE '%Wald%' OR " + N + " ILIKE '%Gehoelz%' OR " + N + " ILIKE '%Gewaess%'")
g = inbuf(alkis, GREEN, poly=True)
g = run("native:dissolve", {"INPUT": g})
block_expr = tag(polys, "fee", ["yes"]) + " OR " + tag(polys, "access", ["private", "no"])
block = inbuf(polys, block_expr, poly=True)
if block.featureCount():
    g = run("native:difference", {"INPUT": g, "OVERLAY": block})
g = run("native:multiparttosingleparts", {"INPUT": g})
greenA = run("native:extractbyexpression", {"INPUT": g, "EXPRESSION": "$area >= 10000"})
greenB = run("native:extractbyexpression", {"INPUT": g, "EXPRESSION": "$area >= 1000"})

def entrance_points(poly):
    edge = run("native:polygonstolines", {"INPUT": poly})
    ent = run("native:lineintersections", {"INPUT": net, "INTERSECT": edge})
    p = [f.geometry().asPoint() for f in ent.getFeatures()]
    p += [f.geometry().pointOnSurface().asPoint() for f in poly.getFeatures()]
    return p

pts_A = entrance_points(greenA)
pts_B = entrance_points(greenB)
fount = inbuf(pts, tag(pts, "amenity", ["fountain", "drinking_water"]))
pts_B += [f.geometry().asPoint() for f in fount.getFeatures()]
report.append("A free green >= 1 ha (district + %d m): %d areas" % (BUFFER_M, greenA.featureCount()))
report.append("B free green >= 0.1 ha: %d areas + %d fountains / drinking water" % (greenB.featureCount(), fount.featureCount()))

# ---------- C doctor / clinic, D pharmacy within buffer ----------
def place_pts(expr):
    out = []
    for layer, is_poly in ((pts, False), (polys, True)):
        e = expr(layer)
        x = run("native:extractbyexpression", {"INPUT": layer, "EXPRESSION": e})
        if is_poly:
            x = run("native:fixgeometries", {"INPUT": x})
            x = run("native:pointonsurface", {"INPUT": x, "ALL_PARTS": False})
        x = run("native:reprojectlayer", {"INPUT": x, "TARGET_CRS": "EPSG:25832"})
        x = run("native:clip", {"INPUT": x, "OVERLAY": buf})
        out += [f.geometry().asPoint() for f in x.getFeatures()]
    return out

pts_C = place_pts(lambda l: tag(l, "amenity", ["doctors", "clinic", "hospital"]) + " OR " +
                            tag(l, "healthcare", ["doctor", "clinic", "hospital"]))
pts_D = place_pts(lambda l: tag(l, "amenity", ["pharmacy"]) + " OR " + tag(l, "healthcare", ["pharmacy"]))
report.append("C doctor / clinic: %d   D pharmacy: %d  (district + %d m)" % (len(pts_C), len(pts_D), BUFFER_M))

# ---------- one multi-source Dijkstra per destination type ----------
def network_costs(points):
    builder = QgsGraphBuilder(net.crs(), True, 1.0)
    tied = director.makeGraph(builder, points)
    gr = builder.graph()
    s0 = gr.addVertex(QgsPointXY(0, 0))
    for t in tied:
        vi = gr.findVertex(t)
        if vi >= 0:
            gr.addEdge(s0, vi, [0.0])
    tree, cst = QgsGraphAnalyzer.dijkstra(gr, s0, 0)
    idx = QgsSpatialIndex()
    for v in range(gr.vertexCount()):
        if v != s0 and cst[v] >= 0:
            f = QgsFeature(v); f.setGeometry(QgsGeometry.fromPointXY(gr.vertex(v).point())); idx.addFeature(f)
    return gr, cst, idx

KEYS = ("A", "B", "C", "D")
NETS = {"A": network_costs(pts_A), "B": network_costs(pts_B), "C": network_costs(pts_C), "D": network_costs(pts_D)}

def walk(p, gr, cst, idx):
    near = idx.nearestNeighbor(p, 1)
    if not near:
        return None
    v = near[0]
    return cst[v] + gr.vertex(v).point().distance(p)

CLASSES = ("<= 300 m", "300-500 m", "> 500 m")   # WHO 300 m; BfN/UBA 500 m walk (Grunewald et al. 2025)
def klass(m):
    return CLASSES[0] if m <= 300 else CLASSES[1] if m <= 500 else CLASSES[2]

# ---------- population share per home (unchanged method) ----------
pop_of = {}
if pop:
    cells = {f.id(): (f.geometry(), f["population"] or 0) for f in pop.getFeatures()}
    cidx = QgsSpatialIndex(pop.getFeatures())
    members = {}
    for h in homes.getFeatures():
        p = h.geometry()
        for cid in cidx.intersects(p.boundingBox()):
            if cells[cid][0].contains(p):
                members.setdefault(cid, []).append((h.id(), h["foot_m2"] or 1))
                break
    for cid, lst in members.items():
        tot = sum(a for _, a in lst) or 1
        for hid, a in lst:
            pop_of[hid] = cells[cid][1] * a / tot

# ---------- heat label per home (unchanged method) ----------
heat_of = {}
if heat:
    hf = "climate_cat" if heat.fields().indexOf("climate_cat") >= 0 else heat.fields()[heat.fields().count() - 1].name()
    r = heat.renderer().clone()
    ctx = QgsRenderContext()
    ectx = QgsExpressionContext(); ectx.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(heat))
    ctx.setExpressionContext(ectx)
    key2label = {it.ruleKey(): it.label() for it in r.legendSymbolItems()}
    r.startRender(ctx, heat.fields())
    hgeo = {}
    for f in heat.getFeatures():
        ectx.setFeature(f)
        lab = ", ".join(key2label.get(k, "") for k in r.legendKeysForFeature(f, ctx) if key2label.get(k, ""))
        hgeo[f.id()] = (f.geometry(), lab or str(f[hf]))
    r.stopRender(ctx)
    hidx = QgsSpatialIndex(heat.getFeatures())
    for h in homes.getFeatures():
        p = h.geometry()
        for fid in hidx.intersects(p.boundingBox()):
            if hgeo[fid][0].contains(p):
                heat_of[h.id()] = hgeo[fid][1]
                break

# ---------- build the homes layer (same fields as the old HH07) ----------
out = QgsVectorLayer("Point?crs=EPSG:25832", "tmp", "memory")
pr = out.dataProvider()
flds = []
for k in KEYS:
    flds += [QgsField("walk_m_" + k, QVariant.Double), QgsField("walk_min_" + k, QVariant.Double),
             QgsField("class_" + k, QVariant.String, len=12)]
flds += [QgsField("pop_est", QVariant.Double), QgsField("heat_class", QVariant.String, len=40),
         QgsField("foot_m2", QVariant.Double)]
pr.addAttributes(flds); out.updateFields()
feats = []
for h in homes.getFeatures():
    p = h.geometry().asPoint()
    vals, ok = [], True
    for k in KEYS:
        d = walk(p, *NETS[k])
        if d is None:
            ok = False; break
        vals += [round(d, 0), round(d / M_PER_MIN, 1), klass(d)]
    if not ok:
        continue
    nf = QgsFeature(out.fields()); nf.setGeometry(h.geometry())
    nf.setAttributes(vals + [round(pop_of.get(h.id(), 0.0), 2), heat_of.get(h.id(), ""), h["foot_m2"]])
    feats.append(nf)
pr.addFeatures(feats)

# ---------- save: keep old file as _district_only, replace HH07 ----------
path = FOLDER + "/HH07_innenstadt_ost_homes_walk_to_free_green_25832.gpkg"
for l in [l for l in prj.mapLayers().values() if l.source().split("|")[0].replace("\\", "/") == path]:
    prj.removeMapLayer(l.id())
if os.path.exists(path):
    try:
        shutil.copy(path, path.replace(".gpkg", "_district_only.gpkg"))
        os.remove(path)
    except OSError:
        path = path.replace(".gpkg", "_buf1km_%s.gpkg" % time.strftime("%H%M%S"))
processing.run("native:savefeatures", {"INPUT": out, "OUTPUT": path})
prj.addMapLayer(QgsVectorLayer(path, "HH07_innenstadt_ost_homes_walk_to_free_green_25832", "ogr"))

# ---------- report ----------
P = lambda fs: sum(f["pop_est"] or 0 for f in fs)
T = P(feats) or 1
report.append("")
report.append("%-24s %10s %10s %10s" % ("Destination", *CLASSES))
NAMES = {"A": "free green >= 1 ha", "B": "any free cool place", "C": "doctor / clinic", "D": "pharmacy"}
for k in KEYS:
    row = [100 * P([f for f in feats if f["class_" + k] == c]) / T for c in CLASSES]
    report.append("%-24s %9.0f%% %9.0f%% %9.0f%%" % (k + " " + NAMES[k], *row))
hot = [f for f in feats if any(x in (f["heat_class"] or "") for x in ("Strong", "Extreme"))]
report.append("")
report.append("People in strong or extreme heat: %.0f" % P(hot))
for k, lim in (("A", 300), ("B", 300), ("C", 500), ("D", 500)):
    report.append("   of them > %d m from %-20s %.0f" % (lim, NAMES[k], P([f for f in hot if f["walk_m_" + k] > lim])))
report.append("")
report.append("Saved: " + path)
report.append("Next: run HH07_show_A_and_B.py (views). HH08 / HH09 must be run again too.")
print("\n".join(["", "=== HH07 with destinations and streets in district + %d m ===" % BUFFER_M] + report))
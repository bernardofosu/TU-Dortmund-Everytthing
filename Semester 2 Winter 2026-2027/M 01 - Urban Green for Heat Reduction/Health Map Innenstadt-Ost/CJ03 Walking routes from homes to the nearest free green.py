# CJ03 Walking routes from homes to the nearest free green >= 1 ha (same method as HH07, 1 km buffer).
# Every home walks its shortest street route to the nearest green entrance; each street segment gets
# the number of residents whose route uses it. Thick lines = the routes most people depend on.
# Run in the "Culture Map Ost" project. Needs loaded: 00_innenstadt_ost_boundary_25832,
#   Dortmund_Lines_Fixed, Dortmund_Multipolygons_Fixed, liegenschaftskataster-nutzart (ALKIS).
# Reads the HH07 homes file from disk (pop_est). Changes no existing layer.
# Output: CJ03_innenstadt_ost_walking_routes_to_green_25832.gpkg in the project folder.
# Run: Plugins > Python Console > Show Editor > open > Run (a few minutes).

import os, time, processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY,
                       QgsCoordinateTransform, QgsVectorFileWriter, QgsLineSymbol,
                       QgsGraduatedSymbolRenderer, QgsRendererRange)
from qgis.analysis import QgsVectorLayerDirector, QgsNetworkDistanceStrategy, QgsGraphBuilder, QgsGraphAnalyzer
from qgis.PyQt.QtCore import QVariant

BASE = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/"
        "M 01 - Urban Green for Heat Reduction")
BUFFER_M = 1000
prj = QgsProject.instance()

def find(test, what):
    for l in prj.mapLayers().values():
        if l.type() == l.VectorLayer and test(l):
            return l
    raise Exception(what + " not found in the project")

def run(alg, p):
    p["OUTPUT"] = "memory:"
    return processing.run(alg, p)["OUTPUT"]

def tag(l, key, vals):
    e = " OR ".join('"other_tags" LIKE \'%%"%s"=>"%s"%%\'' % (key, v) for v in vals)
    if l.fields().indexOf(key) >= 0:
        e = '"%s" IN (%s) OR ' % (key, ",".join("'%s'" % v for v in vals)) + e
    return "(" + e + ")"

bnd = find(lambda l: l.name() == "00_innenstadt_ost_boundary_25832", "Boundary")
lines = find(lambda l: l.name() == "Dortmund_Lines_Fixed", "Dortmund_Lines_Fixed")
polys = find(lambda l: l.name() == "Dortmund_Multipolygons_Fixed", "Dortmund_Multipolygons_Fixed")
alkis = find(lambda l: "liegenschaftskataster" in l.name().lower(), "ALKIS (liegenschaftskataster-nutzart)")

hits = []
for root, _, files in os.walk(BASE):
    for fn in files:
        f = fn.lower()
        if f.endswith("walk_to_free_green_25832.gpkg") and "district_only" not in f:
            hits.append(os.path.join(root, fn))
if not hits:
    raise Exception("HH07 homes file not found under " + BASE)
hits.sort(key=os.path.getmtime)
homes = QgsVectorLayer(hits[-1], "HH07 (read only)", "ogr")
print("HH07 homes:", hits[-1])

# ---------- network and green (as in HH07) ----------
b25 = run("native:reprojectlayer", {"INPUT": bnd, "TARGET_CRS": "EPSG:25832"})
buf = run("native:buffer", {"INPUT": b25, "DISTANCE": BUFFER_M, "SEGMENTS": 16, "DISSOLVE": True})

def inbuf(layer, expr=None, poly=False):
    x = run("native:extractbyexpression", {"INPUT": layer, "EXPRESSION": expr}) if expr else layer
    if poly:
        x = run("native:fixgeometries", {"INPUT": x})
    x = run("native:reprojectlayer", {"INPUT": x, "TARGET_CRS": "EPSG:25832"})
    return run("native:clip", {"INPUT": x, "OVERLAY": buf})

net = inbuf(lines, "\"highway\" IS NOT NULL AND \"highway\" NOT IN ('motorway','motorway_link','trunk','trunk_link')")
N = '"nutzart"'
GREEN = (N + " ILIKE '%Sport%' OR " + N + " ILIKE '%Erholung%' OR " + N + " ILIKE '%Friedhof%' OR "
         + N + " ILIKE '%Wald%' OR " + N + " ILIKE '%Gehoelz%' OR " + N + " ILIKE '%Gewaess%'")
g = run("native:dissolve", {"INPUT": inbuf(alkis, GREEN, poly=True)})
block = inbuf(polys, tag(polys, "fee", ["yes"]) + " OR " + tag(polys, "access", ["private", "no"]), poly=True)
if block.featureCount():
    g = run("native:difference", {"INPUT": g, "OVERLAY": block})
g = run("native:multiparttosingleparts", {"INPUT": g})
greenA = run("native:extractbyexpression", {"INPUT": g, "EXPRESSION": "$area >= 10000"})
edge = run("native:polygonstolines", {"INPUT": greenA})
ent = run("native:lineintersections", {"INPUT": net, "INTERSECT": edge})
targets = [f.geometry().asPoint() for f in ent.getFeatures()]
targets += [f.geometry().pointOnSurface().asPoint() for f in greenA.getFeatures()]

tr = QgsCoordinateTransform(homes.crs(), net.crs(), prj)
H = [(tr.transform(f.geometry().asPoint()), f["pop_est"] or 0) for f in homes.getFeatures()]
H = [(p, w) for p, w in H if w > 0]
print("Homes: %d   green entrances: %d" % (len(H), len(targets)))

# ---------- one graph: green entrances + homes tied in, multi-source Dijkstra ----------
director = QgsVectorLayerDirector(net, -1, "", "", "", QgsVectorLayerDirector.DirectionBoth)
director.addStrategy(QgsNetworkDistanceStrategy())
builder = QgsGraphBuilder(net.crs(), True, 1.0)
tied = director.makeGraph(builder, targets + [p for p, _ in H])
gr = builder.graph()
s0 = gr.addVertex(QgsPointXY(0, 0))
for t in tied[:len(targets)]:
    vi = gr.findVertex(t)
    if vi >= 0:
        gr.addEdge(s0, vi, [0.0])
tree, cost = QgsGraphAnalyzer.dijkstra(gr, s0, 0)

# walk each home back to its green, adding its residents to every segment on the way
use = {}
for (p, w), t in zip(H, tied[len(targets):]):
    v = gr.findVertex(t)
    if v < 0 or cost[v] < 0:
        continue
    while tree[v] != -1:
        e = gr.edge(tree[v])
        u = e.fromVertex()
        if u == s0:
            break
        key = (min(u, v), max(u, v))
        use[key] = use.get(key, 0) + w
        v = u

# ---------- write the route lines ----------
mem = QgsVectorLayer("LineString?crs=EPSG:25832", "r", "memory")
pr = mem.dataProvider()
pr.addAttributes([QgsField("residents", QVariant.Double)])
mem.updateFields()
feats = []
for (a, b), w in use.items():
    f = QgsFeature(mem.fields())
    f.setGeometry(QgsGeometry.fromPolylineXY([gr.vertex(a).point(), gr.vertex(b).point()]))
    f.setAttributes([round(w, 0)])
    feats.append(f)
pr.addFeatures(feats)
mem = run("native:dissolve", {"INPUT": mem, "FIELD": ["residents"]})
mem = run("native:multiparttosingleparts", {"INPUT": mem})

OUT = prj.homePath() or BASE
name = "CJ03_innenstadt_ost_walking_routes_to_green_25832"
path = os.path.join(OUT, name + ".gpkg")
for old in [l for l in prj.mapLayers().values() if l.source().split("|")[0] == path]:
    prj.removeMapLayer(old.id())
if os.path.exists(path):
    try:
        os.remove(path)
    except OSError:
        path = os.path.join(OUT, name + time.strftime("_%H%M%S") + ".gpkg")
processing.run("native:savefeatures", {"INPUT": mem, "OUTPUT": path})
L = QgsVectorLayer(path, "CJ03 walking routes to green (residents)", "ogr")
prj.addMapLayer(L)

# ---------- style: thicker = more residents ----------
CL = [(0, 100, 0.3, "< 100"), (100, 500, 0.7, "100 - 500"), (500, 2000, 1.3, "500 - 2,000"),
      (2000, 1e9, 2.2, "> 2,000")]
rng = [QgsRendererRange(lo, hi, QgsLineSymbol.createSimple({"color": "#1a7837", "width": str(wd),
       "capstyle": "round", "joinstyle": "round"}), lab + " residents") for lo, hi, wd, lab in CL]
L.setRenderer(QgsGraduatedSymbolRenderer("residents", rng))
L.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(L.id())

print("\nRoute segments: %d" % L.featureCount())
print("Most used segments (residents):", sorted((f["residents"] for f in L.getFeatures()), reverse=True)[:5])
print("Saved:", path)
# CJ04 Walking barriers for older and disabled people on the routes to green (Innenstadt-Ost)
# Barriers from OpenStreetMap (Dortmund_Lines_Fixed):
#   Steps               highway=steps
#   Not wheelchair      wheelchair=no or wheelchair=limited
#   Rough surface       surface = gravel, fine_gravel, pebblestone, cobblestone, sett, unhewn_cobblestone,
#                       unpaved, dirt, earth, ground, grass, sand, mud, woodchips
# Benches (rest points): amenity=bench (Dortmund_Points_Fixed)
# Routes: same as HH07 / CJ03 (shortest street walk to the nearest free green >= 1 ha, 1 km buffer).
# For every home it checks whether its route crosses a barrier, and counts residents and residents 65+.
# Run in the "Culture Map Ost" project. Needs loaded: 00_innenstadt_ost_boundary_25832, Dortmund_Lines_Fixed,
#   Dortmund_Points_Fixed, Dortmund_Multipolygons_Fixed, liegenschaftskataster-nutzart (ALKIS).
# Reads the HH09 homes file (pop_est, old65) from disk. Changes no existing layer.
# Output (project folder): CJ04a barriers, CJ04b benches, CJ04c homes with barrier on route.
# Limit: OSM tags are incomplete; a street without tags is not proof that it is barrier-free.
# Run: Plugins > Python Console > Show Editor > open > Run (a few minutes).

import os, time, processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY,
                       QgsCoordinateTransform, QgsSpatialIndex, QgsLineSymbol, QgsMarkerSymbol,
                       QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsSingleSymbolRenderer)
from qgis.analysis import QgsVectorLayerDirector, QgsNetworkDistanceStrategy, QgsGraphBuilder, QgsGraphAnalyzer
from qgis.PyQt.QtCore import QVariant

BASE = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/"
        "M 01 - Urban Green for Heat Reduction")
BUFFER_M = 1000
BENCH_NEAR_ROUTE_M = 20
ROUGH = ["gravel", "fine_gravel", "pebblestone", "cobblestone", "sett", "unhewn_cobblestone", "unpaved",
         "dirt", "earth", "ground", "grass", "sand", "mud", "woodchips"]
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
pts = find(lambda l: l.name() == "Dortmund_Points_Fixed", "Dortmund_Points_Fixed")
polys = find(lambda l: l.name() == "Dortmund_Multipolygons_Fixed", "Dortmund_Multipolygons_Fixed")
alkis = find(lambda l: "liegenschaftskataster" in l.name().lower(), "ALKIS (liegenschaftskataster-nutzart)")

def newest(test, what):
    hits = [os.path.join(r, f) for r, _, fs in os.walk(BASE) for f in fs if test(f.lower())]
    if not hits:
        raise Exception(what + " not found under " + BASE)
    return sorted(hits, key=os.path.getmtime)[-1]

hp = newest(lambda f: f.startswith("hh09") and f.endswith("homes_older_people_25832.gpkg"), "HH09 homes file")
homes = QgsVectorLayer(hp, "HH09 (read only)", "ogr")
print("HH09 homes:", hp)

def save(layer, name, title):
    OUT = prj.homePath() or BASE
    path = os.path.join(OUT, name + ".gpkg")
    for old in [l for l in prj.mapLayers().values() if l.source().split("|")[0] == path]:
        prj.removeMapLayer(old.id())
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            path = os.path.join(OUT, name + time.strftime("_%H%M%S") + ".gpkg")
    processing.run("native:savefeatures", {"INPUT": layer, "OUTPUT": path})
    L = QgsVectorLayer(path, title, "ogr")
    prj.addMapLayer(L)
    print("Saved:", path)
    return L

# ---------- area, network, green (as in HH07) ----------
b25 = run("native:reprojectlayer", {"INPUT": bnd, "TARGET_CRS": "EPSG:25832"})
buf = run("native:buffer", {"INPUT": b25, "DISTANCE": BUFFER_M, "SEGMENTS": 16, "DISSOLVE": True})

def inbuf(layer, expr=None, poly=False, area=None):
    x = run("native:extractbyexpression", {"INPUT": layer, "EXPRESSION": expr}) if expr else layer
    if poly:
        x = run("native:fixgeometries", {"INPUT": x})
    x = run("native:reprojectlayer", {"INPUT": x, "TARGET_CRS": "EPSG:25832"})
    return run("native:clip", {"INPUT": x, "OVERLAY": area or buf})

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
ent = run("native:lineintersections", {"INPUT": net, "INTERSECT": run("native:polygonstolines", {"INPUT": greenA})})
targets = [f.geometry().asPoint() for f in ent.getFeatures()]
targets += [f.geometry().pointOnSurface().asPoint() for f in greenA.getFeatures()]

# ---------- CJ04a barriers ----------
TYPES = [("Steps", lambda l: tag(l, "highway", ["steps"])),
         ("Not wheelchair accessible", lambda l: tag(l, "wheelchair", ["no", "limited"])),
         ("Rough surface", lambda l: tag(l, "surface", ROUGH))]
bar = QgsVectorLayer("LineString?crs=EPSG:25832", "b", "memory")
bp = bar.dataProvider()
bp.addAttributes([QgsField("barrier", QVariant.String), QgsField("length_m", QVariant.Double)])
bar.updateFields()
for lab, ex in TYPES:
    x = run("native:extractbyexpression", {"INPUT": net, "EXPRESSION": ex(net)})
    x = run("native:multiparttosingleparts", {"INPUT": x})
    for f in x.getFeatures():
        nf = QgsFeature(bar.fields()); nf.setGeometry(f.geometry())
        nf.setAttributes([lab, round(f.geometry().length(), 1)]); bp.addFeatures([nf])
bidx = QgsSpatialIndex(bar.getFeatures())      # routes use all barriers (district + 1 km)
bgeo = {f.id(): (f.geometry(), f["barrier"]) for f in bar.getFeatures()}

# ---------- CJ04b benches ----------
bench = inbuf(pts, tag(pts, "amenity", ["bench"]))

# ---------- routes: one multi-source Dijkstra, homes tied into the same graph ----------
tr = QgsCoordinateTransform(homes.crs(), net.crs(), prj)
has65 = homes.fields().indexOf("old65") >= 0
H = []
for f in homes.getFeatures():
    w = f["pop_est"] or 0
    if w > 0:
        H.append((f.geometry(), tr.transform(f.geometry().asPoint()), w, (f["old65"] or 0) if has65 else 0))
print("Homes: %d   green entrances: %d   barrier lines: %d   benches: %d"
      % (len(H), len(targets), bar.featureCount(), bench.featureCount()))

director = QgsVectorLayerDirector(net, -1, "", "", "", QgsVectorLayerDirector.DirectionBoth)
director.addStrategy(QgsNetworkDistanceStrategy())
builder = QgsGraphBuilder(net.crs(), True, 1.0)
tied = director.makeGraph(builder, targets + [h[1] for h in H])
gr = builder.graph()
s0 = gr.addVertex(QgsPointXY(0, 0))
for t in tied[:len(targets)]:
    vi = gr.findVertex(t)
    if vi >= 0:
        gr.addEdge(s0, vi, [0.0])
tree, cost = QgsGraphAnalyzer.dijkstra(gr, s0, 0)

edge_type = {}
def barrier_of(u, v):
    k = (min(u, v), max(u, v))
    if k not in edge_type:
        a, b = gr.vertex(u).point(), gr.vertex(v).point()
        mid = QgsGeometry.fromPointXY(QgsPointXY((a.x() + b.x()) / 2, (a.y() + b.y()) / 2))
        hit = None
        for i in bidx.intersects(mid.buffer(1.5, 4).boundingBox()):
            if bgeo[i][0].distance(mid) < 1.5:
                hit = bgeo[i][1]
                break
        edge_type[k] = hit
    return edge_type[k]

route_edges = set()
out = QgsVectorLayer("Point?crs=EPSG:25832", "h", "memory")
op = out.dataProvider()
op.addAttributes([QgsField("pop_est", QVariant.Double), QgsField("old65", QVariant.Double),
                  QgsField("route_m", QVariant.Double), QgsField("barriers", QVariant.String),
                  QgsField("any_barrier", QVariant.String)])
out.updateFields()
feats = []
for (geom, p, w, o), t in zip(H, tied[len(targets):]):
    v = gr.findVertex(t)
    if v < 0 or cost[v] < 0:
        continue
    found = set(); m = cost[v]
    while tree[v] != -1:
        u = gr.edge(tree[v]).fromVertex()
        if u == s0:
            break
        route_edges.add((min(u, v), max(u, v)))
        bt = barrier_of(u, v)
        if bt:
            found.add(bt)
        v = u
    nf = QgsFeature(out.fields()); nf.setGeometry(QgsGeometry.fromPointXY(p))
    nf.setAttributes([w, o, round(m, 0), ", ".join(sorted(found)), "yes" if found else "no"])
    feats.append(nf)
op.addFeatures(feats)

# benches within 20 m of any route
rgeo = [QgsGeometry.fromPolylineXY([gr.vertex(a).point(), gr.vertex(b).point()]) for a, b in route_edges]
ridx = QgsSpatialIndex()
for i, gm in enumerate(rgeo):
    f = QgsFeature(i); f.setGeometry(gm); ridx.addFeature(f)
# shown and counted inside the district only (the 1 km buffer is only for the route calculation)
dist = QgsGeometry.unaryUnion([f.geometry() for f in b25.getFeatures()])
rgeo = [gm.intersection(dist) for gm in rgeo if gm.intersects(dist)]
ridx = QgsSpatialIndex()
for i, gm in enumerate(rgeo):
    f = QgsFeature(i); f.setGeometry(gm); ridx.addFeature(f)
bench = run("native:clip", {"INPUT": bench, "OVERLAY": b25})
bar = run("native:clip", {"INPUT": bar, "OVERLAY": b25})
bar = run("native:fieldcalculator", {"INPUT": bar, "FIELD_NAME": "length_m", "FIELD_TYPE": 0,
          "FIELD_PRECISION": 1, "FORMULA": "round($length,1)"})
route_km = sum(gm.length() for gm in rgeo) / 1000
b_on = 0
for f in bench.getFeatures():
    gm = f.geometry()
    if any(rgeo[i].distance(gm) <= BENCH_NEAR_ROUTE_M for i in ridx.intersects(gm.buffer(BENCH_NEAR_ROUTE_M, 4).boundingBox())):
        b_on += 1

# ---------- save and style ----------
A = save(bar, "CJ04a_innenstadt_ost_walking_barriers_25832", "CJ04a walking barriers (OSM)")
A.setRenderer(QgsCategorizedSymbolRenderer("barrier", [
    QgsRendererCategory("Steps", QgsLineSymbol.createSimple({"color": "#b2182b", "width": "1.2"}), "Steps"),
    QgsRendererCategory("Not wheelchair accessible", QgsLineSymbol.createSimple(
        {"color": "#d6604d", "width": "0.9", "line_style": "dash"}), "Not wheelchair accessible"),
    QgsRendererCategory("Rough surface", QgsLineSymbol.createSimple(
        {"color": "#a6761d", "width": "0.7", "line_style": "dot"}), "Rough surface (gravel, cobbles ...)")]))
B = save(bench, "CJ04b_innenstadt_ost_benches_25832", "CJ04b benches (OSM)")
B.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple(
    {"name": "square", "color": "#1a7837", "size": "1.6", "outline_color": "#ffffff", "outline_width": "0.2"})))
C = save(out, "CJ04c_innenstadt_ost_homes_barrier_on_route_25832", "CJ04c homes: barrier on route to green")
C.setSubsetString("\"old65\" >= 3")   # show homes with 3+ older residents; clear in Properties > Source to see all
C.setRenderer(QgsCategorizedSymbolRenderer("any_barrier", [
    QgsRendererCategory("yes", QgsMarkerSymbol.createSimple({"name": "circle", "color": "#b2182b", "size": "1.8",
                        "outline_color": "#ffffff", "outline_width": "0.2"}), "65+ with barrier on route"),
    QgsRendererCategory("no", QgsMarkerSymbol.createSimple({"name": "circle", "color": "#bdbdbd", "size": "1.2",
                        "outline_style": "no"}), "65+ without barrier on route")]))
for L in (A, B, C):
    L.triggerRepaint(); iface.layerTreeView().refreshLayerSymbology(L.id())

# ---------- report ----------
P = sum(f["pop_est"] for f in feats) or 1
O = sum(f["old65"] for f in feats) or 1
yes = [f for f in feats if f["any_barrier"] == "yes"]
print("\n=== CJ04 walking barriers, Innenstadt-Ost (OSM) ===")
for lab, _ in TYPES:
    km = sum(f["length_m"] for f in bar.getFeatures() if f["barrier"] == lab) / 1000
    print("   %-28s %6.1f km (inside district)" % (lab, km))
print("\nResidents with at least one barrier on their route to green: %.0f (%.1f %%)"
      % (sum(f["pop_est"] for f in yes), 100 * sum(f["pop_est"] for f in yes) / P))
print("Residents 65+ with at least one barrier:                    %.0f of %.0f (%.1f %%)"
      % (sum(f["old65"] for f in yes), O, 100 * sum(f["old65"] for f in yes) / O))
for lab, _ in TYPES:
    s = [f for f in feats if lab in (f["barriers"] or "")]
    print("   65+ with %-26s %.0f" % (lab.lower() + ":", sum(f["old65"] for f in s)))
print("\nRoute network to green inside district: %.1f km;  benches within %d m of a route: %d (%.1f per km)"
      % (route_km, BENCH_NEAR_ROUTE_M, b_on, b_on / route_km if route_km else 0))
print("Limit: OSM tags are incomplete; untagged streets are not proof of barrier-free access.")
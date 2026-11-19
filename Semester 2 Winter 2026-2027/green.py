# HH07: walking time from HOMES to (A) free green >= 1 ha, (B) any free cool place,
#       (C) nearest doctor / clinic, (D) nearest pharmacy, with population and heat class
# C and D come from HH01 (OSM places inside the district; places just outside are not counted).
# Needs in project: 00_innenstadt_ost_boundary_25832, I00_innenstadt_ost_landuse_full_25832,
#   I01_innenstadt_ost_roads_paths_25832, HH02c_innenstadt_ost_free_green_destinations_25832,
#   I08_innenstadt_ost_buildings_osm_25832 (copy from Infrastructure project),
#   optional: HH05_innenstadt_ost_population_100m_zensus2022_25832, 07_innenstadt_ost_climate_cat
# Homes = building centroids inside housing / mixed-use ALKIS parcels.
# Walking time = straight line from home to nearest street point + network distance to nearest
#   free green entrance; 80 m per minute (4.8 km/h, assumption).
# Population: each 100 m Zensus cell is shared among its homes by building footprint (assumption).
# Run: Plugins > Python Console > Show Editor > open > Run (1-3 minutes). Styles nothing, moves nothing.

import os, time, processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry,
                       QgsPointXY, QgsSpatialIndex)
from qgis.analysis import (QgsVectorLayerDirector, QgsNetworkDistanceStrategy,
                           QgsGraphBuilder, QgsGraphAnalyzer)
from qgis.PyQt.QtCore import QVariant

FOLDER = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/"
          "M 01 - Urban Green for Heat Reduction/Health Map Innenstadt-Ost/02_data_clipped")
M_PER_MIN = 80.0

def find(part, need=True):
    for l in QgsProject.instance().mapLayers().values():
        if part.lower() in l.name().lower():
            return l
    if need:
        raise Exception("Layer not found in project: " + part)
    return None

def run(alg, p):
    return processing.run(alg, p)["OUTPUT"]

boundary = find("00_innenstadt_ost_boundary_25832")
i00 = find("I00_innenstadt_ost_landuse_full")
i01 = find("I01_innenstadt_ost_roads_paths")
free = find("HH02c_innenstadt_ost_free_green")
bld = find("I08_innenstadt_ost_buildings", need=False)
pop = find("HH05_innenstadt_ost_population", need=False)
heat = None
for _l in QgsProject.instance().mapLayers().values():   # exact name, not the "— 06b" duplicate
    if _l.name() == "07_innenstadt_ost_climate_cat":
        heat = _l
if heat is None:
    heat = find("07_innenstadt_ost_climate_cat", need=False)
if bld is None:
    raise Exception("Copy I08_innenstadt_ost_buildings_osm_25832 from the Infrastructure project first")
report = []

# ---------- homes: building centroids in housing / mixed parcels ----------
N = '"nutzart"'
housing = run("native:extractbyexpression", {"INPUT": i00, "EXPRESSION":
              N + " ILIKE '%Wohnbau%' OR " + N + " ILIKE '%gemischt%'", "OUTPUT": "memory:"})
b = run("native:reprojectlayer", {"INPUT": bld, "TARGET_CRS": "EPSG:25832", "OUTPUT": "memory:"})
b = run("native:fixgeometries", {"INPUT": b, "OUTPUT": "memory:"})
b = run("native:fieldcalculator", {"INPUT": b, "FIELD_NAME": "foot_m2", "FIELD_TYPE": 0,
        "FIELD_PRECISION": 1, "FORMULA": "round($area,1)", "OUTPUT": "memory:"})
c = run("native:pointonsurface", {"INPUT": b, "ALL_PARTS": False, "OUTPUT": "memory:"})
homes = run("native:extractbylocation", {"INPUT": c, "PREDICATE": [0], "INTERSECT": housing, "OUTPUT": "memory:"})
report.append("Homes (buildings in housing / mixed parcels): %d" % homes.featureCount())

# ---------- walking network ----------
net = run("native:extractbyexpression", {"INPUT": i01,
          "EXPRESSION": "\"highway\" NOT IN ('motorway','motorway_link','trunk','trunk_link')", "OUTPUT": "memory:"})
director = QgsVectorLayerDirector(net, -1, "", "", "", QgsVectorLayerDirector.DirectionBoth)
director.addStrategy(QgsNetworkDistanceStrategy())

def entrance_points(poly):
    """where paths meet the polygon edge + one inner point per polygon (for small ones)"""
    edge = run("native:polygonstolines", {"INPUT": poly, "OUTPUT": "memory:"})
    ent = run("native:lineintersections", {"INPUT": net, "INTERSECT": edge, "OUTPUT": "memory:"})
    pts = [f.geometry().asPoint() for f in ent.getFeatures()]
    pts += [f.geometry().pointOnSurface().asPoint() for f in poly.getFeatures()]
    return pts

def network_costs(points):
    """one multi-source Dijkstra from all destination points"""
    builder = QgsGraphBuilder(net.crs(), True, 1.0)
    tied = director.makeGraph(builder, points)
    g = builder.graph()
    s0 = g.addVertex(QgsPointXY(0, 0))
    for t in tied:
        vi = g.findVertex(t)
        if vi >= 0:
            g.addEdge(s0, vi, [0.0])
    tree, cst = QgsGraphAnalyzer.dijkstra(g, s0, 0)
    idx = QgsSpatialIndex()
    for v in range(g.vertexCount()):
        if v != s0 and cst[v] >= 0:
            f = QgsFeature(v); f.setGeometry(QgsGeometry.fromPointXY(g.vertex(v).point())); idx.addFeature(f)
    return g, cst, idx

# ---------- destinations A: free green >= 1 ha (HH02c) ----------
pts_A = entrance_points(free)

# ---------- destinations B: A + small free green >= 0.1 ha + fountains / drinking water ----------
GREEN = (N + " ILIKE '%Sport%' OR " + N + " ILIKE '%Erholung%' OR " + N + " ILIKE '%Friedhof%' OR "
         + N + " ILIKE '%Wald%' OR " + N + " ILIKE '%Gehölz%' OR " + N + " ILIKE '%Gewässer%'")
sg = run("native:extractbyexpression", {"INPUT": i00, "EXPRESSION": GREEN, "OUTPUT": "memory:"})
sg = run("native:dissolve", {"INPUT": sg, "OUTPUT": "memory:"})
sg = run("native:multiparttosingleparts", {"INPUT": sg, "OUTPUT": "memory:"})
hh06 = find("HH06_innenstadt_ost_paid_private_green", need=False)
if hh06:
    h6 = run("native:reprojectlayer", {"INPUT": hh06, "TARGET_CRS": "EPSG:25832", "OUTPUT": "memory:"})
    h6 = run("native:fixgeometries", {"INPUT": h6, "OUTPUT": "memory:"})
    sg = run("native:difference", {"INPUT": sg, "OVERLAY": h6, "OUTPUT": "memory:"})
    sg = run("native:multiparttosingleparts", {"INPUT": sg, "OUTPUT": "memory:"})
sg = run("native:extractbyexpression", {"INPUT": sg, "EXPRESSION": "$area >= 1000", "OUTPUT": "memory:"})
pts_B = entrance_points(sg)
w03 = find("W03_innenstadt_ost_water_points", need=False)
n_w = 0
if w03:
    w = run("native:reprojectlayer", {"INPUT": w03, "TARGET_CRS": "EPSG:25832", "OUTPUT": "memory:"})
    for f in w.getFeatures():
        if "Fountain" in str(f["w_class"] if w.fields().indexOf("w_class") >= 0 else "Fountain"):
            pts_B.append(f.geometry().asPoint()); n_w += 1
report.append("Destinations A (free green >= 1 ha): %d areas" % free.featureCount())
report.append("Destinations B (free green >= 0.1 ha + %d fountains / drinking water): %d areas" % (n_w, sg.featureCount()))

# ---------- destinations C (doctor / clinic) and D (pharmacy) from HH01 ----------
hh01 = find("HH01_innenstadt_ost_heat_sensitive_places")
pts_C, pts_D = [], []
for f in hh01.getFeatures():
    t = str(f["place_type"])
    pt = f.geometry().pointOnSurface().asPoint() if f.geometry().isMultipart() else f.geometry().asPoint()
    if t in ("Doctor", "Hospital / clinic"):
        pts_C.append(pt)
    elif t == "Pharmacy":
        pts_D.append(pt)
report.append("Destinations C (doctor / clinic): %d   D (pharmacy): %d" % (len(pts_C), len(pts_D)))

NETS = {"A": network_costs(pts_A), "B": network_costs(pts_B),
        "C": network_costs(pts_C), "D": network_costs(pts_D)}
KEYS = ("A", "B", "C", "D")
LABEL = {"A": "free green >= 1 ha", "B": "any free cool place",
         "C": "doctor / clinic", "D": "pharmacy"}

def walk(p, g, cst, idx):
    near = idx.nearestNeighbor(p, 1)
    if not near:
        return None
    v = near[0]
    return cst[v] + g.vertex(v).point().distance(p)

def klass(mins):
    return ("<= 5 min" if mins <= 5 else "5-10 min" if mins <= 10 else
            "10-15 min" if mins <= 15 else "> 15 min")

# ---------- population share per home ----------
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
    report.append("Population shared over homes: %.0f (from %d Zensus cells)" % (sum(pop_of.values()), len(members)))
else:
    report.append("HH05 population not in project: counting homes only")

# ---------- heat class per home ----------
heat_of = {}
if heat:
    hf = "climate_cat" if heat.fields().indexOf("climate_cat") >= 0 else heat.fields()[heat.fields().count() - 1].name()
    # legend label per heat polygon, read from the layer's own style (works for categorized and rule-based)
    from qgis.core import QgsRenderContext, QgsExpressionContext, QgsExpressionContextUtils
    r = heat.renderer().clone()
    ctx = QgsRenderContext()
    ectx = QgsExpressionContext(); ectx.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(heat))
    ctx.setExpressionContext(ectx)
    key2label = {it.ruleKey(): it.label() for it in r.legendSymbolItems()}
    r.startRender(ctx, heat.fields())
    hgeo = {}
    for f in heat.getFeatures():
        ectx.setFeature(f)
        keys = r.legendKeysForFeature(f, ctx)
        lab = ", ".join(key2label.get(k, "") for k in keys if key2label.get(k, ""))
        hgeo[f.id()] = (f.geometry(), lab or str(f[hf]))
    r.stopRender(ctx)
    report.append("Heat labels found: " + ", ".join(sorted(set(v[1] for v in hgeo.values()))))
    hidx = QgsSpatialIndex(heat.getFeatures())
    for h in homes.getFeatures():
        p = h.geometry()
        for fid in hidx.intersects(p.boundingBox()):
            if hgeo[fid][0].contains(p):
                heat_of[h.id()] = hgeo[fid][1]
                break
    report.append("Heat class field used: " + hf)

# ---------- walking time per home: A, B, C, D ----------
out = QgsVectorLayer("Point?crs=EPSG:25832", "tmp", "memory")
pr = out.dataProvider()
flds = []
for k in KEYS:
    flds += [QgsField("walk_min_" + k, QVariant.Double), QgsField("class_" + k, QVariant.String, len=12)]
flds += [QgsField("pop_est", QVariant.Double), QgsField("heat_class", QVariant.String, len=40),
         QgsField("foot_m2", QVariant.Double)]
pr.addAttributes(flds)
out.updateFields()
summary = {k: {} for k in KEYS}
feats = []
for h in homes.getFeatures():
    p = h.geometry().asPoint()
    vals, ok = [], True
    cls_of = {}
    for k in KEYS:
        g, cst, idx = NETS[k]
        d = walk(p, g, cst, idx)
        if d is None:
            ok = False
            break
        m = d / M_PER_MIN
        cls_of[k] = klass(m)
        vals += [round(m, 1), cls_of[k]]
    if not ok:
        continue
    pe = pop_of.get(h.id(), 0.0)
    nf = QgsFeature(out.fields())
    nf.setGeometry(h.geometry())
    nf.setAttributes(vals + [round(pe, 2), heat_of.get(h.id(), ""), h["foot_m2"]])
    feats.append(nf)
    for k in KEYS:
        sm = summary[k].setdefault(cls_of[k], [0, 0.0]); sm[0] += 1; sm[1] += pe
pr.addFeatures(feats)

path = "%s/HH07_innenstadt_ost_homes_walk_to_free_green_25832.gpkg" % FOLDER
if os.path.exists(path):
    try:
        os.remove(path)
    except OSError:
        path = path.replace(".gpkg", "_%s.gpkg" % time.strftime("%H%M%S"))
processing.run("native:savefeatures", {"INPUT": out, "OUTPUT": path})
QgsProject.instance().addMapLayer(QgsVectorLayer(path, os.path.basename(path)[:-5], "ogr"))

report.append("")
report.append("A = free green >= 1 ha | B = any free cool place | C = doctor / clinic | D = pharmacy")
report.append("People by walking time (share of residents):")
report.append("%-10s %16s %16s %16s %16s" % ("walk", "A", "B", "C", "D"))
tp = {k: (sum(v[1] for v in summary[k].values()) or 1) for k in KEYS}
for cls in ("<= 5 min", "5-10 min", "10-15 min", "> 15 min"):
    row = [cls]
    for k in KEYS:
        n, pp = summary[k].get(cls, [0, 0.0])
        row.append("%.0f (%.0f%%)" % (pp, 100 * pp / tp[k]))
    report.append("%-10s %16s %16s %16s %16s" % tuple(row))

if heat_of:
    hot = [f for f in out.getFeatures() if any(x in (f["heat_class"] or "") for x in ("Strong", "Extreme"))]
    report.append("")
    report.append("People in strong/extreme heat: %.0f" % sum(f["pop_est"] for f in hot))
    for k, lim in (("A", 5), ("B", 5), ("C", 10), ("D", 10)):
        report.append("  of them > %d min from %s (%s): %.0f" % (lim, LABEL[k], k,
                      sum(f["pop_est"] for f in hot if f["walk_min_" + k] > lim)))

print("\n".join(["", "=== Homes to free cool places and care, Innenstadt-Ost ==="] + report))
# Culture and Justice map, Innenstadt-Ost  (run in the "Culture Map Ost" project)
# Builds:
#   CJ01  culture places (OSM points + polygons): heritage, memorials, worship, museums, theatres, libraries,
#         arts / community centres, cinemas
#   CJ01b cemeteries and allotment gardens (ALKIS, from I00 land use)
#   CJ02  100 m grid (Zensus 2022) with social shares and environmental burdens per cell:
#         share_foreign, share_u18, share_65 (and rent_m2 if a Zensus rent file is found)
#         burden_heat  = share of residents in strong / extreme heat         (HH07, LANUK 2026)
#         burden_green = share of residents > 300 m walk from free green >= 1 ha (HH07, WHO)
#         burden_noise = share of residents >= 55 dB Lden                      (HH11, Stadt Dortmund 2022)
# Reference values: district averages from the same official data (no own thresholds):
#   "burdened"   = at least 2 of the 3 burden shares above the district average
#   "vulnerable" = foreign share OR share of children OR share 65+ above the district average
# Inputs it looks for by itself:
#   in the project: 00_innenstadt_ost_boundary_25832, Dortmund_Points_Fixed, Dortmund_Multipolygons_Fixed, I00 land use
#   on disk (anywhere under the M 01 folder): HH07 ...walk_to_free_green_25832.gpkg, HH11 ...homes_road_noise...gpkg,
#   Zensus 2022 100 m CSVs (population, age classes, foreign share; rent optional)
# Output: GeoPackages in the folder of this project (.qgz). Changes no existing layer.
# Run: Plugins > Python Console > Show Editor > open > Run

import os, csv, math, time, processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY,
                       QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsSpatialIndex,
                       QgsFillSymbol, QgsMarkerSymbol, QgsCategorizedSymbolRenderer, QgsRendererCategory,
                       QgsVectorFileWriter, QgsFeatureRequest)
from qgis.PyQt.QtCore import QVariant

BASE = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/"
        "M 01 - Urban Green for Heat Reduction")
HOT = ("Strong heat load", "Extreme heat load")
prj = QgsProject.instance()
C3035 = QgsCoordinateReferenceSystem("EPSG:3035")
C25832 = QgsCoordinateReferenceSystem("EPSG:25832")

def find(test, what, need=True):
    for l in prj.mapLayers().values():
        if l.type() == l.VectorLayer and test(l):
            return l
    if need:
        raise Exception(what + " not found in the project")
    return None

def find_file(test, what, need=True):
    """newest file under BASE whose name passes test"""
    hits = []
    for root, _, files in os.walk(BASE):
        for fn in files:
            if test(fn.lower()):
                hits.append(os.path.join(root, fn))
    if not hits:
        if need:
            raise Exception(what + " not found under " + BASE)
        return None
    hits.sort(key=os.path.getmtime)
    return hits[-1]

def load(path, title):
    l = QgsVectorLayer(path, title, "ogr")
    if not l.isValid():
        raise Exception("Cannot open " + path)
    return l

bnd = find(lambda l: l.name() == "00_innenstadt_ost_boundary_25832", "Boundary")
pts = find(lambda l: l.name() == "Dortmund_Points_Fixed", "Dortmund_Points_Fixed")
polys = find(lambda l: l.name() == "Dortmund_Multipolygons_Fixed", "Dortmund_Multipolygons_Fixed")
i00 = find(lambda l: "I00_innenstadt_ost_landuse_full" in l.name(), "I00 land use", need=False)

hp = find_file(lambda f: f.endswith("walk_to_free_green_25832.gpkg") and "district_only" not in f, "HH07 homes file")
homes = load(hp, "HH07 homes (read only)")
np_ = find_file(lambda f: f.startswith("hh11_innenstadt_ost_homes_road_noise") and f.endswith(".gpkg"),
                "HH11 noise homes file", need=False)
print("HH07 homes:", hp)
print("HH11 noise:", np_ or "not found, noise burden left out")

OUT = prj.homePath() or os.path.dirname(bnd.source().split("|")[0])

def run(alg, p):
    p["OUTPUT"] = "memory:"
    return processing.run(alg, p)["OUTPUT"]

def save(layer, name, title):
    path = os.path.join(OUT, name + ".gpkg")
    for old in [l for l in prj.mapLayers().values() if l.source().split("|")[0] == path]:
        prj.removeMapLayer(old.id())
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            path = os.path.join(OUT, name + time.strftime("_%H%M%S") + ".gpkg")
    opt = QgsVectorFileWriter.SaveVectorOptions(); opt.driverName = "GPKG"; opt.layerName = name
    opt.attributes = [i for i, f in enumerate(layer.fields()) if f.name().lower() not in ("fid", "ogc_fid")]
    err, msg, nf, _ = QgsVectorFileWriter.writeAsVectorFormatV3(layer, path, prj.transformContext(), opt)
    if err != QgsVectorFileWriter.NoError:
        raise Exception(msg)
    lyr = QgsVectorLayer(nf + "|layername=" + name, title, "ogr")
    prj.addMapLayer(lyr)
    return lyr

b25 = run("native:reprojectlayer", {"INPUT": bnd, "TARGET_CRS": C25832})
bgeom = QgsGeometry.unaryUnion([f.geometry() for f in b25.getFeatures()])

# =============== CJ01 culture places ===============
def tag(l, key, vals):
    e = " OR ".join('"other_tags" LIKE \'%%"%s"=>"%s"%%\'' % (key, v) for v in vals) if l.fields().indexOf("other_tags") >= 0 else "FALSE"
    if l.fields().indexOf(key) >= 0:
        e = '"%s" IN (%s) OR ' % (key, ",".join("'%s'" % v for v in vals)) + e
    return "(" + e + ")"

def any_tag(l, key):
    e = '"other_tags" LIKE \'%%"%s"=>%%\'' % key if l.fields().indexOf("other_tags") >= 0 else "FALSE"
    if l.fields().indexOf(key) >= 0:
        e = '"%s" IS NOT NULL OR ' % key + e
    return "(" + e + ")"

CATS = [  # label, expression builder
    ("Heritage / monument", lambda l: any_tag(l, "historic") + " OR " + any_tag(l, "heritage")),
    ("Place of worship", lambda l: tag(l, "amenity", ["place_of_worship"])),
    ("Museum / gallery", lambda l: tag(l, "tourism", ["museum", "gallery"])),
    ("Theatre / cinema / arts", lambda l: tag(l, "amenity", ["theatre", "cinema", "arts_centre"])),
    ("Library / community centre", lambda l: tag(l, "amenity", ["library", "community_centre"])),
]
cmem = QgsVectorLayer("Point?crs=EPSG:25832", "c", "memory")
cp = cmem.dataProvider()
cp.addAttributes([QgsField("category", QVariant.String), QgsField("name", QVariant.String)])
cmem.updateFields()
seen = set()
for lab, ex in CATS:
    for layer, is_poly in ((pts, False), (polys, True)):
        x = run("native:extractbyexpression", {"INPUT": layer, "EXPRESSION": ex(layer)})
        if is_poly:
            x = run("native:fixgeometries", {"INPUT": x})
            x = run("native:pointonsurface", {"INPUT": x, "ALL_PARTS": False})
        x = run("native:reprojectlayer", {"INPUT": x, "TARGET_CRS": C25832})
        for f in x.getFeatures():
            g = f.geometry()
            if not bgeom.contains(g):
                continue
            key = (round(g.asPoint().x()), round(g.asPoint().y()))
            if key in seen:
                continue
            seen.add(key)
            nf = QgsFeature(cmem.fields()); nf.setGeometry(g)
            nm = f["name"] if f.fields().indexOf("name") >= 0 else None
            nf.setAttributes([lab, nm]); cp.addFeatures([nf])
C1 = save(cmem, "CJ01_innenstadt_ost_culture_places_25832", "CJ01 culture places")
SYM = {"Heritage / monument": ("star", "#8c2d04", 3.2), "Place of worship": ("cross2", "#54278f", 2.6),
       "Museum / gallery": ("square", "#d95f0e", 2.4), "Theatre / cinema / arts": ("diamond", "#c51b7d", 2.6),
       "Library / community centre": ("triangle", "#2166ac", 2.6)}
C1.setRenderer(QgsCategorizedSymbolRenderer("category", [
    QgsRendererCategory(k, QgsMarkerSymbol.createSimple({"name": s, "color": c, "size": str(z),
        "outline_color": "#ffffff", "outline_width": "0.3"}), k) for k, (s, c, z) in SYM.items()]))

# cemeteries and allotments (cultural landscape) from ALKIS
if i00:
    cl = run("native:extractbyexpression", {"INPUT": i00, "EXPRESSION":
             "\"nutzart\" ILIKE '%Friedhof%' OR \"bez\" ILIKE '%Kleingarten%'"})
    cl = run("native:fieldcalculator", {"INPUT": cl, "FIELD_NAME": "type", "FIELD_TYPE": 2, "FIELD_LENGTH": 20,
             "FORMULA": "CASE WHEN \"nutzart\" ILIKE '%Friedhof%' THEN 'Cemetery' ELSE 'Allotment gardens' END"})
    cl = run("native:dissolve", {"INPUT": cl, "FIELD": ["type"]})
    cl = run("native:retainfields", {"INPUT": cl, "FIELDS": ["type"]})
    CL = save(cl, "CJ01b_innenstadt_ost_cultural_landscape_25832", "CJ01b cemeteries and allotments")
    CL.setRenderer(QgsCategorizedSymbolRenderer("type", [
        QgsRendererCategory("Cemetery", QgsFillSymbol.createSimple({"color": "#cfd8c4", "outline_color": "#6b7d5c",
                            "outline_width": "0.3", "style": "dense6"}), "Cemetery"),
        QgsRendererCategory("Allotment gardens", QgsFillSymbol.createSimple({"color": "#e5f5c4", "outline_color": "#7fbc41",
                            "outline_width": "0.3", "style": "dense5"}), "Allotment gardens")]))

# =============== CJ02 justice grid ===============
to3035 = QgsCoordinateTransform(homes.crs(), C3035, prj)
def cell_of(pt):
    p = to3035.transform(pt)
    return "CRS3035RES100mN%dE%d" % (math.floor(p.y() / 100) * 100, math.floor(p.x() / 100) * 100)

# noise per home from HH11 (lden_db per home point), matched to HH07 homes by position (1 m)
ndb = {}
if np_:
    nl = load(np_, "HH11 (read only)")
    tr = QgsCoordinateTransform(nl.crs(), homes.crs(), prj)
    for f in nl.getFeatures():
        p = tr.transform(f.geometry().asPoint())
        ndb[(round(p.x()), round(p.y()))] = f["lden_db"] or 0
noise = bool(ndb)

cells = {}
for h in homes.getFeatures():
    pt = h.geometry().asPoint()
    cid = cell_of(pt)
    pop = h["pop_est"] or 0
    loud = ndb.get((round(pt.x()), round(pt.y())), 0) >= 55
    c = cells.setdefault(cid, {"pop": 0, "hot": 0, "far": 0, "loud": 0})
    c["pop"] += pop
    c["hot"] += pop if h["heat_class"] in HOT else 0
    c["far"] += pop if h["class_A"] != "<= 300 m" else 0
    c["loud"] += pop if loud else 0

# Zensus CSVs: find all 100 m files under the M 01 folder and read the cells we need
def num(s):
    s = (s or "").strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None                       # "–" = hidden for privacy
soc = {cid: {} for cid in cells}
found = []
for root, _, files in os.walk(BASE):
    for fn in files:
        if not (fn.lower().endswith(".csv") and "100m" in fn.lower()):
            continue
        path = os.path.join(root, fn)
        for enc in ("utf-8-sig", "cp1252"):
            try:
                with open(path, encoding=enc, newline="") as fh:
                    rd = csv.DictReader(fh, delimiter=";")
                    hdr = rd.fieldnames or []
                    if "GITTER_ID_100m" not in hdr:
                        break
                    found.append(fn)
                    for r in rd:
                        g = r["GITTER_ID_100m"]
                        if g in soc:
                            for k in hdr:
                                lk = k.lower()
                                if "auslaender" in lk or "ausländer" in lk:
                                    soc[g]["foreign"] = num(r[k])
                                elif lk == "unter18":
                                    soc[g]["u18"] = num(r[k])
                                elif lk == "a65undaelter":
                                    soc[g]["o65"] = num(r[k])
                                elif lk == "insgesamt_bevoelkerung":
                                    soc[g]["tot"] = num(r[k])
                                elif "miete" in lk:
                                    soc[g]["rent"] = num(r[k])
                break
            except UnicodeDecodeError:
                continue
print("Zensus 100 m files read:", ", ".join(found) or "none")

# shares per cell
for cid, c in cells.items():
    s = soc[cid]; tot = s.get("tot")
    c["share_hot"] = c["hot"] / c["pop"] if c["pop"] else None
    c["share_far"] = c["far"] / c["pop"] if c["pop"] else None
    c["share_loud"] = c["loud"] / c["pop"] if c["pop"] else None
    f = s.get("foreign")
    c["share_foreign"] = f / 100 if f is not None else None   # Zensus file gives percent
    c["share_u18"] = s["u18"] / tot if tot and s.get("u18") is not None else None
    c["share_65"] = s["o65"] / tot if tot and s.get("o65") is not None else None
    c["rent_m2"] = s.get("rent")

def mean(key):  # population-weighted district average from the same data
    v = [(c[key], c["pop"]) for c in cells.values() if c.get(key) is not None and c["pop"]]
    w = sum(p for _, p in v)
    return sum(x * p for x, p in v) / w if w else None
AVG = {k: mean(k) for k in ("share_hot", "share_far", "share_loud", "share_foreign", "share_u18", "share_65", "rent_m2")}

def above(c, k):
    return c.get(k) is not None and AVG[k] is not None and c[k] > AVG[k]

gmem = QgsVectorLayer("Polygon?crs=EPSG:3035", "g", "memory")
gp = gmem.dataProvider()
F = ["cell_id", "pop", "share_hot", "share_far", "share_loud", "share_foreign", "share_u18", "share_65", "rent_m2",
     "n_burdens", "vulnerable", "justice_class"]
gp.addAttributes([QgsField(F[0], QVariant.String), QgsField(F[1], QVariant.Double)] +
                 [QgsField(k, QVariant.Double) for k in F[2:9]] +
                 [QgsField("n_burdens", QVariant.Int), QgsField("vulnerable", QVariant.String),
                  QgsField("justice_class", QVariant.String)])
gmem.updateFields()
for cid, c in cells.items():
    n = int(cid.split("mN")[1].split("E")[0]); e = int(cid.split("E")[-1])
    rect = QgsGeometry.fromPolygonXY([[QgsPointXY(e, n), QgsPointXY(e + 100, n), QgsPointXY(e + 100, n + 100),
                                       QgsPointXY(e, n + 100), QgsPointXY(e, n)]])
    nb = sum(above(c, k) for k in (("share_hot", "share_far", "share_loud") if noise else ("share_hot", "share_far")))
    vul = above(c, "share_foreign") or above(c, "share_u18") or above(c, "share_65")
    burd = nb >= 2
    jc = ("Hotspot: burdened and vulnerable" if burd and vul else "Burdened" if burd
          else "Socially vulnerable" if vul else "Neither")
    nf = QgsFeature(gmem.fields()); nf.setGeometry(rect)
    r = lambda k: round(c[k], 3) if c.get(k) is not None else None
    nf.setAttributes([cid, round(c["pop"], 1), r("share_hot"), r("share_far"), r("share_loud"), r("share_foreign"),
                      r("share_u18"), r("share_65"), c.get("rent_m2"), nb, "yes" if vul else "no", jc])
    gp.addFeatures([nf])
g25 = run("native:reprojectlayer", {"INPUT": gmem, "TARGET_CRS": C25832})
G = save(g25, "CJ02_innenstadt_ost_justice_grid_100m_25832", "CJ02 environmental justice (100 m)")
COL = {"Hotspot: burdened and vulnerable": "#b2182b", "Burdened": "#f4a582",
       "Socially vulnerable": "#92c5de", "Neither": "#f0f0f0"}
G.setRenderer(QgsCategorizedSymbolRenderer("justice_class", [
    QgsRendererCategory(k, QgsFillSymbol.createSimple({"color": v, "outline_color": "#ffffff", "outline_width": "0.1"}), k)
    for k, v in COL.items()]))
G.setOpacity(0.8)
for l in (C1, G):
    l.triggerRepaint()

# =============== report ===============
pc = lambda x: "-" if x is None else "%.1f %%" % (100 * x)
print("\n=== Culture and Justice, Innenstadt-Ost ===")
print("Culture places: %d" % C1.featureCount())
for k in SYM:
    print("   %-28s %d" % (k, sum(1 for f in C1.getFeatures() if f["category"] == k)))
print("\nDistrict averages (reference, population-weighted):")
for k, lab in (("share_hot", "residents in strong/extreme heat"), ("share_far", "> 300 m from free green >= 1 ha"),
               ("share_loud", ">= 55 dB Lden"), ("share_foreign", "foreign residents"),
               ("share_u18", "under 18"), ("share_65", "65 and older")):
    print("   %-34s %s" % (lab, pc(AVG[k])))
if AVG["rent_m2"]:
    print("   %-34s %.2f EUR/m2" % ("net rent", AVG["rent_m2"]))
tot = sum(c["pop"] for c in cells.values()) or 1
print("\nResidents by justice class (100 m cells):")
for k in COL:
    p = sum(f["pop"] for f in G.getFeatures() if f["justice_class"] == k)
    print("   %-34s %7.0f (%4.1f %%)" % (k, p, 100 * p / tot))
if not noise:
    print("\nNote: no HH11 noise file found, so 'burdened' = both heat AND far from green above average.")
if AVG["share_foreign"] is None:
    print("Note: no Zensus foreign-share file found, so 'vulnerable' uses children and 65+ only.")
print("\nSaved in:", OUT)
# HH10 Air pollution / noise exposure (proxy): residents living close to MAIN ROADS and to
#      INDUSTRIAL / COMMERCIAL areas, Innenstadt-Ost.
# Sources (main roads, industry) are taken from the district + 1 km, so sources just outside count too.
#
# Distance bands (literature-based, please verify before citing):
#   Main roads   50 m  = high exposure    (strongest near-road gradient)
#               150 m  = exposure zone    (Karner, Eisinger & Niemeier 2010, Environ. Sci. Technol. 44(14),
#                                          5334-5344: most traffic pollutants fall to background within
#                                          about 115-570 m, strongest drop in the first ~150 m;
#                                          HEI 2010, Special Report 17: exposure zone 300-500 m from highways)
#   Industry /  100 m  = closest band     (Abstandserlass NRW 2007: smallest separation class VII = 100 m)
#   commerce    200 m  = exposure zone    (Abstandserlass NRW 2007: class VI = 200 m)
#   ALKIS has no plant data, so the two smallest Abstandserlass classes are used (own choice, conservative).
#
# Needs in the Health project: HH09 homes (old65, pop_est, heat_class), 00_innenstadt_ost_boundary_25832,
#   Dortmund_Lines_Fixed, ALKIS full (liegenschaftskataster..., loaded or found in the M 01 folder).
# Makes: HH10a homes with distances + classes, HH10b exposure zones (for the map). Prints the numbers.
# Run: Plugins > Python Console > Show Editor > open > Run

import os, time, processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsVectorFileWriter, QgsField, QgsFeature,
                       QgsSpatialIndex, QgsFillSymbol, QgsCategorizedSymbolRenderer,
                       QgsRendererCategory)
from qgis.PyQt.QtCore import QVariant

ROAD_BANDS = (50, 150)
IND_BANDS = (100, 200)
MAIN = ("motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link",
        "secondary", "secondary_link")
HOT = ("Strong heat load", "Extreme heat load")
prj = QgsProject.instance()

def run(alg, p):
    p["OUTPUT"] = "memory:"
    return processing.run(alg, p)["OUTPUT"]

def find(test, what):
    for l in prj.mapLayers().values():
        if l.type() == l.VectorLayer and test(l):
            return l
    raise Exception(what + " not found in the project")

homes = find(lambda l: l.source().split("|")[0].endswith("homes_older_people_25832.gpkg"), "HH09 homes (run HH09 first)")
boundary = find(lambda l: l.name() == "00_innenstadt_ost_boundary_25832", "Boundary")
lines = find(lambda l: l.name() == "Dortmund_Lines_Fixed", "Dortmund_Lines_Fixed")
FOLDER = os.path.dirname(homes.source().split("|")[0])

alkis = None
for l in prj.mapLayers().values():
    if "liegenschaftskataster" in l.name().lower():
        alkis = l
        break
if alkis is None:
    M01 = os.path.dirname(os.path.dirname(FOLDER))
    for root, _, files in os.walk(M01):
        for fn in files:
            if "liegenschaftskataster" in fn.lower() and fn.lower().endswith((".fgb", ".gpkg", ".shp")):
                alkis = QgsVectorLayer(os.path.join(root, fn), "alkis", "ogr")
                break
        if alkis:
            break
if alkis is None or not alkis.isValid():
    raise Exception("ALKIS (liegenschaftskataster...) not found")

# ---------- sources within district + 1 km ----------
b25 = run("native:reprojectlayer", {"INPUT": boundary, "TARGET_CRS": "EPSG:25832"})
buf = run("native:buffer", {"INPUT": b25, "DISTANCE": 1000, "SEGMENTS": 16, "DISSOLVE": True})

roads = run("native:extractbyexpression", {"INPUT": lines,
            "EXPRESSION": '"highway" IN (%s)' % ",".join("'%s'" % h for h in MAIN)})
roads = run("native:reprojectlayer", {"INPUT": roads, "TARGET_CRS": "EPSG:25832"})
roads = run("native:clip", {"INPUT": roads, "OVERLAY": buf})

N = '"nutzart"'
ind = run("native:extractbyexpression", {"INPUT": alkis,
          "EXPRESSION": N + " ILIKE '%Industrie%' OR " + N + " ILIKE '%Gewerbe%'"})
ind = run("native:fixgeometries", {"INPUT": ind})
ind = run("native:reprojectlayer", {"INPUT": ind, "TARGET_CRS": "EPSG:25832"})
ind = run("native:clip", {"INPUT": ind, "OVERLAY": buf})

def index(layer):
    idx = QgsSpatialIndex(layer.getFeatures(), flags=QgsSpatialIndex.FlagStoreFeatureGeometries)
    geo = {f.id(): f.geometry() for f in layer.getFeatures()}
    return idx, geo

r_idx, r_geo = index(roads)
i_idx, i_geo = index(ind)

def dist(pt_geom, idx, geo):
    near = idx.nearestNeighbor(pt_geom.asPoint(), 1)
    return round(geo[near[0]].distance(pt_geom), 0) if near else 99999

def band(d, bands, labels):
    return labels[0] if d <= bands[0] else labels[1] if d <= bands[1] else labels[2]

R_LAB = ("<= %d m (high)" % ROAD_BANDS[0], "%d-%d m" % ROAD_BANDS, "> %d m" % ROAD_BANDS[1])
I_LAB = ("<= %d m (high)" % IND_BANDS[0], "%d-%d m" % IND_BANDS, "> %d m" % IND_BANDS[1])

# ---------- homes with distances ----------
mem = QgsVectorLayer("Point?crs=" + homes.crs().authid(), "tmp", "memory")
pr = mem.dataProvider()
flds = [f for f in homes.fields() if f.name().lower() not in ("fid", "ogc_fid")]
pr.addAttributes(flds + [QgsField("road_m", QVariant.Double), QgsField("road_cls", QVariant.String),
                         QgsField("ind_m", QVariant.Double), QgsField("ind_cls", QVariant.String),
                         QgsField("exposed", QVariant.String)])
mem.updateFields()
feats = []
for f in homes.getFeatures():
    g = f.geometry()
    rd, idd = dist(g, r_idx, r_geo), dist(g, i_idx, i_geo)
    rc, ic = band(rd, ROAD_BANDS, R_LAB), band(idd, IND_BANDS, I_LAB)
    exp = "yes" if (rd <= ROAD_BANDS[1] or idd <= IND_BANDS[1]) else "no"
    nf = QgsFeature(mem.fields()); nf.setGeometry(g)
    nf.setAttributes([f[x.name()] for x in flds] + [rd, rc, idd, ic, exp])
    feats.append(nf)
pr.addFeatures(feats)

def save(layer, name):
    path = os.path.join(FOLDER, name + ".gpkg")
    for old in [l for l in prj.mapLayers().values() if l.source().split("|")[0] == path]:
        prj.removeMapLayer(old.id())
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            path = os.path.join(FOLDER, name + time.strftime("_%H%M%S") + ".gpkg")
    opt = QgsVectorFileWriter.SaveVectorOptions(); opt.driverName = "GPKG"; opt.layerName = name
    opt.attributes = [i for i, x in enumerate(layer.fields()) if x.name().lower() not in ("fid", "ogc_fid")]
    err, msg, newfile, _ = QgsVectorFileWriter.writeAsVectorFormatV3(layer, path, prj.transformContext(), opt)
    if err != QgsVectorFileWriter.NoError:
        raise Exception(msg)
    lyr = QgsVectorLayer(newfile + "|layername=" + name, name, "ogr")
    prj.addMapLayer(lyr)
    return lyr

save(mem, "HH10a_innenstadt_ost_homes_pollution_exposure_25832")

# ---------- exposure zones for the map (outer bands, clipped to the district) ----------
zr = run("native:buffer", {"INPUT": roads, "DISTANCE": ROAD_BANDS[1], "SEGMENTS": 8, "DISSOLVE": True})
zr = run("native:fieldcalculator", {"INPUT": zr, "FIELD_NAME": "source", "FIELD_TYPE": 2, "FIELD_LENGTH": 30,
                                    "FORMULA": "'Main road (%d m)'" % ROAD_BANDS[1]})
zi = run("native:buffer", {"INPUT": ind, "DISTANCE": IND_BANDS[1], "SEGMENTS": 8, "DISSOLVE": True})
zi = run("native:fieldcalculator", {"INPUT": zi, "FIELD_NAME": "source", "FIELD_TYPE": 2, "FIELD_LENGTH": 30,
                                    "FORMULA": "'Industry / commerce (%d m)'" % IND_BANDS[1]})
z = run("native:mergevectorlayers", {"LAYERS": [zr, zi], "CRS": "EPSG:25832"})
z = run("native:clip", {"INPUT": z, "OVERLAY": b25})
z = run("native:retainfields", {"INPUT": z, "FIELDS": ["source"]})
zl = save(z, "HH10b_innenstadt_ost_pollution_exposure_zones_25832")
def hatch(c):
    return QgsFillSymbol.createSimple({"color": c, "outline_color": c, "outline_width": "0.3",
                                       "style": "b_diagonal"})
zl.setRenderer(QgsCategorizedSymbolRenderer("source", [
    QgsRendererCategory("Main road (%d m)" % ROAD_BANDS[1], hatch("#636363"), "Within %d m of a main road" % ROAD_BANDS[1]),
    QgsRendererCategory("Industry / commerce (%d m)" % IND_BANDS[1], hatch("#8c510a"), "Within %d m of industry / commerce" % IND_BANDS[1]),
]))
zl.triggerRepaint()

# ---------- report ----------
P = lambda fs: sum(x["pop_est"] or 0 for x in fs)
O = lambda fs: sum(x["old65"] or 0 for x in fs) if mem.fields().indexOf("old65") >= 0 else 0
T, TO = P(feats) or 1, O(feats) or 1
def line(label, fs):
    print("  %-38s %7.0f (%4.1f %%)   65+: %6.0f (%4.1f %%)" % (label, P(fs), 100 * P(fs) / T, O(fs), 100 * O(fs) / TO))

print("\n=== Air pollution / noise exposure (proxy), Innenstadt-Ost ===")
print("Main road sources: %.1f km   Industry / commerce: %.1f ha  (district + 1 km)"
      % (sum(x.geometry().length() for x in roads.getFeatures()) / 1000,
         sum(x.geometry().area() for x in ind.getFeatures()) / 10000))
print("\nMain roads")
for c in R_LAB:
    line(c, [x for x in feats if x["road_cls"] == c])
print("\nIndustry / commerce")
for c in I_LAB:
    line(c, [x for x in feats if x["ind_cls"] == c])
print("\nAny exposure (road <= %d m or industry <= %d m)" % (ROAD_BANDS[1], IND_BANDS[1]))
ex = [x for x in feats if x["exposed"] == "yes"]
line("exposed", ex)
hot_ex = [x for x in ex if x["heat_class"] in HOT]
line("exposed AND strong/extreme heat", hot_ex)
print("\nSaved in:", FOLDER)
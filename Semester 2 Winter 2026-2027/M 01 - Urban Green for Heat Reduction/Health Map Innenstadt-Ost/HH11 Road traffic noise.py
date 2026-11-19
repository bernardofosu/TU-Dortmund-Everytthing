# HH11 Road traffic noise (Lden, Umgebungslaermkartierung NRW 2022, round 4): residents per noise class
# Uses the noise layer already loaded (name contains "Road_LDEN"), and the HH09 homes (pop_est, old65, heat_class).
# The dB class is read automatically from the layer's attributes (first number 55-80 found, e.g. "55 - 59 dB").
# Writes HH11 homes with lden_class, styles the noise layer, prints the numbers.
# Threshold: WHO 2018 Environmental Noise Guidelines, road traffic 53 dB Lden (verify); the map starts at 55 dB.
# Run: Plugins > Python Console > Show Editor > open > Run

import os, re, time
from qgis.core import (QgsProject, QgsVectorLayer, QgsVectorFileWriter, QgsField, QgsFeature,
                       QgsSpatialIndex, QgsCoordinateTransform, QgsFillSymbol,
                       QgsCategorizedSymbolRenderer, QgsRendererCategory)
from qgis.PyQt.QtCore import QVariant

HOT = ("Strong heat load", "Extreme heat load")
prj = QgsProject.instance()

def find(test, what):
    for l in prj.mapLayers().values():
        if l.type() == l.VectorLayer and test(l):
            return l
    raise Exception(what + " not found in the project")

noise = find(lambda l: "road_lden" in l.name().lower() or "laerm" in l.name().lower() or "lden" in l.name().lower(),
             "Noise layer (Road_LDEN)")
homes = find(lambda l: l.source().split("|")[0].endswith("homes_older_people_25832.gpkg"), "HH09 homes")
FOLDER = os.path.dirname(homes.source().split("|")[0])
print("Noise layer:", noise.name(), " fields:", ", ".join(f.name() for f in noise.fields()))

# ---------- find the field that holds the dB class ----------
num = re.compile(r"(\d{2})")
def first_db(v):
    if v is None:
        return None
    if isinstance(v, (int, float)) and 45 <= v <= 85:
        return int(v)
    m = num.search(str(v))
    if m and 45 <= int(m.group(1)) <= 85:
        return int(m.group(1))
    return None

sample = [f for i, f in zip(range(300), noise.getFeatures())]
best, score = None, 0
for fld in noise.fields():
    s = sum(1 for f in sample if first_db(f[fld.name()]) is not None)
    if s > score:
        best, score = fld.name(), s
if not best:
    raise Exception("No dB field found. Send Claude a screenshot of the noise attribute table.")
print("dB class field used:", best, " example:", sample[0][best])

def label(db):
    return ">= 75 dB" if db >= 75 else "%d-%d dB" % (db, db + 4)
LABELS = ["55-59 dB", "60-64 dB", "65-69 dB", "70-74 dB", ">= 75 dB"]

# ---------- point in polygon: highest class wins ----------
tr = QgsCoordinateTransform(homes.crs(), noise.crs(), prj)
geo, dbv = {}, {}
for f in noise.getFeatures():
    d = first_db(f[best])
    if d is not None:
        geo[f.id()] = f.geometry(); dbv[f.id()] = d
idx = QgsSpatialIndex()
for fid, g in geo.items():
    ft = QgsFeature(fid); ft.setGeometry(g); idx.addFeature(ft)

mem = QgsVectorLayer("Point?crs=" + homes.crs().authid(), "tmp", "memory")
pr = mem.dataProvider()
flds = [f for f in homes.fields() if f.name().lower() not in ("fid", "ogc_fid")]
pr.addAttributes(flds + [QgsField("lden_db", QVariant.Int), QgsField("lden_class", QVariant.String)])
mem.updateFields()
feats = []
for h in homes.getFeatures():
    g = h.geometry()
    p = g.asPoint() if not g.isMultipart() else g.centroid().asPoint()
    pt = tr.transform(p)
    from qgis.core import QgsGeometry
    pg = QgsGeometry.fromPointXY(pt)
    top = None
    for fid in idx.intersects(pg.boundingBox()):
        if geo[fid].contains(pg) and (top is None or dbv[fid] > top):
            top = dbv[fid]
    nf = QgsFeature(mem.fields()); nf.setGeometry(g)
    nf.setAttributes([h[x.name()] for x in flds] + [top, label(top) if top else "< 55 dB"])
    feats.append(nf)
pr.addFeatures(feats)

# ---------- save ----------
name = "HH11_innenstadt_ost_homes_road_noise_25832"
path = os.path.join(FOLDER, name + ".gpkg")
for old in [l for l in prj.mapLayers().values() if l.source().split("|")[0] == path]:
    prj.removeMapLayer(old.id())
if os.path.exists(path):
    try:
        os.remove(path)
    except OSError:
        path = os.path.join(FOLDER, name + time.strftime("_%H%M%S") + ".gpkg")
opt = QgsVectorFileWriter.SaveVectorOptions(); opt.driverName = "GPKG"; opt.layerName = name
err, msg, newfile, _ = QgsVectorFileWriter.writeAsVectorFormatV3(mem, path, prj.transformContext(), opt)
if err != QgsVectorFileWriter.NoError:
    raise Exception(msg)
lyr = QgsVectorLayer(newfile + "|layername=" + name, "HH11 homes: road noise (Lden)", "ogr")
prj.addMapLayer(lyr, False)   # added but hidden from the panel clutter: drag in from Browser if needed

# ---------- style the noise layer by class (yellow to dark red) ----------
COL = {"55-59 dB": "#fee391", "60-64 dB": "#fec44f", "65-69 dB": "#fe9929", "70-74 dB": "#d95f0e", ">= 75 dB": "#993404"}
expr = "CASE " + " ".join(
    "WHEN to_int(regexp_substr(to_string(\"%s\"), '\\\\d{2}')) >= %d THEN '%s'" % (best, lo, lab)
    for lo, lab in ((75, ">= 75 dB"), (70, "70-74 dB"), (65, "65-69 dB"), (60, "60-64 dB"), (55, "55-59 dB"))) + " END"
noise.setRenderer(QgsCategorizedSymbolRenderer(expr, [
    QgsRendererCategory(lab, QgsFillSymbol.createSimple({"color": COL[lab], "outline_style": "no"}), lab)
    for lab in LABELS]))
noise.setOpacity(0.6)
noise.triggerRepaint()

# ---------- report ----------
P = lambda fs: sum(x["pop_est"] or 0 for x in fs)
O = lambda fs: sum(x["old65"] or 0 for x in fs)
T, TO = P(feats) or 1, O(feats) or 1
print("\n=== Road traffic noise Lden (NRW 2022), Innenstadt-Ost ===")
print("%-10s %16s %16s" % ("Class", "Residents", "65+"))
for lab in ["< 55 dB"] + LABELS:
    fs = [x for x in feats if x["lden_class"] == lab]
    print("%-10s %8.0f (%4.1f%%) %7.0f (%4.1f%%)" % (lab, P(fs), 100 * P(fs) / T, O(fs), 100 * O(fs) / TO))
loud = [x for x in feats if (x["lden_db"] or 0) >= 55]
very = [x for x in feats if (x["lden_db"] or 0) >= 65]
print("\n>= 55 dB (above WHO 53 dB): %.0f residents (%.1f %%), 65+: %.0f" % (P(loud), 100 * P(loud) / T, O(loud)))
print(">= 65 dB:                   %.0f residents (%.1f %%)" % (P(very), 100 * P(very) / T))
hl = [x for x in loud if x["heat_class"] in HOT]
print(">= 55 dB AND strong/extreme heat: %.0f residents, 65+: %.0f" % (P(hl), O(hl)))
print("\nSaved:", newfile)
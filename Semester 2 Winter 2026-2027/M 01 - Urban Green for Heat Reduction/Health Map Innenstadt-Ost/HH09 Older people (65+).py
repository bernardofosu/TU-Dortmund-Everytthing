# HH09 Older people (65+) per walking class and in heat, Innenstadt-Ost
# Uses Zensus 2022 "Alter in 5 Altersklassen", 100 m grid (CSV, semicolon, EPSG:3035).
# Each home already has pop_est (its share of the cell's people). Here it also gets
#   old65 = pop_est x (65+ / total) of its cell.
# Cells where the 65+ value is hidden by the census ("–", secrecy) get the district average share.
# Writes a NEW layer HH09 (copy of the homes with old65), does not change HH07. Prints the numbers.
# Run in the Health project: Plugins > Python Console > Show Editor > open > Run

import os, csv, time, math
from qgis.core import (QgsProject, QgsVectorLayer, QgsVectorFileWriter, QgsField, QgsFeature,
                       QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsMarkerSymbol,
                       QgsGraduatedSymbolRenderer, QgsRendererRange)
from qgis.PyQt.QtCore import QVariant

BASE = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/"
        "M 01 - Urban Green for Heat Reduction/Health Map Innenstadt-Ost")
CSV_NAME = "Zensus2022_Alter_in_5_Altersklassen_100m-Gitter.csv"
HOT = ("Strong heat load", "Extreme heat load")
C = ["<= 300 m", "300-500 m", "> 500 m"]
NAMES = {"A": "free green >= 1 ha", "B": "any free cool place", "C": "doctor / clinic", "D": "pharmacy"}
FAR = {"A": C[1:], "B": C[1:], "C": C[2:], "D": C[2:]}
LIM = {"A": "> 300 m", "B": "> 300 m", "C": "> 500 m", "D": "> 500 m"}

prj = QgsProject.instance()

# ---------- 1 find the CSV ----------
path = None
for root, _, files in os.walk(BASE):
    if CSV_NAME in files:
        path = os.path.join(root, CSV_NAME)
        break
if not path:
    raise Exception("Not found under the Health folder: " + CSV_NAME)
print("CSV:", path)

# ---------- 2 the homes layer ----------
homes = None
for l in prj.mapLayers().values():
    if l.type() == l.VectorLayer and l.source().split("|")[0].endswith("walk_to_free_green_25832.gpkg"):
        homes = l
        break
if homes is None:
    raise Exception("New HH07 homes file not loaded")

to3035 = QgsCoordinateTransform(homes.crs(), QgsCoordinateReferenceSystem("EPSG:3035"), prj)

def cell_id(pt):
    p = to3035.transform(pt)
    return "CRS3035RES100mN%dE%d" % (int(math.floor(p.y() / 100) * 100), int(math.floor(p.x() / 100) * 100))

home_cell = {f.id(): cell_id(f.geometry().centroid().asPoint()) for f in homes.getFeatures()}
needed = set(home_cell.values())

# ---------- 3 read only the cells we need ----------
def num(s):
    s = (s or "").strip()
    return int(s) if s.isdigit() else None          # "–" (hidden) -> None

cells = {}
for enc in ("utf-8-sig", "cp1252"):
    try:
        with open(path, encoding=enc, newline="") as fh:
            rd = csv.DictReader(fh, delimiter=";")
            for r in rd:
                gid = r.get("GITTER_ID_100m")
                if gid in needed:
                    cells[gid] = (num(r.get("Insgesamt_Bevoelkerung")), num(r.get("a65undaelter")))
        break
    except UnicodeDecodeError:
        cells = {}
print("Cells with homes: %d   found in CSV: %d" % (len(needed), len(cells)))

known = [(t, a) for t, a in cells.values() if t and a is not None]
avg_share = sum(a for t, a in known) / sum(t for t, a in known) if known else 0
hidden = sum(1 for t, a in cells.values() if t and a is None)
print("65+ value known in %d cells, hidden in %d cells" % (len(known), hidden))
print("District average share 65+ (known cells): %.1f %%" % (100 * avg_share))

def share(gid):
    t, a = cells.get(gid, (None, None))
    if t and a is not None:
        return a / t, False
    return avg_share, True

# ---------- 4 new layer = homes + old65 ----------
mem = QgsVectorLayer("Point?crs=" + homes.crs().authid(), "tmp", "memory")
pr = mem.dataProvider()
flds = [f for f in homes.fields() if f.name().lower() not in ("fid", "ogc_fid")]
pr.addAttributes(flds + [QgsField("old65", QVariant.Double), QgsField("old65_est", QVariant.String)])
mem.updateFields()
feats, est_people, all_old = [], 0, 0
for f in homes.getFeatures():
    s, est = share(home_cell[f.id()])
    o = (f["pop_est"] or 0) * s
    nf = QgsFeature(mem.fields())
    nf.setGeometry(f.geometry())
    nf.setAttributes([f[x.name()] for x in flds] + [round(o, 2), "yes" if est else "no"])
    feats.append(nf)
    all_old += o
    est_people += o if est else 0
pr.addFeatures(feats)

OUT = os.path.dirname(homes.source().split("|")[0])
name = "HH09_innenstadt_ost_homes_older_people_25832"
out = os.path.join(OUT, name + ".gpkg")
for old in [l for l in prj.mapLayers().values() if l.source().split("|")[0] == out]:
    prj.removeMapLayer(old.id())
if os.path.exists(out):
    try:
        os.remove(out)
    except OSError:
        out = os.path.join(OUT, name + time.strftime("_%H%M%S") + ".gpkg")
opt = QgsVectorFileWriter.SaveVectorOptions()
opt.driverName = "GPKG"; opt.layerName = name
err, msg, newfile, _ = QgsVectorFileWriter.writeAsVectorFormatV3(mem, out, prj.transformContext(), opt)
if err != QgsVectorFileWriter.NoError:
    raise Exception(msg)

# ---------- 5 report ----------
F = feats
O = lambda fs: sum(x["old65"] or 0 for x in fs)
print("\n=== Older people (65+) ===")
print("Older people in homes: %.0f   (of them %.0f from cells with hidden value, estimated)" % (all_old, est_people))
print("\n%-24s %10s %10s %10s" % ("Destination", *C))
for k in "ABCD":
    row = [100 * O([x for x in F if x["class_" + k] == c]) / all_old for c in C]
    print("%-24s %9.0f%% %9.0f%% %9.0f%%" % (k + " " + NAMES[k], *row))
H = [x for x in F if x["heat_class"] in HOT]
print("\nOlder people in strong or extreme heat: %.0f" % O(H))
for k in "ABCD":
    print("   of them %s from %-20s %.0f" % (LIM[k], NAMES[k], O([x for x in H if x["class_" + k] in FAR[k]])))

# ---------- 6 add and style: dot size = older people ----------
lyr = QgsVectorLayer(newfile + "|layername=" + name, "HH09 homes: older people (65+)", "ogr")
prj.addMapLayer(lyr)
def mk(s):
    return QgsMarkerSymbol.createSimple({"name": "circle", "color": "#6a51a3", "size": str(s),
                                         "outline_color": "#ffffff", "outline_width": "0.1"})
lyr.setRenderer(QgsGraduatedSymbolRenderer("old65", [
    QgsRendererRange(0, 1, mk(0.6), "< 1 older person"),
    QgsRendererRange(1, 3, mk(1.0), "1-3"),
    QgsRendererRange(3, 10, mk(1.6), "3-10"),
    QgsRendererRange(10, 100000, mk(2.4), "10 or more"),
]))
lyr.triggerRepaint()
print("\nSaved:", newfile)
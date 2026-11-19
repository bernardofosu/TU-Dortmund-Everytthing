# Zensus 2022 population, 100 m grid, for Innenstadt-Ost
# Reads the big Germany CSV, keeps only cells around the district, builds 100 m squares.
# Set CSV below to where Zensus2022_Bevoelkerungszahl_100m-Gitter.csv is on your PC.
# Run: Plugins > Python Console > Show Editor > open > Run (about 1 minute).

import csv, os, processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsGeometry,
                       QgsRectangle, QgsCoordinateReferenceSystem, QgsCoordinateTransform)
from qgis.PyQt.QtCore import QVariant

CSV = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/M 01 - Urban Green for Heat Reduction/"
       "Health Map Innenstadt-Ost/Zensus2022_Bevoelkerungszahl/Zensus2022_Bevoelkerungszahl_100m-Gitter.csv")
FOLDER = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/"
          "M 01 - Urban Green for Heat Reduction/Health Map Innenstadt-Ost/02_data_clipped")
os.makedirs(FOLDER, exist_ok=True)

def find(part):
    for l in QgsProject.instance().mapLayers().values():
        if part.lower() in l.name().lower():
            return l
    raise Exception("Layer not found: " + part)

boundary = find("00_innenstadt_ost_boundary_25832")
tr = QgsCoordinateTransform(boundary.crs(), QgsCoordinateReferenceSystem("EPSG:3035"), QgsProject.instance())
bb = tr.transformBoundingBox(boundary.extent())
bb.grow(200)

# open with the right encoding and delimiter
for enc in ("utf-8-sig", "latin-1"):
    try:
        f = open(CSV, encoding=enc, newline="")
        head = f.readline(); f.seek(0)
        break
    except UnicodeDecodeError:
        f.close()
delim = ";" if head.count(";") >= head.count(",") else ","
reader = csv.reader(f, delimiter=delim)
cols = next(reader)
print("Columns:", cols)
low = [c.lower() for c in cols]
ix = next(i for i, c in enumerate(low) if c.startswith("x_mp"))
iy = next(i for i, c in enumerate(low) if c.startswith("y_mp"))
ip = next(i for i, c in enumerate(low) if "einwohner" in c or "bevoelkerung" in c or "anzahl" in c)
iid = next((i for i, c in enumerate(low) if "gitter" in c), None)
print("Using x:", cols[ix], "| y:", cols[iy], "| population:", cols[ip])

lyr = QgsVectorLayer("Polygon?crs=EPSG:3035", "tmp", "memory")
pr = lyr.dataProvider()
pr.addAttributes([QgsField("cell_id", QVariant.String, len=40),
                  QgsField("population", QVariant.Int)])
lyr.updateFields()
feats = []
for row in reader:
    try:
        x, y = float(row[ix]), float(row[iy])
    except (ValueError, IndexError):
        continue
    if not (bb.xMinimum() <= x <= bb.xMaximum() and bb.yMinimum() <= y <= bb.yMaximum()):
        continue
    v = row[ip].strip().replace(".", "")
    pop = int(v) if v.lstrip("-").isdigit() and int(v) >= 0 else None   # '-' / '–' = suppressed
    ft = QgsFeature(lyr.fields())
    ft.setGeometry(QgsGeometry.fromRect(QgsRectangle(x - 50, y - 50, x + 50, y + 50)))
    ft.setAttributes([row[iid] if iid is not None else "", pop])
    feats.append(ft)
f.close()
pr.addFeatures(feats)
print("Cells in the district box:", len(feats))

rep = processing.run("native:reprojectlayer", {"INPUT": lyr, "TARGET_CRS": "EPSG:25832", "OUTPUT": "memory:"})["OUTPUT"]
sel = processing.run("native:extractbylocation", {"INPUT": rep, "PREDICATE": [0], "INTERSECT": boundary,
                                                   "OUTPUT": "memory:"})["OUTPUT"]
path = FOLDER + "/HH05_innenstadt_ost_population_100m_zensus2022_25832.gpkg"
processing.run("native:savefeatures", {"INPUT": sel, "OUTPUT": path})
QgsProject.instance().addMapLayer(QgsVectorLayer(path, "HH05_innenstadt_ost_population_100m_zensus2022_25832", "ogr"))

tot = sum(ft["population"] or 0 for ft in sel.getFeatures())
nulls = sum(1 for ft in sel.getFeatures() if ft["population"] is None)
print("\n=== Zensus 2022 population, Innenstadt-Ost ===")
print("Grid cells touching the district:", sel.featureCount())
print("Population (sum of cells, edge cells counted whole):", tot)
print("Cells with suppressed value (secrecy):", nulls)
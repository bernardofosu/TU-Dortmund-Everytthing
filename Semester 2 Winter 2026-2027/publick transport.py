# HH08 Public transport as a backup for homes far from a doctor (C) or pharmacy (D)
# For every home: straight-line distance to the nearest bus / tram stop (I04).
# Homes > 600 m walk from C or D are split into:
#   "far, stop nearby"  stop <= 300 m  (public transport can bridge the gap)
#   "far, no stop"      stop  > 300 m  (truly underserved)
# 300 m to a stop = same walk zone as I04b on the Infrastructure map (our assumption, straight line).
# Writes a NEW layer HH08, does not change HH07. Styles only HH08.
# Run in the Health project: Plugins > Python Console > Show Editor > open > Run

import os, time
import processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsVectorFileWriter, QgsMarkerSymbol,
                       QgsCategorizedSymbolRenderer, QgsRendererCategory)
from qgis.utils import iface

STOP_M = 300
FAR = ("600-900 m", "> 900 m")

prj = QgsProject.instance()

def find(test, what):
    for l in prj.mapLayers().values():
        if l.type() == l.VectorLayer and test(l):
            return l
    raise Exception(what + " not found in this project")

homes = find(lambda l: l.source().split("|")[0].endswith("walk_to_free_green_25832.gpkg"), "New HH07 homes file")
stops = find(lambda l: "I04_innenstadt_ost_stops" in l.name() and "walk" not in l.name(), "I04 stops layer")
OUT = os.path.dirname(homes.source().split("|")[0])

def run(alg, p):
    p["OUTPUT"] = "TEMPORARY_OUTPUT"
    return processing.run(alg, p)["OUTPUT"]

# 1 nearest stop for each home (straight line)
keep = [stops.fields()[0].name()]
j = run("native:joinbynearest", {"INPUT": homes, "INPUT_2": stops, "FIELDS_TO_COPY": keep,
                                 "DISCARD_NONMATCHING": False, "PREFIX": "stop_", "NEIGHBORS": 1})
nf = "n" if j.fields().indexOf("n") >= 0 else [f.name() for f in j.fields() if f.name().startswith("n_")][-1]
df = "distance" if j.fields().indexOf("distance") >= 0 else [f.name() for f in j.fields() if f.name().startswith("distance")][-1]
j = run("native:extractbyexpression", {"INPUT": j, "EXPRESSION": '"%s" = 1' % nf})   # ties: keep one row per home
j = run("native:fieldcalculator", {"INPUT": j, "FIELD_NAME": "stop_m", "FIELD_TYPE": 0, "FIELD_LENGTH": 10,
                                   "FIELD_PRECISION": 0, "FORMULA": 'round("%s")' % df})

def access(k):
    return ("CASE WHEN \"class_%s\" IN ('%s') THEN CASE WHEN \"stop_m\" <= %d THEN 'Far, stop nearby' "
            "ELSE 'Far, no stop' END ELSE 'Near on foot' END" % (k, "','".join(FAR), STOP_M))
for k in ("C", "D"):
    j = run("native:fieldcalculator", {"INPUT": j, "FIELD_NAME": "access_" + k, "FIELD_TYPE": 2,
                                       "FIELD_LENGTH": 20, "FORMULA": access(k)})
orig = [f.name() for f in homes.fields() if f.name().lower() not in ("fid", "ogc_fid")]
j = run("native:retainfields", {"INPUT": j, "FIELDS": orig + ["stop_m", "access_C", "access_D"]})

# 2 save as HH08
name = "HH08_innenstadt_ost_homes_transit_backup_25832"
path = os.path.join(OUT, name + ".gpkg")
for old in [l for l in prj.mapLayers().values() if l.source().split("|")[0] == path]:
    prj.removeMapLayer(old.id())
if os.path.exists(path):
    try:
        os.remove(path)
    except OSError:
        path = os.path.join(OUT, name + time.strftime("_%H%M%S") + ".gpkg")
opt = QgsVectorFileWriter.SaveVectorOptions()
opt.driverName = "GPKG"; opt.layerName = name
opt.attributes = [i for i, f in enumerate(j.fields()) if f.name().lower() not in ("fid", "ogc_fid")]
err, msg, newfile, _ = QgsVectorFileWriter.writeAsVectorFormatV3(j, path, prj.transformContext(), opt)
if err != QgsVectorFileWriter.NoError:
    raise Exception(msg)

# 3 report
F = list(QgsVectorLayer(newfile + "|layername=" + name, "tmp", "ogr").getFeatures())
P = lambda fs: sum(f["pop_est"] or 0 for f in fs)
HOT = ("Strong heat load", "Extreme heat load")
print("\n=== Public transport as backup (stop within %d m, straight line) ===" % STOP_M)
print("Homes: %d   People: %.0f" % (len(F), P(F)))
for k, what in (("C", "doctor / clinic"), ("D", "pharmacy")):
    far = [f for f in F if f["access_" + k] != "Near on foot"]
    near_stop = [f for f in far if f["access_" + k] == "Far, stop nearby"]
    no_stop = [f for f in far if f["access_" + k] == "Far, no stop"]
    print("\n%s  (> 600 m walk)" % what)
    print("   far on foot:          %6.0f people" % P(far))
    print("     with stop nearby:   %6.0f" % P(near_stop))
    print("     no stop nearby:     %6.0f   <- truly underserved" % P(no_stop))
    print("   in strong/extreme heat and no stop: %.0f" % P([f for f in no_stop if f["heat_class"] in HOT]))

# 4 add and style (D shown; switch the field to access_C for doctors)
lyr = QgsVectorLayer(newfile + "|layername=" + name, "HH08 homes: pharmacy by foot or transit", "ogr")
prj.addMapLayer(lyr)
def mk(c, s, oc="#000000", ow=0):
    return QgsMarkerSymbol.createSimple({"name": "circle", "color": c, "size": str(s),
                                         "outline_color": oc, "outline_width": str(ow)})
lyr.setRenderer(QgsCategorizedSymbolRenderer("access_D", [
    QgsRendererCategory("Near on foot",     mk("#d9d9d9", 0.8), "Pharmacy <= 600 m on foot"),
    QgsRendererCategory("Far, stop nearby", mk("#fdae61", 1.0), "Far, but bus/tram stop <= 300 m"),
    QgsRendererCategory("Far, no stop",     mk("#a50026", 1.4, "#000000", 0.1), "Far and no stop nearby"),
]))
lyr.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(lyr.id())
print("\nSaved:", newfile)
print("Map shows D (pharmacy). For doctors: Symbology > Value = access_C > Classify.")
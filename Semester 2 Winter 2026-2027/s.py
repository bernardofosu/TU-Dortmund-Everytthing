# H19d Species records (GBIF, H10a) inside the road risk zones (H19b)
# Which wild species are recorded close to busy roads, and which groups are road-sensitive?
# Road-sensitive groups below are OUR CHOICE for this map (amphibians, reptiles, mammals);
# check against Fahrig & Rytwinski (2009) before citing.
# Run after H19_road_risk_buffers.py, in the Habitat project.
# Run: Plugins > Python Console > Show Editor > open > Run

import os, time
import processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem,
                       QgsMarkerSymbol, QgsCategorizedSymbolRenderer, QgsRendererCategory)
from qgis.utils import iface

SPECIES = "H10a_innenstadt_ost_species_gbif"
ZONES   = "H19b_innenstadt_ost_road_risk_zones_25832"
SENSITIVE = ("Amphibia", "Reptilia", "Mammalia")      # GBIF "class" values

prj = QgsProject.instance()
CRS = QgsCoordinateReferenceSystem("EPSG:25832")

def layer(part):
    for l in prj.mapLayers().values():
        if part.lower() in l.name().lower() and l.type() == l.VectorLayer:
            return l
    raise Exception("Layer not found: " + part)

sp, zones = layer(SPECIES), layer(ZONES)
OUT = os.path.dirname(zones.source().split("|")[0])
f_species = "species" if sp.fields().indexOf("species") >= 0 else None
f_class   = "class"   if sp.fields().indexOf("class")   >= 0 else None
if not f_species:
    raise Exception("Field 'species' not found in " + sp.name())
if not f_class:
    print("No field 'class' in species layer: road-sensitive groups cannot be flagged, all counted.")

def run(alg, params):
    params["OUTPUT"] = "TEMPORARY_OUTPUT"
    return processing.run(alg, params)["OUTPUT"]

sp25832 = run("native:reprojectlayer", {"INPUT": sp, "TARGET_CRS": CRS})
inside = run("native:joinattributesbylocation", {"INPUT": sp25832, "JOIN": zones, "PREDICATE": [5],
                                                 "JOIN_FIELDS": ["risk_tier"], "METHOD": 2,
                                                 "DISCARD_NONMATCHING": True, "PREFIX": ""})
if f_class:
    inside = run("native:fieldcalculator", {"INPUT": inside, "FIELD_NAME": "road_sensitive",
                 "FIELD_TYPE": 2, "FIELD_LENGTH": 3,
                 "FORMULA": "CASE WHEN \"%s\" IN (%s) THEN 'yes' ELSE 'no' END"
                            % (f_class, ",".join("'%s'" % c for c in SENSITIVE))})

# save
name = "H19d_innenstadt_ost_species_in_road_risk_25832"
path = os.path.join(OUT, name + ".gpkg")
if os.path.exists(path):
    try:
        os.remove(path)
    except OSError:
        path = os.path.join(OUT, name + time.strftime("_%H%M%S") + ".gpkg")
opt = QgsVectorFileWriter.SaveVectorOptions()
opt.driverName = "GPKG"; opt.layerName = name
opt.attributes = [i for i, f in enumerate(inside.fields()) if f.name().lower() not in ("fid", "ogc_fid")]
err, msg, newfile, _ = QgsVectorFileWriter.writeAsVectorFormatV3(inside, path, prj.transformContext(), opt)
if err != QgsVectorFileWriter.NoError:
    raise Exception(msg)
for old in [l for l in prj.mapLayers().values() if l.name() == name]:
    prj.removeMapLayer(old.id())
H19d = QgsVectorLayer(newfile + "|layername=" + name, name, "ogr")
prj.addMapLayer(H19d)

# ---------- report ----------
total_all = sp25832.featureCount()
rows = list(H19d.getFeatures())
print("\n=== Wild species records in road risk zones ===")
print("  Records in district: %d   in risk zones: %d (%.1f %%)"
      % (total_all, len(rows), 100 * len(rows) / total_all if total_all else 0))
print("  Species in risk zones: %d" % len({r[f_species] for r in rows if r[f_species]}))
if f_class:
    by_class = {}
    for r in rows:
        k = r[f_class] or "unknown"
        by_class[k] = by_class.get(k, 0) + 1
    print("\n  Records by group (class):")
    for k, v in sorted(by_class.items(), key=lambda x: -x[1]):
        print("     %-16s %5d %s" % (k, v, " <- road-sensitive" if k in SENSITIVE else ""))
    sens = {}
    for r in rows:
        if r["road_sensitive"] == "yes" and r[f_species]:
            sens[(r[f_class], r[f_species])] = sens.get((r[f_class], r[f_species]), 0) + 1
    print("\n  Road-sensitive species in risk zones:")
    for (c, s), v in sorted(sens.items(), key=lambda x: (x[0][0], -x[1])):
        print("     %-10s %-35s %3d records" % (c, s, v))
    if not sens:
        print("     none recorded")

# ---------- style: road-sensitive records stand out ----------
if f_class:
    H19d.setRenderer(QgsCategorizedSymbolRenderer("road_sensitive", [
        QgsRendererCategory("yes", QgsMarkerSymbol.createSimple(
            {"name": "triangle", "color": "#ffff00", "size": "3", "outline_color": "#000000",
             "outline_width": "0.4"}), "Road-sensitive species (amphibians, reptiles, mammals)"),
        QgsRendererCategory("no", QgsMarkerSymbol.createSimple(
            {"name": "circle", "color": "#ffffff", "size": "1.4", "outline_color": "#000000",
             "outline_width": "0.2"}), "Other wild species record"),
    ]))
H19d.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(H19d.id())
print("\nSaved:", newfile)
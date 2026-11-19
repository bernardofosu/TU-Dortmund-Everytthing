# H19 Road risk zones for species, Innenstadt-Ost (Habitat map)
# Busy roads kill animals (collisions), cut habitats apart and bring noise and light.
# This script:
#   H19a  busy roads inside the district, sorted into 3 risk tiers
#   H19b  buffer (risk zone) around each tier, dissolved, clipped to the district
#   H19c  habitat patches (H05) that lie inside a risk zone = conflict areas
# Buffer widths are OUR ASSUMPTIONS (see TIERS). The idea of a "road-effect zone" comes from
# Forman & Deblinger (2000), whose zone for a 4-lane suburban highway was far wider (about 600 m on average);
# we use narrower urban widths so the map shows differences inside the district.
# Styles only the 3 new layers. Nothing else is moved, ticked or changed.
# Run: Plugins > Python Console > Show Editor > open > Run

import os, time
import processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem,
                       QgsProperty, QgsFillSymbol, QgsLineSymbol, QgsCategorizedSymbolRenderer,
                       QgsRendererCategory, QgsSingleSymbolRenderer, QgsLinePatternFillSymbolLayer,
                       QgsSimpleFillSymbolLayer, QgsUnitTypes)
from qgis.utils import iface

ROADS     = "Dortmund_Lines_Fixed"
BOUNDARY  = "00_innenstadt_ost_boundary_25832"
HABITAT   = "H05_innenstadt_ost_habitat_patches_dissolve"
HABITAT_LABELS = ["Woodland", "Urban green", "Open land", "Wetland", "Water", "Bare / pioneer land"]

# tier label, OSM highway values, buffer in metres (assumption)
TIERS = [
    ("1 Motorway / trunk",      ("motorway", "motorway_link", "trunk", "trunk_link"), 100),
    ("2 Primary road",          ("primary", "primary_link"),                            50),
    ("3 Secondary road",        ("secondary", "secondary_link"),                        30),
]

prj = QgsProject.instance()
CRS = QgsCoordinateReferenceSystem("EPSG:25832")

def layer(name):
    for l in prj.mapLayers().values():
        if l.name() == name:
            return l
    for l in prj.mapLayers().values():
        if name.lower() in l.name().lower() and l.type() == l.VectorLayer:
            return l
    raise Exception("Layer not found: " + name)

roads, bnd, hab = layer(ROADS), layer(BOUNDARY), layer(HABITAT)
OUT = os.path.join(os.path.dirname(hab.source().split("|")[0]), "H19_road_risk")
os.makedirs(OUT, exist_ok=True)

def run(alg, params):
    params["OUTPUT"] = "TEMPORARY_OUTPUT"
    return processing.run(alg, params)["OUTPUT"]

def save(lyr, name):
    path = os.path.join(OUT, name + ".gpkg")
    for ext in ("", "-wal", "-shm"):
        if os.path.exists(path + ext):
            try:
                os.remove(path + ext)
            except OSError:
                path = os.path.join(OUT, name + time.strftime("_%H%M%S") + ".gpkg")
                break
    opt = QgsVectorFileWriter.SaveVectorOptions()
    opt.driverName = "GPKG"
    opt.layerName = name
    opt.attributes = [i for i, f in enumerate(lyr.fields()) if f.name().lower() not in ("fid", "ogc_fid")]
    err, msg, newfile, _ = QgsVectorFileWriter.writeAsVectorFormatV3(lyr, path, prj.transformContext(), opt)
    if err != QgsVectorFileWriter.NoError:
        raise Exception(msg)
    for old in [l for l in prj.mapLayers().values() if l.name() == name]:
        prj.removeMapLayer(old.id())
    out = QgsVectorLayer(newfile + "|layername=" + name, name, "ogr")
    prj.addMapLayer(out)
    return out

# ---------- 1 busy roads with tier and buffer width ----------
if roads.fields().indexOf("highway") < 0:
    raise Exception("Field 'highway' not found in " + ROADS)
r25832 = run("native:reprojectlayer", {"INPUT": roads, "TARGET_CRS": CRS})
b25832 = run("native:reprojectlayer", {"INPUT": bnd, "TARGET_CRS": CRS})

all_vals = [v for _, vals, _ in TIERS for v in vals]
busy = run("native:extractbyexpression", {"INPUT": r25832,
           "EXPRESSION": '"highway" IN (' + ",".join("'%s'" % v for v in all_vals) + ")"})
busy = run("native:clip", {"INPUT": busy, "OVERLAY": b25832})

tier_case = "CASE " + " ".join(
    "WHEN \"highway\" IN (%s) THEN '%s'" % (",".join("'%s'" % v for v in vals), lab)
    for lab, vals, _ in TIERS) + " END"
buf_case = "CASE " + " ".join(
    "WHEN \"highway\" IN (%s) THEN %d" % (",".join("'%s'" % v for v in vals), m)
    for _, vals, m in TIERS) + " END"
busy = run("native:fieldcalculator", {"INPUT": busy, "FIELD_NAME": "risk_tier", "FIELD_TYPE": 2,
                                      "FIELD_LENGTH": 30, "FORMULA": tier_case})
busy = run("native:fieldcalculator", {"INPUT": busy, "FIELD_NAME": "buffer_m", "FIELD_TYPE": 1,
                                      "FIELD_LENGTH": 5, "FORMULA": buf_case})
busy = run("native:retainfields", {"INPUT": busy, "FIELDS": ["highway", "name", "risk_tier", "buffer_m"]}) \
    if busy.fields().indexOf("name") >= 0 else \
    run("native:retainfields", {"INPUT": busy, "FIELDS": ["highway", "risk_tier", "buffer_m"]})
H19a = save(busy, "H19a_innenstadt_ost_busy_roads_25832")

# ---------- 2 risk zones: buffer per tier, dissolve, clip ----------
buf = run("native:buffer", {"INPUT": busy, "DISTANCE": QgsProperty.fromExpression('"buffer_m"'),
                            "SEGMENTS": 8, "END_CAP_STYLE": 0, "JOIN_STYLE": 0, "DISSOLVE": False})
buf = run("native:dissolve", {"INPUT": buf, "FIELD": ["risk_tier"]})
buf = run("native:clip", {"INPUT": buf, "OVERLAY": b25832})
# a higher tier wins where zones overlap: cut tier 2 by tier 1, tier 3 by tiers 1 and 2
parts = []
for i, (lab, _, _) in enumerate(TIERS):
    this = run("native:extractbyexpression", {"INPUT": buf, "EXPRESSION": "\"risk_tier\" = '%s'" % lab})
    higher = [t[0] for t in TIERS[:i]]
    if higher:
        hi = run("native:extractbyexpression", {"INPUT": buf, "EXPRESSION":
                 '"risk_tier" IN (' + ",".join("'%s'" % h for h in higher) + ")"})
        this = run("native:difference", {"INPUT": this, "OVERLAY": hi})
    parts.append(this)
zones = run("native:mergevectorlayers", {"LAYERS": parts, "CRS": CRS})
zones = run("native:retainfields", {"INPUT": zones, "FIELDS": ["risk_tier"]})
zones = run("native:fieldcalculator", {"INPUT": zones, "FIELD_NAME": "area_ha", "FIELD_TYPE": 0,
                                       "FIELD_LENGTH": 10, "FIELD_PRECISION": 2,
                                       "FORMULA": "round($area / 10000, 2)"})
H19b = save(zones, "H19b_innenstadt_ost_road_risk_zones_25832")

# ---------- 3 habitat inside risk zones ----------
rend = hab.renderer()
if not isinstance(rend, QgsCategorizedSymbolRenderer):
    raise Exception("H05 must be categorized (Woodland, Urban green ...)")
field = rend.classAttribute()
vals = [c.value() for c in rend.categories() if c.label() in HABITAT_LABELS]
lab_of = {str(c.value()): c.label() for c in rend.categories()}
hab25832 = run("native:reprojectlayer", {"INPUT": hab, "TARGET_CRS": CRS})
green = run("native:extractbyexpression", {"INPUT": hab25832, "EXPRESSION":
            '"%s" IN (%s)' % (field, ",".join("'%s'" % str(v).replace("'", "''") for v in vals))})
conf = run("native:intersection", {"INPUT": green, "OVERLAY": zones,
                                   "INPUT_FIELDS": [field], "OVERLAY_FIELDS": ["risk_tier"]})
conf = run("native:fieldcalculator", {"INPUT": conf, "FIELD_NAME": "area_ha", "FIELD_TYPE": 0,
                                      "FIELD_LENGTH": 10, "FIELD_PRECISION": 2,
                                      "FORMULA": "round($area / 10000, 2)"})
H19c = save(conf, "H19c_innenstadt_ost_habitat_in_road_risk_25832")

# ---------- report ----------
print("\n=== Road risk for species, Innenstadt-Ost ===")
km = {}
for f in H19a.getFeatures():
    km[f["risk_tier"]] = km.get(f["risk_tier"], 0) + f.geometry().length() / 1000
for lab, _, m in TIERS:
    print("  %-22s buffer %3d m   roads %6.2f km" % (lab, m, km.get(lab, 0)))
zone_ha = sum(f["area_ha"] for f in H19b.getFeatures())
hab_ha = sum(f.geometry().area() for f in green.getFeatures()) / 10000
conf_ha = sum(f["area_ha"] for f in H19c.getFeatures())
print("  Risk zones total:          %7.1f ha" % zone_ha)
print("  Habitat (green/blue) total: %7.1f ha" % hab_ha)
print("  Habitat inside risk zones:  %7.1f ha  (%.1f %% of habitat)" % (conf_ha, 100 * conf_ha / hab_ha if hab_ha else 0))
by = {}
for f in H19c.getFeatures():
    k = lab_of.get(str(f[field]), str(f[field]))
    by[k] = by.get(k, 0) + f["area_ha"]
for k, v in sorted(by.items(), key=lambda x: -x[1]):
    print("     %-22s %6.1f ha" % (k, v))

# ---------- style the 3 new layers ----------
def hatch(color, width=0.25, dist=1.6, outline=None):
    s = QgsFillSymbol(); s.deleteSymbolLayer(0)
    lp = QgsLinePatternFillSymbolLayer(); lp.setLineAngle(45); lp.setDistance(dist)
    lp.setDistanceUnit(QgsUnitTypes.RenderMillimeters)
    lp.setSubSymbol(QgsLineSymbol.createSimple({"color": color, "width": str(width)}))
    s.appendSymbolLayer(lp)
    if outline:
        s.appendSymbolLayer(QgsSimpleFillSymbolLayer.create(
            {"style": "no", "outline_color": outline, "outline_width": "0.3"}))
    return s

COL = {TIERS[0][0]: "#99000d", TIERS[1][0]: "#e31a1c", TIERS[2][0]: "#fc9272"}
H19b.setRenderer(QgsCategorizedSymbolRenderer("risk_tier", [
    QgsRendererCategory(lab, hatch(COL[lab], 0.25, 1.6, COL[lab]),
                        "Risk zone %s m: %s" % (m, lab[2:])) for lab, _, m in TIERS]))
H19a.setRenderer(QgsCategorizedSymbolRenderer("risk_tier", [
    QgsRendererCategory(lab, QgsLineSymbol.createSimple({"color": COL[lab], "width": "0.9"}), lab[2:])
    for lab, _, _ in TIERS]))
H19c.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
    {"color": "#e31a1c", "outline_color": "#67000d", "outline_width": "0.2"})))
H19c.setOpacity(0.65)
for l in (H19a, H19b, H19c):
    l.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(l.id())

print("\nSaved to:", OUT)
print("New layers are at the top of the panel. Drag them below H13 key places if you like.")
# HH01: give pharmacies their own symbol (green cross), keep everything else as it is.
# Styles only. No data changed, no layer moved.
# Run: Plugins > Python Console > Show Editor > open > Run

from qgis.core import (QgsProject, QgsRuleBasedRenderer, QgsMarkerSymbol, QgsExpression,
                       QgsFeatureRequest)
from qgis.utils import iface

prj = QgsProject.instance()
L = None
for l in prj.mapLayers().values():
    if "HH01_innenstadt_ost_heat_sensitive_places" in l.name() and l.type() == l.VectorLayer:
        L = l
        break
if L is None:
    raise Exception("HH01 layer not found")

names = [f.name() for f in L.fields()]

# build the "is pharmacy" test from whatever columns exist
tests = []
if "amenity" in names:
    tests.append("lower(coalesce(\"amenity\", '')) = 'pharmacy'")
if "healthcare" in names:
    tests.append("lower(coalesce(\"healthcare\", '')) = 'pharmacy'")
if "shop" in names:
    tests.append("lower(coalesce(\"shop\", '')) = 'chemist'")
if "other_tags" in names:
    tests.append("coalesce(\"other_tags\", '') LIKE '%\"amenity\"=>\"pharmacy\"%'")
    tests.append("coalesce(\"other_tags\", '') LIKE '%\"healthcare\"=>\"pharmacy\"%'")
if "place_type" in names:
    tests.append("lower(coalesce(\"place_type\", '')) LIKE '%pharmac%'")
if "name" in names:
    tests.append("coalesce(\"name\", '') ILIKE '%apotheke%'")
if not tests:
    raise Exception("No column to recognise pharmacies. Columns: " + ", ".join(names))
PHARM = "(" + " OR ".join(tests) + ")"

n = sum(1 for _ in L.getFeatures(QgsFeatureRequest(QgsExpression(PHARM))))
print("Pharmacies found in HH01:", n)
if n == 0:
    raise Exception("No pharmacy found. Send Claude a screenshot of the HH01 attribute table.")

# turn the current style into rules (looks the same) and add a pharmacy rule on top
rb = L.renderer() if isinstance(L.renderer(), QgsRuleBasedRenderer) \
    else QgsRuleBasedRenderer.convertFromRenderer(L.renderer())
root = rb.rootRule()

# old pharmacy rule from an earlier run? remove it
for r in list(root.children()):
    if r.label() == "Pharmacy":
        root.removeChild(r)

# the shared "Doctor / pharmacy / other" rule: exclude pharmacies, rename
for r in root.children():
    if "pharmacy" in r.label().lower():
        if not r.isElse():
            f = r.filterExpression() or "TRUE"
            r.setFilterExpression("(%s) AND NOT %s" % (f, PHARM))
        r.setLabel("Doctor / other")

sym = QgsMarkerSymbol.createSimple({"name": "cross_fill", "color": "#1a9850", "size": "3.2",
                                    "outline_color": "#ffffff", "outline_width": "0.3"})
root.insertChild(0, QgsRuleBasedRenderer.Rule(sym, 0, 0, PHARM, "Pharmacy"))

L.setRenderer(rb)
L.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(L.id())
print("Done: pharmacies = green cross, 'Doctor / other' = grey dot. Hospital / clinic unchanged.")
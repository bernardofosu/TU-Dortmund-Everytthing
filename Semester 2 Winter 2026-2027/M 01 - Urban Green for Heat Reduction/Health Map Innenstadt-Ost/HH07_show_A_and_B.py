# Style the NEW HH07 homes layer as four views: A park, B cool place, C doctor/clinic, D pharmacy.
# Removes the OLD "HH07 homes A/B/C/D" layers from the panel (not the files), uses the newest HH07 file,
# and saves four map themes. Does not move layers or change data.
# Run: Plugins > Python Console > Show Editor > open > Run

from qgis.core import (QgsProject, QgsVectorLayer, QgsMarkerSymbol, QgsCategorizedSymbolRenderer,
                       QgsRendererCategory, QgsMapThemeCollection)
from qgis.utils import iface

prj = QgsProject.instance()
root = prj.layerTreeRoot()

# 1 the NEW layer = the one still carrying the file name and having the C/D fields
new = None
for l in prj.mapLayers().values():
    if "HH07_innenstadt_ost_homes_walk_to_free_green" in l.name() and l.fields().indexOf("class_C") >= 0:
        new = l
if new is None:
    raise Exception("New HH07 layer (with class_C) not found. Run HH07_homes_walk_to_free_green.py first.")
src_path = new.source()

# 2 remove old styled copies from the panel
for l in list(prj.mapLayers().values()):
    if l.name().startswith("HH07 homes") and l.id() != new.id():
        prj.removeMapLayer(l.id())

def mark(c, size, oc, ow):
    return QgsMarkerSymbol.createSimple({"name": "circle", "color": c, "size": str(size),
                                         "outline_color": oc, "outline_width": str(ow)})

def style(layer, field, what):
    layer.setRenderer(QgsCategorizedSymbolRenderer(field, [
        QgsRendererCategory("<= 300 m",   mark("#1a9850", 0.9, "#1a9850", 0),   "<= 300 m (~5 min) to " + what),
        QgsRendererCategory("300-600 m", mark("#fdae61", 0.9, "#fdae61", 0),   "300-600 m (~5-10 min)"),
        QgsRendererCategory("600-900 m", mark("#d7191c", 1.2, "#000000", 0.1), "600-900 m (~10-16 min)"),
        QgsRendererCategory("> 900 m",   mark("#67001f", 1.4, "#000000", 0.1), "> 900 m (> 16 min)"),
    ]))
    layer.triggerRepaint()

VIEWS = [("A", "HH07 homes A: walk to free green >= 1 ha", "free green >= 1 ha", "Health A: large free green"),
         ("B", "HH07 homes B: walk to any free cool place", "any free cool place", "Health B: any free cool place"),
         ("C", "HH07 homes C: walk to doctor / clinic", "doctor / clinic", "Health C: doctor / clinic"),
         ("D", "HH07 homes D: walk to pharmacy", "pharmacy", "Health D: pharmacy")]

layers = {}
for k, name, what, theme in VIEWS:
    if k == "A":
        lyr = new
        lyr.setName(name)
    else:
        lyr = QgsVectorLayer(src_path, name, "ogr")
        prj.addMapLayer(lyr)
    style(lyr, "class_" + k, what)
    layers[k] = lyr

# 3 map themes: same layers, only one homes view ticked
model = iface.layerTreeView().layerTreeModel()
themes = prj.mapThemeCollection()
for k, name, what, theme in VIEWS:
    for k2, l in layers.items():
        root.findLayer(l.id()).setItemVisibilityChecked(k2 == k)
    state = QgsMapThemeCollection.createThemeFromCurrentState(root, model)
    if themes.hasMapTheme(theme):
        themes.update(theme, state)
    else:
        themes.insert(theme, state)

for k2, l in layers.items():
    root.findLayer(l.id()).setItemVisibilityChecked(k2 == "A")
print("Done: 4 homes views (A, B, C, D) and 4 map themes. A is shown now.")
print("B, C, D were added at the top of the panel: drag them next to A if you like.")
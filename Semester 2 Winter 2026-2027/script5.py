# Land use as patterns on top of the heat classes (Climate Function map)
# Run: Plugins > Python Console > Show Editor > open > Run
# Adds "H03 land use overlay" at the top of the Layers panel, unticks original H03.

from qgis.core import (QgsProject, QgsVectorLayer, QgsFillSymbol, QgsLineSymbol,
                       QgsMarkerSymbol, QgsLinePatternFillSymbolLayer,
                       QgsPointPatternFillSymbolLayer, QgsRendererCategory,
                       QgsCategorizedSymbolRenderer, QgsUnitTypes)
from qgis.PyQt.QtGui import QColor

SRC_NAME = "H03_innenstadt_ost_habitat_class"
FIELD = "habitat_8class"

src = QgsProject.instance().mapLayersByName(SRC_NAME)
if not src:
    raise Exception("Layer not found: " + SRC_NAME)
src = src[0]

ov = QgsVectorLayer(src.source(), "H03 land use overlay", src.providerType())

def line_pattern(color, angle, dist, width):
    sym = QgsFillSymbol()
    sym.deleteSymbolLayer(0)
    lp = QgsLinePatternFillSymbolLayer()
    lp.setLineAngle(angle)
    lp.setDistance(dist)
    lp.setDistanceUnit(QgsUnitTypes.RenderMillimeters)
    lp.setSubSymbol(QgsLineSymbol.createSimple({"color": color, "width": str(width)}))
    sym.appendSymbolLayer(lp)
    return sym

def dot_pattern(color, dist, size):
    sym = QgsFillSymbol()
    sym.deleteSymbolLayer(0)
    pp = QgsPointPatternFillSymbolLayer()
    pp.setDistanceX(dist); pp.setDistanceY(dist)
    pp.setDistanceXUnit(QgsUnitTypes.RenderMillimeters)
    pp.setDistanceYUnit(QgsUnitTypes.RenderMillimeters)
    pp.setSubSymbol(QgsMarkerSymbol.createSimple(
        {"name": "circle", "color": color, "size": str(size), "outline_style": "no"}))
    sym.appendSymbolLayer(pp)
    return sym

# (value, legend text, symbol, show?)
classes = [
    ("Woodland",                "Woodland",                 dot_pattern("#00441b", 2.0, 0.6), True),
    ("Urban green",             "Urban green",              line_pattern("#1b5e20", 45, 2.0, 0.2), True),
    ("Water",                   "Water",                    line_pattern("#08519c", 0, 1.5, 0.25), True),
    ("Wetland",                 "Wetland",                  line_pattern("#08519c", 90, 2.0, 0.2), True),
    ("Open land / agriculture", "Open land / agriculture",  line_pattern("#636363", 135, 3.0, 0.2), True),
    ("Bare / pioneer land",     "Bare / pioneer land",      line_pattern("#8c6d31", 135, 3.0, 0.2), True),
    ("Built-up",                "Built-up (no pattern)",    QgsFillSymbol.createSimple({"style": "no", "outline_style": "no"}), False),
    ("Transport",               "Transport (no pattern)",   QgsFillSymbol.createSimple({"style": "no", "outline_style": "no"}), False),
]

cats = [QgsRendererCategory(v, s, lab, show) for v, lab, s, show in classes]
ov.setRenderer(QgsCategorizedSymbolRenderer(FIELD, cats))

QgsProject.instance().addMapLayer(ov, False)
root = QgsProject.instance().layerTreeRoot()
root.insertLayer(0, ov)                       # top of the Layers panel
root.findLayer(src.id()).setItemVisibilityChecked(False)   # untick original H03

ov.triggerRepaint()
print("Done: 'H03 land use overlay' added on top; original H03 unticked.")
print("Move key places (H13), labels and boundary above it if needed.")
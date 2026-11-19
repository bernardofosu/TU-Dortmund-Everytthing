# Climatopes as coloured outlines (no fill) on top of the heat classes
# Run: Plugins > Python Console > Show Editor > open > Run
# Makes a copy "02 climatope outline" with the same colours as strokes,
# drawn only on the inside edge so neighbouring climatopes don't overlap.

from qgis.core import (QgsProject, QgsVectorLayer, QgsFillSymbol,
                       QgsSimpleLineSymbolLayer, QgsCategorizedSymbolRenderer,
                       QgsRendererCategory, QgsUnitTypes)

SRC_NAME = "02_innenstadt_ost_climatope"
WIDTH_MM = 0.8          # drawn inside only, so it looks ~0.4 mm

src = QgsProject.instance().mapLayersByName(SRC_NAME)
if not src:
    raise Exception("Layer not found: " + SRC_NAME)
src = src[0]
r = src.renderer()
if not isinstance(r, QgsCategorizedSymbolRenderer):
    raise Exception("Climatope layer must use a Categorized style")

cats = []
for c in r.categories():
    col = c.symbol().color()
    sym = QgsFillSymbol()
    sym.deleteSymbolLayer(0)
    ln = QgsSimpleLineSymbolLayer(col, WIDTH_MM)
    ln.setWidthUnit(QgsUnitTypes.RenderMillimeters)
    ln.setDrawInsidePolygon(True)
    sym.appendSymbolLayer(ln)
    cats.append(QgsRendererCategory(c.value(), sym, c.label(), c.renderState()))

ov = QgsVectorLayer(src.source(), "02 climatope outline", src.providerType())
ov.setSubsetString(src.subsetString())
ov.setRenderer(QgsCategorizedSymbolRenderer(r.classAttribute(), cats))

QgsProject.instance().addMapLayer(ov, False)
QgsProject.instance().layerTreeRoot().insertLayer(0, ov)
ov.triggerRepaint()
print("Done: '02 climatope outline' added at the top (%d classes)." % len(cats))
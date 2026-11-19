# Restyle HH12 children under 10: cyan dots with dark outline (stand out on the orange/red heat map).
# Styles only. Run: Plugins > Python Console > Show Editor > open > Run
from qgis.core import QgsProject, QgsMarkerSymbol, QgsGraduatedSymbolRenderer, QgsRendererRange
lyr = next(l for l in QgsProject.instance().mapLayers().values() if l.name().startswith("HH12"))
def mk(s):
    return QgsMarkerSymbol.createSimple({"name": "circle", "color": "#00b4d8", "size": str(s),
                                         "outline_color": "#023e58", "outline_width": "0.2"})
lyr.setRenderer(QgsGraduatedSymbolRenderer("child10", [
    QgsRendererRange(0, 1, mk(0.6), "< 1 child"),
    QgsRendererRange(1, 3, mk(1.0), "1-3"),
    QgsRendererRange(3, 10, mk(1.6), "3-10"),
    QgsRendererRange(10, 100000, mk(2.4), "10 or more")]))
lyr.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(lyr.id())
print("HH12 restyled: cyan")
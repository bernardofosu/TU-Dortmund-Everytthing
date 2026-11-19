# Base land use (I00) as a light "stroke" design: each class keeps its colour as outline,
# with a very pale fill (or none). Styles only, keeps categories, does not move layers.
# Run: Plugins > Python Console > Show Editor > open > Run

from qgis.core import QgsProject, QgsFillSymbol, QgsCategorizedSymbolRenderer, QgsRuleBasedRenderer

FILL_OPACITY = 0.15     # 0 = outline only, 0.15 = pale tint
STROKE_WIDTH = "0.35"   # mm

# outline colour per class (matched by the start of the legend label)
COL = {
    "Grey: transport": "#9e9e9e",
    "Grey: industry": "#7a7a7a",
    "Grey: housing": "#b0b0b0",
    "Green": "#4daf4a",
    "Blue": "#3a8fd1",
    "Soil": "#b8955a",
    "Other": "#cccccc",
}

lyr = next(l for l in QgsProject.instance().mapLayers().values()
           if "I00_innenstadt_ost_landuse_full" in l.name())
r = lyr.renderer().clone()

def hex_alpha(h, a):
    h = h.lstrip("#")
    return "%d,%d,%d,%d" % (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * a))

def stroke(label):
    col = next((v for k, v in COL.items() if (label or "").startswith(k)), "#999999")
    print("%-45s outline %s" % (label, col))
    return QgsFillSymbol.createSimple({
        "color": hex_alpha(col, FILL_OPACITY),
        "style": "solid" if FILL_OPACITY > 0 else "no",
        "outline_color": col, "outline_width": STROKE_WIDTH,
        "outline_style": "solid", "joinstyle": "round"})

if isinstance(r, QgsCategorizedSymbolRenderer):
    for i, c in enumerate(r.categories()):
        r.updateCategorySymbol(i, stroke(c.label()))
elif isinstance(r, QgsRuleBasedRenderer):
    def walk(rule):
        for ch in rule.children():
            if ch.symbol():
                ch.setSymbol(stroke(ch.label()))
            walk(ch)
    walk(r.rootRule())
else:
    raise Exception("I00 renderer is '%s'; set it to Categorized or Rule-based first" % r.type())

lyr.setRenderer(r)
lyr.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(lyr.id())
print("Done: I00 styled with strokes")
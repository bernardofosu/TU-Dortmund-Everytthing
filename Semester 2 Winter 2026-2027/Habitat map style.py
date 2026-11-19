# Habitat map Innenstadt-Ost: style ALL layers
# SAFE version: styles only. No layer moving, nothing ticked or unticked, no data changed.
# Labels (H13 key places) are kept as they are.
# Run: Plugins > Python Console > Show Editor > open > Run
# Change colours in the PALETTE block below if you want, then run again.

from qgis.core import (QgsProject, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol,
                       QgsSingleSymbolRenderer, QgsCategorizedSymbolRenderer,
                       QgsRuleBasedRenderer, QgsLinePatternFillSymbolLayer,
                       QgsSimpleFillSymbolLayer, QgsUnitTypes)
from qgis.utils import iface
from qgis.PyQt.QtGui import QColor

# ---------------- PALETTE ----------------
# Habitat classes (H05). Built-up is light grey so the green network stands out.
HABITAT = {
    "Woodland":          "#1b7837",
    "Urban green":       "#a6dba0",
    "Open land":         "#d9f0a3",
    "Wetland":           "#66c2a5",
    "Water":             "#6baed6",
    "Bare / pioneer land": "#dfc27d",
    "Built-up":          "#e0e0e0",
    "Transport":         "#bdbdbd",
}
TREE      = "#00441b"   # single trees (H09)
LSG       = "#33a02c"   # landscape protection area hatch
GLB       = "#33dd33"   # protected landscape component outline (H18b, H18c), same as legend
MONUMENT  = "#e6ac00"   # natural monument star (H18a), same as legend
DARK      = "#000000"   # dark green corridor hatch (H17)
LIGHT     = "#fff7bc"   # light zone (H17c)
MAIN_ROAD = "#7f7f7f"   # same as legend
STREET    = "#bdbdbd"   # same as legend
BOUNDARY  = "#ff00ff"
# ------------------------------------------

prj = QgsProject.instance()

def find_all(part):
    """all layers whose name contains part (H09 is in the project twice)"""
    out = [l for l in prj.mapLayers().values() if part.lower() in l.name().lower()]
    if not out:
        print("not found:", part)
    return out

def done(layer):
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())

def single(part, sym):
    for l in find_all(part):
        l.setRenderer(QgsSingleSymbolRenderer(sym.clone()))
        done(l)

def outline_only(color, width):
    return QgsFillSymbol.createSimple({"style": "no", "outline_color": color,
                                       "outline_width": str(width)})

def hatch(color, angles=(45,), dist=1.5, width=0.2, outline=None, outline_width=0.4, opacity=1.0):
    s = QgsFillSymbol()
    s.deleteSymbolLayer(0)
    for a in angles:
        lp = QgsLinePatternFillSymbolLayer()
        lp.setLineAngle(a)
        lp.setDistance(dist)
        lp.setDistanceUnit(QgsUnitTypes.RenderMillimeters)
        lp.setSubSymbol(QgsLineSymbol.createSimple({"color": color, "width": str(width)}))
        s.appendSymbolLayer(lp)
    if outline:
        s.appendSymbolLayer(QgsSimpleFillSymbolLayer.create(
            {"style": "no", "outline_color": outline, "outline_width": str(outline_width)}))
    s.setOpacity(opacity)
    return s

def mark(name, color, size, outline="#000000", ow=0.2, opacity=1.0):
    s = QgsMarkerSymbol.createSimple({"name": name, "color": color, "size": str(size),
                                      "outline_color": outline, "outline_width": str(ow)})
    s.setOpacity(opacity)
    return s

# ---------- H05 habitat classes: recolour the existing categories by their label ----------
for l in find_all("H05_innenstadt_ost_habitat_patches_dissolve"):
    r = l.renderer()
    if isinstance(r, QgsCategorizedSymbolRenderer):
        for i, c in enumerate(r.categories()):
            col = HABITAT.get(c.label())
            if col:
                r.updateCategorySymbol(i, QgsFillSymbol.createSimple(
                    {"color": col, "outline_style": "no"}))
            else:
                print("H05 class without colour (kept):", c.label())
        done(l)
    else:
        print("H05 is not categorized, skipped")

# ---------- protection ----------
single("H07b_innenstadt_ost_landscape_protection_LSG",
       hatch(LSG, (45,), 2.0, 0.2, outline=LSG, outline_width=0.4))
single("H18b_innenstadt_ost_ostfriedhof_protected_trees", outline_only(GLB, 0.8))
single("H18c_innenstadt_ost_pond_bird_grove", outline_only(GLB, 0.8))
single("H18a_innenstadt_ost_natural_monuments", mark("star", MONUMENT, 4.0, "#000000", 0.3))

# ---------- trees: small, half transparent, so they read as texture not as blobs ----------
single("H09_innenstadt_ost_trees", mark("circle", TREE, 0.7, TREE, 0, opacity=0.55))

# ---------- light at night ----------
single("H17 dark green", hatch(DARK, (45, 135), 1.6, 0.15, opacity=0.6))
single("H17c light zone", QgsFillSymbol.createSimple(
    {"color": LIGHT, "outline_style": "no"}))
for l in find_all("H17c light zone"):
    l.setOpacity(0.45)
    done(l)

# ---------- species records: keep each group's colour, make points smaller with white edge ----------
for l in find_all("H10a_innenstadt_ost_species_gbif"):
    r = l.renderer()
    if isinstance(r, QgsCategorizedSymbolRenderer):
        for i, c in enumerate(r.categories()):
            s = c.symbol().clone()
            s.setSize(1.3)
            for k in range(s.symbolLayerCount()):
                sl = s.symbolLayer(k)
                if hasattr(sl, "setStrokeColor"):
                    sl.setStrokeColor(QColor("#ffffff"))
                    sl.setStrokeWidth(0.15)
            r.updateCategorySymbol(i, s)
        done(l)
    else:
        l.setRenderer(QgsSingleSymbolRenderer(mark("circle", "#762a83", 1.3, "#ffffff", 0.15)))
        done(l)

# ---------- key places: keep labels, tidy marker ----------
single("H13_innenstadt_ost_key_places_final", mark("diamond", "#000000", 2.2, "#ffffff", 0.3))

# ---------- roads: recolour the two existing rules by label ----------
for l in find_all("Dortmund_Lines_Fixed"):
    r = l.renderer()
    if isinstance(r, QgsRuleBasedRenderer):
        for rule in r.rootRule().children():
            lab = rule.label().lower()
            if "main" in lab:
                rule.setSymbol(QgsLineSymbol.createSimple(
                    {"color": MAIN_ROAD, "width": "0.6", "capstyle": "round"}))
            elif "street" in lab:
                rule.setSymbol(QgsLineSymbol.createSimple(
                    {"color": STREET, "width": "0.25", "capstyle": "round"}))
        done(l)

# ---------- boundary ----------
single("00_innenstadt_ost_boundary_25832", outline_only(BOUNDARY, 0.8))

print("Habitat map styled. Nothing moved, nothing ticked or unticked.")
print("Remember: the legend HTML must use the same habitat colours (ask Claude to update it).")
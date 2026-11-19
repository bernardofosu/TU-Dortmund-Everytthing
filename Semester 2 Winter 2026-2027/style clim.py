# Climate function map Innenstadt-Ost: style ALL layers
# SAFE version: styles only. No layer moving, nothing ticked or unticked, no data changed,
# category LABELS are not changed (the health scripts read the heat labels).
# Run: Plugins > Python Console > Show Editor > open > Run
# Aim: heat classes read first, everything else (outlines, patterns, height points) calmer.

from qgis.core import (QgsProject, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol,
                       QgsSingleSymbolRenderer, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRuleBasedRenderer,
                       QgsLinePatternFillSymbolLayer, QgsSimpleFillSymbolLayer, QgsUnitTypes)
from qgis.utils import iface
from qgis.PyQt.QtGui import QColor

# ---------------- PALETTE ----------------
HEAT = {                         # 07 climate_cat, by label (ColorBrewer RdYlGn)
    "Cooling area":       "#1a9641",
    "Low heat load":      "#a6d96a",
    "Moderate heat load": "#fee08b",
    "Strong heat load":   "#f46d43",
    "Extreme heat load":  "#a50026",
}
CLIMATOPE_WIDTH  = 0.45   # inner edge lines of the climatopes (was thicker)
CLIMATOPE_ALPHA  = 0.85
PATTERN_WIDTH    = 0.15   # land use overlay hatch lines
PATTERN_ALPHA    = 0.55
HEIGHT_ALPHA     = 0.35   # 94 height points: background information only
COLD_AIR         = "#2171b5"
FLOW             = "#4292c6"
AIR_EXCHANGE     = "#ffd700"
MAIN_ROAD        = "#7f7f7f"
STREET           = "#bdbdbd"
BOUNDARY         = "#ff00ff"  # same as the other maps
# ------------------------------------------

prj = QgsProject.instance()

def find_all(part):
    out = [l for l in prj.mapLayers().values() if part.lower() in l.name().lower()]
    if not out:
        print("not found:", part)
    return out

def done(layer):
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())

def single(part, sym):
    for l in find_all(part):
        if l.type() != l.VectorLayer:
            continue
        l.setRenderer(QgsSingleSymbolRenderer(sym.clone()))
        done(l)

def mark(name, color, size, outline="#000000", ow=0.2):
    return QgsMarkerSymbol.createSimple({"name": name, "color": color, "size": str(size),
                                         "outline_color": outline, "outline_width": str(ow)})

def hatch_outline(color, dist=2.0, width=0.25, ow=0.5):
    s = QgsFillSymbol()
    s.deleteSymbolLayer(0)
    lp = QgsLinePatternFillSymbolLayer()
    lp.setLineAngle(45); lp.setDistance(dist)
    lp.setDistanceUnit(QgsUnitTypes.RenderMillimeters)
    lp.setSubSymbol(QgsLineSymbol.createSimple({"color": color, "width": str(width)}))
    s.appendSymbolLayer(lp)
    s.appendSymbolLayer(QgsSimpleFillSymbolLayer.create(
        {"style": "no", "outline_color": color, "outline_width": str(ow)}))
    return s

def each_category(layer, fn):
    """run fn(index, symbol_clone) on every category / range; fn returns the new symbol"""
    r = layer.renderer()
    if isinstance(r, QgsCategorizedSymbolRenderer):
        for i, c in enumerate(r.categories()):
            r.updateCategorySymbol(i, fn(c.label(), c.symbol().clone()))
    elif isinstance(r, QgsGraduatedSymbolRenderer):
        for i, rg in enumerate(r.ranges()):
            r.updateRangeSymbol(i, fn(rg.label(), rg.symbol().clone()))
    else:
        return False
    return True

# ---------- 07 heat classes: new colours, same labels ----------
for l in find_all("07_innenstadt_ost_climate_cat"):
    if l.type() != l.VectorLayer or "night" in l.name().lower():
        continue                         # skip the joined "— 06b…night" copy
    def heat(label, s):
        col = HEAT.get(label)
        if col:
            return QgsFillSymbol.createSimple({"color": col, "outline_style": "no"})
        print("07 class without colour (kept):", label)
        return s
    if each_category(l, heat):
        done(l)

# ---------- 02 climatope outline: keep colours, thinner lines ----------
for l in find_all("climatope outline"):
    def thin(label, s):
        for k in range(s.symbolLayerCount()):
            sl = s.symbolLayer(k)
            if hasattr(sl, "setStrokeWidth"):
                sl.setStrokeWidth(CLIMATOPE_WIDTH)
            elif hasattr(sl, "setWidth"):
                sl.setWidth(CLIMATOPE_WIDTH)
            if hasattr(sl, "subSymbol") and sl.subSymbol():
                sl.subSymbol().setWidth(CLIMATOPE_WIDTH)
        return s
    if each_category(l, thin):
        l.setOpacity(CLIMATOPE_ALPHA)
        done(l)

# ---------- H03 land use overlay: keep patterns, thinner and lighter ----------
for l in find_all("H03 land use overlay"):
    def soft(label, s):
        for k in range(s.symbolLayerCount()):
            sl = s.symbolLayer(k)
            if isinstance(sl, QgsLinePatternFillSymbolLayer) and sl.subSymbol():
                sl.subSymbol().setWidth(PATTERN_WIDTH)
        return s
    if each_category(l, soft):
        l.setOpacity(PATTERN_ALPHA)
        done(l)

# ---------- 94 height points: keep classes, fade them ----------
for l in find_all("94_practice_points_height_clip"):
    l.setOpacity(HEIGHT_ALPHA)
    def small(label, s):
        s.setSize(1.0)
        return s
    each_category(l, small)
    done(l)

# ---------- cold air ----------
single("03_innenstadt_ost_coldair_production_1km", hatch_outline(COLD_AIR, 2.0, 0.25, 0.5))
# arrows keep their shape, size and rotation; only the colour changes
for l in find_all("03_innenstadt_ost_flow_arrows"):
    if l.type() != l.VectorLayer:
        continue
    r = l.renderer()
    if isinstance(r, QgsSingleSymbolRenderer):
        r.symbol().setColor(QColor(FLOW))
    else:
        def blue(label, s):
            s.setColor(QColor(FLOW))
            return s
        each_category(l, blue)
    done(l)

# ---------- air exchange points ----------
single("Air exchange area", mark("star", AIR_EXCHANGE, 4.5, "#000000", 0.3))
single("PL_KY_KL_Austausch", mark("star", AIR_EXCHANGE, 4.5, "#000000", 0.3))

# ---------- key places ----------
single("H13_innenstadt_ost_key_places_final", mark("diamond", "#000000", 2.2, "#ffffff", 0.3))

# ---------- roads ----------
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

# ---------- boundary (only the real one, not the copies) ----------
for l in prj.mapLayers().values():
    if l.name() == "00_innenstadt_ost_boundary_25832":
        l.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
            {"style": "no", "outline_color": BOUNDARY, "outline_width": "0.8"})))
        done(l)

print("Climate map styled. Nothing moved, nothing ticked or unticked, labels unchanged.")
print("Remember: the heat legend HTML must use the new HEAT colours (ask Claude to update it).")
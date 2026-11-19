# Health map Innenstadt-Ost: style the HH layers. SAFE: styles only, no layer moving, no data change.
# Run: Plugins > Python Console > Show Editor > open > Run

from qgis.core import (QgsProject, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsSymbol,
                       QgsSingleSymbolRenderer, QgsCategorizedSymbolRenderer, QgsRendererCategory,
                       QgsRuleBasedRenderer, QgsGraduatedSymbolRenderer, QgsRendererRange,
                       QgsLinePatternFillSymbolLayer, QgsSimpleFillSymbolLayer, QgsUnitTypes)
from qgis.PyQt.QtGui import QColor

prj = QgsProject.instance()

def find(part):
    best = None
    for l in prj.mapLayers().values():
        if l.name() == part:
            return l
        if part.lower() in l.name().lower() and best is None:
            best = l
    if best is None:
        print("not found:", part)
    return best

def fill(c, oc="no", ow=0.2, alpha=1.0):
    s = QgsFillSymbol.createSimple({"color": c, "outline_color": oc if oc != "no" else c,
                                    "outline_style": "no" if oc == "no" else "solid",
                                    "outline_width": str(ow)})
    s.setOpacity(alpha)
    return s

def outline(c, w=0.5, style="solid"):
    return QgsFillSymbol.createSimple({"style": "no", "outline_color": c, "outline_width": str(w),
                                       "outline_style": style})

def hatch(c, angle=45, dist=1.6, w=0.25, oc=None):
    s = QgsFillSymbol()
    s.deleteSymbolLayer(0)
    lp = QgsLinePatternFillSymbolLayer()
    lp.setLineAngle(angle); lp.setDistance(dist)
    lp.setDistanceUnit(QgsUnitTypes.RenderMillimeters)
    lp.setSubSymbol(QgsLineSymbol.createSimple({"color": c, "width": str(w)}))
    s.appendSymbolLayer(lp)
    if oc:
        ol = QgsSimpleFillSymbolLayer.create({"style": "no", "outline_color": oc, "outline_width": "0.3"})
        s.appendSymbolLayer(ol)
    return s

def mark(name, c, size, oc="#ffffff", ow=0.25):
    return QgsMarkerSymbol.createSimple({"name": name, "color": c, "size": str(size),
                                         "outline_color": oc, "outline_width": str(ow)})

def single(l, sym):
    if l:
        l.setRenderer(QgsSingleSymbolRenderer(sym)); l.triggerRepaint()

def cats(l, field, items):
    if l:
        l.setRenderer(QgsCategorizedSymbolRenderer(field, [QgsRendererCategory(v, s, lab) for v, lab, s in items]))
        l.triggerRepaint()

def rules(l, items):
    if not l:
        return
    r = QgsRuleBasedRenderer(QgsSymbol.defaultSymbol(l.geometryType()))
    top = r.rootRule(); top.removeChildAt(0)
    for lab, flt, sym in items:
        top.appendChild(QgsRuleBasedRenderer.Rule(sym, 0, 0, flt, lab))
    l.setRenderer(r); l.triggerRepaint()

# 1 heat base: keep its own classes, just lighter
heat = find("07_innenstadt_ost_climate_cat")
if heat:
    heat.setOpacity(0.55); heat.triggerRepaint()

# 2 homes by walking time to free green >= 1 ha (main message)
cats(find("HH07_innenstadt_ost_homes_walk_to_free_green"), "class_A", [
    ("<= 5 min",  "Home: <= 5 min to free green",  mark("circle", "#1a9850", 1.3, "#1a9850", 0)),
    ("5-10 min",  "Home: 5-10 min",                mark("circle", "#fdae61", 1.3, "#fdae61", 0)),
    ("10-15 min", "Home: 10-15 min",               mark("circle", "#d7191c", 1.6, "#000000", 0.15)),
    ("> 15 min",  "Home: > 15 min",                mark("circle", "#67001f", 1.8, "#000000", 0.15)),
])

# 3 free green destinations + paid / private green
single(find("HH02c_innenstadt_ost_free_green_destinations"), fill("#74c476", "#00441b", 0.4, 0.85))
rules(find("HH06_innenstadt_ost_paid_private_green"), [
    ("Paid entry (Westfalenpark)", "\"other_tags\" LIKE '%\"fee\"=>\"yes\"%'", hatch("#6a3d9a", 45, 1.4, 0.35, "#6a3d9a")),
    ("Private / restricted green", "ELSE",                                     hatch("#525252", 135, 1.4, 0.25, "#525252")),
])

# 4 walking zones (outline only so homes stay visible)
single(find("HH03fa_innenstadt_ost_walk_5min_to_free_green"), outline("#00441b", 0.5, "dash"))
single(find("HH03fb_innenstadt_ost_walk_10min_to_free_green"), outline("#00441b", 0.3, "dot"))
single(find("HH02bf_innenstadt_ost_free_entrances"), mark("circle", "#00441b", 0.9, "#ffffff", 0.1))

# 5 heat-sensitive places, red ring when > 10 min from free green
PT = '"place_type"'
FAR = ' AND "walk_free" = \'> 10 min\''
def place(shape, c, s):
    return mark(shape, c, s, "#ffffff", 0.3)
def far(shape, c, s):
    return mark(shape, c, s, "#e31a1c", 0.8)
rules(find("HH01_innenstadt_ost_heat_sensitive_places"), [
    ("Care home (> 10 min)",    PT + " ILIKE 'Care%'" + FAR,         far("square", "#7b3294", 3.2)),
    ("Kindergarten (> 10 min)", PT + " ILIKE 'Kindergarten%'" + FAR, far("triangle", "#e66101", 3.2)),
    ("School (> 10 min)",       PT + " = 'School'" + FAR,            far("diamond", "#2c7bb6", 3.2)),
    ("Care home / social facility", PT + " ILIKE 'Care%'",           place("square", "#7b3294", 2.6)),
    ("Kindergarten / childcare",    PT + " ILIKE 'Kindergarten%'",   place("triangle", "#e66101", 2.6)),
    ("School",                      PT + " = 'School'",              place("diamond", "#2c7bb6", 2.6)),
    ("Hospital / clinic",           PT + " ILIKE 'Hospital%'",       place("cross_fill", "#d7191c", 3.0)),
    ("Doctor / pharmacy / other",   "ELSE",                          place("circle", "#636363", 1.8)),
])

# 6 main road zone
single(find("HH04_innenstadt_ost_main_road_zone"), hatch("#737373", 45, 2.0, 0.2))

# 7 population grid (for an inset or toggle): graduated purple, no outline
pop = find("HH05_innenstadt_ost_population_100m")
if pop:
    edges = [(0, 25), (25, 75), (75, 150), (150, 250), (250, 100000)]
    cols = ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f"]
    labs = ["< 25", "25-75", "75-150", "150-250", "> 250"]
    rr = [QgsRendererRange(lo, hi, fill(c, alpha=0.8), "Residents per ha: " + lab)
          for (lo, hi), c, lab in zip(edges, cols, labs)]
    pop.setRenderer(QgsGraduatedSymbolRenderer("population", rr)); pop.triggerRepaint()

print("Health map styled. Untick: HH02, HH02b, HH03a/HH03b (all-green versions), I00, Dortmund_*_Fixed,")
print("and HH05 population (show it as an inset map instead).")
# Style water layers (W01-W03) for the infrastructure map. SAFE: styles only.
# Natural water = solid blue, artificial = dashed / dark blue. Run after copying W01-W03 in.

from qgis.core import (QgsProject, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol,
                       QgsRuleBasedRenderer, QgsSymbol)

prj = QgsProject.instance()

def find(part):
    for l in prj.mapLayers().values():
        if part.lower() in l.name().lower():
            return l
    print("not found:", part)
    return None

def rules(layer, items):
    if not layer:
        return
    r = QgsRuleBasedRenderer(QgsSymbol.defaultSymbol(layer.geometryType()))
    top = r.rootRule()
    top.removeChildAt(0)
    for label, flt, sym in items:
        top.appendChild(QgsRuleBasedRenderer.Rule(sym, 0, 0, flt, label))
    layer.setRenderer(r)
    layer.triggerRepaint()

def line(c, w, st="solid"):
    return QgsLineSymbol.createSimple({"color": c, "width": str(w), "line_style": st, "capstyle": "round"})

def poly(c, oc, st="solid"):
    return QgsFillSymbol.createSimple({"color": c, "outline_color": oc, "outline_width": "0.3",
                                       "outline_style": st})

def mark(n, c, s):
    return QgsMarkerSymbol.createSimple({"name": n, "color": c, "size": str(s),
                                         "outline_color": "#ffffff", "outline_width": "0.2"})

W = '"w_class"'
rules(find("W01_innenstadt_ost_water_lines"), [
    ("Stream (open)",                 W + " ILIKE 'Stream%'",    line("#2171b5", 0.7)),
    ("Stream in pipe (culverted)",    W + " ILIKE 'Culverted%'", line("#2171b5", 0.5, "dot")),
    ("Ditch / drain (artificial)",    W + " ILIKE 'Ditch%' OR " + W + " ILIKE 'Other%'", line("#08306b", 0.4, "dash")),
])
rules(find("W02_innenstadt_ost_water_areas"), [
    ("Pond / lake",                   W + " ILIKE 'Pond%'",      poly("#6baed6", "#2171b5")),
    ("Wetland",                       W + " ILIKE 'Wetland%'",   poly("#9ecae1", "#2171b5", "dash")),
    ("Rainwater retention basin",     W + " ILIKE 'Rainwater%'", poly("#c6dbef", "#08306b", "dash")),
    ("Swimming pool / fountain",      W + " ILIKE 'Swimming%' OR " + W + " ILIKE 'Fountain%'", poly("#4eb3d3", "#08306b")),
    ("Water supply / wastewater site", W + " ILIKE 'Water supply%'", poly("#08519c", "#000000")),
])
rules(find("W03_innenstadt_ost_water_points"), [
    ("Fountain / drinking water / well", W + " ILIKE 'Fountain%'",     mark("circle", "#4eb3d3", 1.8)),
    ("Water supply site (tower, pump)",  W + " ILIKE 'Water supply%'", mark("square", "#08519c", 2.6)),
    ("Spring",                           W + " ILIKE 'Spring%'",       mark("circle", "#2171b5", 1.8)),
])
print("Water styled. Move W01-W03 above I00 and below the roads.")
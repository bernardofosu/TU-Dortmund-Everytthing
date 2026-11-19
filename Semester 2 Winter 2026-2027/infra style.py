# Infrastructure map Innenstadt-Ost: style ALL layers + set layer order
# SAFE version: styles only, no layer moving.
# Run: Plugins > Python Console > Show Editor > open > Run
# Grey / green / blue / soil base from I00 (ALKIS nutzart), then grey network on top.

from qgis.core import (QgsProject, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol,
                       QgsRuleBasedRenderer, QgsSingleSymbolRenderer, QgsSymbol,
                       QgsLinePatternFillSymbolLayer, QgsUnitTypes)

prj = QgsProject.instance()
root = prj.layerTreeRoot()

def find(part):
    for l in prj.mapLayers().values():
        if part.lower() in l.name().lower():
            return l
    print("not found:", part)
    return None

def rules(layer, items):
    """items = [(label, filter, symbol)]; features matching no rule are not drawn"""
    if not layer:
        return
    r = QgsRuleBasedRenderer(QgsSymbol.defaultSymbol(layer.geometryType()))
    top = r.rootRule()
    top.removeChildAt(0)
    for label, flt, sym in items:
        top.appendChild(QgsRuleBasedRenderer.Rule(sym, 0, 0, flt, label))
    layer.setRenderer(r)
    layer.triggerRepaint()

def single(layer, sym):
    if layer:
        layer.setRenderer(QgsSingleSymbolRenderer(sym))
        layer.triggerRepaint()

def fill(color, alpha=255):
    s = QgsFillSymbol.createSimple({"color": color, "outline_style": "no"})
    s.setOpacity(alpha / 255)
    return s

def hatch(color, angle=45, dist=1.5, width=0.25, outline=None):
    s = QgsFillSymbol()
    s.deleteSymbolLayer(0)
    lp = QgsLinePatternFillSymbolLayer()
    lp.setLineAngle(angle); lp.setDistance(dist)
    lp.setDistanceUnit(QgsUnitTypes.RenderMillimeters)
    lp.setSubSymbol(QgsLineSymbol.createSimple({"color": color, "width": str(width)}))
    s.appendSymbolLayer(lp)
    return s

def line(color, width, style="solid"):
    return QgsLineSymbol.createSimple({"color": color, "width": str(width), "line_style": style,
                                       "capstyle": "round"})

def mark(name, color, size, outline="#000000"):
    return QgsMarkerSymbol.createSimple({"name": name, "color": color, "size": str(size),
                                         "outline_color": outline, "outline_width": "0.2"})

# ---------- I00 land use: grey / green / blue / soil ----------
N = '"nutzart"'
rules(find("I00_innenstadt_ost_landuse_full"), [
    ("Grey: transport (roads, paths, squares, rail)",
     N + " ILIKE '%verkehr%' OR " + N + " ILIKE 'Weg%' OR " + N + " ILIKE 'Platz%'", fill("#bdbdbd")),
    ("Grey: industry and commerce",
     N + " ILIKE '%Industrie%' OR " + N + " ILIKE '%Gewerbe%'", fill("#969696")),
    ("Grey: housing, mixed and public buildings",
     N + " ILIKE '%Wohnbau%' OR " + N + " ILIKE '%gemischt%' OR " + N + " ILIKE '%funktional%'", fill("#d9d9d9")),
    ("Green: parks, sport, cemeteries, woodland",
     N + " ILIKE '%Sport%' OR " + N + " ILIKE '%Erholung%' OR " + N + " ILIKE '%Friedhof%' OR "
     + N + " ILIKE '%Wald%' OR " + N + " ILIKE '%Gehölz%'", fill("#74c476")),
    ("Blue: water",
     N + " ILIKE '%Gewässer%' OR " + N + " ILIKE '%Hafen%'", fill("#6baed6")),
    ("Soil: open land, agriculture, bare land",
     N + " ILIKE '%Landwirtschaft%' OR " + N + " ILIKE '%Unland%' OR " + N + " ILIKE '%Heide%' OR "
     + N + " ILIKE '%Sumpf%' OR " + N + " ILIKE '%Moor%'", fill("#c9a66b")),
    ("Other", "ELSE", fill("#f0f0f0")),
])

# ---------- I01 roads and paths ----------
G = '"road_group"'
rules(find("I01_innenstadt_ost_roads_paths"), [
    ("Track",      G + " = 'Track'",      line("#8c6d31", 0.2, "dash")),
    ("Local road", G + " = 'Local road'", line("#ffffff", 0.35)),
    ("Footpath",   G + " = 'Footpath'",   line("#1b7a3a", 0.25, "dash")),
    ("Cycleway",   G + " = 'Cycleway'",   line("#2171b5", 0.35, "dot")),
    ("Main road",  G + " = 'Main road'",  line("#525252", 0.9)),
])

single(find("I02_innenstadt_ost_rail_tram"), line("#000000", 0.5, "dash"))
single(find("I03_innenstadt_ost_parking"), hatch("#636363", 45, 1.2, 0.2, outline="#636363"))
single(find("I04_innenstadt_ost_stops"), mark("circle", "#2171b5", 1.2, "#ffffff"))
single(find("I04b_innenstadt_ost_stop_walk"),
       QgsFillSymbol.createSimple({"style": "no", "outline_color": "#2171b5", "outline_width": "0.5",
                                   "outline_style": "dash"}))
single(find("I05b_innenstadt_ost_roads_at_air_exchange"), line("#e31a1c", 1.6))

# ---------- I06 energy (only meaningful objects drawn) ----------
OT = '"other_tags"'
rules(find("I06_innenstadt_ost_energy_osm_points"), [
    ("Solar PV", OT + " LIKE '%\"generator:source\"=>\"solar\"%'", mark("circle", "#fdd835", 1.8, "#7f6000")),
    ("Transformer (110 kV)", OT + " LIKE '%\"power\"=>\"transformer\"%'", mark("square", "#7b3294", 2.4)),
])
rules(find("I06_innenstadt_ost_energy_osm_lines"), [
    ("Power line 110 kV", OT + " LIKE '%\"power\"=>\"line\"%' AND " + OT + " LIKE '%110000%'",
     line("#7b3294", 0.6, "dash dot")),
])
rules(find("I06_innenstadt_ost_energy_osm_multipolygons"), [
    ("Heating plant", '"name" ILIKE \'%kraftwerk%\' OR ' + OT + " LIKE '%\"power\"=>\"plant\"%'",
     QgsFillSymbol.createSimple({"color": "#d7301f", "outline_color": "#000000", "outline_width": "0.3"})),
    ("Substation", OT + " LIKE '%\"power\"=>\"substation\"%'",
     QgsFillSymbol.createSimple({"color": "#c2a5cf", "outline_color": "#7b3294", "outline_width": "0.3"})),
])

single(find("I07_innenstadt_ost_water_infra"), mark("circle", "#08519c", 2.4, "#ffffff"))
single(find("I09_innenstadt_ost_waste_sites"), mark("triangle", "#8c510a", 1.8, "#ffffff"))
single(find("Klimaanalyse-Planungshinweiskarte"), mark("star", "#ffd700", 4.5))
single(find("00_innenstadt_ost_boundary_25832"),
       QgsFillSymbol.createSimple({"style": "no", "outline_color": "#ff00ff", "outline_width": "0.8"}))

print("Styled. Set layer order by hand (see chat). Nothing moved, nothing unticked.")
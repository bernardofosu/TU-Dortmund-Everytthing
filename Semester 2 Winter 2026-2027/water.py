# Water layers for Innenstadt-Ost from the OSM export (natural + artificial)
# Run: Plugins > Python Console > Show Editor > open > Run
# Output (folder created if missing):
#   W01_..._water_lines_25832     streams / ditches / canals / culverts  -> field w_class
#   W02_..._water_areas_25832     ponds, lakes, basins, pools, reservoirs -> field w_class
#   W03_..._water_points_25832    fountains, wells, water towers, pumps   -> field w_class
# Field "artificial" = yes / no for every feature.

import os, re, processing
from qgis.core import (QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsWkbTypes)
from qgis.PyQt.QtCore import QVariant

FOLDER = ("D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/"
          "M 01 - Urban Green for Heat Reduction/Water Map Innenstadt-Ost/02_data_clipped")
BOUNDARY = "00_innenstadt_ost_boundary_25832"
os.makedirs(FOLDER, exist_ok=True)

def lyr(n):
    l = QgsProject.instance().mapLayersByName(n)
    if not l:
        raise Exception("Layer not found: " + n)
    return l[0]

def tag(f, fields, key):
    """Value of an OSM key from its own column or from other_tags."""
    if key in fields and f[key] not in (None, ""):
        return str(f[key])
    ot = f["other_tags"] if "other_tags" in fields else None
    if ot:
        m = re.search(r'"%s"=>"([^"]*)"' % re.escape(key), str(ot))
        if m:
            return m.group(1)
    return ""

def classify(f, fields, geom):
    ww  = tag(f, fields, "waterway")
    nat = tag(f, fields, "natural")
    wat = tag(f, fields, "water")
    lu  = tag(f, fields, "landuse")
    lei = tag(f, fields, "leisure")
    am  = tag(f, fields, "amenity")
    mm  = tag(f, fields, "man_made")
    bas = tag(f, fields, "basin")
    tun = tag(f, fields, "tunnel")
    if geom == "line":
        if ww in ("river", "stream", "brook"):
            return ("Culverted stream (underground)" if tun in ("culvert", "yes") else "Stream / river", "no" if tun == "" else "yes")
        if ww in ("canal", "ditch", "drain"):
            return ("Ditch / drain / canal", "yes")
        if ww:
            return ("Other waterway (%s)" % ww, "yes")
        return None
    if geom == "area":
        if bas in ("retention", "detention", "infiltration") or wat in ("basin",) or lu == "basin":
            return ("Rainwater retention basin", "yes")
        if lei in ("swimming_pool", "water_park") or am == "swimming_pool":
            return ("Swimming pool", "yes")
        if mm in ("wastewater_plant", "reservoir_covered", "water_works", "storage_tank") or lu == "reservoir" or wat in ("reservoir", "wastewater"):
            return ("Water supply / wastewater site", "yes")
        if am == "fountain" or wat == "fountain":
            return ("Fountain", "yes")
        if nat == "water" or wat in ("pond", "lake", "oxbow") or lu == "pond":
            return ("Pond / lake", "no")
        if nat == "wetland":
            return ("Wetland", "no")
        return None
    # points
    if am in ("fountain", "drinking_water", "water_point") or mm in ("water_well", "water_tap"):
        return ("Fountain / drinking water / well", "yes")
    if mm in ("water_tower", "pumping_station", "water_works", "wastewater_plant", "storage_tank", "monitoring_station"):
        return ("Water supply site (%s)" % mm, "yes")
    if nat == "spring":
        return ("Spring", "no")
    if ww:
        return ("Waterway point (%s)" % ww, "yes")
    return None

def make_out(geomstr):
    l = QgsVectorLayer("%s?crs=EPSG:25832" % geomstr, "tmp", "memory")
    l.dataProvider().addAttributes([QgsField("name", QVariant.String, len=120),
                                    QgsField("w_class", QVariant.String, len=80),
                                    QgsField("artificial", QVariant.String, len=5),
                                    QgsField("length_m", QVariant.Double),
                                    QgsField("area_m2", QVariant.Double)])
    l.updateFields()
    return l

boundary = lyr(BOUNDARY)
jobs = [("Dortmund_Lines_Fixed", "line", "MultiLineString", "W01_innenstadt_ost_water_lines_25832"),
        ("Dortmund_Multipolygons_Fixed", "area", "MultiPolygon", "W02_innenstadt_ost_water_areas_25832"),
        ("Dortmund_Points_Fixed", "point", "Point", "W03_innenstadt_ost_water_points_25832")]

for src_name, geom, geomstr, out_name in jobs:
    src = lyr(src_name)
    rep = processing.run("native:reprojectlayer", {"INPUT": src, "TARGET_CRS": "EPSG:25832", "OUTPUT": "memory:"})["OUTPUT"]
    clip = processing.run("native:clip", {"INPUT": rep, "OVERLAY": boundary, "OUTPUT": "memory:"})["OUTPUT"]
    fields = [f.name() for f in clip.fields()]
    out = make_out(geomstr)
    counts = {}
    for f in clip.getFeatures():
        c = classify(f, fields, geom)
        if not c:
            continue
        g = f.geometry()
        if geom == "point" and g.isMultipart():
            g = g.pointOnSurface()
        nf = QgsFeature(out.fields())
        nf.setGeometry(g)
        nf.setAttributes([f["name"] if "name" in fields else None, c[0], c[1],
                          round(g.length(), 1) if geom == "line" else None,
                          round(g.area(), 1) if geom == "area" else None])
        out.dataProvider().addFeature(nf)
        counts[c[0]] = counts.get(c[0], 0) + 1
    print("\n==", out_name, ":", out.featureCount(), "features")
    for k, v in sorted(counts.items()):
        print("   ", k, ":", v)
    if out.featureCount():
        path = "%s/%s.gpkg" % (FOLDER, out_name)
        processing.run("native:savefeatures", {"INPUT": out, "OUTPUT": path})
        QgsProject.instance().addMapLayer(QgsVectorLayer(path, out_name, "ogr"))

print("\nDone. Style each layer: Categorized on w_class. Heavy rain and groundwater: external data (see chat).")
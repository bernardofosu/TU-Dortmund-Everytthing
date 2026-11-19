# Rebuild H13 key places with English names + themes, as a NEW file (v2).
# Close the other QGIS window first (only ONE project may have H13 open).
# Run: Plugins > Python Console > Show Editor > open > Run. Takes ~40 s.
#
# Positions: from H13 if it still has points, otherwise from H16.
# Names: names you typed by hand are kept; the rest are set from
#        OSM reverse geocoding + keyword rules (list below).
# Output: H13_innenstadt_ost_key_places_v3_25832.gpkg (same folder as H13/H16)

import os, json, time
from qgis.core import (QgsProject, QgsVectorLayer, QgsFeature, QgsField,
                       QgsCoordinateTransform, QgsCoordinateReferenceSystem,
                       QgsVectorFileWriter, QgsBlockingNetworkRequest, QgsGeometry)
from qgis.PyQt.QtCore import QVariant, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

def lyr(part):
    for l in QgsProject.instance().mapLayers().values():
        if part in l.name():
            return l
    return None

h13 = lyr("H13_innenstadt_ost_key_places_25832")
h16 = lyr("H16_innenstadt_ost_key_places_osm_25832")
h13_feats = list(h13.getFeatures()) if h13 else []
if h13_feats:
    src, feats = h13, h13_feats
elif h16:
    src, feats = h16, list(h16.getFeatures())
else:
    raise Exception("Neither H13 nor H16 found in the project")
print("Positions taken from:", src.name(), "(%d points really readable)" % len(feats))
if not feats:
    raise Exception("No readable points in " + src.name())

# OSM names in H16 (to tell them apart from names you typed by hand)
osm_names = set()
if h16:
    for f in h16.getFeatures():
        osm_names.add(str(f["name_en"]))

# Rules: first match wins. Each rule = (list of alternatives, final name).
# An alternative is a tuple of words that must ALL appear.
RULES = [
    ([("seerosen",), ("water lily",)],                  "Water Lily Pond"),
    ([("buschmühl",), ("buschmuhl",)],                  "Buschmühle Pond"),
    ([("rennbahn",), ("galopp",), ("racecourse",)],     "Dortmund Racecourse"),
    ([("wasserturm",), ("water tower",)],               "Südbahnhof Water Tower"),
    ([("großmarkt",), ("grossmarkt",), ("wholesale",)], "Wholesale market (Großmarkt)"),
    ([("südbad",), ("suedbad",)],                       "Südbad swimming pool"),
    ([("deggingstr",)],                                 "Open meadow at Deggingstraße"),
    ([("weißenburger",), ("weissenburger",)],           "Weißenburger Straße industrial area"),
    ([("josefinenstift",)],                             "St. Josefinenstift care home"),
    ([("zehnthof", "garten"), ("zehnthof", "allotment")], "Zehnthof allotment gardens"),
    ([("zehnthof",)],                                   "Zehnthof care centre"),
    ([("flora",)],                                      "Flora allotment gardens"),
    ([("sv körne",), ("sports ground",), ("sportplatz",)], "SV Körne 83 sports ground"),
    ([("kronen",)],                                     "Former Kronen Brewery"),
    ([("muk",), ("music and culture",)],                "MUK Music and Culture Centre"),
    ([("kaiserviertel",), ("senior",)],                 "Kaiserviertel Senior Centre"),
    ([("jüdisch",), ("jewish",), ("synagog",)],         "Jewish Community of Greater Dortmund"),
    ([("ostfriedhof",), ("east cemetery",)],            "Ostfriedhof"),
    ([("berswordt",)],                                  "Berswordt Primary School"),
    ([("gesamtschule",), ("comprehensive",)],           "Gartenstadt Comprehensive School"),
    ([("kronprinzenviertel",)],                         "Kronprinzenviertel (development site)"),
    ([("stadewäldchen",), ("stadewaldchen",)],          "Stadewäldchen"),
    ([("westfalenhalle",)],                             "Green area at the Westfalenhallen"),
    ([("ruhrallee",)],                                  "Ruhrallee"),
    ([("märkische",), ("markische",)],                  "Märkische Straße"),
    ([("bananen",)],                                    "Bananenradweg green corridor"),
    ([("kaiserbrunnen",), ("insel",)],                  "Kaiserbrunnen"),
    ([("körnepark",), ("körne park",)],                 "Körne Park"),
    ([("kaiserplatz",), ("kaiser square",)],            "Kaiser Square"),
    ([("gewerbe",), ("business park",), ("industrial",)], "Körne business park"),
    ([("westfalenpark",)],                              "Westfalenpark"),
]

THEME = {
    "Water Lily Pond": "Water, cooling",
    "Buschmühle Pond": "Water, cooling",
    "Dortmund Racecourse": "Cold air, outside",
    "Südbahnhof Water Tower": "Heat hotspot",
    "Wholesale market (Großmarkt)": "Heat hotspot",
    "Südbad swimming pool": "Health, Water",
    "Open meadow at Deggingstraße": "Urban green, cooling, cold air",
    "Weißenburger Straße industrial area": "Heat hotspot",
    "St. Josefinenstift care home": "Health, heat-sensitive people",
    "Zehnthof allotment gardens": "Urban green, cooling",
    "Zehnthof care centre": "Health, heat-sensitive people",
    "Flora allotment gardens": "Urban green, cooling",
    "SV Körne 83 sports ground": "Health, open space",
    "Former Kronen Brewery": "Heat hotspot",
    "MUK Music and Culture Centre": "Culture",
    "Kaiserviertel Senior Centre": "Health, heat-sensitive people",
    "Jewish Community of Greater Dortmund": "Culture",
    "Ostfriedhof": "Habitat, green, cooling",
    "Berswordt Primary School": "Health, heat-sensitive people",
    "Gartenstadt Comprehensive School": "Health, heat-sensitive people",
    "Kronprinzenviertel (development site)": "Urban green, cooling",
    "Stadewäldchen": "Habitat, green, cooling",
    "Green area at the Westfalenhallen": "Urban green, cooling, Habitat",
    "Ruhrallee": "Heat hotspot",
    "Märkische Straße": "Heat hotspot",
    "Bananenradweg green corridor": "Urban green, cooling, Habitat",
    "Kaiserbrunnen": "Urban green, cooling",
    "Körne Park": "Urban green, cooling",
    "Kaiser Square": "Heat hotspot",
    "Körne business park": "Heat hotspot",
    "Westfalenpark": "Urban green, cooling, cold air, Habitat",
}

tr = QgsCoordinateTransform(src.crs(), QgsCoordinateReferenceSystem("EPSG:4326"),
                            QgsProject.instance())

def reverse(lat, lon):
    url = ("https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=18"
           "&lat=%f&lon=%f&accept-language=de" % (lat, lon))
    req = QNetworkRequest(QUrl(url))
    req.setRawHeader(b"User-Agent", b"TU-Dortmund-student-QGIS")
    r = QgsBlockingNetworkRequest()
    if r.get(req) != QgsBlockingNetworkRequest.NoError:
        return ""
    d = json.loads(bytes(r.reply().content()).decode("utf-8"))
    parts = [d.get("name") or "", d.get("display_name") or ""]
    parts += [str(v) for v in d.get("address", {}).values()]
    return " ".join(parts)

def match(text):
    t = text.lower()
    for alts, name in RULES:
        for words in alts:
            if all(w in t for w in words):
                return name
    return None

fields_present = [f.name() for f in src.fields()]
def val(f, n):
    return f[n] if n in fields_present and f[n] not in (None, "") else None

out = QgsVectorLayer("Point?crs=EPSG:25832", "tmp", "memory")
pr = out.dataProvider()
pr.addAttributes([QgsField("name", QVariant.String, len=150),
                  QgsField("theme", QVariant.String, len=150),
                  QgsField("source", QVariant.String, len=150),
                  QgsField("how", QVariant.String, len=20)])
out.updateFields()

rows = []
for f in sorted(feats, key=lambda x: x.id()):
    g = QgsGeometry.fromPointXY(f.geometry().pointOnSurface().asPoint())  # works for Point and MultiPoint
    current = val(f, "name") or val(f, "name_en")
    if current and str(current) not in osm_names and str(current) in THEME:
        name, how = str(current), "kept"
    else:
        p = tr.transform(g.asPoint())
        info = reverse(p.y(), p.x())
        time.sleep(1.1)
        name = match(info + " " + str(current or "")) or current
        how = "osm-rule" if name != current else "unchanged"
    theme = THEME.get(str(name), val(f, "theme") or "CHECK")
    nf = QgsFeature(out.fields())
    nf.setGeometry(g)
    nf.setAttributes([name, theme, "© OpenStreetMap contributors, 2026", how])
    if not pr.addFeature(nf):
        print("COULD NOT ADD fid", f.id())
    rows.append((f.id(), name, theme, how))

folder = os.path.dirname(src.source().split("|")[0])
path = os.path.join(folder, "H13_innenstadt_ost_key_places_v3_25832.gpkg")
opt = QgsVectorFileWriter.SaveVectorOptions()
opt.driverName = "GPKG"
print("Points in memory before saving:", out.featureCount())
err = QgsVectorFileWriter.writeAsVectorFormatV3(out, path, QgsProject.instance().transformContext(), opt)
print("Write result:", err[0], err[1])
QgsProject.instance().addMapLayer(QgsVectorLayer(path, "H13_innenstadt_ost_key_places_v3_25832", "ogr"))

print("\nold fid | name | theme | how")
for r in rows:
    print(" | ".join(str(x) for x in r))
names = [r[1] for r in rows]
dups = sorted({n for n in names if names.count(n) > 1})
print("\nDuplicates to check by hand:", dups)
print("Missing names:", [r[0] for r in rows if not r[1]])
print("Saved:", path)
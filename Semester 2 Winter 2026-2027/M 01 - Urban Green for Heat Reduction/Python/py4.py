"""
Add key places to H13 by looking them up in OpenStreetMap (Nominatim).
Run in QGIS: Plugins > Python Console > Show Editor > paste > Run.
"""
import json
import time
from qgis.core import (QgsProject, QgsFeature, QgsGeometry, QgsPointXY,
                       QgsCoordinateTransform, QgsCoordinateReferenceSystem,
                       QgsBlockingNetworkRequest)
from qgis.PyQt.QtCore import QUrl, QUrlQuery
from qgis.PyQt.QtNetwork import QNetworkRequest

LAYER_NAME = "H13_innenstadt_ost_key_places_25832"

# search text, name, theme, source
PLACES = [
    ("Westfalenhallen, Dortmund", "Green area at the Westfalenhallen", "climate (green corridor)", "INSEKT 2021, p. 52"),
    ("Kaiserbrunnen, Dortmund", "Kaiserbrunnen", "climate (green deficit)", "INSEKT 2021, p. 51"),
    ("Ruhrallee, Dortmund", "Ruhrallee", "climate (air corridor)", "INSEKT 2021, p. 72"),
    ("Märkische Straße, Dortmund", "Märkische Straße", "climate (air corridor)", "INSEKT 2021, p. 72"),
    ("Großmarkt Dortmund", "Großmarkt", "climate (heat hotspot)", "INSEKT 2021, p. 72"),
    ("Körne, Dortmund", "Gewerbegebiet Körne", "climate (heat hotspot)", "INSEKT 2021, p. 71"),
]

# search only inside this box around Innenstadt-Ost (lon/lat: left, top, right, bottom)
VIEWBOX = "7.45,51.53,7.55,51.48"

layer = QgsProject.instance().mapLayersByName(LAYER_NAME)[0]
to_25832 = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"),
                                  layer.crs(), QgsProject.instance())
existing = {f["name"] for f in layer.getFeatures()}


def geocode(text):
    """Return (lon, lat, display_name) of the first Nominatim hit, or None."""
    url = QUrl("https://nominatim.openstreetmap.org/search")
    query = QUrlQuery()
    for key, value in (("q", text), ("format", "json"), ("limit", "1"),
                       ("viewbox", VIEWBOX), ("bounded", "1")):
        query.addQueryItem(key, value)
    url.setQuery(query)
    request = QNetworkRequest(url)
    request.setRawHeader(b"User-Agent", b"M01-student-project-QGIS")
    blocking = QgsBlockingNetworkRequest()
    if blocking.get(request) != QgsBlockingNetworkRequest.ErrorCode.NoError:
        print(f"  network error: {blocking.errorMessage()}")
        return None
    hits = json.loads(bytes(blocking.reply().content()).decode("utf-8"))
    if not hits:
        return None
    return float(hits[0]["lon"]), float(hits[0]["lat"]), hits[0]["display_name"]


if not layer.isEditable():
    layer.startEditing()

for text, name, theme, source in PLACES:
    if name in existing:
        print(f"SKIP  {name} (already in layer)")
        continue
    hit = geocode(text)
    time.sleep(1.1)  # Nominatim allows max. 1 request per second
    if hit is None:
        print(f"NOT FOUND  {name}  -> add this one by hand")
        continue
    lon, lat, found = hit
    point = to_25832.transform(QgsPointXY(lon, lat))
    feature = QgsFeature(layer.fields())
    feature.setGeometry(QgsGeometry.fromPointXY(point))
    feature.setAttribute("name", name)
    feature.setAttribute("theme", theme)
    feature.setAttribute("source", source)
    layer.addFeature(feature)
    print(f"ADDED  {name}\n       found: {found}")

layer.commitChanges()
layer.triggerRepaint()
print("Done. Check each point on the map.")
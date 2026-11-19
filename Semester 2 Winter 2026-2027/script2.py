# Restore name / theme / source on H13 from nearest H16 (name_en) and H15b (theme7)
# Keeps H13 itself, so fid and label rotations stay.
# Back up the H13 .gpkg in Explorer before running.

from qgis.core import QgsProject, QgsField, QgsSpatialIndex, QgsFeatureRequest
from qgis.PyQt.QtCore import QVariant

MAXD = 30  # metres

def lyr(part):
    for l in QgsProject.instance().mapLayers().values():
        if part in l.name():
            return l
    raise Exception("Layer not found: " + part)

h13  = lyr("H13_innenstadt_ost_key_places_25832")
h16  = lyr("H16_innenstadt_ost_key_places_osm_25832")
h15b = lyr("H15b_innenstadt_ost_named_places_25832")

def nearest_value(src, field, geom):
    idx = QgsSpatialIndex(src.getFeatures())
    ids = idx.nearestNeighbor(geom.asPoint() if not geom.isMultipart() else geom.centroid().asPoint(), 1, MAXD)
    if not ids:
        return None, None
    f = next(src.getFeatures(QgsFeatureRequest(ids[0])))
    return f[field], round(f.geometry().distance(geom), 1)

pr = h13.dataProvider()
names = [f.name() for f in h13.fields()]
new = [QgsField(n, QVariant.String, len=150) for n in ("name", "theme", "source") if n not in names]
if new:
    pr.addAttributes(new)
    h13.updateFields()

i_name, i_theme, i_src = (h13.fields().indexOf(n) for n in ("name", "theme", "source"))
changes, empty = {}, []
for f in h13.getFeatures():
    g = f.geometry()
    n, d1 = nearest_value(h16, "name_en", g)
    t, d2 = nearest_value(h15b, "theme7", g)
    changes[f.id()] = {i_name: n, i_theme: t,
                       i_src: "© OpenStreetMap contributors, 2026"}
    print(f.id(), "|", n, "(%s m)" % d1, "|", t)
    if not n:
        empty.append(f.id())

pr.changeAttributeValues(changes)
h13.triggerRepaint()
print("\nDone. Rows without a name (type by hand):", empty)
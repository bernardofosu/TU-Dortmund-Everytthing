import json, time, urllib.request, urllib.parse
from qgis.core import (QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem,
                       QgsVectorLayer, QgsField, QgsFeature)
from qgis.PyQt.QtCore import QVariant

# 1. the practice points with flow values
src = QgsProject.instance().mapLayersByName('92_practice_points_values')[0]
to_wgs = QgsCoordinateTransform(src.crs(), QgsCoordinateReferenceSystem('EPSG:4326'), QgsProject.instance())

# 2. new temporary layer = same points + a height column
out = QgsVectorLayer('Point?crs=EPSG:25832', '93_practice_points_height', 'memory')
pr = out.dataProvider()
pr.addAttributes(src.fields().toList() + [QgsField('height_m', QVariant.Double)])
out.updateFields()

# 3. ask the elevation service, 100 points at a time
feats = list(src.getFeatures())
for i in range(0, len(feats), 100):
    batch = feats[i:i+100]
    locs = []
    for f in batch:
        p = to_wgs.transform(f.geometry().asPoint())
        locs.append(f'{p.y():.6f},{p.x():.6f}')
    url = 'https://api.opentopodata.org/v1/eudem25m?locations=' + urllib.parse.quote('|'.join(locs), safe=',.')
    data = json.loads(urllib.request.urlopen(url, timeout=60).read())
    new = []
    for f, r in zip(batch, data['results']):
        nf = QgsFeature(out.fields())
        nf.setGeometry(f.geometry())
        nf.setAttributes(f.attributes() + [r['elevation']])
        new.append(nf)
    pr.addFeatures(new)
    print(f'{i+len(batch)} / {len(feats)} points done')
    time.sleep(1.2)

out.updateExtents()
QgsProject.instance().addMapLayer(out)
print('Finished')
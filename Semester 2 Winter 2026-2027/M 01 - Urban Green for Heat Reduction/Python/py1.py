from qgis.core import (QgsProject, QgsFeature, QgsCoordinateTransform)

SRC = "H15b_innenstadt_ost_named_places_25832"
DST = "H13_innenstadt_ost_key_places_25832"

PICK = {
    "Körner Park": ("Körne Park", "Climate (cool area)", "OSM"),
    "Kaiserplatz": ("Kaiser Square", "Climate (cool area)", "OSM"),
    "Kleingartenanlage Zehnthof": ("Zehnthof allotment gardens", "Climate (cool area)", "OSM; INSEKT 2021, p. 71"),
    "Gartenverein Flora e.V.": ("Flora allotment gardens", "Species and Habitats", "OSM"),
    "Seerosenteich": ("Water Lily Pond", "Water", "OSM"),
    "Kronprinzenviertel": ("Kronprinzenviertel (development site)", "Soil", "OSM; INSEKT 2021, p. 128"),
    "Ehemalige Kronenbrauerei": ("Former Kronen Brewery", "Soil", "OSM; INSEKT 2021, p. 101"),
    'Seniorenzentrum "Im Kaiserviertel"': ("Kaiserviertel Senior Centre", "Human Health", "OSM; INSEKT 2021, p. 84"),
    "Wohn- und Begegnungszentrum Zehnthof": ("Zehnthof care centre", "Human Health", "OSM; INSEKT 2021, p. 84"),
    "St. Josefinenstift": ("St. Josefinenstift care home", "Human Health", "OSM"),
    "Südbad": ("Südbad swimming pool", "Human Health", "OSM"),
    "Sportplatz SV Körne 83 e.V.": ("SV Körne 83 sports ground", "Human Health", "OSM"),
    "Gesamtschule Gartenstadt": ("Gartenstadt Comprehensive School", "Culture and Justice", "OSM; INSEKT 2021, p. 82"),
    "Berswordt-Grundschule": ("Berswordt Primary School", "Culture and Justice", "OSM; INSEKT 2021, p. 155"),
    "Musik- und Kulturzentrum MUK": ("MUK Music and Culture Centre", "Culture and Justice", "OSM"),
    "Jüdische Gemeinde Groß-Dortmund": ("Jewish Community of Greater Dortmund", "Culture and Justice", "OSM; INSEKT 2021, p. 84"),
    "Wasserturm Dortmund Südbahnhof": ("Südbahnhof Water Tower", "Culture and Justice", "OSM"),
}

project = QgsProject.instance()
src = project.mapLayersByName(SRC)[0]
dst = project.mapLayersByName(DST)[0]
xform = QgsCoordinateTransform(src.crs(), dst.crs(), project)

print("Source:", src.name(), "| features:", src.featureCount(),
      "| filter:", repr(src.subsetString()), "| CRS:", src.crs().authid())

existing = {f["name"] for f in dst.getFeatures()}
best = {}
for f in src.getFeatures():
    n = (f["name"] or "").strip()
    if n in PICK:
        g = f.geometry()
        g.transform(xform)                      # to EPSG:25832
        if n not in best or g.area() > best[n].area():
            best[n] = g

dst.startEditing()
added = 0
for n, g in best.items():
    name_en, theme, source = PICK[n]
    if name_en in existing:
        print("SKIP ", name_en)
        continue
    feat = QgsFeature(dst.fields())
    feat.setGeometry(g.pointOnSurface())
    feat["name"], feat["theme"], feat["source"] = name_en, theme, source
    dst.addFeature(feat)
    added += 1
    print("ADDED", name_en)
dst.commitChanges()
dst.triggerRepaint()

print("Not found:", sorted(set(PICK) - set(best)) or "none")
print(f"Done: {added} points added to H13.")
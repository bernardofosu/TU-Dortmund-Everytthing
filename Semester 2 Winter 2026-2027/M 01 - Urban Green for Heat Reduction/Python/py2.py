import processing
from qgis.core import QgsProject, QgsVectorLayer, QgsField
from qgis.PyQt.QtCore import QVariant

SRC = "H15b_innenstadt_ost_named_places_25832"
OUT = r"D:/TU Dortmund Everytthing/Semester 2 Winter 2026-2027/M 01 - Urban Green for Heat Reduction/Habitat Map Innenstadt-Ost/H16_innenstadt_ost_key_places_osm_25832.gpkg"

EN = {
    "Westfalenpark": "Westfalenpark",
    "Ostfriedhof": "East Cemetery (Ostfriedhof)",
    "Stadewäldchen": "Stadewäldchen green corridor",
    "Körner Park": "Körne Park",
    "Kaiserplatz": "Kaiser Square",
    "Kleingartenanlage Zehnthof": "Zehnthof allotment gardens",
    "Bolmke": "Bolmke nature reserve",
    "Seerosenteich": "Water Lily Pond",
    "Buschmühlenteich": "Buschmühle Pond",
    "Gartenverein Flora e.V.": "Flora allotment gardens",
    "Flamingoteich": "Flamingo Pond",
    "Kaiserhainteich": "Kaiserhain Pond",
    "Brauerbrunnen": "Brewers' Fountain",
    "Wasserherz": "Water Heart fountain",
    "Kronprinzenviertel": "Kronprinzenviertel (development site)",
    "Ehemalige Kronenbrauerei": "Former Kronen Brewery",
    'Seniorenzentrum "Im Kaiserviertel"': "Kaiserviertel Senior Centre",
    "Wohn- und Begegnungszentrum Zehnthof": "Zehnthof care and community centre",
    "St. Josefinenstift": "St. Josefinenstift care home",
    "Südbad": "Südbad swimming pool",
    "Spielplatz Am Kaiserhain": "Kaiserhain playground",
    "Sportplatz SV Körne 83 e.V.": "SV Körne 83 sports ground",
    "Max-Planck-Gymnasium": "Max Planck Grammar School",
    "Gesamtschule Gartenstadt": "Gartenstadt Comprehensive School",
    "Berswordt-Grundschule": "Berswordt Primary School",
    "Franziskus-Grundschule": "Franziskus Primary School",
    "Musik- und Kulturzentrum MUK": "MUK Music and Culture Centre",
    "Kinder- und Jugendtheater": "Children's and Youth Theatre",
    "Jüdische Gemeinde Groß-Dortmund": "Jewish Community of Greater Dortmund",
    "Wasserturm Dortmund Südbahnhof": "Südbahnhof Water Tower",
}

project = QgsProject.instance()
found = project.mapLayersByName(SRC)
if not found:
    raise SystemExit(f"Layer '{SRC}' not in the Layers panel.")
names = ",".join("'" + n.replace("'", "''") + "'" for n in EN)

# 1. keep chosen places, 2. reproject to 25832 and save
kept = processing.run("native:extractbyexpression", {
    "INPUT": found[0], "EXPRESSION": f'"name" IN ({names})',
    "OUTPUT": "TEMPORARY_OUTPUT"})["OUTPUT"]
processing.run("native:reprojectlayer", {
    "INPUT": kept, "TARGET_CRS": "EPSG:25832", "OUTPUT": OUT})

# 3. load it and add English names
layer = QgsVectorLayer(OUT, "H16_innenstadt_ost_key_places_osm_25832", "ogr")
project.addMapLayer(layer)
layer.dataProvider().addAttributes([QgsField("name_en", QVariant.String, len=80)])
layer.updateFields()
idx = layer.fields().indexOf("name_en")
layer.startEditing()
for f in layer.getFeatures():
    layer.changeAttributeValue(f.id(), idx, EN.get(f["name"], f["name"]))
layer.commitChanges()

print(f"H16 created with {layer.featureCount()} places.")
missing = set(EN) - {f["name"] for f in layer.getFeatures()}
if missing:
    print("Not found (check spelling in H15b):", sorted(missing))
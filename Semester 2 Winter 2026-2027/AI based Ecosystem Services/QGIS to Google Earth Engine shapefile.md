# 🗺️ QGIS to Google Earth Engine: Study-Area Workflow

This guide records the process for selecting the **Innenstadt-Ost** district in QGIS, exporting it as a shapefile, uploading it to Google Earth Engine (GEE), and using it in a script.

## 1. 🔎 Select Innenstadt-Ost in QGIS

1. Open the district layer’s attribute table.
2. Choose **Select features using an expression**.
3. Enter this expression:

   ```qgis
   "stadtbezirk_bezeichnung" = 'Innenstadt-Ost'
   ```

4. Run the expression. The matching district should be highlighted on the map and selected in the attribute table.

## 2. 📤 Export the selected district as a shapefile

1. In the **Layers** panel, right-click the district layer and choose **Export → Save As…** (in this QGIS version, **Save As…** is the export option).
2. Set **Format** to **ESRI Shapefile**.
3. Click the **…** button beside **File name**, choose a folder you can find again, and save with a name such as `Innenstadt-Ost.shp`.
4. Set the CRS to **EPSG:4326 — WGS 84**.
5. Check **Save only selected features** so only Innenstadt-Ost is exported.
6. In **Select fields to export**, uncheck `geographische_koordinaten`. It is a JSON/map field, which the shapefile attribute table cannot store. Keep the ordinary fields you want, such as the district name or number.
7. Leave **Geometry type** as **Automatic** and click **OK**.

### 📁 Keep the shapefile parts together

A shapefile is made up of several files with the same base name. Keep the files together in the export folder. Common parts include:

- `Innenstadt-Ost.shp` — the feature geometry
- `Innenstadt-Ost.shx` — the geometry index
- `Innenstadt-Ost.dbf` — the attribute table
- `Innenstadt-Ost.prj` — the coordinate reference system

QGIS may also create other sidecar files. Include the related files when packaging the shapefile. For Earth Engine, select the complete set together or put the components in a ZIP file and upload the ZIP.

## 3. ☁️ Upload the shapefile to Earth Engine

1. Open the **Assets** tab in the Earth Engine Code Editor.
2. Choose **New → Table Upload → Shape files**.
3. Select the shapefile components together, or select the ZIP containing them.
4. Give the asset a name such as `Innenstadt-Ost` and start the upload.
5. Wait for ingestion to finish. The uploaded item should appear under **Cloud Assets** as a table.

If Earth Engine reports that the `.shp` file must be accompanied by `.dbf` and `.shx`, only the `.shp` was selected. Go back and upload the companion files as well (a ZIP containing them is convenient).

## 4. 📥 Import the asset into your script

1. In the Code Editor, open the **Assets** tab.
2. Find the uploaded `Innenstadt-Ost` table.
3. Click **IMPORT**. Earth Engine adds an import at the top of the script, with a variable name such as `table` or `table2`.
4. Use the exact variable name shown under **Imports** in your script. For example, if the import is named `table`:

   ```javascript
   Map.centerObject(table, 12);
   Map.addLayer(table, {}, 'Innenstadt-Ost');
   ```

   If Earth Engine assigned a different name, replace `table` in both lines with that exact name.

The error **“table is not defined”** means the script uses `table` but there is no import or variable with that name. Import the asset first, or update the code to match the imported variable name.

## ✅ Quick checklist

- [ ] The expression selected only `Innenstadt-Ost`.
- [ ] **Save only selected features** was checked.
- [ ] The JSON field `geographische_koordinaten` was excluded from the shapefile export.
- [ ] The shapefile components were kept together and uploaded as a set or ZIP.
- [ ] The upload finished and the table appears in **Cloud Assets**.
- [ ] The asset was imported into the script, and the code uses the exact imported variable name.


https://open-data.dortmund.de/explore/dataset/fb62-stadtbezirke/export/?disjunctive.stadtbezirk_nr&disjunctive.stadtbezirk_bezeichnung



https://www.govdata.de/suche/daten/verwaltungsgebiete-1-250-000-stand-31-12
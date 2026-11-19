# 🗺️ Export Dortmund's Boundary from QGIS to Google Earth Engine (GEE)

This guide explains how to save **only Dortmund's city boundary** from the German VG250 administrative-boundary dataset and upload it to Google Earth Engine.

> ⚠️ **Study-area check:** The steps below export the whole independent city of Dortmund. If your project is specifically about **Innenstadt-Ost**, follow the alternative workflow near the end.

---

## 1️⃣ Select Dortmund in QGIS

1. In QGIS, locate the `VG250_KRS` layer.
2. Right-click it and open **Attribute Table**.
3. Click **Select Features by Expression**.
4. Enter:

   ```qgis
   "GEN" = 'Dortmund'
   ```

5. Click **Select Features**.
6. Check the attribute table/map to confirm that only Dortmund is selected.

The attribute table should identify Dortmund as a **Kreisfreie Stadt** (independent city).

---

## 2️⃣ Export only the selected feature

1. Close the attribute table.
2. In the Layers panel, right-click `VG250_KRS`.
3. Choose **Export → Save Selected Features As…**.
4. Set these options:

   - **Format:** `ESRI Shapefile`
   - **File name:** `Dortmund_boundary.shp`
   - **CRS:** `EPSG:4326 — WGS 84` (recommended for this upload workflow)
   - **Save only selected features:** make sure this option is enabled.

5. Click **OK**.

✅ The exported shapefile should contain only Dortmund, not every county or independent city in Germany.

---

## 3️⃣ Put the shapefile components into a ZIP archive

A shapefile consists of several companion files. In the output folder, select the files with the same base name when present:

- `Dortmund_boundary.shp` — geometry
- `Dortmund_boundary.shx` — geometry index
- `Dortmund_boundary.dbf` — attribute table
- `Dortmund_boundary.prj` — coordinate reference system
- `Dortmund_boundary.cpg` — character encoding (optional, if created)

Right-click the selected files and choose the Windows option to **Compress to ZIP file**.

Name the archive:

`Dortmund_boundary.zip`

⚠️ Keep all shapefile components together. Do not upload only the `.shp` file.

---

## 4️⃣ Upload the ZIP to Google Earth Engine

1. Open the [Google Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Open the **Assets** tab.
3. Choose **NEW → Table upload** (the exact wording can vary slightly).
4. Select `Dortmund_boundary.zip`.
5. Start the upload/ingestion task.
6. Wait until the task completes successfully.
7. Copy the asset ID shown in the Assets tab.

---

## 5️⃣ Use the boundary in GEE JavaScript

Replace the example asset path with the **exact asset ID** shown in your GEE Assets tab.

```javascript
var dortmund = ee.FeatureCollection(
  'projects/your-project/assets/Dortmund_boundary'
);

Map.centerObject(dortmund, 10);
Map.addLayer(dortmund, {color: 'red'}, 'Dortmund boundary');

// Example: clip an image to Dortmund
var clippedImage = image.clip(dortmund.geometry());
```

📝 The variable `image` is a placeholder. Replace it with the image or composite you want to clip, such as a Landsat image or an NDVI/LST composite.

### Example: clip a Landsat image collection composite

```javascript
var landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterBounds(dortmund)
  .filterDate('2025-05-01', '2025-09-30')
  .median()
  .clip(dortmund.geometry());

Map.centerObject(dortmund, 10);
Map.addLayer(landsat, {}, 'Landsat composite clipped to Dortmund');
```

This is an example workflow; apply the appropriate cloud masking, scaling, and band selection before using the imagery for quantitative analysis.

---

## 📍 Alternative: export Innenstadt-Ost instead

If your actual study area is **Innenstadt-Ost**, do not export the whole Dortmund boundary. Use the Dortmund city-district layer `fb62-stadtbezirke` instead.

1. Open the `fb62-stadtbezirke` attribute table.
2. Choose **Select Features by Expression**.
3. Use:

   ```qgis
   "stadtbezirk_bezeichnung" = 'Innenstadt-Ost'
   ```

4. Select the feature and export it with **Export → Save Selected Features As…**.
5. Use the same shapefile, EPSG:4326, ZIP, and GEE upload steps above.
6. Give it a clear name, such as `Innenstadt_Ost_boundary.zip`.

---

## 🧭 Which boundary should I use?

| Research area | QGIS layer | Feature to export |
|---|---|---|
| Whole city of Dortmund | `VG250_KRS` | `GEN = 'Dortmund'` |
| Innenstadt-Ost only | `fb62-stadtbezirke` | `stadtbezirk_bezeichnung = 'Innenstadt-Ost'` |

**Remember:** use the boundary that matches the actual study area defined for your project. A city-wide boundary and a single city-district boundary cover very different areas.

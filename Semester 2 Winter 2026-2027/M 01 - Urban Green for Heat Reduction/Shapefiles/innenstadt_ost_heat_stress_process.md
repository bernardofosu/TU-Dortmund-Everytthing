# 🌡️ M 01 Urban Green for Heat Reduction: Heat Stress Layer (Day)

**Study area:** Dortmund Innenstadt-Ost
**Topic:** Map 1 Climate, Step 3 Climate Elements (heat production / heat stress)
**Software:** QGIS 4.2.0, GDAL 3.13.1

---

## 📥 1. Data source

| Item | Details |
|---|---|
| 🏛️ Provider | LANUK NRW (Landesamt für Natur, Umwelt und Klima Nordrhein-Westfalen) |
| 📦 Dataset | Klimaanalyse NRW 2026, Klimaanalysekarte (Tag) |
| 🔗 Download | https://www.opengeodata.nrw.de/produkte/umwelt_klima/klima/klimaanalyse/analyse-tag/ |
| 📄 File used | `Klimaanalyse-Karte-Tag_2026_EPSG25832_TIFF.zip` (234.6 MB) |
| 📜 Licence | Datenlizenz Deutschland, Zero, Version 2.0 (free use) |
| 📘 Method paper | https://www.klimaatlas.nrw.de/sites/default/files/2026-03/Methodik_Planung_Klimaanalyse_Methodik.pdf |

⚠️ **Note:** the other file in the same folder, `Klimaanalyse-Tag_2026_EPSG25832_GeoPackage.zip`, only contains water and traffic areas (Wasser- und Verkehrsflächen). It is **not** the heat map.

### 🗂️ Files inside the zip

| File | Meaning | Use |
|---|---|---|
| `PL_KY_TAG_TYP.tif` | Typical summer day | ✅ Main analysis |
| `PL_KY_TAG_EXT.tif` | Extreme summer day | 🔁 Optional comparison |

(PL = Planung, KY = Klima, TAG = day, TYP = typical, EXT = extreme)

---

## 🔍 2. What the data is

- 🧮 **Variable:** PET (Physiological Equivalent Temperature) in °C at 15:00
- 🖥️ **How it was made:** modelled with FITNAH-3D for a summer radiation day (clear, calm weather), following VDI 3787 Part 1. No satellite LST is used.
- 📐 **Resolution:** 25 m × 25 m pixels
- 🔢 **Data type:** Float32, continuous values (not classes)
- 🚫 **NoData value:** -999 (pixels outside NRW, ignored automatically)
- 🌍 **CRS:** EPSG:25832, ETRS89 / UTM zone 32N
- 📊 **NRW range (TYP):** 17.9 to 43.7 °C, mean 34.0 °C

---

## 🛠️ 3. Processing steps

### Step 1: Check CRS 🧭
- Raster `PL_KY_TAG_TYP`: EPSG:25832 ✅
- Boundary `Innenstadt-Ost`: EPSG:4326 ❌ (needed reprojecting)
- Project: EPSG:25832 ✅

### Step 2: Reproject the boundary 🔄
- Tool: **Vector general, Reproject layer**
- Input: `Innenstadt-Ost` (EPSG:4326)
- Target CRS: EPSG:25832
- Output: `00_innenstadt_ost_boundary_25832.gpkg`
- 💡 Reason: reproject the vector to match the raster, not the other way round (reprojecting a raster resamples pixels and changes values)

### Step 3: Clip the raster ✂️
- Tool: **GDAL, Raster extraction, Clip raster by mask layer**
- Input: `PL_KY_TAG_TYP`
- Mask: `00_innenstadt_ost_boundary_25832`
- ✅ Match the extent of the clipped raster to the extent of the mask layer
- ✅ Keep resolution of input raster
- ⬜ Set output file resolution (leave unticked)
- Output: `03_innenstadt_ost_pet_day_typ.tif`
- 📊 **Result range in Innenstadt-Ost:** 21.5 to 43 °C

### Step 4: Symbology 🎨
- Render type: **Singleband pseudocolor**
- Interpolation: **Discrete** (one colour per class)
- Colour ramp: light yellow to dark red

| PET (°C) | Class |
|---|---|
| up to 23 | 🟨 No heat stress |
| 23 to 29 | 🟧 Slight heat stress |
| 29 to 35 | 🟠 Moderate heat stress |
| 35 to 41 | 🟥 Strong heat stress |
| above 41 (inf) | 🔴 Extreme heat stress |

📚 PET thresholds: Matzarakis and Mayer (1996); Matzarakis, Mayer and Iziomon (1999). PET method: Höppe (1999).

---

## ❌➡️✅ 4. Errors and how we fixed them

| # | Problem | Cause | Fix |
|---|---|---|---|
| 1 | 🔗 Open.NRW dataset link showed **404 Not Found** | LANUK replaced the old dataset with the 2026 version | Downloaded from OpenGeodata.NRW (`klimaanalyse/analyse-tag/`) |
| 2 | 🧩 Raster not available in the Clip window | Used **Vector overlay, Clip**, which only works with vectors | Used **GDAL, Clip raster by mask layer** |
| 3 | 🌐 Boundary in EPSG:4326, raster in EPSG:25832 | Different CRS | Reprojected boundary to EPSG:25832 before clipping |
| 4 | 📏 Y Resolution showed 1.0 / 2.0 | Leftover value in the resolution field | Cleared it (Not set) |
| 5 | 🚨 **ERROR 1: Duplicate argument -tap** | Both "Keep resolution" and "Set output file resolution" were ticked, so GDAL got the same instruction twice | Unticked "Set output file resolution" |
| 6 | 💾 **"." files are not supported** | Typed only the file name, without folder and `.tif` | Used **Save to File…** so QGIS adds folder and extension |
| 7 | ⚠️ **Missing parameter value Clipped (mask)** | Output box was empty after clearing it | Chose the output file again |
| 8 | 🔁 Mask reset to the 4326 layer after reopening the tool | Tool remembers the first layer in the list | Selected `00_innenstadt_ost_boundary_25832` again |
| 9 | 🏷️ Labels did not match values | Values were still the automatic equal intervals (25.8, 30.1, 34.4, 38.7) | Changed values to 23, 29, 35, 41, inf |
| 10 | 🔃 Legend shows low at top, high at bottom | Discrete raster legends cannot be reversed; Legend Settings only works with Linear | Planned fix: Reclassify by table, Polygonize, Categorized symbology, drag Extreme to top |

---

## 💡 5. Key concepts learned

- 🟦 **Raster vs vector:** a raster is a grid of pixels with one value each, so it has **no attribute table**. Values become attributes only after Zonal Statistics or Polygonize.
- ⬛ **Raster is always a rectangle:** pixels outside the study area are filled with NoData (-999) and ignored in calculations. They do not need to be removed.
- 🔎 **Check pixel values:** Identify Features tool (Ctrl+Shift+I), click on the map.
- 🌡️ **PET vs LST:** PET = how hot **people feel** (modelled, day and night). LST = how hot **surfaces** are (satellite, one moment only). PET is the main layer for this project; LST is optional supporting evidence and can cover winter.
- 🧍 **Why PET 35 °C is already stress:** the body (core 37 °C) must lose heat to its surroundings. When the felt temperature approaches skin temperature (about 33 to 35 °C), heat loss becomes difficult.
- ☀️❄️ **Limitation:** the model is one idealised summer day. Winter cold must come from DWD station data or a winter LST scene.

---

## 📁 6. Files created

| File | Content |
|---|---|
| `00_innenstadt_ost_boundary_25832.gpkg` | Study area boundary, reprojected |
| `03_innenstadt_ost_pet_day_typ.tif` | Day PET, typical summer day, clipped |

---

## ⏭️ 7. Next steps

- [ ] 🔃 Reclassify + Polygonize the day PET (legend order, and easier overlay)
- [ ] 🌙 Download and clip the **night** map (`klimaanalyse/analyse-nacht/`, take TYP)
- [ ] 🗺️ Download and clip the **climatope map** (Step 2), save as `02_innenstadt_ost_climatope.gpkg`
- [ ] ❄️ Add cold air layers (night)
- [ ] 📊 Zonal Statistics: attach day and night values to climatope polygons
- [ ] 🧩 Overlay step by step into the Climate Function Map

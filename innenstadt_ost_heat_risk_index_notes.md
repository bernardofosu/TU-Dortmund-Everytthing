# 🔥 Heat Risk Index for Innenstadt-Ost (BNPB-style)
### M 01 Urban Green for Heat Reduction · TU Dortmund · Work log 28 to 29 October 2026

This note records what we did today, in the order that works, with all file names. It continues the Climate Function Map guide (`innenstadt_ost_climate_map_guide.md`).

**Software:** QGIS 4.2 · **CRS:** EPSG:25832 · **Data:** LANUK (2026), Klimaanalyse NRW 2026

---

## 🧭 1. The idea

We built a **heat risk index** following the risk formula used by Indonesia's disaster agency BNPB for its earthquake risk map:

**R = (H × V × (1 − C))^(1/3)**

| Letter | BNPB meaning | Our heat version | Data |
|---|---|---|---|
| **H** | Hazard | How hot a block gets, day and night | LANUK day PET + night air temperature |
| **V** | Vulnerability | How dense / built-up the block is (proxy) | LANUK climatopes |
| **C** | Capacity | How much cool air flows within 200 m | LANUK cold air flow (KVSD) |

- **H × V**: risk is high only where it is hot **and** dense.
- **× (1 − C)**: cool air nearby **reduces** risk.
- **^(1/3)**: cube root (geometric mean of the three), back on a 0 to 1 scale.

⚠️ The formula is BNPB's (earthquake risk). Using it for heat is **our adaptation**; say so on the slide and justify the indicators.

💡 **Visual vs analytical overlay:** placing maps on top of each other is a *visual* overlay. This index is an *analytical* overlay: values from several layers are **calculated** into a new value per block.

---

## 🗺️ 2. Step 2 climatopes: reclassified to her 8 classes (+ Transport)

**Why:** her slide lists 8 classes; LANUK has 12. We grouped them.

| Her class | LANUK `Klimatoptyp` |
|---|---|
| Open land and agricultural areas | Freilandklima |
| Water bodies | Gewässer-, Seeklima |
| Forests | Waldklima |
| Parks | Klima innerstädtischer Grünflächen |
| Villages and low-density settlements | Vorstadtklima |
| Residential areas | Stadtrandklima |
| Urban cores and dense inner-city areas | Stadtklima, Innenstadtklima |
| Commercial and industrial zones | Gewerbe-, Industrieklima (offen, dicht) |
| Transport (extra) | Bahnverkehr, Straßenverkehr |

- ✅ Checked with **List unique values**: all **12** LANUK values covered, so no polygon is left empty.
- 🧹 One "Unclassified" row was a clip **sliver** (`KT_R02_2` = 0, `Klimatoptyp` NULL, area ≈ 0 m²): deleted. **829** polygons remain.
- 📁 Field: **`climatope_9`** in `02_innenstadt_ost_climatope copy`

**RVR comparison map (view only):**
- 🌐 WMS: `https://geodaten.metropoleruhr.de/klima/regionalklima?` (layer **klimatope**)
- ⚠️ `https://services-rv.geoportal.ruhr/klima/regionalklima` gives **404** in QGIS
- WMS is a picture only: no clipping, no attribute table. RVR data files are not downloadable.
- To make it *look* clipped: duplicate the boundary, Symbology **Inverted Polygons**, white fill, place above the WMS.
- RVR has no road class and draws without outlines, which is why it looks smoother.

---

## 🛠️ 3. Processing steps (correct order)

### 📊 Step 1: Night temperature into the blocks
Toolbox, **Raster analysis, Zonal statistics**
- Input: `02_innenstadt_ost_climatope copy`
- Raster: `03_innenstadt_ost_temp_night_typ_clip`
- Prefix: `nighttemp_` (QGIS adds `mean`, so the column is **`nighttemp_mean`**)
- Statistic: Mean
- 💾 **`20_innenstadt_ost_clim_night_mean.gpkg`**

ℹ️ NULL for water, parks, forest, open land is **correct**: LANUK gives night temperature only for built-up areas (Wirkraum).

### ☀️ Step 2: Day heat stress into the blocks
Zonal statistics
- Input: `20_innenstadt_ost_clim_night_mean`
- Raster: `03_innenstadt_ost_heat_stress_day_typ_clip`
- Prefix: `daytemp_` (column **`daytemp_mean`**)
- 💾 **`21_innenstadt_ost_clim_night_day_mean.gpkg`**

ℹ️ Day PET covers **every** polygon, so no NULLs.

### 🏷️ Step 3: Give each block an ID
Field Calculator on layer 21
- Name: **`block_id`**, Integer, expression `@row_number`
- Save edits (pencil, Save) **before** the next step

💡 **Why:** the Buffer tool may renumber `fid`. `block_id` is our own name tag that is copied unchanged, so ring values can be joined back to the right block.

### ⭕ Step 4: 200 m ring around each block
Toolbox, **Buffer**
- Input: `21_innenstadt_ost_clim_night_day_mean`
- Distance: **200** m, Segments 5
- ⬜ **Dissolve unticked** (each block keeps its own ring)
- 💾 **`21_innenstadt_ost_clim_ring200.gpkg`**

ℹ️ It looks messy (829 overlapping rings). That's normal; it's a working layer.

### ❄️ Step 5: Bigger cold air flow raster
The rings reach outside the district, so the cold air map must too.

**Clip raster by mask layer**
- Input: `PL_KY_NACHT_KVSD_TYP_coldair_flow`
- Mask: `00_innenstadt_ost_buffer_1km`
- ✅ Match extent, ✅ Keep resolution, ⬜ Set output file resolution
- 💾 **`03_innenstadt_ost_coldair_flow_typ_1km.tif`**

### 🌬️ Step 6: Cold air in each ring
Zonal statistics
- Input: `21_innenstadt_ost_clim_ring200`
- Raster: `03_innenstadt_ost_coldair_flow_typ_1km`
- Prefix: `cold_` (column **`cold_mean`**)
- 💾 **`21_innenstadt_ost_clim_ring200_cold_mean.gpkg`**

ℹ️ NULL = no cool air flows within 200 m (counted as 0 later).

### 🔗 Step 7: Bring the ring values back to the blocks
Toolbox, **Join attributes by field value**
- Input: `21_innenstadt_ost_clim_night_day_mean`, field `block_id`
- Input 2: `21_innenstadt_ost_clim_ring200_cold_mean`, field `block_id`
- Copy only: `cold_mean`
- Join type: one-to-one; ⬜ Discard unticked
- 💾 **`22_innenstadt_ost_clim_night_day_cold_mean.gpkg`**

### 🧮 Step 8: Normalise and calculate (Field Calculator on layer 22)
All fields **Decimal number (real)**, ⬜ virtual field unticked. **Save after each one.**

**Min-max normalisation** rescales each indicator to 0 to 1 within the district:
`x_norm = (x − min) / (max − min)` (0 = lowest block in Innenstadt-Ost, 1 = highest; relative, not absolute)

| Field | Expression | Meaning |
|---|---|---|
| 🌙 `H_night` | `("nighttemp_mean" - minimum("nighttemp_mean")) / (maximum("nighttemp_mean") - minimum("nighttemp_mean"))` | Night hazard 0 to 1 |
| ☀️ `h_day` | `("daytemp_mean" - minimum("daytemp_mean")) / (maximum("daytemp_mean") - minimum("daytemp_mean"))` | Day hazard 0 to 1 |
| 🔥 `hazard` | `CASE WHEN "H_night" IS NOT NULL THEN ("H_night" + "h_day") / 2 END` | **H**: day and night, equal weight (our choice) |
| 🏙️ `vulnerability` | see below | **V**: density proxy |
| 🌬️ `capacity` | `coalesce("cold_mean", 0) / maximum(coalesce("cold_mean", 0))` | **C**: cool air nearby, 0 to 1 |
| ⚠️ `risk` | see below | **R**: BNPB formula |

**Vulnerability:**
```
CASE
 WHEN "Klimatoptyp" = 'Innenstadtklima' THEN 1
 WHEN "Klimatoptyp" IN ('Stadtklima', 'Gewerbe-, Industrieklima (dicht)') THEN 0.75
 WHEN "Klimatoptyp" IN ('Stadtrandklima', 'Gewerbe-, Industrieklima (offen)') THEN 0.5
 WHEN "Klimatoptyp" = 'Vorstadtklima' THEN 0.25
END
```
Order follows LANUK's density classes (Vorstadt < 20 %, Stadtrand 20 to 40 %, Stadt > 40 % built over; LANUK 2026, Methodik-Papier Klimatopkarte). The scores 0.25 to 1 are **our choice**.

**Risk:**
```
CASE
 WHEN "hazard" IS NOT NULL AND "vulnerability" IS NOT NULL
 THEN ("hazard" * "vulnerability" * (1 - "capacity")) ^ (1.0/3)
END
```

**Test case ✅:** block 14 (Innenstadtklima): hazard 0.99, vulnerability 1, capacity 0, so **risk 0.997**, the highest in the district.

### 🎨 Step 9: Risk classes and map
⚠️ Make this field **Text (string)**, length 30 (not a number type, or every row stays NULL).

Safer: use the **Processing** Field Calculator (Toolbox, Vector table, Field calculator), which writes a new file.

```
CASE
 WHEN "risk" IS NULL THEN 'Cooling area / no risk'
 WHEN "risk" >= 0.66 THEN 'High'
 WHEN "risk" >= 0.33 THEN 'Medium'
 ELSE 'Low'
END
```
- 💾 **`23_innenstadt_ost_clim_heat_risk_index.gpkg`**
- Thresholds: equal thirds of 0 to 1 (**our choice**)

| Class | Colour |
|---|---|
| 🔴 High | `#d73027` |
| 🟡 Medium | `#fee08b` |
| 🟢 Low | `#1a9850` |
| 🟩 Cooling area / no risk | `#a6d96a` |

Symbology: Categorized by `risk_class`, Stroke **No Pen**. Basemap: ESRI Gray (light).

---

## 🔎 4. First result

| Class | Where |
|---|---|
| 🔴 High | North, along the rail and industrial edge (Westfalenhütte side), and the west next to the city centre |
| 🟡 Medium | Most of the middle |
| 🟢 Low | East: **Gartenstadt** |
| 🟩 Cooling area | Parks, cemeteries, Westfalenpark, green strips |

Matches the earlier findings: hot, dense and far from cool air in the north-west; cool and green in Gartenstadt.

⚠️ **Check:** the large red area in the north is mostly **dense commercial/industrial**. It is high because V scores it like dense housing (0.75), but few people live there. Either lower its V (e.g. 0.5) or replace V with population data. Slide note: *"V currently uses building density as a proxy; population data will replace it."*

---

## 📁 5. Files created today

| | File | Content |
|---|---|---|
| 🗺️ | `02_innenstadt_ost_climatope copy` | Climatopes + `climatope_9` (her 8 classes + Transport) |
| 🌙 | `20_innenstadt_ost_clim_night_mean.gpkg` | + `nighttemp_mean` |
| ☀️ | `21_innenstadt_ost_clim_night_day_mean.gpkg` | + `daytemp_mean`, `block_id` |
| ⭕ | `21_innenstadt_ost_clim_ring200.gpkg` | 200 m ring per block (working layer) |
| ❄️ | `03_innenstadt_ost_coldair_flow_typ_1km.tif` | Cold air flow, 1 km buffer |
| 🌬️ | `21_innenstadt_ost_clim_ring200_cold_mean.gpkg` | Rings + `cold_mean` (working layer) |
| 🔗 | `22_innenstadt_ost_clim_night_day_cold_mean.gpkg` | Blocks + all values + H, V, C, R |
| 🔥 | `23_innenstadt_ost_clim_heat_risk_index.gpkg` | Final: + `risk_class` |

**Naming pattern:** each step's name grows by what it adds (`clim` + `night` + `day` + `cold`), ending in `_mean` while values are being collected.

---

## ❌➡️✅ 6. Problems and fixes

| Problem | Cause | Fix |
|---|---|---|
| ❓ "Unclassified" in the legend | One clip sliver with no class | Deleted the row (829 polygons left) |
| 🔢 `nighttemp_mean` NULL for green and water | By design: night temp only for built-up areas | Keep; these become "Cooling area" |
| 🆔 Ring values could join to the wrong block | Buffer may renumber `fid` | Own `block_id` with `@row_number` before buffering |
| 🗂️ Field Calculator opened on the ring layer | Wrong layer selected | Check the window title before running |
| 👻 Field not saved | "Create virtual field" ticked | Untick it |
| 🔤 `risk_class` all NULL | Field created as a number type | Must be **Text (string)** |
| 💥 **QGIS crashed** (access violation) when deleting / creating a field | Files on **Google Drive** + editing in place; stack trace showed Python multiprocessing (possibly the SCP plugin) | Work on the **local disk (D:)**, don't delete fields, use the Processing Field Calculator, temporarily switch off SCP |
| 📂 Layers gone after restart | Project saved before layers 20 to 22 were added | Re-add the .gpkg files from the folder; save project often |
| 🔗 Project still loads from Google Drive | `.qgz` stores full paths (`I:\…`) | New project or **Save As** on D:, add layers from D: |
| 🌐 RVR WMS gives 404 | Wrong service address | Use `geodaten.metropoleruhr.de/klima/regionalklima?` |

### 💾 Saving rules (learned the hard way)
1. After **every** Field Calculator step: pencil, **Save**
2. Save the project often: **Ctrl + S**
3. Work on **D:**, copy to Google Drive only as a backup
4. **Don't delete fields** in GeoPackages; ignore wrong ones or make a new field
5. Prefer tools that **write a new file** (Processing) over editing in place

---

## 💡 7. Concepts explained today

- 🔍 **Unique values** check that every class is covered before trusting a reclassification.
- 📐 **Min-max normalisation**: brings different units onto 0 to 1 so they can be combined; it is relative to the study area and sensitive to outliers. Composite index guidance: OECD (2008) (check the full reference in Zotero).
- 🧩 **Zonal statistics vs Union**: zonal statistics adds raster values to polygons without cutting them; Union only works for two vectors.
- 🏷️ **Prefix + statistic = column name** (`nighttemp_` + `mean` = `nighttemp_mean`).
- 🌡️ **PET vs LST vs night air temperature:** PET = felt heat (heat stress, day); night air temperature = urban heat island (air, night); LST = surface heat (satellite, supporting only). Shade lowers both PET and LST; sealing vs green changes LST much more than PET for a person standing in the sun.
- 🎨 **Why the RVR map looks nicer:** no outlines, merged classes, smoothed edges, no road class. Ours can look similar: Stroke No Pen, Dissolve (display only).

---

## ⏭️ 8. Next steps

- [ ] Save layer 22 / 23 and the project on D:
- [ ] Decide on industrial V (lower to 0.5, or wait for population)
- [ ] Add population: LANUK **Betroffenheitsanalyse** (`PL_KY_BTA_Kinderdichte`, `_Hochaltrigendichte`, `_Nettokaltmiete`, Zensus 2022) as the real V
- [ ] Compare the result with LANUK's **Planungshinweiskarte** (`PL_KY_PHK_HP`)
- [ ] Optional: EXT scenario as a stress test
- [ ] Slide: formula, indicator table, rule thresholds, map, limitations

---

## 📖 References

- BNPB (2026): Indeks Risiko Bencana Gempabumi (earthquake risk index map and formula R = (H × V × (1 − C))^(1/3)). Badan Nasional Penanggulangan Bencana, Jakarta. (check full reference)
- LANUK (2026): Klimaanalyse NRW 2026, Methodik-Papiere (Hintergrund und Methodik; Klimatopkarte; Klimaanalysekarte Tag; Klimaanalysekarte Nacht). Landesamt für Natur, Umwelt und Klima NRW.
- OECD (2008): Handbook on Constructing Composite Indicators: Methodology and User Guide. OECD Publishing, Paris. (check details in Zotero)
- Regionalverband Ruhr (2022): Regionale Klimatope auf Basis der Flächennutzung im Ruhrgebiet. WMS, geodaten.metropoleruhr.de.
- VDI (2022): VDI-Richtlinie 3787 Blatt 2. Düsseldorf.

# 🗺️ German Administrative Boundaries in QGIS — Complete Notes

## 🎯 Purpose

These notes explain how to use Germany's VG250 administrative-boundary dataset together with the City of Dortmund's local **Stadtbezirke** dataset in QGIS.

The key distinction is:

- **VG250** provides administrative boundaries from the federal-state level down to municipalities/counties, depending on the layer.
- **Dortmund's `fb62-stadtbezirke`** dataset provides Dortmund's 12 city districts (*Stadtbezirke*), which are smaller local subdivisions within the city.

For a study focused on **Dortmund-Innenstadt-Ost**, use the VG250 layers for the wider administrative context and `fb62-stadtbezirke` for the exact city-district boundary.

---

## 🔗 Data sources

### 1. City of Dortmund — City districts

[Open the Dortmund `fb62-stadtbezirke` dataset and export page](https://open-data.dortmund.de/explore/dataset/fb62-stadtbezirke/export/?disjunctive.stadtbezirk_nr&disjunctive.stadtbezirk_bezeichnung)

- Publisher: City of Dortmund.
- Contains **12 Stadtbezirke**.
- Includes the district-name field `stadtbezirk_bezeichnung`.
- Includes the district-number field `stadtbezirk_nr`.
- Use this dataset to select and export a specific Dortmund city district, such as **Innenstadt-Ost**.

### 2. Germany — VG250 administrative areas

[GovData: Verwaltungsgebiete 1:250,000 (VG250)](https://www.govdata.de/suche/daten/verwaltungsgebiete-1-250-000-stand-31-12)

The VG250 dataset contains national administrative boundaries at several levels. The downloaded shapefile package contains separate layers for different administrative levels.

> **Important:** VG250 does not provide Dortmund's 12 *Stadtbezirke* as a dedicated layer. Use the Dortmund municipal dataset for those.

---

## 🏛️ Germany's administrative hierarchy

A simplified hierarchy relevant to mapping Dortmund is:

1. 🇩🇪 **Germany** — *Staat*
2. 🟦 **Federal state** — *Bundesland / Land*; Dortmund is in **North Rhine-Westphalia (Nordrhein-Westfalen, NRW)**.
3. 🟩 **Government district** — *Regierungsbezirk*; Dortmund is in **Regierungsbezirk Arnsberg**.
4. 🟧 **County or independent city** — *Kreis or kreisfreie Stadt*; Dortmund is a **kreisfreie Stadt** (an independent city, not part of a Landkreis).
5. 🟪 **Municipality/city level** — *Gemeinde / Stadt*. In VG250, Dortmund is represented as a city/municipality-level administrative unit.
6. 🏙️ **Dortmund city district** — *Stadtbezirk*. Dortmund has 12 city districts; **Innenstadt-Ost** is one of them.

**Terminology note:** German administrative structures differ by state. The hierarchy above is a practical mapping sequence for Dortmund, not a claim that every German state has the same intermediate levels. Dortmund's *Stadtbezirke* are municipal subdivisions, not a separate nationwide administrative level in VG250.

---

## 🧭 VG250 layers and what they mean

The layer suffix is a useful clue to the administrative level.

| Layer | German meaning | English meaning | How it is useful |
|---|---|---|---|
| `VG250_LAN` | Länder / Bundesländer | **Federal states** | Select North Rhine-Westphalia to show the state containing Dortmund. |
| `VG250_RBZ` | Regierungsbezirke | **Government districts** | Select Regierungsbezirk Arnsberg. This level exists in NRW, but not in every German state. |
| `VG250_KRS` | Kreise and kreisfreie Städte | **Counties and independent cities** | Select Dortmund, which is a *kreisfreie Stadt*. |
| `VG250_GEM` | Gemeinden / Städte | **Municipalities and cities** | Shows municipality/city-level units across Germany, including Dortmund as a city. |

Other suffixes may appear in the package. Their exact content depends on the VG250 product/version and the particular shapefile. Use the layer name and its attribute table to identify the relevant level rather than assuming every file is needed.

### Why does `VG250_KRS` include Dortmund?

The attribute table for `VG250_KRS` shows a record with:

- `GEN`: `Dortmund`
- `BEZ`: `Kreisfreie Stadt`

That means Dortmund is mapped at the **county/independent-city level**. It is not a Landkreis; it is an independent city with county-level status.

### Why does `VG250_GEM` contain many more records?

`VG250_GEM` contains municipality/city-level records across Germany, so it has thousands of features. It is not a list of Dortmund's 12 city districts. For the local districts, use `fb62-stadtbezirke`.

---

## 🧾 Attribute fields visible in the VG250 tables

The screenshots show fields such as `GEN`, `BEZ`, `ARS`, `AGS`, and `LKZ`.

- **`GEN`** — name of the administrative unit, for example `Dortmund`.
- **`BEZ`** — type/designation of the unit, for example `Kreisfreie Stadt`, `Landkreis`, `Land`, or `Gemeinde`.
- **`ARS`** — *Amtlicher Regionalschlüssel* (official regional key), a hierarchical administrative identifier.
- **`AGS`** — *Amtlicher Gemeindeschlüssel* (official municipality key), used to identify municipality-level units.
- **`LKZ`** — a state-related code shown in the table; check the dataset's official metadata/data dictionary before relying on it for analysis.

The exact fields available can vary by layer. To confirm the values for a feature, open that layer's attribute table and inspect the row for the place you need.

---

## 📥 Load the downloaded VG250 shapefiles in QGIS

The downloaded package may contain many files with extensions such as `.shp`, `.shx`, `.dbf`, `.prj`, and `.cpg`.

### What these files do

- `.shp` — stores the vector geometry.
- `.shx` — geometry index used with the shapefile.
- `.dbf` — attribute table.
- `.prj` — coordinate reference system information.
- `.cpg` — character encoding information, when provided.

**Keep the companion files together.** Do not move or delete individual sidecar files. To load a layer, add the `.shp` file to QGIS; QGIS reads the related files from the same folder.

### Steps

1. Extract the downloaded ZIP file into a normal folder.
2. In QGIS, use **Layer → Add Layer → Add Vector Layer**, or drag the required `.shp` file into the map.
3. Load only the layers you need for the task, for example:
   - `VG250_LAN` for federal states,
   - `VG250_RBZ` for government districts,
   - `VG250_KRS` for counties and independent cities,
   - `VG250_GEM` for municipalities/cities.
4. Open the attribute table of the relevant layer.
5. Use **Select Features by Expression** to select the target feature.
6. Right-click the layer and choose **Zoom to Selection** to check the result.

### Example: select Dortmund in `VG250_KRS`

Because the table shows `GEN` as the name field and `BEZ` as the unit type, an expression for Dortmund may be:

```qgis
"GEN" = 'Dortmund'
```

Check the preview and the selected row before proceeding. If a layer contains multiple versions/records or the name field differs, inspect its attribute table first.

### Example: select North Rhine-Westphalia in `VG250_LAN`

The `GEN` field in the screenshot displays the state name in a shortened form (`Nordrhein-Wes...`). The full value is likely `Nordrhein-Westfalen`. To avoid guessing, use the expression builder's field/value list or copy the exact value from the attribute table.

---

## 🏙️ Select Innenstadt-Ost in the Dortmund city-district layer

The `fb62-stadtbezirke` attribute table shows the field:

- `stadtbezirk_bezeichnung` — city-district name.

Use this exact expression in **Select Features by Expression**:

```qgis
"stadtbezirk_bezeichnung" = 'Innenstadt-Ost'
```

### Steps

1. Select the `fb62-stadtbezirke` layer in the Layers panel.
2. Open its attribute table.
3. Click **Select Features by Expression**.
4. Paste the expression above.
5. Click **Select Features**.
6. Close the expression window. The **Innenstadt-Ost** polygon should be highlighted (yellow in the current selection style).

If the expression returns no selection, check the field spelling and the exact district name in the attribute table. Do not use `"stadtbezirk"` unless that field actually exists; the screenshot confirms the name field is `stadtbezirk_bezeichnung`.

---

## 💾 Export Innenstadt-Ost as a separate boundary layer

After selecting Innenstadt-Ost:

1. Close the expression window.
2. In the Layers panel, right-click `fb62-stadtbezirke`.
3. Choose **Export → Save Selected Features As…**
4. Set **Format** to `GeoPackage`.
5. Choose a file name and location, for example `Innenstadt_Ost.gpkg`.
6. Ensure **Save only selected features** is enabled.
7. Give the output layer a name such as `Innenstadt_Ost`.
8. Click **OK**.

You now have a separate boundary layer for Innenstadt-Ost. Keep the original `fb62-stadtbezirke` layer too, so the full set of 12 districts remains available.

---

## 🧠 Which layer should I use?

| Task | Recommended layer |
|---|---|
| Show Germany's federal states | `VG250_LAN` |
| Show Regierungsbezirk Arnsberg | `VG250_RBZ` |
| Show Dortmund's city boundary at county/independent-city level | `VG250_KRS` |
| Show municipality/city-level boundaries | `VG250_GEM` |
| Show all 12 Dortmund city districts | `fb62-stadtbezirke` |
| Analyze only Innenstadt-Ost | Export the selected feature from `fb62-stadtbezirke` as `Innenstadt_Ost.gpkg` |

### Recommended workflow for a Dortmund-Innenstadt-Ost study

1. Use `VG250_LAN` to establish the state context: **North Rhine-Westphalia**.
2. Use `VG250_RBZ` for the regional context: **Regierungsbezirk Arnsberg**.
3. Use `VG250_KRS` for Dortmund as an independent city.
4. Use `fb62-stadtbezirke` to locate **Innenstadt-Ost**.
5. Export Innenstadt-Ost as a separate GeoPackage if you need a clean study-area boundary for clipping or spatial analysis.

You do not need to keep every VG250 layer visible at once. For most analysis, it is clearer to keep the study-area boundary above the wider administrative layers and turn off layers that are not currently needed.

---

## ⚠️ Common mistakes to avoid

- **Confusing a city with a city district:** Dortmund is a *kreisfreie Stadt*; Innenstadt-Ost is a *Stadtbezirk* inside Dortmund.
- **Assuming `VG250_GEM` contains the 12 Stadtbezirke:** it does not replace the Dortmund-specific city-district dataset.
- **Loading every layer with visibility enabled:** overlapping polygons can obscure one another. Turn layers on and off as needed.
- **Deleting `.dbf`, `.shx`, or `.prj` files:** these are companion files used by the shapefile.
- **Exporting all districts by mistake:** make sure **Save only selected features** is enabled when exporting Innenstadt-Ost.
- **Treating rescaled map display as new data detail:** changing map scale or symbol size does not add spatial detail to the underlying boundary data.

---

## ✅ Quick reference

- **Federal state:** `VG250_LAN` → North Rhine-Westphalia.
- **Government district:** `VG250_RBZ` → Arnsberg.
- **County / independent city:** `VG250_KRS` → Dortmund (`Kreisfreie Stadt`).
- **Municipality/city:** `VG250_GEM` → municipality/city-level units.
- **Dortmund city districts:** `fb62-stadtbezirke` → 12 Stadtbezirke.
- **Innenstadt-Ost expression:**

  ```qgis
  "stadtbezirk_bezeichnung" = 'Innenstadt-Ost'
  ```

- **Dortmund dataset:** [fb62-stadtbezirke](https://open-data.dortmund.de/explore/dataset/fb62-stadtbezirke/export/?disjunctive.stadtbezirk_nr&disjunctive.stadtbezirk_bezeichnung)
- **VG250 dataset:** [GovData — Verwaltungsgebiete 1:250,000](https://www.govdata.de/suche/daten/verwaltungsgebiete-1-250-000-stand-31-12)

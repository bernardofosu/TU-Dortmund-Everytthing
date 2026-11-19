# 🗺️ QGIS Notes: Fixing the NRW 2026 Climatope Clipping Error

## 🎯 Goal

Clip the NRW 2026 climatope vector layer to the Dortmund city boundary
in QGIS.

## 📂 Input data

-   **Input layer:** `PL_KY_KLIMATOP`
-   **Source GeoPackage:**
    `C:/Users/ofosu/Downloads/Klimaanalyse-Klimatopkarte_2026_EPSG25832_GeoPackage/Klimaanalyse-Klimatopkarte_2026_EPSG25832.gpkg|layername=PL_KY_KLIMATOP`
-   **Dortmund boundary layer:** `fb62-stadtgrenze`
-   **Target output:** `Klimatop_Dortmund.gpkg`

## ❌ Error encountered

The Clip algorithm failed because an input feature has invalid geometry:

``` text
Feature (603326) ... has invalid geometry. Please fix the geometry or change the "Invalid features filtering" option for this input or globally in Processing settings.
```

**Meaning:** At least one polygon in the NRW climatope layer has invalid
geometry. QGIS's Clip tool cannot process that feature under the current
invalid-feature handling settings.

## ✅ Recommended workflow: reduce the data first

Fixing the entire NRW dataset can be slow and can create a very large
output. A more manageable approach is to make a Dortmund-sized subset
first.

### 1. 📐 Extract an approximate Dortmund-area subset

1.  In the **Processing Toolbox**, search for **Extract by extent**.
2.  Choose `PL_KY_KLIMATOP` as the input layer.
3.  Set an extent that covers Dortmund and a small margin around it. Use
    the extent selector/map canvas if available.
4.  Save the result to a new file, for example
    `NRW_Klimatop_Dortmund_extent.gpkg`.
5.  Run the tool.

> This is only a rectangular preliminary subset, not the final
> city-boundary clip.

### 2. 🛠️ Fix geometries on the subset

1.  In the Processing Toolbox, search for **Fix geometries**.
2.  Set `NRW_Klimatop_Dortmund_extent` as the input.
3.  Save the output as `NRW_Klimatop_Dortmund_fixed.gpkg`.
4.  Run the tool and check that the output layer appears in the Layers
    panel.

### 3. ✂️ Clip the repaired subset to Dortmund

1.  Open **Clip** under **Vector overlay**.
2.  **Input layer:** `NRW_Klimatop_Dortmund_fixed`
3.  **Overlay layer:** `fb62-stadtgrenze`
4.  **Output file:** `Klimatop_Dortmund.gpkg`
5.  Click **Run**.

### 4. 🔎 Check the result

-   Confirm the output layer appears in QGIS.
-   Zoom to the output layer and check that it follows the Dortmund
    boundary.
-   Open its attribute table and confirm that climatope categories are
    present.
-   If the tool fails again, keep the full error message; do not
    repeatedly rerun the same failing Clip operation.

## ⚠️ Alternative: skip invalid features

QGIS has an **Invalid features filtering** setting under **Processing
Settings → General** (the exact wording/location can vary by QGIS
version).

You may set it to **Skip invalid input features** and rerun Clip.
However, this can omit invalid features from the output, so the result
may have gaps. Use this only if you accept that limitation and check the
output carefully.

## 🧾 Previous output to verify

A prior attempt reportedly created:

`C:/Users/ofosu/Downloads/Dortmund_Climatopes_fixed.gpkg`

Do **not** assume this file is available or is the correct repaired NRW
layer. It may have come from an earlier attempt using a different input.
Check the file path and its layer source in QGIS before reusing it.

## 💡 Key lesson

**Extract a Dortmund-sized subset → Fix geometries → Clip to
`fb62-stadtgrenze` → Validate the result.**

Keep the original NRW GeoPackage unchanged as your source dataset.

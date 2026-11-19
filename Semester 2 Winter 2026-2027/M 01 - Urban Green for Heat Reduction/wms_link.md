# 🌡️ Adding the RVR FITNAH-3D Climate Layer in QGIS

This guide records the steps used to add the Ruhr Regional Association
(RVR) FITNAH-3D air-temperature map to QGIS and display it over
Dortmund.

## 1. 🗺️ Open the WMS/WMTS connection manager

In QGIS, open:

**Layer → Add Layer → Add WMS/WMTS Layer...**

You can also use the shortcut **Ctrl + Shift + W** in many QGIS
versions.

## 2. ➕ Create a new connection

In the WMS/WMTS window:

1.  Click **New**.

2.  In **Name**, enter a clear name, for example:
    `RVR FITNAH-3D Climate`.

3.  In **URL**, paste:

    `https://geodaten.metropoleruhr.de/klima/klima_fitnah`

4.  Leave authentication as **No Authentication** unless your service
    administrator says otherwise.

5.  Click **OK** to save the connection.

> 💡 The connection name is just a label in QGIS; the URL tells QGIS
> which map service to contact.

## 3. 🔌 Connect to the service

1.  Select the new `RVR FITNAH-3D Climate` connection from the list.
2.  Click **Connect**.
3.  Wait for QGIS to retrieve the available layers.

When the connection works, the layer list includes FITNAH-3D climate
outputs such as air temperature, PET, night-time cooling, cold-air
production/flow, wind fields, land use, and structure height.

## 4. 🌙 Select the air-temperature layer

In the returned layer list, select:

-   **ID:** `3`
-   **Name:** `temperatur_01uhr`
-   **Meaning:** modelled air temperature at **01:30 a.m. (CEST)**

The title/abstract describes air temperature in °C under an
autochthonous weather condition.

Then:

1.  Click the layer row `temperatur_01uhr`.
2.  Click **Add**.
3.  Click **Close** after the layer is added.

## 5. 🎨 Check the map and legend

The FITNAH-3D layer should appear in the QGIS Layers panel and render in
the map canvas.

The legend shown for this layer has temperature classes:

-   `≤ 15 °C`
-   `> 15–16 °C`
-   `> 16–17 °C`
-   `> 17–18 °C`
-   `> 18–19 °C`
-   `> 19–20 °C`
-   `> 20–21 °C`
-   `> 21 °C`
-   Buildings (`Gebäude`)

🔎 **Interpretation:** the colours show modelled temperature classes for
a particular hot-summer scenario. They are not live temperatures and
should not be treated as conditions for every day of the year.

## 6. 🧭 Add the Dortmund municipal boundary

The Dortmund boundary layer was downloaded from the City of Dortmund
Open Data portal and loaded into QGIS.

1.  Download the boundary dataset and extract the ZIP archive.
2.  In QGIS, choose **Layer → Add Layer → Add Vector Layer...**
3.  Browse to the extracted `.shp` file and click **Add**.
4.  Keep the related shapefile components together in the same folder
    (`.shp`, `.shx`, `.dbf`, and `.prj`, when provided).
5.  In the Layers panel, keep the boundary visible so it draws as an
    outline over the climate map.

Official portal links: - [Dortmund Open Data
Portal](https://open-data.dortmund.de/) - [Dortmund city-boundary
dataset](https://open-data.dortmund.de/explore/dataset/fb62-stadtgrenze/)

## 7. 🔍 Zoom to Dortmund

To focus on the city:

1.  In the Layers panel, right-click the Dortmund boundary layer.
2.  Choose **Zoom to Layer**.
3.  Check that the boundary outline sits over the FITNAH-3D map.

If the outline is too thick, right-click the boundary layer →
**Properties → Symbology** and reduce the outline width.

## 8. 📚 Useful next layers for the climate assessment

After confirming the temperature layer, add and inspect other layers one
at a time:

  -----------------------------------------------------------------------
  Layer name / theme                  What it helps assess
  ----------------------------------- -----------------------------------
  `abkuehlung_01uhr`                  Night-time cooling around 01:30

  `abkuehlung_04uhr`                  Night-time cooling around 05:30

  `pet_11uhr`                         PET / thermal stress around 12:30

  `pet_14uhr`                         PET / thermal stress around 15:30

  Cold-air volume flow                Movement of cooling air

  Climate-ecological functions        Areas that provide cooling and
                                      areas that benefit from it
  -----------------------------------------------------------------------

⚠️ Add one layer at a time and check its title, legend, coverage, and
meaning before combining it with other layers.

## 9. ℹ️ Important WMS limitation

This connection is a **WMS (Web Map Service)**. It streams a rendered
map image into QGIS, including the service's colours and legend. It is
useful for viewing and comparing map patterns, but it does **not
automatically provide the underlying editable polygons or the original
numerical raster values**.

For calculations, clipping, raster algebra, or quantitative zonal
statistics, look for an official downloadable raster/vector dataset or
another service designed to provide features or data values.

## 10. 🧾 Save the QGIS project

1.  Choose **Project → Save As...**
2.  Save the project as a `.qgz` file.
3.  Use a clear name, for example: `Dortmund_Climate_Assessment.qgz`.

The QGIS project stores the layer connections and project settings. The
WMS still depends on the remote service being available.

------------------------------------------------------------------------

### 🔗 Reference

-   [Official QGIS documentation: WMS/WMTS
    connections](https://docs.qgis.org/3.44/en/docs/user_manual/working_with_ogc/ogc_client_support.html)
-   [RVR FITNAH-3D climate
    service](https://geodaten.metropoleruhr.de/klima/klima_fitnah)

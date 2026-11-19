# 🌍 GIS Data Sources for Landscape Analysis in Dortmund

## 🗺️ OpenStreetMap (OSM)

**OpenStreetMap** is a collaborative project to create a free, editable
map of the world. It can provide vector data for roads, buildings,
waterways, paths, parks, and mapped trees.

-   🌐 [OpenStreetMap ---
    AlternativeTo](https://images.openai.com/static-rsc-4/MiH_t_qVHHRh62ZfWbCyRYs8v1N6eEuaPVcJG2H7-kID_vM_r52g55DiVlHuKoT2N9qeJhbMudrnVsHKCnMJBhdOdObqy-ECOwTVpTyQCJPT4Obm0G4SSrMsjT5yHUbXuDdrXZIg-7OdKPPFPTL5EsdiUAmki5g_ByVMuekgbEs?purpose=inline)
-   📥 [Geofabrik --- Germany
    downloads](https://download.geofabrik.de/europe/germany.html?utm_source=chatgpt.com)
-   🧩 [QuickOSM plugin for
    QGIS](https://plugins.qgis.org/plugins/QuickOSM/?utm_source=chatgpt.com)

## 🏙️ Dortmund Geoportal and Open Data

Official city information and potentially more detailed local datasets
for Dortmund.

-   🗺️ [Dortmund
    Geoportal](https://www.dortmund.de/services/geo-portal.html?utm_source=chatgpt.com)
-   📂 [Dortmund Open
    Data](https://open-data.dortmund.de/?utm_source=chatgpt.com)
-   🏢 [Märkische Straße 235 --- Dortmunder
    Stadtentwicklungsgesellschaft](https://images.openai.com/static-rsc-4/rj9kPyjHNKQf7BEZuFpF1TbOqluHFtc3KLOKwoc0IKpbqfDP-BK1SXIWakhmZXKv4Rla9uS9tzV8GsMFSmbXKz2pB-ENmKb_ae5Q5SFcQ5Mgis_MaqSVlqzz46A8Mp74Fbf7CGRzSpm9tYsp16IxxaBvTR35paGxTgc-DiBXn5M?purpose=inline)

## 🌿 NRW Official Geodata

Look for official datasets covering hydrography, topographic objects,
land cover, forests, and habitats.

-   🗺️ [Geoportal
    NRW](https://www.geoportal.nrw/?utm_source=chatgpt.com)
-   🌱 [LANUK NRW](https://www.lanuk.nrw.de/?utm_source=chatgpt.com)
-   🖼️ [North Rhine-Westphalia land-use map --- Wikimedia
    Commons](https://images.openai.com/static-rsc-4/A9lnMjKeS_qKaV-CYwAc1zW9aiviV3UafA5TNiWuEuDLH1zDYzfnOXQhgErWxKMx8vGIVJFK3z2vKpjaWHoHcgpR3BoljDrFRm6W7IjKuhxgu4kljudAQJmXSashrCDNAgm0IjccNG7RP1OniAW47kHa_8Z2Kss-X-NkT2B7PVc?purpose=inline)

## 🛰️ Copernicus Sentinel-2

Free satellite imagery useful for vegetation analysis and land-cover
classification in Google Earth Engine (GEE).

-   🛰️ [Copernicus Data
    Space](https://dataspace.copernicus.eu/?utm_source=chatgpt.com)
-   🖼️ [Sentinel-2 image of Warsaw, 1 June 2020 --- Wikimedia
    Commons](https://images.openai.com/static-rsc-4/6qhUec7Gudb-6c52DRCchFD5Eq-SvIZQYrlFXkIens4xwBDYH-ArUbJzmc1l_DLG-ATbAgDrmMHLxcX3dSD6qVjY4xsQEgEhLpMKmoT7uFZi-Guld1Yis_9BRxgHf2I3sqcxZZL_FSkMGoCuqsSeZ9tytPDgF1nr2QIzUBu5T3o?purpose=inline)

------------------------------------------------------------------------

## ✅ Suggested GIS workflow

1.  Download relevant vector datasets for roads, buildings, water,
    trees, green spaces, and habitats.
2.  Load your study-area boundary shapefile in QGIS.
3.  Clip vector layers to the study-area boundary.
4.  Use Sentinel-2 imagery in GEE to complement the vector data and
    assess vegetation cover.
5.  Keep each theme as a separate layer, then overlay them in QGIS for
    your landscape analysis.

**Reminder:** Check the data license, date, coordinate reference system
(CRS), and spatial coverage before using each dataset in your project.

# 🌍 Thesis Proposal Structure: Urban Heat Vulnerability and Green Infrastructure Prioritisation

## 🎯 Recommended thesis title

**GeoAI-Based Land Cover Dynamics and Spatio-Temporal Assessment of Urban Heat Vulnerability for Green Infrastructure Prioritisation in Greater Accra, Ghana (2015–2025)**

## 🧭 Core research logic

Combine the useful ideas from Elmarakby and Elkadi (2024) with your independent multi-year Land Use/Land Cover (LULC) analysis and Urban Heat Vulnerability Index (UHVI).

- **🛰️ Land-cover dynamics:** What changed between 2015 and 2025?
- **🌡️ Urban heat vulnerability:** Where are exposure, sensitivity, and limited adaptive capacity associated with greater vulnerability?
- **🌳 Green Infrastructure prioritisation:** Where should interventions be prioritised, and which types may be appropriate?

Elmarakby and Elkadi provide a reference for combining heat, lack of green cover, and population density into a spatial priority index. Their Heat Risk Index (HRI) is not the same as your proposed UHVI, and you do not need to copy their formula.

---

## 📝 1. Introduction

Introduce climate change and urban heat, explain how land-cover change influences urban thermal conditions, and establish why heat vulnerability and Green Infrastructure (GI) planning matter in Greater Accra.

## 🚩 2. Problem statement

Explain the challenge of increasing built-up surfaces, declining or unevenly distributed vegetation, urban heat patterns, and unequal vulnerability. Identify the need to integrate multi-year LULC analysis with a spatially explicit vulnerability assessment to guide GI priorities.

## 🎯 3. Research aim, objectives, and questions

### Research aim

To assess land-cover dynamics and spatio-temporal urban heat vulnerability in Greater Accra, Ghana, from 2015 to 2025, and identify priority areas and potential Green Infrastructure interventions.

### Specific objectives

1. To classify and analyse land-use/land-cover dynamics in Greater Accra for 2015, 2020, and 2025 using satellite imagery and GeoAI-based classification.
2. To assess the spatial and temporal patterns of land surface temperature (LST) and urban thermal conditions across the study period.
3. To develop and map a UHVI based on the Exposure, Sensitivity, and Adaptive Capacity framework.
4. To identify GI priority areas by integrating UHVI results with relevant land-cover characteristics and recommend potential interventions based on scientific literature.

### Research questions

1. How has LULC changed in Greater Accra between 2015 and 2025?
2. How have LST and urban thermal conditions varied spatially and temporally during the study period?
3. How does urban heat vulnerability vary across Greater Accra when assessed through exposure, sensitivity, and adaptive capacity?
4. How can heat vulnerability and land-cover characteristics guide the prioritisation of areas and selection of potential GI interventions?

*The three dates are a proposed design, not a requirement. They provide three snapshots for change analysis, provided imagery and classification quality are adequate.*

---

## 📚 4. Literature review and conceptual framework

Organise the literature review around these themes:

1. 🌡️ **Urban heat and land-cover dynamics** — relationships between built-up land, vegetation, and thermal conditions.
2. 🧍 **Urban heat vulnerability** — exposure, sensitivity, and adaptive capacity frameworks.
3. 🧮 **UHVI construction** — indicator selection, normalisation, weighting, aggregation, and uncertainty.
4. 🤖 **GeoAI for LULC classification** — machine learning for land-cover mapping and accuracy assessment.
5. 🌳 **Green Infrastructure prioritisation** — using heat and land-cover evidence to identify priority areas and guide potential interventions.

### How the two core articles fit

#### 📍 Elmarakby & Elkadi (2024) — heat-risk mapping

Use this paper to inform the logic of priority mapping. It demonstrates combining heat intensity, lack of green cover, and population density into a composite HRI, followed by standardisation, index aggregation, and mapping. It is an example of heat-risk mapping, not a complete method for your UHVI or a system that assigns specific GI interventions to individual sites.

#### 🌳 Norton et al. (2015) — GI planning

Use this paper to support the conceptual connection between urban heat, cooling mechanisms, GI options, and prioritisation. It informs how priority-area characteristics can be translated into potential intervention types. It does not replace your own UHVI or LULC analysis.

---

## 🗺️ 5. Study area and methodology

Structure the methodology around the analytical sequence rather than simply listing software and indices.

### Stage 1 — 🗃️ Data collection and preparation

Potential data include:

- Landsat 8 and 9 imagery for selected years.
- Greater Accra administrative boundaries.
- Population and suitable demographic/socioeconomic indicators.
- Supporting spatial datasets relevant to LULC, heat, and vulnerability.

Check data availability, spatial resolution, dates, and compatibility before finalising the indicator list.

### Stage 2 — 🛰️ GeoAI-based LULC classification

Use Google Earth Engine to prepare and process Landsat imagery. A Random Forest classifier can classify selected land-cover classes for each year.

Assess classification performance using:

- Confusion matrix.
- Overall accuracy.
- User's accuracy.
- Producer's accuracy.
- F1-score, where appropriate.

Calculate land-cover areas and transitions between 2015, 2020, and 2025. This can reveal built-up expansion, vegetation changes, and other land-cover transitions.

**Keep the role of GeoAI clear:** in this design, machine learning classifies LULC. SHAP and deep learning are not required unless a specific research question calls for them.

### Stage 3 — 🌡️ LST, spectral indices, and UTFVI

Retrieve LST consistently for each selected year and analyse its spatial distribution and temporal differences. Calculate relevant indices such as NDVI and, where justified, NDBI and NDWI.

UTFVI can help describe thermal conditions, but it is not itself a complete measure of social vulnerability. Explain its role separately from UHVI.

Use comparable seasonal windows and processing procedures. Differences between years can otherwise reflect acquisition timing, weather, or cloud conditions rather than long-term change.

### Stage 4 — 🧮 Constructing your own UHVI

This is where your study differs from the Manchester HRI approach.

| Dimension | What it represents | Candidate indicators to assess |
|---|---|---|
| **Exposure** | Where people and places experience heat | LST, a justified thermal indicator, population distribution |
| **Sensitivity** | Who or what may be more adversely affected | Age structure or other defensible demographic indicators |
| **Adaptive capacity** | Ability to cope with or respond to heat | Suitable socioeconomic or service-access indicators |

These are candidate indicators, not a final list. Select indicators based on the vulnerability literature, data availability, spatial resolution, and avoid counting the same concept more than once.

Recommended steps:

1. Define each indicator and its expected relationship with vulnerability.
2. Harmonise spatial and temporal coverage.
3. Normalise indicators so they can be combined.
4. Reverse indicators where higher original values imply lower vulnerability, such as a defensible measure of adaptive capacity.
5. Select and justify the weighting method.
6. Combine indicators into a UHVI and classify vulnerability levels.
7. Test sensitivity to reasonable changes in weights or classification thresholds where feasible.

Do not automatically use equal weights simply because Elmarakby and Elkadi did. Equal weighting is one possible choice, but it needs justification for your framework.

### Stage 5 — 🌳 Identifying GI priority areas

Use UHVI and LULC results together.

For example, examine areas with high or very high UHVI in terms of their land-cover characteristics. This can help distinguish places where tree planting, green open spaces, green roofs, or other GI approaches may be appropriate.

Define explicit rules for:

- What counts as a priority area.
- How UHVI categories influence priority.
- How land-cover characteristics influence potential intervention recommendations.

Use Norton et al. (2015) and other relevant literature to inform the relationship between cooling mechanisms, GI types, and appropriate locations. Treat these recommendations as literature-based guidance, not proof that a particular intervention will work at every site in Greater Accra.

**Scope boundary:** unless you also analyse detailed information on existing GI, access, land ownership, available parcels, and technical feasibility, describe the result as a *GI priority-area assessment with potential intervention recommendations*, not a fully validated site-suitability model.

### Stage 6 — 📊 Analysis and outputs

Expected outputs include:

- LULC classification maps for 2015, 2020, and 2025.
- LULC change and transition statistics.
- LST and UTFVI maps for the selected years.
- UHVI maps and comparisons of spatial vulnerability patterns over time.
- A final GI priority-area map.
- A literature-based matrix linking priority-area characteristics to potential GI interventions.

---

## 🧠 6. Conceptual workflow

```text
🌍 Data collection
        ↓
🛰️ GeoAI-based LULC classification
        ↓
📈 LULC change analysis
        ↓
🌡️ LST + spectral indices + UTFVI
        ↓
🧮 UHVI: Exposure + Sensitivity + Adaptive Capacity
        ↓
🗺️ Integrate UHVI with LULC characteristics
        ↓
🌳 GI priority-area map
        ↓
🌱 Recommend potential GI interventions from literature
```

## 📌 7. Expected results and significance

Describe the outputs you expect to produce without claiming results before analysis:

- Evidence of LULC change over the study period.
- Maps showing spatial and temporal patterns in LST and UTFVI.
- UHVI maps that identify areas of comparatively higher and lower vulnerability.
- A spatial assessment of GI priority areas.
- Potential GI intervention recommendations based on heat and land-cover characteristics.

The research can support spatial planning by connecting remote-sensing evidence with a transparent prioritisation process.

## ⚠️ 8. Limitations and methodological decisions

Address these issues explicitly:

- **Spatial resolution:** demographic or socioeconomic data may be much coarser than 30 m Landsat pixels. Resampling does not create finer-resolution information.
- **Temporal comparability:** indicator data may not be available for every study year. Clearly distinguish historical thermal analysis from vulnerability assessment years where necessary.
- **Index assumptions:** normalisation, weighting, and class thresholds can affect UHVI results.
- **Thermal comparability:** use consistent seasonal windows and processing methods across years.
- **GI feasibility:** heat and LULC patterns alone cannot confirm land availability, ownership, cost, access, or engineering feasibility.

## 📅 9. Work plan

Create a timeline covering literature review, data acquisition, LULC classification and validation, LST/UTFVI analysis, UHVI development, GI prioritisation, interpretation, writing, and revision.

## 📚 10. References

Include full bibliographic details for the articles and datasets actually used. Ensure every in-text citation has a matching reference-list entry.

---

## ❓ Important decision before finalising the proposal

Will you calculate UHVI for **all three years (2015, 2020, and 2025)**, or only for the most recent year?

Because the title says *spatio-temporal assessment*, calculating UHVI for all three years is preferable **if comparable demographic and socioeconomic data are available**. If not, clearly separate the historical thermal analysis from the present-day vulnerability and GI-priority assessment.

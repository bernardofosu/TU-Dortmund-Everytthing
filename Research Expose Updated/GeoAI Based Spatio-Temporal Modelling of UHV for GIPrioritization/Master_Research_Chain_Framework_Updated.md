# 🧭 Master Research Chain & Framework

## 🎯 Central Research Question

> **How can GeoAI-derived land-surface dynamics and heat-vulnerability indicators be integrated into a spatial decision-support framework to prioritize and identify potentially suitable Green Infrastructure (GI) interventions across Greater Accra?**

### 🔗 Master Research Chain

```text
   🎯 CENTRAL RESEARCH QUESTION
   How can GeoAI & vulnerability indicators guide GI spatial prioritization and selection?
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
 [ RQ1: Diagnosis ]    [ RQ2: Explanation ]   [ RQ3: Vulnerability ]
 What changed in LULC,  Which variables predict  Where is urban heat
 LST & UTFVI            heat most effectively?   vulnerability highest?
 (2015–2025)?                    │                     │
        │                        │                     │
        └────────────────────────┼─────────────────────┘
                                 │
                                 ▼
                    [ RQ4: Prioritization ]
                    Where should GI be prioritized?
                                 │
                                 ▼
                      [ RQ5: Intervention ]
                  Which GI typologies fit these
                         priority zones?
```

### 🔄 Research Chain

**1. What has changed?**  
↓  
**2. Which factors are important for predicting heat?**  
↓  
**3. Where is urban heat vulnerability high?**  
↓  
**4. Where should GI be prioritized?**  
↓  
**5. Which GI interventions may be appropriate?**

This establishes the **spatio-temporal baseline**, explains the heat pattern, assesses vulnerability, and then moves toward the spatial-planning response.

---

## 📋 Formulated Research Questions & Objectives

### **RQ1 — Spatio-Temporal Baseline (Diagnosis)**

- **Research Question:** How have land use/land cover (LULC) and associated thermal conditions changed spatially and temporally across Greater Accra from 2015 to 2025?
- **Objective:** Map and quantify changes in LULC, spectral indices (NDVI, NDBI, MNDWI), Land Surface Temperature (LST), and the Urban Thermal Field Variance Index (UTFVI).
- **Key Method:** GeoAI classification & Landsat/Sentinel thermal processing.

### **RQ2 — Driving Factors & Predictors (Explanation)**

- **Research Question:** Which environmental, demographic, and socioeconomic variables are most important for predicting spatial variations in urban heat across Greater Accra?
- **Objective:** Rank and evaluate the relative importance and directional influence of biophysical and socioeconomic drivers on surface thermal patterns.
- **Key Method:** Random Forest / XGBoost Regression + SHAP (SHapley Additive exPlanations) values.

### **RQ3 — Spatial Heat Vulnerability (Vulnerability Assessment)**

- **Research Question:** How is urban heat vulnerability distributed spatially across Greater Accra based on combined environmental, demographic, and socioeconomic conditions?
- **Objective:** Construct and map an integrated Urban Heat Vulnerability Index (UHVI) based on Exposure, Sensitivity, and Adaptive Capacity (ESAC).
- **Key Method:** OECD/JRC indicator normalization and equal-weighting aggregation.

### **RQ4 — GI Priority Mapping (Spatial Prioritization)**

- **Research Question:** Which areas across Greater Accra should be prioritized for Green Infrastructure (GI) interventions based on their level of urban heat vulnerability?
- **Objective:** Delineate district-level and neighborhood-scale spatial priority tiers (e.g., High, Moderate, Low Priority) for urban greening.
- **Key Method:** GIS multi-criteria spatial decision mapping.

### **RQ5 — Intervention Typologies (Planning Response)**

- **Research Question:** Which types of green infrastructure interventions are potentially suitable for the identified priority areas based on their observed land-cover and urban spatial characteristics?
- **Objective:** Match high-priority vulnerability hotspots with context-appropriate GI typologies (e.g., street trees, public pocket parks, green roofs, or private micro-scale greening).
- **Key Method:** Spatial overlay & urban morphological profiling (distinguishing public vs. private land opportunities).

---

## 🧩 Master Methodological Framework

```text
🌍 Greater Accra, Ghana
          │
          ▼
🛰️ Landsat / Sentinel + Demographic + Socioeconomic Data
          │
          ▼
🗺️ RQ1 — SPATIO-TEMPORAL DIAGNOSIS
   LULC + NDVI + NDBI + MNDWI
   LST + UTFVI (2015–2025)
          │
          ▼
🤖 RQ2 — GEOAI EXPLANATION
   Random Forest / XGBoost
   + SHAP Explainability
          │
          ▼
🔥 RQ3 — HEAT VULNERABILITY
   Exposure + Sensitivity + Adaptive Capacity
          │
          ▼
   UHVI
          │
          ▼
🌳 RQ4 — GI SPATIAL PRIORITIZATION
   UHVI + Spatial Priority Mapping
          │
          ▼
🏙️ RQ5 — GI INTERVENTION TYPOLOGIES
   Priority Zones ×
   Land-Cover & Urban Density Typologies
          │
          ▼
📍 Spatial Decision Support for Climate-Responsive Planning
```

---

## 💪 Key Strengths of This Revised Structure

1. **Eliminates Methodological Redundancy:** By dropping GWR, the framework keeps the focus on machine-learning feature importance and explainability for RQ2.

2. **Defensible Planning Scope:** Framing RQ5 around **potentially suitable GI types** rather than implementation feasibility keeps the study firmly anchored in spatial planning without overpromising ground-level engineering, financial, land-tenure, or implementation feasibility.

3. **Clear Analytical Progression:** The framework moves from **diagnosis → explanation → vulnerability assessment → spatial prioritization → planning intervention**.

4. **Strong GeoAI–Planning Connection:** GeoAI functions as the analytical engine, while spatial planning provides the decision-support application.

5. **Direct Alignment with the Thesis Outcome:** The research moves beyond simply mapping urban heat toward identifying where GI should receive spatial priority and which intervention typologies may be appropriate based on observable spatial characteristics.

---

## 🎯 Concise / Direct Alternative Central Question

If a more direct, outcome-focused central question is preferred:

> **Where and how should Green Infrastructure (GI) be spatially prioritized across Greater Accra to mitigate urban heat vulnerability based on GeoAI driver modeling and spatial land-cover characteristics?**

---

## 🔍 Why the Main Central Question Works

- **“GeoAI-derived land-surface dynamics”** → RQ1: LULC, NDVI, NDBI, LST, UTFVI and their changes.
- **“heat-vulnerability indicators”** → RQ3: Exposure, Sensitivity, Adaptive Capacity → UHVI.
- **“integrated”** → connects the separate analytical components.
- **“spatial decision-support framework”** → establishes the Spatial Planning contribution.
- **“prioritize”** → RQ4: GI priority mapping.
- **“identify potentially suitable GI interventions”** → RQ5: intervention typologies.
- **“across Greater Accra”** → clearly defines the spatial scope.

### Terminology Note

The preferred wording is **“land-surface dynamics”** rather than “land surface dynamics” because it reads more naturally in this research context.

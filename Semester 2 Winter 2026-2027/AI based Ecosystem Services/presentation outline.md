# 🗺️ Complete presentation outline with references and GEE practicals
Seminar: AI-Driven Assessment of Urban Green Infrastructure and the Urban Heat Island Effect
I’ve organised the material around your lecturer’s course description and incorporated the relevant content from your exposé: Landsat, Google Earth Engine (GEE), Random Forest, Support Vector Machine, LULC classification, LST, NDVI, NDBI, population distribution, green infrastructure planning, and Greater Accra as a possible example.
The references below are assigned to the sections where they are most relevant. I’ve distinguished established scientific literature and official technical documentation from references cited in your exposé whose full bibliographic details still need checking.
## 🌡️ Part 1 — Introduction and urban heat islands
### 🌱 1. Introduction to AI-based ecosystem assessment
Content
- Define ecosystem assessment and explain its role in understanding urban environmental conditions.
- Introduce artificial intelligence (AI), machine learning and geospatial AI (GeoAI).
- Explain how satellite imagery, drone imagery, machine learning and GIS can be combined to assess urban green infrastructure.
- Introduce the seminar’s central question: how can AI-informed assessment help cities decide where green infrastructure should be located?
References
- Maes, J., et al. (2020). Mapping and Assessment of Ecosystems and their Services: An EU ecosystem assessment. European Commission. Useful background on ecosystem assessment and indicators.
- Sobhaninia et al. (2025), Where should the green go? Useful for connecting spatial assessment to green infrastructure planning. 
  
  ScienceDirect
### 🌆 2. Understanding the urban heat island (UHI) effect
Content
- Define the urban heat island effect.
- Distinguish surface urban heat islands from atmospheric urban heat islands.
- Explain urban–rural temperature differences.
- Introduce the distinction between land surface temperature (LST) and air temperature.
- Explain why satellite thermal imagery is useful for examining surface heat patterns.
References
- Oke, T. R. (1982). The energetic basis of the urban heat island. Quarterly Journal of the Royal Meteorological Society, 108(455), 1–24. https://doi.org/10.1002/qj.49710845502
- U.S. Geological Survey (USGS). Landsat Surface Temperature. Official explanation of the surface-temperature product. 
  
  U.S. Geological Survey
### 🏙️ 3. Causes of urban heat islands
Content
- Urbanisation and expansion of built-up areas.
- Loss of vegetation and green spaces.
- Heat absorption and storage by buildings, asphalt and concrete.
- Impervious surfaces and reduced evapotranspiration.
- Anthropogenic heat from transport, industry and buildings.
- Urban density, building geometry, shade and ventilation.
References
- Oke (1982), for the urban energy balance and the physical basis of urban heat islands.
- Yuan, J., et al. (2026). Urban Heat Island mitigation strategies: a comprehensive review of recent advances. City and Environment Interactions. https://doi.org/10.1016/j.cacint.2026.100351 
  
  ScienceDirect
### ❤️ 4. Health and environmental effects of urban heat
Content
- Heat stress, heat exhaustion and heatstroke.
- Cardiovascular and respiratory effects.
- Risks to older adults, outdoor workers and other vulnerable populations.
- Increased demand for cooling and electricity.
- Effects on urban vegetation, ecosystems and environmental quality.
- Why heat exposure and social vulnerability should be considered together in planning.
References
- World Health Organization Regional Office for Europe (2016). Urban green spaces and health. 
  
  who.int
- Nazish, A., Abbas, K., & Sattar, E. (2024). Health impact of urban green spaces: a systematic review of heat-related morbidity and mortality. BMJ Open, 14, e081632. https://doi.org/10.1136/bmjopen-2023-081632 
  
  PubMed
## 🌳 Part 2 — Urban green infrastructure and heat mitigation
### 🌿 5. Concept of urban green infrastructure (GI)
Content
- Define urban green infrastructure and explain its environmental and planning functions.
- Introduce urban parks, street trees, urban forests, green corridors, green roofs, green walls and vegetation restoration.
- Distinguish isolated green spaces from connected green networks.
- Explain how GI can support cooling, biodiversity, recreation and wider urban resilience.
References
- Cohen-Shacham, E., et al. (2016). Nature-based Solutions to Address Global Societal Challenges. IUCN. https://doi.org/10.2305/IUCN.CH.2016.13.en
- Norton, B. A., et al. (2015). Planning for cooler cities: A framework to prioritise green infrastructure to mitigate high temperatures in urban landscapes. Landscape and Urban Planning, 134, 127–138. https://doi.org/10.1016/j.landurbplan.2014.10.018 
  
  ScienceDirect
### 💧 6. How green infrastructure influences urban heat
Content
- Shade and reduced solar radiation.
- Evapotranspiration and energy exchange.
- How vegetation cover, canopy structure and plant characteristics influence cooling.
- How the size, connectivity and location of green spaces can affect their benefits.
- Why cooling performance varies with climate, vegetation type, water availability and urban form.
References
- Bowler, D. E., et al. (2010). Urban greening to cool towns and cities: A systematic review of the empirical evidence. Landscape and Urban Planning, 97(3), 147–155. https://doi.org/10.1016/j.landurbplan.2010.05.006
- Norton et al. (2015), for linking cooling mechanisms to green infrastructure planning.
- Yuan et al. (2026), for a recent review of urban heat mitigation strategies. 
  
  ScienceDirect
## 🛰️ Part 3 — Remote sensing, AI and geospatial assessment
### 🛰️ 7. Remote sensing for urban green infrastructure assessment
Content
- Satellite imagery for city-wide monitoring.
- Drone imagery for detailed local mapping.
- Optical and multispectral imagery for vegetation and land-cover assessment.
- Thermal imagery for surface temperature.
- Differences in spatial, temporal and spectral resolution.
- How satellite and drone data can complement one another.
References
- USGS. Landsat Surface Temperature. https://www.usgs.gov/landsat-missions/landsat-surface-temperature
- USGS. Landsat Collection 2 Surface Reflectance. https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-reflectance 
  
  U.S. Geological Survey
For the drone component, add a study that specifically uses high-resolution aerial or UAV imagery to map urban trees or vegetation. A drone RGB camera should not be described as measuring surface temperature unless thermal imagery is used.
### 🤖 8. AI and machine learning for mapping green infrastructure
Content
- Explain supervised machine learning and training data.
- Introduce Random Forest (RF), Support Vector Machine (SVM) and deep learning.
- Explain how spectral bands and indices support land-cover classification.
- Map vegetation, built-up areas, bare land and water.
- Explain training and independent validation, confusion matrices, overall accuracy, producer’s accuracy and user’s accuracy.
- Distinguish the classification of existing land cover from the later task of prioritising new GI.
References
- Breiman, L. (2001). Random forests. Machine Learning, 45, 5–32. https://doi.org/10.1023/A:1010933404324
- Mountrakis, G., Im, J., & Ogole, C. (2011). Support vector machines in remote sensing: A review. ISPRS Journal of Photogrammetry and Remote Sensing, 66(3), 247–259. https://doi.org/10.1016/j.isprsjprs.2010.11.001
- Olofsson, P., et al. (2014). Good practices for estimating area and assessing accuracy of land change. Remote Sensing of Environment, 148, 42–57. https://doi.org/10.1016/j.rse.2014.02.015
- Kasahun and Legesse (2024), and Amponsah et al. (2026), cited in your exposé as relevant RF/SVM comparison literature. Verify their full titles and publication details before including them in the final bibliography.
### 🧪 Practical 1 — LULC classification in Google Earth Engine
Demonstration: From Landsat imagery to a land-cover map

Suggested duration: 7–9 minutes
1. Load a study-area boundary, such as Greater Accra.
2. Retrieve Landsat imagery in GEE.
3. Mask clouds and cloud shadows, then create a composite.
4. Select spectral bands and indices as classification predictors.
5. Use training samples to run a Random Forest classifier.
6. Display the classified map with four classes: built-up, vegetation, bare land and water.
7. Briefly explain how classification accuracy would be assessed.
Show: The input satellite image, the classification code's key steps, and the final LULC map.
References: Breiman (2001); Olofsson et al. (2014); USGS Landsat Collection 2 documentation.

### 📊 9. Geospatial indicators for assessing urban heat and green infrastructure
Content
- LST: land surface thermal conditions.
- NDVI: vegetation greenness.
- NDBI: built-up intensity indicator.
- NDWI: water-related spectral information, where useful.
- Population density as a contextual indicator of how many people may be exposed to hot areas.
- GIS integration of these indicators.
Explain that NDVI and NDBI are indicators, not direct measurements of the cooling effect of a specific intervention. Similarly, population density alone does not establish individual heat exposure.
References
- Avdan, U., & Jovanovska, G. (2016). Algorithm for automated mapping of land surface temperature using LANDSAT 8 satellite data. Journal of Sensors, 2016, 1480307. https://doi.org/10.1155/2016/1480307
- Sobrino, J. A., Jiménez-Muñoz, J. C., & Paolini, L. (2004). Land surface temperature retrieval from LANDSAT TM 5. Remote Sensing of Environment, 90(4), 434–440. https://doi.org/10.1016/j.rse.2004.02.003
- Waleed and Sajjad (2022), and Eshetie (2024), cited in your exposé for land-cover, NDVI, NDBI, population and LST relationships. Verify full bibliographic details before final use.
- USGS, for the technical basis and interpretation of Landsat surface-temperature products. 
  
  U.S. Geological Survey
### 🌡️ Practical 2 — Land Surface Temperature mapping in GEE
Demonstration: Mapping hot and cool surfaces

Suggested duration: 5–7 minutes
1. Load Landsat thermal data for the same study area.
2. Apply the appropriate quality masks.
3. Use the official Landsat Collection 2 Level-2 surface-temperature product and its scale and offset, or demonstrate a clearly documented manual retrieval workflow.
4. Convert temperature to degrees Celsius for display.
5. Display the LST map and identify warmer and cooler surfaces.
6. Explain the distinction between LST and air temperature.
Show: The thermal data source, the temperature calculation or scaling step, and the final LST map.
References: Avdan and Jovanovska (2016); USGS Landsat Surface Temperature documentation.
Technical note: For Collection 2 Level-2 surface temperature, USGS specifies \(ST = DN \times 0.00341802 + 149.0\) in Kelvin. Convert to Celsius by subtracting 273.15. Do not combine official Level-2 temperatures with manually retrieved temperatures as if they were the same product. 

U.S. Geological Survey




### 🔄 10. AI-based mapping and assessment workflow
Content
- Acquire and preprocess imagery.
- Classify land cover using AI.
- Derive LST and vegetation indicators.
- Integrate the layers in GIS.
- Compare thermal patterns across land-cover classes.
- Produce maps that help planners investigate where green infrastructure may be needed.
References
- Breiman (2001), for Random Forest.
- Olofsson et al. (2014), for classification accuracy and area estimation.
- Waleed et al. (2023), cited in your exposé for integrating remote sensing and spatial modelling. Verify the full reference.
### 🗺️ Practical 3 — Overlay LULC, LST and NDVI in GEE
Demonstration: Connecting land cover and surface heat

Suggested duration: 4–5 minutes
1. Display the LULC map.
2. Add LST and NDVI layers.
3. Compare areas with high surface temperatures, low vegetation and extensive built-up cover.
4. Identify areas for further investigation.
5. Explain how these maps could inform green infrastructure planning.
Output: A combined visual assessment showing where thermal conditions, vegetation and urban development overlap.
References: Norton et al. (2015); Avdan and Jovanovska (2016); Olofsson et al. (2014).

## 📍 Part 4 — Green infrastructure prioritisation
### 🔥 11. Identifying urban areas with high heat and low green cover
Content
- Identify areas with high LST and low vegetation cover.
- Examine built-up intensity and population distribution.
- Compare the spatial distribution of heat and vegetation.
- Consider whether people who may be more vulnerable to heat have access to green spaces.
- Explain why a hot pixel alone is not enough to determine where an intervention should be built.
References
- Norton et al. (2015), for identifying and prioritising locations for GI.
- Sobhaninia, S., Meerow, S., Dugger, A., Hopson, T., He, C., & Wilhelmi, O. (2025). Where should the green go? A systematic literature review of methods for siting green infrastructure to mitigate rising heat and stormwater risks in cities worldwide. Urban Forestry & Urban Greening, 107, 128790. https://doi.org/10.1016/j.ufug.2025.128790 
  
  ScienceDirect
- Nazish et al. (2024), for the relationship between urban green spaces and heat-related health outcomes.
### 📍 12. AI-supported green infrastructure prioritisation
Content
- Explain how AI-based land-cover maps and thermal indicators can inform planning.
- Combine heat, vegetation, built-up intensity and population information.
- Identify locations where multiple indicators suggest a need for further investigation.
- Explain how priority areas can be classified and mapped.
- Distinguish prioritisation from selecting construction-ready sites.
Connection to your exposé: Your proposed Green Infrastructure Prioritisation Index (PI_GI) combines normalised LST, population density, built-up intensity and vegetation deficit. This can be presented as an example of combining geospatial indicators, rather than as the seminar’s main methodology.
References
- Norton et al. (2015).
- Sobhaninia et al. (2025).
- Perdinan et al. (2026), cited in your exposé as a relevant tropical-city prioritisation study. Verify the complete publication details before citing it.
- Brenner and Hack (2026), cited in your exposé for strategic green-roof planning in Wuppertal. Verify the title, journal and DOI before use.
### 🌳 13. Potential green infrastructure interventions
Content
- Street trees and tree-canopy expansion.
- New or improved urban parks.
- Green corridors and connected vegetation.
- Green roofs and vertical greening.
- Vegetation restoration.
- Matching possible intervention types to local urban form and planning context.
References
- Norton et al. (2015), for selecting interventions that are fit for place and purpose.
- Cohen-Shacham et al. (2016), for nature-based solutions.
- Sobhaninia et al. (2025), for methods used to identify suitable GI locations.
## ⚖️ Part 5 — Targeted versus uniform distribution
### 🟰 14. Uniform distribution of green infrastructure
Content
- Explain the idea of distributing green interventions broadly across an urban area.
- Potential advantages: broad geographical coverage, neighbourhood access and distribution of benefits.
- Potential disadvantages: equal investment may not address unequal heat conditions or unequal levels of need.
- Explain why uniform distribution does not necessarily mean equal benefits for every neighbourhood.
References
- Sobhaninia et al. (2025), for approaches to GI siting and the choices involved in spatial planning.
- WHO Regional Office for Europe (2016), for green-space access and health considerations.
Important: Present uniform distribution as a planning strategy to evaluate, not as an approach that is inherently ineffective.
### 🎯 15. Targeted distribution of green infrastructure
Content
- Explain how planners can direct interventions towards areas identified as priorities.
- Use AI classification and geospatial indicators to inform location decisions.
- Discuss potential benefits for cooling, populations exposed to heat and areas with limited vegetation.
- Consider land availability, maintenance, access and community preferences.
- Explain how targeted investments may overlook other neighbourhoods if equity is not considered.
References
- Norton et al. (2015).
- Sobhaninia et al. (2025).
- Brenner and Hack (2026), from your exposé, after verifying its full bibliographic details.
### ⚖️ 16. Does targeted placement outperform uniform distribution?
This should be the central analytical section of the seminar.
Content
- What scientific studies report about targeted versus uniform GI placement.
- Compare potential cooling outcomes under comparable intervention budgets and areas.
- Consider how many people may benefit and where they live.
- Examine environmental justice and access to green space.
- Consider implementation costs, land availability, maintenance and feasibility.
- Discuss when targeted, uniform or combined approaches might be preferable.
- Distinguish results from modelling studies from evidence based on implemented interventions.
References
- Norton et al. (2015), for a spatial prioritisation framework.
- Sobhaninia et al. (2025), for the wider evidence on GI siting approaches.
- Bowler et al. (2010), for empirical evidence on urban greening and cooling.
- Liu et al. (2026), the paper identified in your earlier research materials, DOI: https://doi.org/10.1016/j.scs.2026.107228. Check the article's full title and methods before using it to support a direct comparison.
How to present the comparison: Use a table that compares the two strategies across cooling potential, geographical coverage, distribution of beneficiaries, equity, cost and feasibility. Only conclude that one strategy performs better where the evidence supports that conclusion.
### ✅ 17. Evaluating the effectiveness of AI-supported GI planning
Content
- How to measure surface-temperature changes.
- How to evaluate land-cover classification accuracy.
- How to assess vegetation coverage and green-space accessibility.
- How to compare alternative intervention-placement scenarios.
- How to account for uncertainty, cost, equity and maintenance.
- Why a high-performing AI classifier does not automatically prove that a GI intervention will work.
References
- Olofsson et al. (2014), for classification accuracy and uncertainty.
- Norton et al. (2015), for evaluating GI prioritisation in planning.
- Sobhaninia et al. (2025), for GI siting methods and the implications of planning choices.
## 🏙️ Part 6 — Case study, challenges and conclusion
### 🇬🇭 18. Case study: Applying AI-based assessment in an urban area
Recommended example: Greater Accra, Ghana
Content
- Introduce Greater Accra and its urbanisation context.
- Explain how satellite imagery can map land-cover changes.
- Show a LULC classification and LST map, ideally generated in your GEE practical.
- Discuss how vegetation patterns, built-up development and surface temperature can be examined together.
- Illustrate how the results might inform GI planning.
- Use published evidence to discuss targeted versus uniform placement rather than claiming your maps independently prove which strategy is more effective.
References drawn from your exposé
- Wemegah et al. (2020), for urban thermal conditions in Greater Accra.
- Gyile et al. (2025), for land-cover change and urban thermal patterns.
- Waleed and Sajjad (2022), for LULC and LST analysis.
- Ghana Statistical Service (GSS, 2021 or 2022), for census and administrative context.
The complete titles and publication details of the cited Ghana-focused studies should be checked against your exposé's reference list before finalising the slides.
### 🧭 19. Challenges and considerations
Content
- Spatial resolution and data availability.
- Cloud contamination and seasonal differences.
- Classification errors and uncertainty.
- Differences between surface and air temperature.
- Transferability of AI models between cities.
- Land ownership, land availability, maintenance and funding.
- Community participation and equitable planning.
- Limitations of using satellite-derived indicators to select individual intervention sites.
References
- Olofsson et al. (2014), for accuracy assessment and uncertainty.
- USGS Landsat documentation, for surface-reflectance and temperature product specifications.
- Sobhaninia et al. (2025), for challenges in GI siting and spatial planning.
### 💡 20. Conclusion and recommendations
Content
- Summarise how AI and remote sensing support urban ecosystem assessment.
- Explain the contribution of LULC mapping, LST and vegetation indicators.
- Show how these data can inform GI prioritisation.
- Summarise the evidence on targeted versus uniform distribution.
- Recommend that planners combine geospatial evidence with local verification, community input and feasibility assessment.
References
- Norton et al. (2015).
- Sobhaninia et al. (2025).
- Bowler et al. (2010).
- WHO Regional Office for Europe (2016).
### 📚 21. References
Include a complete reference list in the final slides. Prioritise the peer-reviewed studies and official technical documentation listed above. Add the Ghana-focused studies and other sources from your exposé only after confirming their full bibliographic details.
### 💬 22. Questions, discussion and Kahoot
This follows the presentation and is part of the lecturer's additional discussion session.
- Audience questions.
- Discussion of the main seminar question.
- A 5–7-minute multiple-choice Kahoot quiz.
- Discussion of whether AI-informed targeting should replace uniform distribution or complement it.

## ⏱️ Suggested timing
Section	Approx. time
1–4. Introduction and urban heat	9 min
5–6. Green infrastructure and cooling	6 min
7–10. Remote sensing, AI and indicators	8 min
GEE practicals 1–3	16 min
11–13. GI prioritisation and interventions	5 min
14–17. Targeted versus uniform distribution	7 min
18–20. Case study, challenges and conclusion	4 min
Total	55 min
The Kahoot quiz and discussion then take place during the subsequent 30-minute session.
One final point about the references: the strongest starting sources are Norton et al. (2015), Sobhaninia et al. (2025), Bowler et al. (2010), Breiman (2001), Mountrakis et al. (2011), Olofsson et al. (2014), Avdan and Jovanovska (2016), and the USGS Landsat documentation. Together, these cover the planning question, cooling evidence, AI methods, accuracy assessment and the technical basis of your GEE demonstrations.

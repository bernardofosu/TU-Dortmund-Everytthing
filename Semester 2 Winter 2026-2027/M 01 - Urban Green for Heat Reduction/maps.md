Map 1: Climate Function Map
1. Weather description — rainfall and temperature charts showing minimum, maximum, patterns, duration and seasons.
2. Climatope map — classify the eight climate zones.
3. Climate elements map — air corridors, heat production, day/night cooling, cold- and fresh-air production, and cool/warm-air circulation.
4. Climate protection map — CO₂ emissions and CO₂ fixation capacity.
5. Exposure map — sun exposure and humidity hotspots over time.
6. Final Climate Function Map — overlay the relevant GIS layers and identify strengths and weaknesses.
Map 2: Habitats/Species Map
1. Habitat map — land-cover types, protected areas, percentage cover, habitat mosaics, specificity and quality.
2. Environmental flows map — corridors, barriers, fragmentation, connectivity/percolation and seasonal uses.
3. Species map — species diversity, species richness and species of interest, using existing databases or your own mapping.
4. Quality and risks map — mortality risks, habitat patches, stepping stones, corridors and fragmentation.
5. Climate interactions diagram — use IF/THEN relationships linking temperature, rain and snow to ecological effects, supported by evidence where possible.
6. Final Habitats/Species Map — visualise and assess the mapped habitats and species.


Which data do we need, and what do we overlay at each step?
Based on your lecturer's PPTClimate.pdf and PPT Biotop.pdf, we need to separate three things:
- Input data: the datasets you download or obtain from existing portals.
- Individual maps: the maps you create from those datasets.
- GIS overlays: the maps and layers you combine to produce an assessment.
You do not need to overlay everything at every step. Each overlay should answer a specific question.
Map 1 — Climate Function Map
Step 1. Weather description
Lecturer's slides: PPTClimate, page 6

Data to obtain
- Air-temperature records: minimum, maximum and seasonal patterns.
- Rainfall records: amounts, patterns, duration and seasonal variation.
- Historical records, where available.
Output: temperature and rainfall charts, not necessarily a GIS map.
Data	Source options
Temperature and rainfall observations	DWD weather stations or suitable climate datasets
Historical and seasonal trends	Station records or gridded climate datasets

Overlay needed: none for the charts. If you map the stations, you can overlay their locations with your study-area boundary.
Step 2. Climatope map
Lecturer's slides: PPTClimate, page 7

Data to obtain
- Land-cover data.
- Vegetation and green-space data.
- Building footprints, density and urban morphology.
- Elevation/topography.
- Water bodies.
Output: a map classifying the area into the eight climate zones specified by your lecturer.
Input layer	Purpose
Land cover	Distinguish vegetation, built-up areas, agriculture and open land
Buildings / urban morphology	Identify dense urban, residential and industrial forms
Elevation	Account for terrain differences
Vegetation and water	Help distinguish green-space and water-related climate zones

Overlay in GIS: combine these layers to support classification into the eight climatopes. This is a classification exercise, not simply adding all layers together.
Step 3. Climate elements map
Lecturer's slides: PPTClimate, page 8

Data to obtain
- FITNAH-3D air temperature at 01:30, 05:30, 12:30 and 15:30.
- Cold-air production and night-time cooling layers.
- Cold-air flow direction, velocity and air corridors.
- Land cover, green spaces and topography as supporting layers.
Your existing FITNAH-3D connection is useful here.
Individual map/layer	What it tells you
Air temperature	Where warmer and cooler air occurs
Cold-air production	Where cold air is generated
Cold-air flow and corridors	Where cold air moves through the landscape
Day/night cooling	Where cooling processes are stronger or weaker
Heat production	Where the landscape is associated with heat accumulation or production

Overlay in GIS
1. Air temperature + your study-area boundary → identify warm and cool areas.
2. Cold-air production + terrain + land cover → examine potential cold-air source areas.
3. Cold-air flow + buildings/roads + green spaces → interpret possible air corridors and barriers.
4. Daytime and night-time layers → compare how the climate pattern changes by time of day.
Keep the individual layers separate until you understand them; then combine them into a climate-elements assessment.
Step 4. Climate protection map
Lecturer's slides: PPTClimate, page 9

Data to obtain
- CO₂ emissions data, ideally spatially attributed to relevant sources or areas.
- CO₂ fixation or sequestration capacity data.
- Land cover and vegetation.
- Tree or forest data, where available.
Output: a map of climate-protection needs and potential.

Overlay in GIS
- Emissions data + study-area boundary → map the spatial distribution of emissions.
- Vegetation/forest data + carbon-fixation estimates → map potential CO₂ fixation.
- Emissions + fixation capacity → compare climate-protection pressures and potential, if the datasets are compatible.
Important: ordinary land-cover data alone do not give you actual CO₂ emissions or sequestration rates. You need suitable measurements, estimates or a documented calculation method.
Step 5. Exposure map
Lecturer's slides: PPTClimate, page 10

Data to obtain
- Solar radiation or sun-exposure data.
- Humidity observations or suitable humidity datasets.
- Building heights and shadows, if relevant to your method.
- Vegetation and land cover.
- Time-specific climate data, if you want to assess changes over time.
Overlay in GIS
- Solar radiation + buildings/vegetation → assess where solar exposure is high or low.
- Humidity data + study-area boundary → map humidity patterns or hotspots.
- Exposure layers + land cover → assess which landscape types experience greater exposure.
Do not assume that FITNAH provides every humidity or solar-exposure layer you need; check the available layer catalogue first.
Step 6. Final Climate Function Map
Lecturer's slides: PPTClimate, page 11

This is where the previous climate analyses come together.
Climatope map

Climate-zone classification

Climate-elements map

Heat, cooling and air movement

Climate-protection and exposure maps

CO₂, solar exposure and humidity

Climate Function Map

Identify strengths and weaknesses


You can use GIS overlay, spatial comparison and a documented assessment method to identify, for example:
- Important cool-air source areas and ventilation corridors.
- Areas with high heat stress and limited cooling.
- Green spaces with important climate functions.
- Locations where climate-protection measures may be needed.
Do not automatically add every variable into a single weighted index unless your lecturer or your group has chosen and justified that method.
Map 2 — Habitats/Species Map
Step 1. Habitat map
Lecturer's slides: PPT Biotop, page 5

Data to obtain
- Land-cover and habitat polygons.
- Protected-area boundaries, such as Natura 2000 where relevant.
- Vegetation, tree and green-space data.
- Habitat condition or ecological-quality data, where available.
Overlay in GIS
- Land cover + protected areas → map habitat types and protection status.
- Land-cover polygons + study-area boundary → calculate percentage cover.
- Habitat polygons + vegetation or ecological-quality information → assess habitat condition where evidence exists.
Output: habitat distribution, percentage cover, habitat mosaics, specificity and quality.
Step 2. Environmental flows map
Lecturer's slides: PPT Biotop, page 6

Data to obtain
- Habitat polygons.
- Green corridors and connecting vegetation.
- Roads, railways, fences or other relevant barriers.
- Watercourses and other potential ecological connections.
- Species movement or seasonal-use information, if available.
Overlay in GIS
Overlay	Purpose
Habitats + green corridors	Identify connections between habitat patches
Habitats + roads/railways	Identify potential fragmentation and barriers
Habitat patches + landscape barriers	Assess potential connectivity
Ecological network + seasonal-use information	Identify seasonal connections or movement patterns

Output: ecological corridors, barriers, fragmentation and potential habitat connectivity.

A map of potential connectivity does not, by itself, prove that a species actually uses a corridor.
Step 3. Species map
Lecturer's slides: PPT Biotop, page 7

Data to obtain
- Species occurrence records.
- Biodiversity databases or field-survey observations.
- Habitat polygons, to provide ecological context.
- Records of species of interest.
Overlay in GIS
- Species observations + study-area boundary → map species locations.
- Species records + habitat polygons → assess which habitats have recorded species.
- Species records grouped by species → calculate richness or diversity where the data support it.
Output: species distribution, richness, diversity and species of interest.

Species records are observations, not a complete census of all species present.
Step 4. Habitat quality and risks map
Lecturer's slides: PPT Biotop, page 8

Data to obtain
- Habitat area, structure, condition and management.
- Roads and other mortality hazards.
- Drought or other relevant environmental-risk data.
- Habitat patches and potential stepping stones.
- Corridor and barrier layers from Step 2.
Overlay in GIS
- Habitat patches + road network → identify potential road-related risks.
- Habitat condition + drought data → assess potential drought-related risks.
- Habitat patches + corridors + barriers → identify isolated patches and potential stepping stones.
- Quality indicators + risk indicators → assess habitat strengths and weaknesses.
Output: habitat quality, potential mortality risks, fragmentation and connectivity priorities.
Step 5. Climate interactions diagram
Lecturer's slides: PPT Biotop, page 10

This is an IF/THEN diagram, not necessarily a GIS map.

You need climate evidence such as temperature, rainfall or snow information, together with evidence about ecological effects.

For example:
- IF temperature increases, THEN a heat-sensitive species may experience greater thermal stress.
- IF drought duration increases, THEN water stress in sensitive habitats may increase.
- IF snow cover decreases, THEN effects on particular species or habitats may occur, depending on the local ecology.
These are hypotheses to investigate, not conclusions to assume. Support each relationship with relevant literature, observations or other evidence.
Step 6. Final Habitats/Species Map
Lecturer's slides: PPT Biotop, page 9

Bring together the habitat, connectivity, species and quality/risk assessments to communicate:
- Important habitat areas.
- Species records and areas of ecological interest.
- Corridors, barriers and isolated patches.
- Habitat-quality strengths and weaknesses.
- Priorities for ecological improvement.
The final map should communicate the assessment clearly. It does not mean every layer must be merged into one raster or one score.
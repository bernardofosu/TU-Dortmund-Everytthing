# 🗺️ Climate Function Map: HTML Label Codes for the QGIS Layout

**Project:** M 01 Urban Green for Heat Reduction, TU Dortmund
**Study area:** Dortmund Innenstadt-Ost
**Data:** LANUK Klimaanalyse NRW 2026
**Main layer:** `07_innenstadt_ost_climate_cat`

---

## 🧭 How to add any label

1. ➕ **Add Item → Add Label** and draw a box in the layout
2. ✅ In **Item Properties**, tick **Render as HTML**
3. 🗑️ Delete the default text
4. 📋 Paste the code
5. 🔄 Click **Refresh** if the numbers do not show at once

💡 **Tips**
- Everything between `[% … %]` is **calculated live** by QGIS from your layers. The numbers update by themselves.
- If a layer name in your project is different, change it in the code (e.g. `'07_innenstadt_ost_climate_cat'`).
- `'Vorstadtklima'` (suburban climate) stays German because it is the value stored in the LANUK data. It does not appear on the map.
- 💾 **Ctrl + S** saves the layout inside the project. The template (`.qpt`) is only updated with **Layout → Save as Template…**

---

## 1️⃣ Title 🏷️

```html
<div style="font-family:Arial;">
<span style="font-size:16pt; font-weight:bold;">Climate Function Map: Dortmund Innenstadt-Ost</span><br>
<span style="font-size:9pt; color:#555555;">Typical summer day (21 June) · LANUK Klimaanalyse NRW 2026</span>
</div>
```

🎨 For the TU green title colour, add `color:#00873d;` after `font-weight:bold;`

---

## 2️⃣ Thermal component table 🌡️

```html
<div style="font-family:Arial;">
<b style="font-size:11pt;">Thermal component: heat load (day and night)</b>
<table style="border-collapse:collapse; width:100%; font-size:8pt; margin-top:6px;">
<tr style="background:#bfbfbf;">
 <th style="border:1px solid #888; padding:4px; width:16%;">Category</th>
 <th style="border:1px solid #888; padding:4px; width:26%;">Name</th>
 <th style="border:1px solid #888; padding:4px;">Description</th>
</tr>
<tr>
 <td style="border:1px solid #888; background:#1a9850; height:40px;"></td>
 <td style="border:1px solid #888; padding:4px;"><b>Cooling area</b></td>
 <td style="border:1px solid #888; padding:4px;">Open land, forest, urban green and water. Cold- and fresh-air generation.</td>
</tr>
<tr>
 <td style="border:1px solid #888; background:#91cf60; height:40px;"></td>
 <td style="border:1px solid #888; padding:4px;"><b>Low heat load</b></td>
 <td style="border:1px solid #888; padding:4px;">Built-up. Low heat load by day and night.</td>
</tr>
<tr>
 <td style="border:1px solid #888; background:#ffffbf; height:40px;"></td>
 <td style="border:1px solid #888; padding:4px;"><b>Moderate heat load</b></td>
 <td style="border:1px solid #888; padding:4px;">Built-up. PET 29–35 °C by day, or slightly warm nights (17–18 °C).</td>
</tr>
<tr>
 <td style="border:1px solid #888; background:#fc8d59; height:40px;"></td>
 <td style="border:1px solid #888; padding:4px;"><b>Strong heat load</b></td>
 <td style="border:1px solid #888; padding:4px;">Built-up. PET 35–41 °C by day and/or warm nights (18–19 °C).</td>
</tr>
<tr>
 <td style="border:1px solid #888; background:#d73027; height:40px;"></td>
 <td style="border:1px solid #888; padding:4px;"><b>Extreme heat load</b></td>
 <td style="border:1px solid #888; padding:4px;">Built-up. PET above 41 °C by day and/or very warm nights (above 19 °C).</td>
</tr>
</table>
</div>
```

📏 Row height: change `height:40px`.

---

## 3️⃣ Dynamic component table 🌬️

```html
<div style="font-family:Arial;">
<b style="font-size:11pt;">Dynamic component: cold air</b>
<table style="border-collapse:collapse; width:100%; font-size:8pt; margin-top:6px;">
<tr style="background:#bfbfbf;">
 <th style="border:1px solid #888; padding:4px; width:16%;">Symbol</th>
 <th style="border:1px solid #888; padding:4px; width:26%;">Name</th>
 <th style="border:1px solid #888; padding:4px;">Description</th>
</tr>
<tr>
 <td style="border:1px solid #888; text-align:center; font-size:16pt; color:#08519c;">&#8593;</td>
 <td style="border:1px solid #888; padding:4px;"><b>Cold air flow</b></td>
 <td style="border:1px solid #888; padding:4px;">Direction and speed of cold air at night (04:00). Arrow size shows speed.</td>
</tr>
<tr>
 <td style="border:1px solid #888; text-align:center; font-size:16pt; color:#2166ac;">&#9636;</td>
 <td style="border:1px solid #888; padding:4px;"><b>Cold air production</b></td>
 <td style="border:1px solid #888; padding:4px;">Above-average cold air production (more than 26 m³ per m² per hour).</td>
</tr>
<tr>
 <td style="border:1px solid #888; text-align:center; font-size:16pt; color:#ffd700;">&#9733;</td>
 <td style="border:1px solid #888; padding:4px;"><b>Air exchange area</b></td>
 <td style="border:1px solid #888; padding:4px;">Where cold air from green areas flows into the built-up area.</td>
</tr>
</table>
</div>
```

🔣 Symbols: `&#8593;` = ↑ arrow, `&#9636;` = ▤ hatched square, `&#9733;` = ★ star

---

## 4️⃣ Terrain height bar (ruler style) ⛰️

```html
<div style="font-family:Arial; font-size:8pt;">
<b style="font-size:10pt;">Terrain height (m above sea level)</b>
<table cellspacing="0" cellpadding="0" style="margin-top:4px;">
<tr>
 <td width="45" bgcolor="#fee0d2" style="font-size:10pt;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
 <td width="45" bgcolor="#fcbba1" style="font-size:10pt;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
 <td width="45" bgcolor="#fc9272" style="font-size:10pt;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
 <td width="45" bgcolor="#fb6a4a" style="font-size:10pt;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
 <td width="45" bgcolor="#cb181d" style="font-size:10pt;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
 <td></td>
</tr>
<tr>
 <td width="45">75</td><td width="45">90</td><td width="45">105</td>
 <td width="45">112</td><td width="45">122</td><td>135 m</td>
</tr>
</table>
<span style="color:#555555;">North (low) &#8594; South (high)</span>
</div>
```

⚠️ Why `bgcolor` and `&nbsp;`: QGIS ignores CSS width and height on **empty** cells, so they collapse. `bgcolor` + `width` + spaces keep the bar visible.
📏 Longer bar: change every `width="45"` to `55`. Thicker bar: change `font-size:10pt` in the colour cells to `14pt`.
🎨 Copy the exact colours from your height layer classes (HTML notation).

---

## 5️⃣ Box: hot areas, highest values 🔥

```html
<div style="font-family:Arial; font-size:9pt; line-height:1.4;">
<b style="color:#d73027;">Hot areas (strong and extreme heat load)</b><br>
Area: <b>[% round(aggregate('07_innenstadt_ost_climate_cat','sum',$area,filter:="climate_cat">=4)/10000,1) %] ha</b><br>
Highest PET by day (14:00): <b>[% round(aggregate('07_innenstadt_ost_climate_cat','max',"day_mean",filter:="climate_cat">=4),1) %] °C</b><br>
Highest air temperature at night (04:00): <b>[% round(aggregate('07_innenstadt_ost_climate_cat','max',"night_mean",filter:="climate_cat">=4),1) %] °C</b>
</div>
```

---

## 6️⃣ Box: cool areas, lowest values 🌳

```html
<div style="font-family:Arial; font-size:9pt; line-height:1.4;">
<b style="color:#1a9850;">Cool areas (cooling areas)</b><br>
Area: <b>[% round(aggregate('07_innenstadt_ost_climate_cat','sum',$area,filter:="climate_cat"=1)/10000,1) %] ha</b><br>
Lowest PET by day (14:00): <b>[% round(aggregate('07_innenstadt_ost_climate_cat','min',"day_mean",filter:="climate_cat"=1),1) %] °C</b><br>
Lowest air temperature at night (04:00): <b>[% round(aggregate('07_innenstadt_ost_climate_cat','min',"night_mean",filter:="climate_cat"=1),1) %] °C</b>
</div>
```

---

## 7️⃣ Box: urban heat island 🏙️🌙

```html
<div style="font-family:Arial; font-size:9pt; line-height:1.4;">
<b style="color:#08306b;">Urban heat island (night, 04:00)</b><br>
Highest night temperature, hot areas: <b>[% round(aggregate('07_innenstadt_ost_climate_cat','max',"night_mean",filter:="climate_cat">=4),1) %] °C</b><br>
Lowest night temperature, suburban areas: <b>[% round(aggregate('07_innenstadt_ost_climate_cat','min',"night_mean",filter:="Klimatoptyp"='Vorstadtklima'),1) %] °C</b><br>
<b>Maximum UHI intensity: +[% round(aggregate('07_innenstadt_ost_climate_cat','max',"night_mean",filter:="climate_cat">=4),1) - round(aggregate('07_innenstadt_ost_climate_cat','min',"night_mean",filter:="Klimatoptyp"='Vorstadtklima'),1) %] °C</b>
</div>
```

🧮 This version **rounds first, then subtracts**, so the box adds up for the reader (e.g. 18.7 − 13.9 = 4.8). Subtracting the exact values gives 4.7, because both numbers above are rounded.
📖 UHI here = highest night air temperature in hot areas minus lowest in suburban areas. LANUK has no night values over open land, so suburban areas are the reference.

---

## 8️⃣ Statistics heading 📊

```html
<div style="font-family:Arial;">
<span style="font-size:12pt; font-weight:bold;">Highest and lowest values: heat, cooling and UHI</span><br>
<span style="font-size:8pt; color:#555555;">PET at 14:00 · air temperature at 04:00 · LANUK 2026</span>
</div>
```

---

## 9️⃣ Source line 📚

```html
<div style="font-family:Arial; font-size:7pt; color:#555555;">
Data: LANUK Klimaanalyse NRW 2026 (FITNAH-3D, typical summer day, 21 June; PET 14:00, air temperature 04:00). Classification rules after SenSBW / GEO-NET (2025). Terrain: EU-DEM 25 m. Basemap: Esri Light Gray. Roads: © OpenStreetMap contributors. EPSG:25832.
</div>
```

```html
<html><body style="background:#fff; margin:12px; width:640px;">
<div style="font-family:Arial; font-size:7.5pt; color:#333333;">
<b style="font-size:10pt;">How the 5 classes were made</b><br>
<span style="color:#555555;">Mean values per climatope (zonal statistics, LANUK 2026). Limits and table after Berlin (SenSBW / GEO-NET 2025).</span>
<table cellspacing="0" cellpadding="3" style="margin-top:5px; border-collapse:collapse; font-size:7.5pt; font-family:Arial;">
<tr>
<td valign="top">
 <b>1. Day stage</b> (PET at 14:00)
 <table cellspacing="0" cellpadding="3" border="1" style="border-collapse:collapse; margin-top:3px; font-size:7.5pt; font-family:Arial;">
 <tr bgcolor="#d9d9d9"><td><b>PET</b></td><td><b>Stage</b></td></tr>
 <tr><td>up to 29 °C</td><td align="center">1</td></tr>
 <tr><td>29–35 °C</td><td align="center">2</td></tr>
 <tr><td>35–41 °C</td><td align="center">3</td></tr>
 <tr><td>above 41 °C</td><td align="center">4</td></tr>
 </table>
</td>
<td width="12"></td>
<td valign="top">
 <b>2. Night stage</b> (air temp. at 04:00)
 <table cellspacing="0" cellpadding="3" border="1" style="border-collapse:collapse; margin-top:3px; font-size:7.5pt; font-family:Arial;">
 <tr bgcolor="#d9d9d9"><td><b>Temperature</b></td><td><b>Stage</b></td></tr>
 <tr><td>up to 17 °C</td><td align="center">1</td></tr>
 <tr><td>17–18 °C</td><td align="center">2</td></tr>
 <tr><td>18–19 °C</td><td align="center">3</td></tr>
 <tr><td>above 19 °C</td><td align="center">4</td></tr>
 </table>
</td>
<td width="12"></td>
<td valign="top">
 <b>3. Residential: day &#215; night</b>
 <table cellspacing="0" cellpadding="3" border="1" style="border-collapse:collapse; margin-top:3px; font-size:7.5pt; font-family:Arial;">
 <tr bgcolor="#d9d9d9"><td><b>Day \ Night</b></td><td width="22" align="center"><b>1</b></td><td width="22" align="center"><b>2</b></td><td width="22" align="center"><b>3</b></td><td width="22" align="center"><b>4</b></td></tr>
 <tr><td align="center"><b>1</b></td><td bgcolor="#91cf60" width="20" align="center">2</td><td bgcolor="#ffffbf" align="center">3</td><td bgcolor="#ffffbf" align="center">3</td><td bgcolor="#fc8d59" align="center">4</td></tr>
 <tr><td align="center"><b>2</b></td><td bgcolor="#91cf60" width="20" align="center">2</td><td bgcolor="#ffffbf" align="center">3</td><td bgcolor="#fc8d59" align="center">4</td><td bgcolor="#fc8d59" align="center">4</td></tr>
 <tr><td align="center"><b>3</b></td><td bgcolor="#ffffbf" align="center">3</td><td bgcolor="#ffffbf" align="center">3</td><td bgcolor="#fc8d59" align="center">4</td><td bgcolor="#d73027" align="center"><font color="#ffffff">5</font></td></tr>
 <tr><td align="center"><b>4</b></td><td bgcolor="#fc8d59" align="center">4</td><td bgcolor="#fc8d59" align="center">4</td><td bgcolor="#fc8d59" align="center">4</td><td bgcolor="#d73027" align="center"><font color="#ffffff">5</font></td></tr>
 </table>
</td>
</tr>
</table>
<table cellspacing="0" cellpadding="2" style="margin-top:6px; font-size:7.5pt; font-family:Arial;">
<tr><td bgcolor="#1a9850" width="14">&nbsp;</td><td><b>Class 1:</b> open land, forest, urban green and water (cooling areas), always class 1</td></tr>
<tr><td align="center" width="14">&#8226;</td><td><b>Commercial, industrial, roads, rail:</b> day stage only (stage 1&#8211;4 = class 2&#8211;5)</td></tr>
<tr><td align="center" width="14">&#8226;</td><td><b>Residential:</b> table above (night weighted more, people sleep there)</td></tr>
</table>
</div></body></html>
```

## 🧩 Not HTML

- 📏 **Scale bar:** Add Item → Add Scale Bar
- 🧭 **North arrow:** Add Item → Add North Arrow
- 🗺️ **Map:** Add Item → Add Map (set **Follow map theme** if you use themes)

---

## ✅ Before you finish

- [ ] Practice layers (90–94) unticked
- [ ] Production hatching drawn on the map
- [ ] Boundary visible (black line)
- [ ] UHI box uses the rounded version (#7)
- [ ] 💾 Ctrl + S
- [ ] 📤 Layout → Save as Template… (`M01_overlay_map_template.qpt`)
- [ ] 🖼️ Layout → Export as Image (300 dpi)

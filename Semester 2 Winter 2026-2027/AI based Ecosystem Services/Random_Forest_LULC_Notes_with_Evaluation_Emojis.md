# Random Forest LULC classification code

Your Google Earth Engine (GEE) script uses Random Forest, a supervised machine-learning algorithm, to classify land cover in Accra, Ghana, for 2020.

It produces a map with four classes:

- Water
- Vegetation
- Bareland
- Built-up

The model learns from your labelled training points, extracts Sentinel-2 spectral values at those locations, learns patterns associated with each class, and predicts the class of other pixels across Accra.

Let's go through the code section by section, using simple examples.

## 1. Understand the complete workflow

Your labelled training points

Water, vegetation, bareland and built-up

Sentinel-2 imagery for 2020

Cloud masking and median composite

Extract spectral features

B2, B3, B4, B8, B11 and B12

Train Random Forest

100 decision trees

Classify and validate

Land-cover map and accuracy assessment

## 2. Section 1 — Load your uploaded assets

Your code starts with:

```
var water = ee.FeatureCollection(
  'projects/seraphic-music-452922-a5/assets/Water'
);
```

It does the same for vegetation, bareland, built-up and your Accra boundary.

### What is an asset?

An asset is a dataset stored in your Google Earth Engine account or project.

Your four class assets contain the reference locations you prepared for training. In this script, they are expected to be point or other geometries that represent the relevant land-cover classes.

The Accra boundary defines the area of interest (AOI):

```
var aoi = accra.geometry();

Map.centerObject(accra, 9);
```

- `accra.geometry()` extracts the boundary geometry.
- `Map.centerObject(accra, 9)` zooms the map to Accra.
- `Map.addLayer(...)` displays the boundary, initially hidden because its final argument is `false`.

Why this matters: the boundary tells GEE where to collect imagery and where to produce the final land-cover map.

## 3. Section 2 — Assign numeric class labels

Your code assigns these labels:

| Class label | Land-cover class | Map colour |
| ----------- | ---------------- | ---------- |
| 0           | Water            | Blue       |
| 1           | Vegetation       | Green      |
| 2           | Bareland         | Yellow     |
| 3           | Built-up         | Red        |

For example:

```
water = water.map(function(f) {
  return f.set('class', 0);
});
```

This means: go through every water feature and add a property called `class` with the value `0`.

The other datasets receive their corresponding labels.

### Why use numbers?

The classifier needs a target property to learn. Instead of learning the text label `"Water"`, it learns the numeric class value `0`.

The class number is simply an identifier; it does not mean water is less important than built-up land.

### Combine the training points

```
var allPoints = water
  .merge(vegetation)
  .merge(bareland)
  .merge(builtup);

allPoints = allPoints.filterBounds(aoi);
```

- `.merge()` combines the four feature collections into one.
- `.filterBounds(aoi)` retains features that intersect the Accra boundary.

You now have one collection containing labelled examples from all four classes.

The `print()` statements report collection sizes. Note that the class-specific counts are printed before the final combined collection is filtered to Accra, so those individual counts may include features outside the boundary.

## 4. Section 3 — Load Sentinel-2 imagery for 2020

Your code:

```
var s2 = ee.ImageCollection(
  'COPERNICUS/S2_SR_HARMONIZED'
)
.filterBounds(aoi)
.filterDate('2020-01-01', '2021-01-01')
.filter(
  ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 70)
);
```

Let's break it down.

- `ImageCollection`: loads a collection of Sentinel-2 images.
- `filterBounds(aoi)`: keeps images that intersect Accra.
- `filterDate(...)`: selects images from January 1, 2020, up to but not including January 1, 2021.
- `CLOUDY_PIXEL_PERCENTAGE < 70`: excludes scenes with 70% or more reported cloud cover.

Important: the cloud-percentage filter applies to the whole image scene, not just the part covering Accra. An image can have high overall cloud cover while the area over Accra is relatively clear.

### What does the cloud-masking function do?

```
function maskS2(image) {
  var scl = image.select('SCL');

  var mask = scl.neq(1)
    .and(scl.neq(3))
    .and(scl.neq(8))
    .and(scl.neq(9))
    .and(scl.neq(10))
    .and(scl.neq(11));

  return image.updateMask(mask);
}
```

The `SCL` band is the Sentinel-2 Scene Classification Layer. Your function masks selected categories:

| SCL value | Meaning                       |
| --------- | ----------------------------- |
| 1         | Saturated or defective pixels |
| 3         | Cloud shadows                 |
| 8         | Medium-probability clouds     |
| 9         | High-probability clouds       |
| 10        | Cirrus                        |
| 11        | Snow or ice                   |

The function keeps pixels that do not belong to those categories.

In simple terms, it attempts to remove contaminated observations before the model uses the imagery. It does not guarantee that every cloud or shadow is removed.

### What is the median composite?

```
var composite = s2
  .map(maskS2)
  .median()
  .clip(aoi);
```

For each pixel location, GEE calculates the median of the available unmasked observations for each band.

Imagine the same pixel has three valid observations of a band:

`100, 120, 900`

The median is `120`, which is less affected by the unusually high value than the mean would be.

The composite combines observations across 2020; it is not a single satellite image from one date.

`clip(aoi)` limits the image to the Accra boundary.

## 5. Section 4 — Select the predictor bands

Your code selects six Sentinel-2 bands:

```
var bands = [
  'B2', 'B3', 'B4',
  'B8', 'B11', 'B12'
];

var image = composite.select(bands);
```

These bands become the features (predictors) that Random Forest uses to learn land-cover patterns.

| Band | Name                      | What it measures               |
| ---- | ------------------------- | ------------------------------ |
| B2   | Blue                      | Reflected blue light           |
| B3   | Green                     | Reflected green light          |
| B4   | Red                       | Reflected red light            |
| B8   | Near-infrared (NIR)       | Near-infrared reflectance      |
| B11  | Shortwave infrared (SWIR) | Shortwave infrared reflectance |
| B12  | Shortwave infrared (SWIR) | Shortwave infrared reflectance |

Different surfaces reflect light differently. For example, healthy vegetation often reflects strongly in NIR, while water commonly absorbs much of it. Built-up surfaces and bare soil can have overlapping spectral patterns.

Random Forest learns combinations of these band values that help distinguish your four labelled classes.

Note on resolution: B2, B3, B4 and B8 have 10 m native resolution, whereas B11 and B12 have 20 m native resolution. Selecting all six bands does not make the SWIR bands intrinsically 10 m. Sampling and classification at 10 m require GEE to align the bands to the requested scale; the 20 m bands do not gain additional spatial detail.

## 6. Section 5 — Extract spectral values at the training points

Your code:

```
var samples = image.sampleRegions({
  collection: allPoints,
  properties: ['class'],
  scale: 10,
  geometries: true,
  tileScale: 4
});
```

This is where your labelled locations are connected to the satellite imagery.

For each training feature, GEE extracts the predictor-band values and preserves the `class` property.

Imagine one labelled vegetation point. Its sample might look conceptually like this:

| Feature | Illustrative value |
| ------- | ------------------ |
| B2      | 450                |
| B3      | 700                |
| B4      | 350                |
| B8      | 3,200              |
| B11     | 1,100              |
| B12     | 650                |
| `class` | 1                  |

These are illustrative numbers, not values extracted from your actual data.

The model receives the six band values as inputs and `class = 1` as the known answer.

The `geometries: true` setting retains the sample geometries, and `tileScale: 4` can help manage memory use.

Next:

```
samples = samples.filter(
  ee.Filter.notNull(bands.concat(['class']))
);
```

This removes samples that have missing values for any selected predictor or the class property.

In simple terms: each usable training sample now has input features and a known class label.

## 7. Section 6 — Split the data into training and validation sets

```
var randomSamples = samples.randomColumn('random', 42);

var training = randomSamples.filter(
  ee.Filter.lt('random', 0.7)
);

var validation = randomSamples.filter(
  ee.Filter.gte('random', 0.7)
);
```

The code creates a random number for each sample and splits the collection:

- Training set: random value below 0.7, approximately 70%.
- Validation set: random value greater than or equal to 0.7, approximately 30%.

The `42` is the random seed. It makes the random split reproducible when the input collection remains unchanged.

### Why split the data?

The training samples teach the model. The held-out validation samples check how well the trained model predicts samples it did not train on.

For example, if a vegetation sample is placed in the validation set, the model should not use that sample's label to learn. It must predict the class from the sample's spectral values.

A limitation to be aware of: a random split can put nearby or spectrally similar samples in both sets, potentially making accuracy look better than performance in a new area. Spatially separated validation is often more informative when the goal is to map unfamiliar locations.

Also, this script does not force the 70/30 split to be balanced within each class. Check the sample counts and class distribution in the Console.

## 8. Section 7 — Train the Random Forest

This is the core machine-learning step:

```
var rf = ee.Classifier.smileRandomForest({
  numberOfTrees: 100,
  seed: 42
}).train({
  features: training,
  classProperty: 'class',
  inputProperties: bands
});
```

### What does each part mean?

- `smileRandomForest`: creates a Random Forest classifier.
- `numberOfTrees: 100`: builds an ensemble of 100 decision trees.
- `features: training`: supplies the training samples.
- `classProperty: 'class'`: tells the model which property contains the known answer.
- `inputProperties: bands`: tells the model to use B2, B3, B4, B8, B11 and B12 as predictors.

### How do the 100 trees work?

Each tree learns rules for separating the land-cover classes. Random Forest uses bootstrap samples of the training data and random subsets of features when considering splits, which helps create diversity among the trees.

For example, different trees might learn different combinations of red, NIR and SWIR reflectance that distinguish vegetation from built-up surfaces.

When classifying a pixel, the trees each produce a class prediction. The forest combines their predictions by majority vote.

`rf.explain()` prints information about the trained model in the Console.

## 9. Section 8 — Classify the whole image

```
var classified = image.classify(rf).rename('LULC');
```

This applies the trained Random Forest to the predictor image.

For every classifiable pixel, the model predicts one of the four numeric labels:

- `0` — Water
- `1` — Vegetation
- `2` — Bareland
- `3` — Built-up

The output is a land-use/land-cover classification image, named `LULC`.

Your palette then assigns colours:

```
var palette = [
  '1565C0',
  '238B45',
  'E6C84F',
  'D73027'
];
```

These colours correspond to blue, green, yellow and red. They are display colours; the underlying pixel values remain the numeric class labels.

## 10. Section 9 — Validate the classification

Your code applies the model to the held-out validation samples:

```
var validated = validation.classify(rf);
```

It then compares the predicted class with the known class:

```
var confusionMatrix = validated.errorMatrix(
  'class',
  'classification',
  [0, 1, 2, 3]
);
```

The confusion matrix compares the reference labels (`class`) with the predictions (`classification`).

For example, it shows how many reference vegetation samples were correctly classified as vegetation and how many were confused with water, bareland or built-up.

Your code prints five evaluation outputs:

| Output              | Meaning                                                                           |
| ------------------- | --------------------------------------------------------------------------------- |
| Confusion matrix    | Counts correct and incorrect class predictions                                    |
| Overall accuracy    | Proportion of validation samples classified correctly                             |
| Kappa coefficient   | Agreement measure adjusted for chance agreement                                   |
| Producer's accuracy | How well reference samples of each class were detected                            |
| Consumer's accuracy | How reliable the predicted labels are for each class; also called user's accuracy |

Overall accuracy is calculated as:

\\[ \text{Overall Accuracy}= \frac{\text{Correct predictions}} {\text{All validation samples}} \\]

For instance, if 270 out of 300 validation samples are correctly classified, the overall accuracy is 90%. That is an example only; your actual result will appear in the GEE Console.

Producer's accuracy is especially useful for understanding omission errors, while consumer's accuracy helps reveal commission errors.

## 11. Section 10 — Export the final map

```
Export.image.toDrive({
  image: classified.toByte(),
  description: 'Accra_RF_LULC_2020',
  folder: 'GEE_Exports',
  fileNamePrefix: 'Accra_RF_LULC_2020',
  region: aoi,
  scale: 10,
  maxPixels: 1e13
});
```

This creates an export task for the classified image.

- `classified.toByte()`: stores the class labels as small integer values.
- `description` and `fileNamePrefix`: name the export.
- `folder`: specifies the Google Drive folder.
- `region: aoi`: exports the Accra area.
- `scale: 10`: requests a 10 m output pixel size.
- `maxPixels`: allows the export to process a large number of pixels.

# 🌍 Random Forest Model Evaluation — Ecosystem Mapping

## 1. 🎯 The Four Possible Outcomes

We use **vegetation** as the class we want to detect. All other classes (water, bareland and built-up) are treated as **not vegetation**.

### 🟢 True Positive (TP) — Correct Detection
- **Actual:** Vegetation
- **Predicted:** Vegetation
- The pixel really is vegetation, and the model correctly identifies it.

### 🟢 True Negative (TN) — Correct Rejection
- **Actual:** Not vegetation
- **Predicted:** Not vegetation
- The pixel is not vegetation, and the model correctly rejects it as vegetation.

### 🔴 False Positive (FP) — False Alarm
- **Actual:** Not vegetation
- **Predicted:** Vegetation
- The model incorrectly labels water, bareland or built-up as vegetation.
- This is a **commission error** for vegetation.

### 🔴 False Negative (FN) — Missed Detection
- **Actual:** Vegetation
- **Predicted:** Not vegetation
- The pixel really is vegetation, but the model labels it as another class.
- This is an **omission error** for vegetation.

**Remember:**
- ✅ **True** = the prediction is correct.
- ❌ **False** = the prediction is incorrect.
- 🎯 **Positive** = the class being detected (vegetation).
- 🚫 **Negative** = everything outside that class.

For a four-class land-cover map, calculate these outcomes separately for each class by treating one class as positive and all other classes as negative.

---

## 2. 📊 Confusion Matrix Example

Suppose we validate 100 reference pixels for vegetation versus not vegetation. These numbers are illustrative.

| Actual class | Predicted vegetation | Predicted not vegetation | Total |
|---|---:|---:|---:|
| 🌿 Vegetation | 40 (TP) | 10 (FN) | 50 |
| 🏙️ Not vegetation | 5 (FP) | 45 (TN) | 50 |
| **Total** | **45** | **55** | **100** |

- ✅ 40 vegetation pixels were correctly detected.
- ✅ 45 non-vegetation pixels were correctly rejected.
- ❌ 5 non-vegetation pixels were incorrectly labelled vegetation.
- ❌ 10 vegetation pixels were missed.

The confusion matrix helps identify which classes the model confuses.

---

## 3. 📈 Evaluation Metrics and Formulas

### 🎯 1. Overall Accuracy

**Question:** How many predictions were correct out of all validation pixels?

\[
\text{Overall Accuracy}=\frac{TP+TN}{TP+TN+FP+FN}
\]

Example:

\[
\frac{40+45}{100}=85\%
\]

**Interpretation:** The model correctly classified 85% of the 100 validation pixels.

### 🌿 2. Sensitivity / Recall / Producer's Accuracy

**Question:** Of all the pixels that really are vegetation, how many did the model detect?

\[
\text{Sensitivity}=\text{Recall}=\frac{TP}{TP+FN}
\]

Example:

\[
\frac{40}{40+10}=80\%
\]

**Interpretation:** The model detected 80% of the actual vegetation pixels and missed 20%.

- High sensitivity = few actual vegetation pixels are missed.
- Low sensitivity = many actual vegetation pixels are missed.

### 🛡️ 3. Specificity

**Question:** Of all the pixels that are not vegetation, how many did the model correctly identify as not vegetation?

\[
\text{Specificity}=\frac{TN}{TN+FP}
\]

Example:

\[
\frac{45}{45+5}=90\%
\]

**Interpretation:** The model correctly rejected 90% of the pixels that were not vegetation.

### 🔍 4. Precision / Consumer's Accuracy / User's Accuracy

**Question:** Of all the pixels predicted as vegetation, how many really are vegetation?

\[
\text{Precision}=\frac{TP}{TP+FP}
\]

Example:

\[
\frac{40}{40+5}\approx88.9\%
\]

**Interpretation:** About 88.9% of the pixels labelled vegetation by the model were actually vegetation.

- High precision = few false alarms.
- Low precision = many pixels labelled vegetation actually belong to another class.

### ⚖️ 5. F1-score

**Question:** How well does the model balance precision and recall?

\[
F1=2\frac{\text{Precision}\times\text{Recall}}
{\text{Precision}+\text{Recall}}
\]

Example:

\[
F1\approx84.2\%
\]

**Interpretation:** The F1-score combines precision and recall into one measure. It is useful when you want to balance false alarms and missed detections.

### 🤝 6. Kappa Coefficient

**Question:** How much agreement is there between the model and reference labels after accounting for agreement expected by chance?

\[
\kappa=\frac{p_o-p_e}{1-p_e}
\]

Where:
- \(p_o\) = observed agreement (overall accuracy).
- \(p_e\) = agreement expected by chance based on the class totals.

**Interpretation:** Kappa summarizes chance-adjusted agreement across the confusion matrix. Interpret it alongside overall accuracy and class-specific metrics rather than using it alone.

### 🧩 7. Confusion Matrix

**Question:** Which land-cover classes are being confused?

The confusion matrix compares reference labels with predicted labels. For example, it can show whether vegetation is often misclassified as built-up or bareland.

It is a table of counts, not a single accuracy score.

---

## 4. 🧠 Quick Comparison Table

| Metric | Simple meaning |
|---|---|
| 📊 Confusion matrix | Which classes were correctly or incorrectly predicted? |
| 🎯 Overall accuracy | What percentage of all predictions were correct? |
| 🌿 Sensitivity / Recall / Producer's accuracy | How much of the actual class did we detect? |
| 🛡️ Specificity | How well did we reject pixels outside the target class? |
| 🔍 Precision / Consumer's accuracy | How trustworthy are the pixels predicted as this class? |
| ⚖️ F1-score | How well are precision and recall balanced? |
| 🤝 Kappa | How much agreement remains after accounting for chance? |

---

## 5. 🌍 Applying These Metrics to Accra LULC

Your Random Forest model classifies four land-cover classes:

- 💧 Water
- 🌿 Vegetation
- 🟡 Bareland
- 🏙️ Built-up

Calculate producer's accuracy, consumer's accuracy, sensitivity/recall, precision and F1-score for **each class separately**.

For example, when evaluating built-up, treat built-up as the positive class and water, vegetation and bareland as the negative classes.

**Important:** These metrics describe performance on the validation samples. A random validation split can overestimate how well the map transfers to new locations if nearby or similar samples appear in both training and validation sets. Spatially separated validation can help assess that limitation.

### ✅ Key Takeaway

- **Sensitivity/recall:** How much of the real class did we find?
- **Precision:** How many of our predicted pixels were correct?
- **Specificity:** How well did we reject the other classes?
- **F1-score:** How well did we balance precision and recall?
- **Overall accuracy:** How many predictions were correct overall?
- **Kappa:** How much agreement is there after accounting for chance?
- **Confusion matrix:** Which classes are being confused?

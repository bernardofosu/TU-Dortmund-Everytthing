# 🌍 GeoAI for Spatial Planning — Systematic Review Research Archive

## 🗂️ Recommended Research Storage Strategy

Use **OneDrive or Google Drive as the main research archive**, and a **private GitHub repository for code, scripts, and version control**.

- ☁️ **OneDrive / Google Drive** → master research archive
- 🐙 **Private GitHub** → code, scripts, analysis workflow, version history
- 💾 **External backup** → periodic backup of the whole project

## ☁️ 1. Master Research Archive

```text
GeoAI_Spatial_Planning_Systematic_Review/
│
├── 01_Protocol/
│   ├── Research_Plan.docx
│   ├── Search_Strategy.docx
│   └── Inclusion_Exclusion_Criteria.docx
│
├── 02_Search_Documentation/
│   ├── Scopus/
│   │   ├── Search_String.txt
│   │   ├── Screenshots/
│   │   └── Export/
│   │
│   └── Web_of_Science/
│       ├── Search_String.txt
│       ├── Screenshots/
│       └── Export/
│
├── 03_Raw_Data/
│   ├── Scopus_Raw_Export/
│   └── WoS_Raw_Export/
│
├── 04_Zotero/
│
├── 05_Screening/
│   ├── Title_Abstract/
│   ├── Full_Text/
│   └── PRISMA/
│
├── 06_Extraction/
│   └── Literature_Extraction_Matrix.xlsx
│
├── 07_Analysis/
│   ├── VOSviewer/
│   ├── R/
│   └── Python/
│
├── 08_Figures_Tables/
├── 09_Manuscript/
└── 10_Backup/
```

## 🔎 2. Search Documentation

For every database search, save:

- 🔍 Exact search string
- 📅 Date of search
- 🗃️ Database used
- ⚙️ Filters and limits
- 🔢 Number of retrieved records
- 📸 Screenshots of important search/result pages
- 📤 Original export files

Example:

```text
02_Search_Documentation/
├── Scopus/
│   ├── Search_String.txt
│   ├── Screenshots/
│   │   ├── 01_Search_String.png
│   │   ├── 02_Search_Results.png
│   │   ├── 03_Filters.png
│   │   └── 04_Export.png
│   └── Export/
│
└── Web_of_Science/
    ├── Search_String.txt
    ├── Screenshots/
    │   ├── 01_Search_String.png
    │   ├── 02_Search_Results.png
    │   ├── 03_Filters.png
    │   └── 04_Export.png
    └── Export/
```

These screenshots are mainly **research/audit documentation**. They do not all have to appear in the final paper.

## 📦 3. Raw Data

Keep the original database exports **untouched**.

```text
03_Raw_Data/
├── Scopus_Raw_Export/
└── WoS_Raw_Export/
```

⚠️ Do not overwrite the original exports after cleaning or deduplication.

## 📚 4. Zotero

Use Zotero for:

- 📖 Bibliographic management
- 🔄 Duplicate detection
- 📎 PDF organization
- 🏷️ Tags and collections
- 📝 References for the manuscript

Keep a record of important duplicate-removal results.

## 🧪 5. Screening

```text
05_Screening/
├── Title_Abstract/
├── Full_Text/
└── PRISMA/
```

Record:

- Initial records
- Duplicates removed
- Title/abstract exclusions
- Full-text exclusions
- Reasons for exclusion
- Final included studies

This information will support the **PRISMA flow diagram** and Methods section.

## 📊 6. Literature Extraction

```text
06_Extraction/
└── Literature_Extraction_Matrix.xlsx
```

The matrix can contain:

- Bibliographic information
- Planning application and problem
- Data sources
- Predictors/features
- Data fusion
- ML/DL algorithms
- Spatial/temporal modelling
- Software and platforms
- Training and validation
- Performance metrics
- Explainability
- Uncertainty
- Generalization
- Reproducibility
- Research gaps
- Planning implications
- Important evidence
- Your conceptual notes

## 📈 7. Analysis

```text
07_Analysis/
├── VOSviewer/
├── R/
└── Python/
```

Possible materials:

- VOSviewer maps
- Network data
- R scripts
- Python scripts
- Statistical analysis
- Tables generated from the extraction matrix
- Intermediate analysis files

## 🖼️ 8. Figures and Tables

```text
08_Figures_Tables/
```

Examples:

- PRISMA diagram
- Publication trends
- Keyword co-occurrence networks
- Sankey diagrams
- Model/application relationships
- Data-source relationships
- Summary tables

## 📝 9. Manuscript

```text
09_Manuscript/
```

Keep versions such as:

```text
Draft_01.docx
Draft_02.docx
Draft_03.docx
Final_Submission.docx
```

## 🐙 Private GitHub Repository

Use GitHub mainly for **code and reproducibility**, rather than as the main archive for the whole review.

```text
GeoAI-Spatial-Planning-SLR/
├── README.md
├── search/
├── screening/
├── extraction/
├── analysis/
│   ├── R/
│   └── Python/
├── figures/
└── docs/
```

Good things to keep in GitHub:

- 🐍 Python scripts
- 📊 R scripts
- 🔎 Search strings
- 📓 Analysis notebooks
- 📈 Data-processing scripts
- 📄 Documentation
- 🔄 Version history
- 📖 README files

🔒 Keep the repository **private** while the project is being developed.

## 💾 Backup Strategy

Do not rely on only one location.

```text
☁️ OneDrive / Google Drive
        ↓
   Master archive
        ↓
🐙 Private GitHub
   Code + workflow
        ↓
💾 External backup
   Periodic full backup
```

## 🚀 Tomorrow's Search Workflow

Create the folder structure **before running the searches**.

1. 🔍 Finalize the Scopus search string.
2. 🔍 Finalize the Web of Science search string.
3. ▶️ Run the Scopus search.
4. 📸 Save important screenshots.
5. 🔢 Record the number of retrieved records.
6. 📤 Export the Scopus records.
7. 💾 Save the original export.
8. ▶️ Run the Web of Science search.
9. 📸 Save important screenshots.
10. 🔢 Record the number of retrieved records.
11. 📤 Export the Web of Science records.
12. 💾 Save the original export.
13. 📚 Import/manage the records in Zotero.
14. 🔄 Identify and remove duplicates.
15. 📝 Record exactly how many duplicates were removed.
16. 📋 Begin title/abstract screening.
17. 📋 Record exclusion decisions and reasons.
18. 📄 Continue to full-text screening.
19. 📊 Build the final included-study dataset.
20. 🧮 Later perform the systematic and bibliometric analyses.

## 🧠 Important Principle

The **search process itself is part of the methodology**.

Keep the evidence showing:

> **What you searched → where you searched → when you searched → what you found → what you removed → why you removed it → what remained.**

This will make it easier to write the **Materials and Methods**, report the **PRISMA workflow**, and defend the systematic-review process.

## 🎯 Project Philosophy

The review should also build a transferable understanding of GeoAI:

```text
🌍 Geographic problem
        ↓
🗃️ Data sources
        ↓
🧹 Preprocessing
        ↓
🔢 Features / representations
        ↓
🗺️ Spatial relationships
        ↓
⏱️ Temporal relationships
        ↓
🔗 Data fusion
        ↓
🤖 ML / DL model
        ↓
🏋️ Training
        ↓
🧪 Validation / testing
        ↓
🎯 Prediction
        ↓
📏 Performance / error assessment
        ↓
🌐 Generalization / transferability
        ↓
🏙️ Planning decision / implication
```

The geographic application can change while the underlying GeoAI reasoning and workflow remain transferable.

For example:

```text
Urban heat in Accra
        ↓
Flooding in Kumasi
        ↓
Land-use / land-cover modelling elsewhere
```

The **problem, data, and study area may change**, but much of the methodological reasoning can be reused.

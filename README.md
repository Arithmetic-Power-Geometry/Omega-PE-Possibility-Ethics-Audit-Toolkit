# Omega-PE: Possibility Ethics Audit Toolkit

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21373090.svg)](https://doi.org/10.5281/zenodo.21373090)

## Reproducible Computational Framework for Possibility Ethics

**Omega-PE** is the reference implementation of the computational framework introduced in:

> **Possibility Ethics: Measuring Moral Value as the Expansion of Safe Future Options in Sociotechnical Systems**

The software provides a deterministic and fully reproducible implementation of the Possibility Ethics audit framework for evaluating how sociotechnical system designs expand or restrict ethically admissible future opportunities.

The package accompanies the published software archive and reproduces every computational result reported in the manuscript.

---

# Version

**Version:** 1.0.1

**Software DOI**

https://doi.org/10.5281/zenodo.21373090

---

# Overview

Omega-PE implements the complete computational audit pipeline described in the paper, including

- deterministic Option Entropy computation;
- viability filtering;
- harm screening;
- deterministic outcome clustering;
- vulnerability-sensitive aggregation;
- subgroup floor evaluation;
- cohort-level non-regression analysis;
- Option Repair identification;
- parameter sensitivity analysis;
- synthetic benchmark generation;
- real-data OULAD audit;
- publication-quality tables and figures.

The implementation is deterministic.

No random sampling or stochastic simulation is used.

Running the software multiple times on the same inputs produces identical outputs.

---

# Included reproducibility materials

The software archive contains

- complete source code;
- synthetic benchmark specification;
- synthetic benchmark parameter manifest;
- synthetic benchmark design definitions;
- OULAD audit implementation;
- processed analytical datasets;
- generated benchmark outputs;
- publication tables;
- publication figures;
- validation report;
- reproducibility documentation.

These materials reproduce every computational result reported in the accompanying manuscript.

---

# Repository structure

```text
Omega-PE/

├── code/
├── data/
├── figures/
├── outputs/
├── synthetic_benchmark/
│   ├── synthetic_parameter_manifest.json
│   ├── synthetic_design_definitions.csv
│   └── README.md
├── README.md
├── LICENSE
└── VALIDATION_REPORT.json
```

---

# Reproducing the analyses

From the project directory execute

```bash
python code/run_oulad_possibility_ethics.py
```

The software automatically generates

- processed OULAD feature tables;
- Option Entropy values;
- vulnerability-weighted opportunity levels;
- comparative scores;
- Option Repair records;
- synthetic benchmark outputs;
- sensitivity-analysis outputs;
- publication tables;
- publication figures;
- validation report.

---

# OULAD analytical dataset

The real-data demonstration uses the Open University Learning Analytics Dataset (OULAD), module BBB.

The authoritative processed analytical file is

```
outputs/oulad_student_pathway_features_BBB.csv
```

The processed dataset contains exactly

| Presentation | Student-presentation records |
|--------------|----------------------------:|
| 2013B | 1,767 |
| 2013J | 2,237 |
| 2014B | 1,613 |
| 2014J | 2,292 |
| **Total** | **7,909** |

These counts are computed from the one-row-per-student-presentation analytical file.

Because vulnerability cohorts overlap, aggregate opportunity levels are interpreted as audit-stratum indices rather than person-level welfare measures.

---

# Synthetic benchmark

The software includes a deterministic synthetic benchmark used to verify the computational behaviour of the framework.

The benchmark compares

- Baseline
- Exit/Offline
- Personalized Assistant

using four representative cohorts.

The benchmark specification, parameter manifest, design definitions, generated outputs, and documentation are included in the `synthetic_benchmark` directory.

---

# Interpretation

The synthetic benchmark verifies the computational properties of the framework under controlled conditions.

The OULAD analysis demonstrates the operational feasibility of the audit on a substantial public observational dataset.

Neither analysis should be interpreted as establishing causal effects or validating a complete moral theory.

---

# Citation

If you use this software, please cite:

**Akhtar, M. A. K. (2026).**

*Omega-PE: Possibility Ethics Audit Toolkit (Version 1.0.1).*

Zenodo.

https://doi.org/10.5281/zenodo.21373090

---

# Dataset citation

Kuzilek J., Hlosta M., & Zdrahal Z.

**Open University Learning Analytics Dataset (OULAD).**

Scientific Data, 4, 170171 (2017).

https://doi.org/10.1038/sdata.2017.171

---

# License

## Source code

Apache License 2.0

The software may be used, modified, and redistributed in accordance with the Apache License 2.0.

## Dataset

The Open University Learning Analytics Dataset (OULAD) is **not** distributed under the Apache License.

Users must comply with the original OULAD license and attribution requirements when using the dataset.

---

# Author

**Dr. Mohammad Amir Khusru Akhtar**

Faculty of Computing and Information Technology

Usha Martin University

Ranchi – 834001

Jharkhand, India

Email: akakhtar.2024@gmail.com

---

# Disclaimer

Omega-PE is a computational decision-support framework.

It is intended to improve transparency, reproducibility, and auditability of opportunity-structure evaluations.

The software does **not** replace ethical deliberation, legal review, institutional governance, or democratic decision-making.

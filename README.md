# Omega-PE: Possibility Ethics Audit Toolkit

## Reproducible OULAD Real-Data Audit

This package provides the deterministic implementation and reproducibility materials
for the Possibility Ethics audit of the Open University Learning Analytics Dataset
(OULAD), module BBB.

## Correct analytic sample

The authoritative processed file is:

`outputs/oulad_student_pathway_features_BBB.csv`

It contains exactly **7,909 student-presentation records**, distributed as follows:

| Presentation | Student-presentation records |
|---|---:|
| 2013B | 1,767 |
| 2013J | 2,237 |
| 2014B | 1,613 |
| 2014J | 2,292 |
| **Total** | **7,909** |

These counts are computed directly from the one-row-per-student-presentation analytic
file. Cohort memberships overlap, but overlapping cohort membership does not alter
the number of student-presentation records.

## Main results

| Presentation | Records | L(d) | J(d | 2013B) | Minimum cohort Omega | Rank |
|---|---:|---:|---:|---:|---:|
| 2013B | 1,767 | 7.106 | 0.000 | 1.609 | 3 |
| 2013J | 2,237 | 7.106 | 0.000 | 1.609 | 3 |
| 2014B | 1,613 | 7.143 | 0.036 | 1.609 | 2 |
| 2014J | 2,292 | 7.773 | 0.666 | 1.386 | 1 |

Two cohort-level non-regression cases are retained in the Option Repair queue:

- Repeat-attempt cohort in 2014B: delta = -0.1823
- Disability cohort in 2014J: delta = -0.2231

## Reproduce the analysis

From the package root, run:

```bash
python code/run_oulad_possibility_ethics.py
```

The script regenerates:

- the processed student-presentation feature file;
- cohort-level Option Entropy results;
- corrected presentation-level record counts;
- Option Repair records;
- synthetic-versus-real comparison output;
- PDF and PNG figures;
- the validation report.

## Repository structure

```text
code/
data/
figures/
outputs/
README.md
LICENSE
VALIDATION_REPORT.json
```

## Interpretation

The OULAD analysis is observational. It demonstrates the operational feasibility of
the Possibility Ethics audit but does not estimate causal effects of educational
interventions.

The vulnerability-weighted level is an audit-stratum index. Because vulnerability
cohorts may overlap, it should not be interpreted as a person-level welfare total.

## Dataset

Kuzilek, J., Hlosta, M., and Zdrahal, Z. (2017). Open University Learning Analytics
Dataset. *Scientific Data*, 4, 170171.
DOI: 10.1038/sdata.2017.171

## Software citation

Akhtar, Mohammad Amir Khusru. (2026). *Omega-PE: Possibility Ethics Audit Toolkit
for Reproducible Real-Data Analysis Using the Open University Learning Analytics
Dataset (OULAD)* (Version 1.0.0) [Software]. Zenodo.
DOI: 10.5281/zenodo.21373090

## License

The source code is licensed under the Apache License 2.0. The OULAD dataset remains
subject to its original license and attribution requirements.

## Author

**Dr. Mohammad Amir Khusru Akhtar**  
Faculty of Computing and Information Technology  
Usha Martin University  
Ranchi, 834001, Jharkhand, India

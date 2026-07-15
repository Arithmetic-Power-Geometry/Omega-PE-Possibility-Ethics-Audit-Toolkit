#!/usr/bin/env python3
"""Reproduce the Omega-PE OULAD real-data audit.

Run from the package root:
    python code/run_oulad_possibility_ethics.py

The script regenerates the processed student-level feature file, cohort-level
Option Entropy results, presentation comparison table, Option Repair queue,
synthetic/real comparison file, figures, and validation report.
"""
from pathlib import Path
import json
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

MODULE = "BBB"
PRESENTATIONS = ["2013B", "2013J", "2014B", "2014J"]
KAPPA = 1.0
WEIGHTS = {
    "Disabled": 1.2,
    "Low-IMD": 1.1,
    "Low prior education": 1.0,
    "Repeat attempt": 0.9,
}

# ---------- Load and filter OULAD ----------
info = pd.read_csv(DATA / "studentInfo.csv").query(
    "code_module == @MODULE and code_presentation in @PRESENTATIONS"
).copy()
reg = pd.read_csv(DATA / "studentRegistration.csv").query(
    "code_module == @MODULE and code_presentation in @PRESENTATIONS"
).copy()
ass = pd.read_csv(DATA / "assessments.csv").query(
    "code_module == @MODULE and code_presentation in @PRESENTATIONS"
).copy()

# ---------- Assessment features ----------
sa = pd.read_csv(DATA / "studentAssessment.csv").merge(
    ass[["id_assessment", "code_module", "code_presentation",
         "assessment_type", "date"]],
    on="id_assessment",
    how="inner",
)
sa["on_time"] = (sa["date_submitted"] <= sa["date"]).astype(int)

assessment_agg = (
    sa.groupby(["code_module", "code_presentation", "id_student"])
      .agg(
          submitted_count=("id_assessment", "nunique"),
          mean_score=("score", "mean"),
          on_time_rate=("on_time", "mean"),
          assessment_type_count=("assessment_type", "nunique"),
      )
      .reset_index()
)
available_assessments = (
    ass.groupby(["code_module", "code_presentation"])["id_assessment"]
       .nunique()
       .rename("available_assessments")
       .reset_index()
)

# ---------- VLE features, read in chunks ----------
vle_meta = pd.read_csv(DATA / "vle.csv")[
    ["id_site", "code_module", "code_presentation", "activity_type"]
].drop_duplicates()

parts = []
for chunk in pd.read_csv(DATA / "studentVle.csv", chunksize=1_500_000):
    chunk = chunk.query(
        "code_module == @MODULE and code_presentation in @PRESENTATIONS"
    )
    if chunk.empty:
        continue
    chunk = chunk.merge(
        vle_meta,
        on=["id_site", "code_module", "code_presentation"],
        how="left",
    )
    parts.append(
        chunk.groupby(["code_module", "code_presentation", "id_student"])
             .agg(
                 total_clicks=("sum_click", "sum"),
                 active_days=("date", "nunique"),
                 activity_type_count=("activity_type", "nunique"),
             )
             .reset_index()
    )

vle_agg = (
    pd.concat(parts, ignore_index=True)
      .groupby(["code_module", "code_presentation", "id_student"], as_index=False)
      .agg(
          total_clicks=("total_clicks", "sum"),
          active_days=("active_days", "sum"),
          activity_type_count=("activity_type_count", "max"),
      )
)

# ---------- One row per student-presentation ----------
df = (
    info.merge(reg, on=["code_module", "code_presentation", "id_student"], how="left")
        .merge(assessment_agg,
               on=["code_module", "code_presentation", "id_student"], how="left")
        .merge(available_assessments,
               on=["code_module", "code_presentation"], how="left")
        .merge(vle_agg,
               on=["code_module", "code_presentation", "id_student"], how="left")
)

for col in [
    "submitted_count", "mean_score", "on_time_rate",
    "assessment_type_count", "total_clicks", "active_days",
    "activity_type_count",
]:
    df[col] = df[col].fillna(0)

df["submission_ratio"] = np.where(
    df["available_assessments"] > 0,
    df["submitted_count"] / df["available_assessments"],
    0,
)
df["persisted"] = df["date_unregistration"].isna().astype(int)
df["imd_num"] = pd.to_numeric(
    df["imd_band"].astype(str).str.extract(r"(\d+)")[0],
    errors="coerce",
)

# Audit strata
df["Disabled"] = df["disability"].eq("Y")
df["Low-IMD"] = df["imd_num"].le(20)
df["Low prior education"] = df["highest_education"].eq("Lower Than A Level")
df["Repeat attempt"] = df["num_of_prev_attempts"].gt(0)

# Deterministic pathway signature
def engagement_bin(x):
    if x == 0:
        return "none"
    if x < 100:
        return "low"
    if x < 500:
        return "medium"
    return "high"

def breadth_bin(x):
    if x == 0:
        return "none"
    if x <= 2:
        return "narrow"
    if x <= 5:
        return "moderate"
    return "broad"

def submission_bin(x):
    if x == 0:
        return "none"
    if x < 0.75:
        return "partial"
    return "complete"

df["signature"] = (
    df["total_clicks"].map(engagement_bin)
    + "|" + df["activity_type_count"].map(breadth_bin)
    + "|" + df["submission_ratio"].map(submission_bin)
    + "|" + np.where(
        df["submitted_count"].eq(0),
        "none",
        np.where(df["on_time_rate"].ge(0.5), "mostly_on_time", "mostly_late"),
    )
    + "|" + np.where(df["persisted"].eq(1), "persisted", "withdrew")
)
df["adverse_outcome"] = df["final_result"].isin(["Fail", "Withdrawn"]).astype(int)

# Save the authoritative one-row-per-student-presentation file
df.to_csv(OUT / "oulad_student_pathway_features_BBB.csv", index=False)

# ---------- Cohort-level Option Entropy ----------
rows = []
for presentation in PRESENTATIONS:
    for cohort, weight in WEIGHTS.items():
        subset = df[
            (df["code_presentation"] == presentation) & df[cohort]
        ].copy()
        signatures = (
            subset.groupby("signature")
                  .agg(
                      n=("id_student", "size"),
                      adverse_rate=("adverse_outcome", "mean"),
                  )
                  .reset_index()
        )
        admissible = signatures[
            (signatures["n"] >= 3) & (signatures["adverse_rate"] <= 0.50)
        ]
        k = int(len(admissible))
        omega = math.log(KAPPA + k) - math.log(KAPPA)
        rows.append({
            "presentation": presentation,
            "cohort": cohort,
            "n_students": int(len(subset)),
            "observed_signatures": int(len(signatures)),
            "admissible_option_classes_K": k,
            "option_entropy": omega,
            "vulnerability_weight": weight,
            "weighted_option_level": weight * omega,
        })

results = pd.DataFrame(rows)
results.to_csv(OUT / "oulad_option_entropy_by_cohort.csv", index=False)

# ---------- Correct presentation-level record counts ----------
# These counts are computed from the authoritative one-row-per-student-presentation
# analytic file and therefore sum exactly to 7,909.
record_counts = (
    df.groupby("code_presentation")
      .size()
      .reindex(PRESENTATIONS)
      .rename("student_presentation_records")
      .reset_index()
      .rename(columns={"code_presentation": "presentation"})
)

levels = (
    results.groupby("presentation")
           .agg(
               vulnerability_weighted_level=("weighted_option_level", "sum"),
               min_cohort_omega=("option_entropy", "min"),
               mean_cohort_omega=("option_entropy", "mean"),
           )
           .reset_index()
           .merge(record_counts, on="presentation", how="left")
)

baseline_level = float(
    levels.loc[
        levels["presentation"].eq("2013B"),
        "vulnerability_weighted_level",
    ].iloc[0]
)
levels["J_vs_2013B"] = (
    levels["vulnerability_weighted_level"] - baseline_level
)
levels["rank"] = (
    levels["vulnerability_weighted_level"]
    .rank(ascending=False, method="min")
    .astype(int)
)

levels = levels[
    [
        "presentation",
        "student_presentation_records",
        "vulnerability_weighted_level",
        "min_cohort_omega",
        "mean_cohort_omega",
        "J_vs_2013B",
        "rank",
    ]
]
levels.to_csv(OUT / "oulad_presentation_comparison.csv", index=False)

# ---------- Cohort-level non-regression and Option Repair ----------
baseline_omega = (
    results[results["presentation"].eq("2013B")]
    .set_index("cohort")["option_entropy"]
)
results_with_delta = results.copy()
results_with_delta["delta_vs_2013B"] = results_with_delta.apply(
    lambda row: row["option_entropy"] - baseline_omega[row["cohort"]],
    axis=1,
)
repairs = results_with_delta[
    results_with_delta["delta_vs_2013B"] < 0
][
    [
        "presentation", "cohort", "n_students",
        "admissible_option_classes_K", "option_entropy",
        "delta_vs_2013B",
    ]
]
repairs.to_json(
    OUT / "option_repair_queue.json",
    orient="records",
    indent=2,
)

# ---------- Synthetic comparison ----------
synthetic = pd.DataFrame({
    "design": ["Baseline", "Exit/offline", "Assistant"],
    "weighted_option_level": [3.808453, 5.129289, 3.604365],
})
synthetic.to_csv(OUT / "existing_synthetic_benchmark.csv", index=False)

comparison = {
    "existing_synthetic": synthetic.to_dict(orient="records"),
    "real_oulad_module": MODULE,
    "analytic_student_presentation_records": int(len(df)),
    "real_presentations": levels.to_dict(orient="records"),
    "interpretation": (
        "Synthetic and OULAD values are not directly commensurable because "
        "the cohort definitions and option-class construction differ. "
        "The comparison is methodological: both use the same logarithmic "
        "index and vulnerability-weighted aggregation."
    ),
}
(OUT / "synthetic_vs_real_comparison.json").write_text(
    json.dumps(comparison, indent=2),
    encoding="utf-8",
)

# ---------- Figures ----------
plt.figure(figsize=(8, 5))
values = levels["vulnerability_weighted_level"].to_numpy()
plt.bar(levels["presentation"], values)
for idx, value in enumerate(values):
    plt.text(idx, value + 0.03, f"{value:.3f}",
             ha="center", va="bottom", fontsize=9)
plt.ylabel("Vulnerability-weighted opportunity level L(d)")
plt.xlabel("OULAD BBB presentation")
plt.tight_layout()
plt.savefig(FIG / "oulad_realdata_weighted_levels.pdf", bbox_inches="tight")
plt.savefig(FIG / "oulad_realdata_weighted_levels.png",
            dpi=300, bbox_inches="tight")
plt.close()

pivot = results.pivot(
    index="cohort",
    columns="presentation",
    values="option_entropy",
).reindex(index=list(WEIGHTS.keys()), columns=PRESENTATIONS)

plt.figure(figsize=(8, 4.8))
image = plt.imshow(pivot.values, aspect="auto")
plt.colorbar(image, label="Option Entropy")
plt.xticks(range(len(pivot.columns)), pivot.columns)
plt.yticks(range(len(pivot.index)), pivot.index)
for row in range(pivot.shape[0]):
    for col in range(pivot.shape[1]):
        plt.text(col, row, f"{pivot.iloc[row, col]:.3f}",
                 ha="center", va="center", fontsize=8)
plt.xlabel("Presentation")
plt.ylabel("Vulnerability cohort")
plt.tight_layout()
plt.savefig(FIG / "oulad_cohort_option_entropy_heatmap.pdf",
            bbox_inches="tight")
plt.savefig(FIG / "oulad_cohort_option_entropy_heatmap.png",
            dpi=300, bbox_inches="tight")
plt.close()

# ---------- Validation report ----------
validation = {
    "software": "Omega-PE Possibility Ethics Audit Toolkit",
    "module": MODULE,
    "presentations": PRESENTATIONS,
    "analytic_student_presentation_records": int(len(df)),
    "records_by_presentation": {
        row["presentation"]: int(row["student_presentation_records"])
        for _, row in levels.iterrows()
    },
    "records_sum_check": int(
        levels["student_presentation_records"].sum()
    ),
    "records_match_analytic_file": bool(
        levels["student_presentation_records"].sum() == len(df)
    ),
    "cohorts": list(WEIGHTS.keys()),
    "option_repair_cases": int(len(repairs)),
    "best_presentation": str(
        levels.sort_values(
            "vulnerability_weighted_level", ascending=False
        ).iloc[0]["presentation"]
    ),
    "best_weighted_level": float(
        levels["vulnerability_weighted_level"].max()
    ),
    "note": (
        "Presentation record counts are computed from the authoritative "
        "one-row-per-student-presentation analytic file. Cohort memberships "
        "overlap, but this does not alter the presentation record counts."
    ),
}
(ROOT / "VALIDATION_REPORT.json").write_text(
    json.dumps(validation, indent=2),
    encoding="utf-8",
)

print("\nCorrected presentation comparison")
print(levels.to_string(index=False))
print(f"\nAnalytic record total: {len(df)}")
print(
    "Presentation count sum:",
    int(levels["student_presentation_records"].sum()),
)
print("Option Repair cases:", len(repairs))

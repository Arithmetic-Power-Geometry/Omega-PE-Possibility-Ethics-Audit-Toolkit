#!/usr/bin/env python3
"""Reproduce the OULAD Possibility Ethics real-data audit.
Run from the package root:
    python code/run_oulad_possibility_ethics.py
"""
from pathlib import Path
import math, json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT, FIG = ROOT/"data", ROOT/"outputs", ROOT/"figures"
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
MODULE="BBB"; presentations=["2013B","2013J","2014B","2014J"]; KAPPA=1.0
weights={"Disabled":1.2,"Low-IMD":1.1,"Low prior education":1.0,"Repeat attempt":0.9}

info=pd.read_csv(DATA/"studentInfo.csv").query("code_module==@MODULE and code_presentation in @presentations")
reg=pd.read_csv(DATA/"studentRegistration.csv").query("code_module==@MODULE and code_presentation in @presentations")
ass=pd.read_csv(DATA/"assessments.csv").query("code_module==@MODULE and code_presentation in @presentations")
sa=pd.read_csv(DATA/"studentAssessment.csv").merge(ass[["id_assessment","code_module","code_presentation","assessment_type","date"]],on="id_assessment",how="inner")
sa["on_time"]=(sa["date_submitted"]<=sa["date"]).astype(int)
aa=sa.groupby(["code_module","code_presentation","id_student"]).agg(submitted_count=("id_assessment","nunique"),mean_score=("score","mean"),on_time_rate=("on_time","mean"),assessment_type_count=("assessment_type","nunique")).reset_index()
avail=ass.groupby(["code_module","code_presentation"])["id_assessment"].nunique().rename("available_assessments").reset_index()
meta=pd.read_csv(DATA/"vle.csv")[["id_site","code_module","code_presentation","activity_type"]].drop_duplicates()
parts=[]
for ch in pd.read_csv(DATA/"studentVle.csv",chunksize=1500000):
    ch=ch.query("code_module==@MODULE and code_presentation in @presentations")
    if ch.empty: continue
    ch=ch.merge(meta,on=["id_site","code_module","code_presentation"],how="left")
    parts.append(ch.groupby(["code_module","code_presentation","id_student"]).agg(total_clicks=("sum_click","sum"),active_days=("date","nunique"),activity_type_count=("activity_type","nunique")).reset_index())
va=pd.concat(parts).groupby(["code_module","code_presentation","id_student"],as_index=False).agg(total_clicks=("total_clicks","sum"),active_days=("active_days","sum"),activity_type_count=("activity_type_count","max"))
df=info.merge(reg,on=["code_module","code_presentation","id_student"],how="left").merge(aa,on=["code_module","code_presentation","id_student"],how="left").merge(avail,on=["code_module","code_presentation"],how="left").merge(va,on=["code_module","code_presentation","id_student"],how="left")
for c in ["submitted_count","mean_score","on_time_rate","assessment_type_count","total_clicks","active_days","activity_type_count"]: df[c]=df[c].fillna(0)
df["submission_ratio"]=np.where(df.available_assessments>0,df.submitted_count/df.available_assessments,0)
df["persisted"]=df.date_unregistration.isna().astype(int)
df["imd_num"]=pd.to_numeric(df.imd_band.astype(str).str.extract(r"(\d+)")[0],errors="coerce")
df["Disabled"]=df.disability.eq("Y"); df["Low-IMD"]=df.imd_num.le(20)
df["Low prior education"]=df.highest_education.eq("Lower Than A Level"); df["Repeat attempt"]=df.num_of_prev_attempts.gt(0)
eb=lambda x:"none" if x==0 else ("low" if x<100 else ("medium" if x<500 else "high"))
bb=lambda x:"none" if x==0 else ("narrow" if x<=2 else ("moderate" if x<=5 else "broad"))
sb=lambda x:"none" if x==0 else ("partial" if x<.75 else "complete")
df["signature"]=df.total_clicks.map(eb)+"|"+df.activity_type_count.map(bb)+"|"+df.submission_ratio.map(sb)+"|"+np.where(df.submitted_count.eq(0),"none",np.where(df.on_time_rate.ge(.5),"mostly_on_time","mostly_late"))+"|"+np.where(df.persisted.eq(1),"persisted","withdrew")
df["adverse_outcome"]=df.final_result.isin(["Fail","Withdrawn"]).astype(int)
rows=[]
for p in presentations:
  for cohort in weights:
    s=df[(df.code_presentation==p)&df[cohort]]
    g=s.groupby("signature").agg(n=("id_student","size"),adverse_rate=("adverse_outcome","mean")).reset_index()
    K=len(g[(g.n>=3)&(g.adverse_rate<=.50)])
    om=math.log(1+K)
    rows.append([p,cohort,len(s),len(g),K,om,weights[cohort],weights[cohort]*om])
res=pd.DataFrame(rows,columns=["presentation","cohort","n_students","observed_signatures","admissible_option_classes_K","option_entropy","vulnerability_weight","weighted_option_level"])
lev=res.groupby("presentation").agg(vulnerability_weighted_level=("weighted_option_level","sum"),min_cohort_omega=("option_entropy","min"),mean_cohort_omega=("option_entropy","mean")).reset_index()
base=float(lev.loc[lev.presentation.eq("2013B"),"vulnerability_weighted_level"].iloc[0]); lev["J_vs_2013B"]=lev.vulnerability_weighted_level-base
res.to_csv(OUT/"oulad_option_entropy_by_cohort.csv",index=False); lev.to_csv(OUT/"oulad_presentation_comparison.csv",index=False)
print(lev.to_string(index=False))

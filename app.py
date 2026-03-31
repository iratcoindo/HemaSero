import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("📊 Hematology Data Input")

# ===============================
# UPLOAD SECTION
# ===============================
st.subheader("📥 Upload Data")

col1, col2, col3 = st.columns(3)

baseline_file = col1.file_uploader("Baseline (Day 0)", type=["xlsx","csv"])
midline_file  = col2.file_uploader("Midline", type=["xlsx","csv"])
endline_file  = col3.file_uploader("Endline", type=["xlsx","csv"])

# ===============================
# FUNCTION LOAD
# ===============================

def load_data(file, label):
    if file is None:
        return None
    
    if file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)

    # ===============================
    # 🔥 FILTER PARAMETER HEMATOLOGI
    # ===============================
    hematology_params = ["	WBC","	Neu#","	Lym#","	Mon#","	Eos#","	Bas#","	Neu%","	Lym%","	Mon%","	Eos%","	Bas%","	RBC",
                         "	HGB","	HCT","	MCV","	MCH","	MCHC","	RDW-CV","	RDW-SD","	PLT","	MPV","	PDW","	PCT"]

    df = df[df[df.columns[0]].isin(hematology_params)]

    # ===============================
    # TRANSFORM KE LONG
    # ===============================
    df_long = df.melt(
        id_vars=df.columns[0],
        var_name="Sample",
        value_name="Value"
    )
    
    df_long.columns = ["Parameter", "Sample", "Value"]
    
    # ===============================
    # 🔥 CLEAN VALUE
    # ===============================
    df_long["Value"] = pd.to_numeric(df_long["Value"], errors="coerce")
    
    # ===============================
    # ADD TIMEPOINT
    # ===============================
    df_long["Timepoint"] = label
    
    return df_long

# ===============================
# LOAD ALL
# ===============================
df_list = []

df_baseline = load_data(baseline_file, "Baseline")
df_midline  = load_data(midline_file, "Midline")
df_endline  = load_data(endline_file, "Endline")

for df in [df_baseline, df_midline, df_endline]:
    if df is not None:
        df_list.append(df)

# ===============================
# COMBINE
# ===============================
if len(df_list) > 0:

    df_all = pd.concat(df_list, ignore_index=True)

    # ===============================
    # 🧬 GROUP ASSIGNMENT (RANGE INPUT)
    # ===============================
    st.markdown("---")
    st.subheader("🧪 Assign Group by Range")
    
    unique_samples = sorted(df_all["Sample"].unique())
    st.write("Detected samples:", unique_samples)
    
    # fungsi parser
    def parse_range(text):
        samples = []
        parts = text.split(",")
    
        for p in parts:
            p = p.strip()
            if "-" in p:
                start, end = p.split("-")
                samples += [str(i) for i in range(int(start), int(end)+1)]
            elif p != "":
                samples.append(p)
        return samples
    
    # jumlah group
    n_group = st.number_input("Jumlah kelompok", 1, 10, 2)
    
    group_map = {}
    
    for i in range(n_group):
        col1, col2 = st.columns(2)
    
        with col1:
            gname = st.text_input(f"Nama Group {i+1}", f"Group {i+1}", key=f"gname{i}")
    
        with col2:
            grange = st.text_input(
                f"Range Sample (contoh: 1-5 atau 1-3,5,7-9)",
                key=f"grange{i}"
            )
    
        try:
            parsed = parse_range(grange)
    
            for p in parsed:
                # 🔥 cocokkan dengan sample name
                for s in unique_samples:
                    if s.endswith(str(p)):   # fleksibel (S1, ID_1, dll)
                        group_map[s] = gname
    
        except:
            st.warning(f"Format salah di Group {i+1}")
    
    # ===============================
    # APPLY GROUP
    # ===============================
    df_all["Group"] = df_all["Sample"].map(group_map)
    
    # ===============================
    # PREVIEW
    # ===============================
    st.subheader("📋 Group Mapping")
    st.dataframe(df_all[["Sample","Group"]].drop_duplicates())

    # ===============================
    # INFO DETECTION
    # ===============================
    st.subheader("🔍 Detected Structure")

    st.write("Jumlah sample:", df_all["Sample"].nunique())
    st.write("Jumlah parameter:", df_all["Parameter"].nunique())
    st.write("Timepoints:", df_all["Timepoint"].unique())

    # ===============================
    # SAFE BOXPLOT (NO POSITIONS)
    # ===============================
    box_data = []
    box_colors = []
    labels = []
    
    for g in df_all["Group"].dropna().unique():
        for tp in ["Baseline", "Midline", "Endline"]:
    
            vals = df_param[
                (df_param["Group"] == g) &
                (df_param["Timepoint"] == tp)
            ]["Value"].dropna()
    
            if len(vals) > 0:
                box_data.append(vals)
                box_colors.append(colors[tp])
                labels.append(f"{g}-{tp}")
    
    if len(box_data) > 0:
    
        fig, ax = plt.subplots(figsize=(2.5,2.5))
    
        bp = ax.boxplot(
            box_data,
            patch_artist=True
        )
    
        # warna
        for patch, color in zip(bp["boxes"], box_colors):
            patch.set_facecolor(color)
    
        ax.set_xticks(range(1, len(labels)+1))
        ax.set_xticklabels(labels, rotation=45, fontsize=6)
    
        ax.set_title(param, fontsize=8)
    
        st.pyplot(fig)
        # ===============================
        # 📊 STATISTICAL TEST (AUTO)
        # ===============================
        st.markdown("---")
        st.subheader("📊 Statistical Analysis (Per Group × Parameter)")
        
        from scipy.stats import wilcoxon, kruskal
        
        results = []
        
        parameters = df_all["Parameter"].unique()
        groups = df_all["Group"].dropna().unique()
        
        for param in parameters:
            for g in groups:
        
                df_sub = df_all[
                    (df_all["Parameter"] == param) &
                    (df_all["Group"] == g)
                ]
        
                # pivot untuk paired
                pivot = df_sub.pivot_table(
                    index="Sample",
                    columns="Timepoint",
                    values="Value"
                )
        
                # ambil timepoint yang ada
                available_tp = [tp for tp in ["Baseline","Midline","Endline"] if tp in pivot.columns]
        
                # ===============================
                # CASE 1: 2 TIMEPOINT → WILCOXON
                # ===============================
                if len(available_tp) == 2:
        
                    t1, t2 = available_tp
        
                    paired = pivot[[t1, t2]].dropna()
        
                    if len(paired) >= 2:
                        try:
                            stat, p = wilcoxon(paired[t1], paired[t2])
                            test_used = "Wilcoxon"
                        except:
                            stat, p = np.nan, np.nan
                            test_used = "Wilcoxon (fail)"
                    else:
                        stat, p = np.nan, np.nan
                        test_used = "Wilcoxon (n<2)"
        
                # ===============================
                # CASE 2: ≥3 TIMEPOINT → KRUSKAL
                # ===============================
                elif len(available_tp) >= 3:
        
                    groups_data = []
                    for tp in available_tp:
                        vals = pivot[tp].dropna()
                        if len(vals) > 0:
                            groups_data.append(vals)
        
                    if len(groups_data) >= 2:
                        try:
                            stat, p = kruskal(*groups_data)
                            test_used = "Kruskal-Wallis"
                        except:
                            stat, p = np.nan, np.nan
                            test_used = "Kruskal (fail)"
                    else:
                        stat, p = np.nan, np.nan
                        test_used = "Kruskal (no data)"
        
                else:
                    stat, p = np.nan, np.nan
                    test_used = "Not enough timepoints"
        
                results.append({
                    "Parameter": param,
                    "Group": g,
                    "Timepoints": ", ".join(available_tp),
                    "Test": test_used,
                    "n": len(pivot),
                    "p-value": p
                })
        
        # ===============================
        # RESULT TABLE
        # ===============================
        result_df = pd.DataFrame(results)
        
        # ===============================
        # SIGNIFICANCE LABEL
        # ===============================
        def p_to_star(p):
            if pd.isna(p):
                return ""
            elif p < 0.0001:
                return "****"
            elif p < 0.001:
                return "***"
            elif p < 0.01:
                return "**"
            elif p < 0.05:
                return "*"
            else:
                return "ns"
        
        result_df["Signif"] = result_df["p-value"].apply(p_to_star)
        
        st.dataframe(result_df, use_container_width=True)
   

else:
    st.info("Silakan upload minimal data baseline")

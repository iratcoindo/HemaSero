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
    # 📊 BOXPLOT GROUP + TIMEPOINT
    # ===============================
    st.markdown("---")
    st.subheader("📦 Hematology Boxplot (Group × Timepoint)")
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    parameters = df_all["Parameter"].unique()
    groups_unique = df_all["Group"].dropna().unique()
    timepoints = ["Baseline", "Midline", "Endline"]
    
    # warna timepoint
    colors = {
        "Baseline": "#3b82f6",   # biru
        "Midline": "#10b981",    # hijau
        "Endline": "#ef4444"     # merah
    }
    
    cols_per_row = 6
    
    for i in range(0, len(parameters), cols_per_row):
    
        subset_params = parameters[i:i+cols_per_row]
        cols = st.columns(len(subset_params))
    
        for j, param in enumerate(subset_params):
    
            with cols[j]:
    
                df_param = df_all[df_all["Parameter"] == param]
    
                fig, ax = plt.subplots(figsize=(2.5,2.5))
    
                positions = []
                box_data = []
                box_colors = []
                
                pos = 0
                
                for g in groups_unique:
                
                    for tp in timepoints:
                
                        vals = df_param[
                            (df_param["Group"] == g) &
                            (df_param["Timepoint"] == tp)
                        ]["Value"].dropna()
                
                        if len(vals) > 0:
                            box_data.append(vals)
                            positions.append(pos)
                            box_colors.append(colors[tp])
                
                            pos += 1
                
                    pos += 1
    
                # plot
                bp = ax.boxplot(
                    box_data,
                    positions=positions,
                    widths=0.6,
                    patch_artist=True
                )
    
                # warna
                for patch, color in zip(bp["boxes"], box_colors):
                    patch.set_facecolor(color)
    
                # label group di tengah cluster
                xticks = []
                xticklabels = []
    
                pos = 0
                for g in groups_unique:
                    xticks.append(pos + 1)
                    xticklabels.append(g)
                    pos += len(timepoints) + 1
    
                ax.set_xticks(xticks)
                ax.set_xticklabels(xticklabels, fontsize=6)
    
                ax.set_title(param, fontsize=8)
    
                ax.tick_params(axis='y', labelsize=6)
    
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
    
                st.pyplot(fig)
   

else:
    st.info("Silakan upload minimal data baseline")

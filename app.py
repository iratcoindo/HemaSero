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
    # TRANSFORM
    # ===============================
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
    # 🧪 GROUP ASSIGNMENT
    # ===============================
    st.markdown("---")
    st.subheader("🧬 Assign Sample Groups")
    
    unique_samples = sorted(df_all["Sample"].unique())
    
    st.write("Detected samples:", unique_samples)
    
    # jumlah group
    n_group = st.number_input("Jumlah kelompok", min_value=1, max_value=10, value=2)
    
    group_map = {}
    
    for i in range(n_group):
        col1, col2 = st.columns([1,3])
    
        with col1:
            group_name = st.text_input(f"Group {i+1} Name", f"Group {i+1}", key=f"gname{i}")
    
        with col2:
            selected_samples = st.multiselect(
                f"Pilih sample untuk {group_name}",
                unique_samples,
                key=f"gsample{i}"
            )
    
        for s in selected_samples:
            group_map[s] = group_name
    
    # ===============================
    # APPLY GROUP
    # ===============================
    df_all["Group"] = df_all["Sample"].map(group_map)
    
    # ===============================
    # PREVIEW
    # ===============================
    st.subheader("📋 Grouped Data")
    st.dataframe(df_all)

    # ===============================
    # INFO DETECTION
    # ===============================
    st.subheader("🔍 Detected Structure")

    st.write("Jumlah sample:", df_all["Sample"].nunique())
    st.write("Jumlah parameter:", df_all["Parameter"].nunique())
    st.write("Timepoints:", df_all["Timepoint"].unique())

    # ===============================
    # 📊 MINI BOXPLOT PER PARAMETER
    # ===============================
    st.markdown("---")
    st.subheader("📦 Hematology Boxplot (Per Parameter)")
    
    parameters = df_all["Parameter"].unique()
    
    # jumlah kolom per baris
    cols_per_row = 6
    
    for i in range(0, len(parameters), cols_per_row):
    
        subset_params = parameters[i:i+cols_per_row]
    
        cols = st.columns(len(subset_params))
    
        for j, param in enumerate(subset_params):
    
            with cols[j]:
    
                df_param = df_all[df_all["Parameter"] == param]
    
                # ambil per timepoint
                groups = []
                labels = []
    
                for tp in ["Baseline", "Midline", "Endline"]:
                    vals = df_param[df_param["Timepoint"] == tp]["Value"].dropna()
                    if len(vals) > 0:
                        groups.append(vals)
                        labels.append(tp)
    
                # skip kalau kosong
                if len(groups) == 0:
                    st.write(f"{param} (No data)")
                    continue
    
                # plot kecil
                fig, ax = plt.subplots(figsize=(2,2))
    
                ax.boxplot(groups, labels=labels)
    
                ax.set_title(param, fontsize=8)
                ax.tick_params(axis='x', labelrotation=45, labelsize=6)
                ax.tick_params(axis='y', labelsize=6)
    
                # minimal styling
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
    
                st.pyplot(fig)

else:
    st.info("Silakan upload minimal data baseline")

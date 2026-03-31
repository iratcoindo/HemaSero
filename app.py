import streamlit as st
import pandas as pd

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
        df_long = df.melt(
            id_vars=df.columns[0],
            var_name="Sample",
            value_name="Value"
        )
        df_long.columns = ["Parameter", "Sample", "Value"]
    
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

    st.subheader("📋 Combined Data")
    st.dataframe(df_all)

    # ===============================
    # INFO DETECTION
    # ===============================
    st.subheader("🔍 Detected Structure")

    st.write("Jumlah sample:", df_all["Sample"].nunique())
    st.write("Jumlah parameter:", df_all["Parameter"].nunique())
    st.write("Timepoints:", df_all["Timepoint"].unique())

else:
    st.info("Silakan upload minimal data baseline")

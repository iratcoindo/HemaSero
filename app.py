import streamlit as st
import pandas as pd

st.title("📊 Hematology Data Input")

uploaded_file = st.file_uploader("Upload Excel/CSV", type=["xlsx","csv"])

if uploaded_file is not None:

    # ===============================
    # LOAD DATA
    # ===============================
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.subheader("📋 Raw Data")
    st.dataframe(df)

    # ===============================
    # AUTO DETECT
    # ===============================
    # asumsi kolom pertama = parameter
    parameters = df.iloc[:, 0]

    # sample ID = kolom selain pertama
    samples = df.columns[1:]

    st.subheader("🔍 Detected Structure")

    st.write(f"Jumlah parameter: {len(parameters)}")
    st.write(f"Jumlah sample: {len(samples)}")

    st.write("Parameter:")
    st.write(list(parameters))

    st.write("Sample ID:")
    st.write(list(samples))

    # ===============================
    # TRANSFORM (KE LONG FORMAT)
    # ===============================
    df_long = df.melt(
        id_vars=df.columns[0],
        var_name="Sample",
        value_name="Value"
    )

    df_long.columns = ["Parameter", "Sample", "Value"]

    st.subheader("🔄 Long Format (Siap Analisis)")
    st.dataframe(df_long)

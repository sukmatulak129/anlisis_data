import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set konfigurasi halaman
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# 1. HELPER FUNCTIONS
def create_rfm_df(df):
    """Fungsi untuk menghitung parameter RFM"""
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mencari tanggal order terakhir
        "order_id": "nunique",             # menghitung jumlah order (Frequency)
        "price": "sum"                     # menghitung total belanja (Monetary)
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    # Menghitung kapan terakhir pelanggan bertransaksi dalam hitungan hari (Recency)
    recent_date = df["order_purchase_timestamp"].max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df


# 2. LOAD DATA
all_df = pd.read_csv("all_data.csv")

# Konversi kolom tanggal ke datetime agar filter berfungsi
datetime_columns = ["order_purchase_timestamp"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# 3. SIDEBAR (FILTER)
with st.sidebar:
    st.title("E-Commerce Analysis")
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Filter Rentang Waktu
    min_date = all_df["order_purchase_timestamp"].min()
    max_date = all_df["order_purchase_timestamp"].max()
    
    try:
        start_date, end_date = st.date_input(
            label='Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except Exception:
        start_date, end_date = min_date, max_date

# Filter data utama berdasarkan input tanggal
main_df = all_df[(all_df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & 
                (all_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))]

# Menyiapkan dataframe RFM berdasarkan data yang difilter
rfm_df = create_rfm_df(main_df)

# 4. MAIN PAGE (VISUALISASI)
st.header('E-Commerce Analysis Dashboard :sparkles:')

# --- PERTANYAAN 1: REVIEW SCORE ---
st.subheader("Product Category Review Score")

# Menghitung rata-rata skor per kategori
category_review_df = main_df.groupby("product_category_name_english").review_score.mean().sort_values(ascending=False).reset_index()

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Top 5 Categories")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x="review_score", 
        y="product_category_name_english", 
        data=category_review_df.head(5), 
        palette="viridis", 
        ax=ax
    )
    ax.set_title("Highest Rated Categories", fontsize=15)
    ax.set_xlabel("Average Score")
    ax.set_ylabel(None)
    st.pyplot(fig)

with col2:
    st.markdown("#### Bottom 5 Categories")
    fig, ax = plt.subplots(figsize=(10, 6))
    # Diurutkan agar yang paling rendah ada di paling bawah grafik
    sns.barplot(
        x="review_score", 
        y="product_category_name_english", 
        data=category_review_df.tail(5).sort_values(by="review_score", ascending=True), 
        palette="magma", 
        ax=ax
    )
    ax.set_title("Lowest Rated Categories", fontsize=15)
    ax.set_xlabel("Average Score")
    ax.set_ylabel(None)
    st.pyplot(fig)

# --- PERTANYAAN 2: RFM ANALYSIS ---
st.subheader("Best Customers Based on RFM Parameters")

# Menampilkan metrik rata-rata
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Avg Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Avg Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "BRL", locale='pt_BR') 
    st.metric("Avg Monetary", value=avg_monetary)

# Visualisasi 5 Pelanggan Terbaik
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

# Grafik Recency
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Customer ID", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='x', labelsize=35, rotation=45)

# Grafik Frequency
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Customer ID", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='x', labelsize=35, rotation=45)

# Grafik Monetary
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("Customer ID", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='x', labelsize=35, rotation=45)

st.pyplot(fig)

st.caption('Copyright © Sukma Novianti Tulak 2026')

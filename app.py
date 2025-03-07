import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Mengatur style Seaborn
sns.set(style='dark')

# Load cleaned data
bike_sharing_df = pd.read_csv("all_data.csv")

# Mengatur kolom datetime
datetime_columns = ["dteday"]
bike_sharing_df.sort_values(by="dteday", inplace=True)
bike_sharing_df.reset_index(drop=True, inplace=True)

# Konversi kolom tanggal menjadi datetime
for column in datetime_columns:
    bike_sharing_df[column] = pd.to_datetime(bike_sharing_df[column])

# Menghitung Recency
recent_date = bike_sharing_df['dteday'].max()
bike_sharing_df['recency'] = (recent_date - bike_sharing_df['dteday']).dt.days

# Filter data berdasarkan tanggal
min_date = bike_sharing_df["dteday"].min()
max_date = bike_sharing_df["dteday"].max()

# Sidebar Streamlit
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("20945494.jpg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter main_df berdasarkan rentang tanggal yang dipilih
main_df = bike_sharing_df[(bike_sharing_df["dteday"] >= pd.to_datetime(start_date)) & 
                          (bike_sharing_df["dteday"] <= pd.to_datetime(end_date))]

# Mengelompokkan data berdasarkan musim dan menghitung rata-rata penyewaan
seasonal_demand = main_df.groupby('season')['cnt'].mean().reset_index()
seasonal_demand.rename(columns={'cnt': 'average_rentals'}, inplace=True)

# Mengubah kolom 'season' menjadi kategori dan mengganti label
seasonal_demand['season'] = pd.Categorical(seasonal_demand['season'], categories=[1, 2, 3, 4], ordered=True)
season_labels = ['Musim Semi', 'Musim Panas', 'Musim Gugur', 'Musim Dingin']
seasonal_demand['season'] = seasonal_demand['season'].replace({1: 'Musim Semi', 2: 'Musim Panas', 3: 'Musim Gugur', 4: 'Musim Dingin'})

# Menampilkan judul di Streamlit
st.header('Dashboard Analisis Penyewaan Sepeda')

# Layout dengan dua kolom untuk menampilkan metrik
col1, col2 = st.columns(2)

with col1:
    st.metric("Total orders", main_df['cnt'].sum())  # Menampilkan total penyewaan

with col2:
    max_rentals_row = main_df.loc[main_df['cnt'].idxmax()]
    st.metric("Jumlah penyewaan maksimum", max_rentals_row['cnt'])  # Menampilkan jumlah penyewaan maksimum

# Temukan tanggal dengan jumlah penyewaan maksimum
last_peak_date = max_rentals_row['dteday']
last_peak_rentals = max_rentals_row['cnt']

# Visualisasi total penyewaan sepeda per hari dengan garis dan tanda puncak
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(main_df['dteday'], main_df['cnt'], color='blue', label='Total Penyewaan')
ax.axvline(x=last_peak_date, color='red', linestyle='--', label='Puncak Penyewaan')
ax.scatter([last_peak_date], [last_peak_rentals], color='red', s=100, zorder=5)

# Pengaturan judul, label, dan tampilan visualisasi
ax.set_title('Total Penyewaan Sepeda per Hari', fontsize=20)
ax.set_xlabel('Tanggal', fontsize=14)
ax.set_ylabel('Jumlah Penyewaan', fontsize=14)
ax.tick_params(axis='x', labelsize=12, rotation=45)
ax.tick_params(axis='y', labelsize=12)

# Tampilkan legenda
ax.legend()

# Tampilkan visualisasi di Streamlit
st.pyplot(fig)

st.header('Analisis Penyewaan Sepeda Berdasarkan Musim')

# Plot bar rata-rata penyewaan berdasarkan musim
plt.figure(figsize=(8, 6))
colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(x='average_rentals', y='season', data=seasonal_demand, palette=colors_)

# Menambahkan judul dan label untuk plot
plt.title("Rata-rata Penyewaan Sepeda Berdasarkan Musim", loc="center", fontsize=15)
plt.ylabel("Musim")
plt.xlabel("Rata-rata Penyewaan")
plt.tick_params(axis='y', labelsize=12)

# Menampilkan plot di Streamlit
st.pyplot(plt)

# Statistik Penyewaan Berdasarkan Hari Kerja
st.header("Statistik Penyewaan Sepeda Berdasarkan Hari Kerja")
stats = main_df.groupby(by="workingday").agg({
    "cnt": ["max", "min", "mean", "std", "median", "sum", "count"]
}).reset_index()
stats.columns = ['workingday', 'cnt_max', 'cnt_min', 'cnt_mean', 'cnt_std', 'cnt_median', 'cnt_sum', 'cnt_count']

# Plot statistik
plt.figure(figsize=(12, 6))
x = range(len(stats))
plt.bar(x, stats['cnt_mean'], width=0.4, label='Mean', color='lightblue', align='center')
plt.bar(x, stats['cnt_max'], width=0.4, label='Max', color='lightsalmon', align='edge')
plt.xticks(x, ['Bukan Hari Kerja (0)', 'Hari Kerja (1)'])
plt.ylabel('Jumlah Penyewaan Sepeda')
plt.title('Statistik Penyewaan Sepeda Berdasarkan Hari Kerja')
plt.legend()
st.pyplot(plt)

# Total Penyewaan Sepeda antara Pengguna Terdaftar dan Kasual
st.header("Perbandingan Penyewaan Pengguna Terdaftar dan Kasual")
usage_comparison = main_df[['casual', 'registered']].agg({
    'casual': ['sum'],
    'registered': ['sum']
}).reset_index()
usage_comparison.columns = ['metric', 'casual', 'registered']
usage_comparison = usage_comparison.melt(id_vars='metric', var_name='user_type', value_name='count')

# Plot perbandingan pengguna
plt.figure(figsize=(8, 5))
sns.barplot(x='user_type', y='count', data=usage_comparison, palette='pastel')
plt.ylabel('Total Penyewaan')
plt.title('Total Penyewaan Sepeda antara Pengguna Terdaftar dan Kasual')
plt.xticks(rotation=0)
st.pyplot(plt)

# Total Penyewaan Sepeda Per Bulan
st.header("Total Penyewaan Sepeda Per Bulan")

# Filter data bulanan sesuai dengan rentang tanggal
monthly_rentals = main_df.groupby('mnth')['cnt'].sum().reset_index()
monthly_rentals.columns = ['month', 'total_rentals']

# Cek apakah data hasil filter kosong
if not monthly_rentals.empty:
    monthly_rentals['month'] = monthly_rentals['month'].apply(lambda x: f'{x:02}')
    total_rentals = monthly_rentals['total_rentals'].sum()
    monthly_rentals['percentage'] = (monthly_rentals['total_rentals'] / total_rentals) * 100

    # Plot total penyewaan per bulan
    plt.figure(figsize=(10, 6))

    # Buat ticks menggunakan range sesuai dengan panjang data
    ticks = range(len(monthly_rentals))  # Sesuaikan ticks dengan jumlah data yang ada

    # Plot dengan lineplot
    sns.lineplot(data=monthly_rentals, x='month', y='total_rentals', marker='o', color='blue')

    # Gunakan ticks yang sesuai dengan jumlah data
    plt.xticks(ticks=ticks, labels=[
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ][:len(ticks)])  # Ambil hanya label sebanyak ticks yang ada

    plt.title('Total Penyewaan Sepeda Per Bulan', fontsize=15)
    plt.xlabel('Bulan', fontsize=12)
    plt.ylabel('Total Penyewaan', fontsize=12)
    plt.grid()

    # Tampilkan plot di Streamlit
    st.pyplot(plt)
else:
    st.write("Tidak ada data untuk rentang tanggal yang dipilih.")

# Analisis Penyewaan Berdasarkan Kondisi Cuaca
st.header("Analisis Penyewaan Berdasarkan Kondisi Cuaca")
weather_rentals = main_df.groupby('weathersit')['cnt'].agg(['mean', 'sum']).reset_index()

# Visualisasi kondisi cuaca
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
sns.barplot(x='weathersit', y='mean', data=weather_rentals, palette='pastel')
plt.title('Rata-rata Penyewaan Berdasarkan Kondisi Cuaca', fontsize=16)
plt.xlabel('Kondisi Cuaca', fontsize=12)
plt.ylabel('Rata-rata Penyewaan', fontsize=12)

plt.subplot(1, 2, 2)
sns.barplot(x='weathersit', y='sum', data=weather_rentals, palette='pastel')
plt.title('Total Penyewaan Berdasarkan Kondisi Cuaca', fontsize=16)
plt.xlabel('Kondisi Cuaca', fontsize=12)
plt.ylabel('Total Penyewaan', fontsize=12)

# Menampilkan plot di Streamlit
st.pyplot(plt)

# RFM Analysis: Frequency dan Monetary per season
seasonal_rfm = bike_sharing_df.groupby('season').agg(
    recency=('recency', 'mean'),  # Rata-rata recency per season
    frequency=('dteday', 'nunique'),  # Jumlah hari unik penyewaan
    monetary=('cnt', 'sum')  # Total penyewaan
).reset_index()

# Membuat DataFrame RFM
rfm_df = pd.DataFrame(seasonal_rfm)

st.header("RFM Analysis Based on Seasons")

# Visualisasi RFM
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20, 6))

# Visualisasi Recency
sns.barplot(x='season', y='recency', data=rfm_df, palette="Blues", ax=ax[0])
ax[0].set_title("Average Recency by Season (days)", loc="center", fontsize=18)
ax[0].set_ylabel("Recency (days)")
ax[0].set_xlabel("Season")

# Visualisasi Frequency
sns.barplot(x='season', y='frequency', data=rfm_df, palette="Greens", ax=ax[1])
ax[1].set_title("Frequency by Season", loc="center", fontsize=18)
ax[1].set_ylabel("Frequency (unique rental days)")
ax[1].set_xlabel("Season")

# Visualisasi Monetary
sns.barplot(x='season', y='monetary', data=rfm_df, palette="Reds", ax=ax[2])
ax[2].set_title("Monetary by Season", loc="center", fontsize=18)
ax[2].set_ylabel("Total Rentals")
ax[2].set_xlabel("Season")

plt.show()

# Menampilkan plot RFM di Streamlit
st.pyplot(fig)

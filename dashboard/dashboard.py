from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")
BASE = Path(__file__).parent

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")


@st.cache_data
def load_data():
    day = pd.read_csv(BASE / "day_data.csv", parse_dates=["dteday"])
    hour = pd.read_csv(BASE / "main_data.csv", parse_dates=["dteday"])
    return day, hour


day_df, hour_df = load_data()

WEATHER_ORDER = ["Cerah", "Mist/Berawan", "Hujan/Salju Ringan"]
SEASON_ORDER = ["Semi", "Panas", "Gugur", "Dingin"]
TOD_ORDER = ["Dini Hari (00-05)", "Pagi (06-09)", "Siang (10-15)", "Sore (16-19)", "Malam (20-23)"]
COLORS = {"Hari Kerja": "#1f77b4", "Akhir Pekan/Libur": "#ff7f0e"}

# ---------------- Sidebar ----------------
st.sidebar.title("🚲 Filter")
min_date, max_date = day_df["dteday"].min().date(), day_df["dteday"].max().date()
date_range = st.sidebar.date_input("Rentang tanggal", (min_date, max_date),
                                   min_value=min_date, max_value=max_date)
if len(date_range) != 2:
    st.sidebar.info("Pilih tanggal mulai dan tanggal akhir.")
    st.stop()
start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

seasons = st.sidebar.multiselect("Musim", SEASON_ORDER, default=SEASON_ORDER)

d = day_df[(day_df["dteday"].between(start, end)) & (day_df["season_label"].isin(seasons))]
h = hour_df[(hour_df["dteday"].between(start, end)) & (hour_df["season_label"].isin(seasons))]

if d.empty or h.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

# ---------------- Header & metrik ----------------
st.title("Dashboard Penyewaan Sepeda (Capital Bikeshare, 2011-2012)")
st.caption("Menjawab dua pertanyaan bisnis: jam puncak penyewaan dan pengaruh cuaca/suhu.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total penyewaan", f"{d['cnt'].sum():,}")
c2.metric("Rata-rata per hari", f"{d['cnt'].mean():,.0f}")
c3.metric("Pengguna terdaftar", f"{d['registered'].sum() / d['cnt'].sum() * 100:.1f}%")
c4.metric("Pengguna kasual", f"{d['casual'].sum() / d['cnt'].sum() * 100:.1f}%")

st.divider()

# ---------------- Pertanyaan 1 ----------------
st.header("Pertanyaan 1: Jam berapa penyewaan memuncak?")

pattern = h.groupby(["day_type", "hr"])["cnt"].mean().unstack(0)

fig, ax = plt.subplots(figsize=(11, 4.8))
for tipe in pattern.columns:
    ax.plot(pattern.index, pattern[tipe], marker="o", linewidth=2.2, color=COLORS[tipe], label=tipe)
    pk, val = pattern[tipe].idxmax(), pattern[tipe].max()
    ax.annotate(f"Puncak {pk}:00 ({val:.0f})", xy=(pk, val), xytext=(pk + 0.6, val + 35),
                color=COLORS[tipe], fontweight="bold")
ax.set_xticks(range(24))
ax.set_xlabel("Jam dalam sehari")
ax.set_ylabel("Rata-rata penyewaan per jam")
ax.set_title("Pola penyewaan per jam: hari kerja vs akhir pekan/libur", loc="left")
ax.legend(frameon=False)
sns.despine()
st.pyplot(fig)

bins = [-1, 5, 9, 15, 19, 23]
h = h.copy()
h["time_of_day"] = pd.cut(h["hr"], bins=bins, labels=TOD_ORDER)
tod = h.groupby(["day_type", "time_of_day"], observed=True)["cnt"].sum().unstack(0).reindex(TOD_ORDER)
tod_pct = tod / tod.sum() * 100

fig, ax = plt.subplots(figsize=(9, 4.2))
tod_pct.plot(kind="bar", ax=ax, color=[COLORS.get(c, "#999") for c in tod_pct.columns], width=0.75)
for cont in ax.containers:
    ax.bar_label(cont, fmt="%.1f%%", padding=2, fontsize=9)
ax.set_xlabel("")
ax.set_ylabel("Porsi total penyewaan (%)")
ax.set_title("Porsi penyewaan per rentang waktu", loc="left")
plt.xticks(rotation=0)
ax.legend(title="", frameon=False)
sns.despine()
st.pyplot(fig)

st.info("Hari kerja punya dua puncak (08:00 dan 17:00, jam komuter), sedangkan akhir pekan/libur "
        "memuncak sekali sekitar pukul 13:00.")

st.divider()

# ---------------- Pertanyaan 2 ----------------
st.header("Pertanyaan 2: Pengaruh cuaca dan suhu")

col_a, col_b = st.columns(2)

weather = d.groupby("weather_label")["cnt"].mean().reindex(WEATHER_ORDER).dropna()
with col_a:
    fig, ax = plt.subplots(figsize=(6, 4.5))
    cols = ["#2a9d8f", "#a8c5c0", "#e76f51"][: len(weather)]
    ax.bar(weather.index, weather.values, color=cols)
    base = weather.iloc[0]
    for i, v in enumerate(weather.values):
        label = f"{v:,.0f}" if i == 0 else f"{v:,.0f}\n(-{(1 - v / base) * 100:.0f}%)"
        ax.text(i, v + base * 0.02, label, ha="center", fontweight="bold")
    ax.set_ylim(0, base * 1.25)
    ax.set_ylabel("Rata-rata penyewaan per hari")
    ax.set_title("Rata-rata penyewaan per kondisi cuaca", loc="left", fontsize=11)
    plt.xticks(fontsize=9)
    sns.despine()
    st.pyplot(fig)

temp_bins = [0, 10, 20, 30, 50]
temp_labels = ["< 10 C", "10-20 C", "20-30 C", "> 30 C"]
d = d.copy()
d["temp_bin"] = pd.cut(d["temp_c"], bins=temp_bins, labels=temp_labels)
temp = d.groupby("temp_bin", observed=True)["cnt"].mean()
with col_b:
    fig, ax = plt.subplots(figsize=(6, 4.5))
    top = temp.idxmax()
    ax.bar(temp.index.astype(str), temp.values, color=["#2a9d8f" if k == top else "#b8c4c2" for k in temp.index])
    for i, v in enumerate(temp.values):
        ax.text(i, v + temp.max() * 0.02, f"{v:,.0f}", ha="center", fontweight="bold")
    ax.set_ylim(0, temp.max() * 1.2)
    ax.set_xlabel("Rentang suhu rata-rata harian")
    ax.set_title("Rata-rata penyewaan per rentang suhu", loc="left", fontsize=11)
    sns.despine()
    st.pyplot(fig)

season = d.groupby("season_label")["cnt"].mean().reindex(SEASON_ORDER).dropna()
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(season.index, season.values, color=["#2a9d8f" if k == season.idxmax() else "#b8c4c2" for k in season.index])
for i, v in enumerate(season.values):
    ax.text(i, v + season.max() * 0.02, f"{v:,.0f}", ha="center", fontweight="bold")
ax.set_ylabel("Rata-rata penyewaan per hari")
ax.set_title("Rata-rata penyewaan per musim", loc="left")
sns.despine()
st.pyplot(fig)

# ---------------- Analisis lanjutan ----------------
st.subheader("Analisis lanjutan: tingkat permintaan harian (manual grouping)")
st.caption("Rendah < 3.000, Sedang 3.000-6.000, Tinggi > 6.000 sewa/hari.")
d["demand_level"] = pd.cut(d["cnt"], bins=[0, 3000, 6000, 10000], labels=["Rendah", "Sedang", "Tinggi"])
demand = (pd.crosstab(d["weather_label"], d["demand_level"], normalize="index") * 100)
demand = demand.reindex([w for w in WEATHER_ORDER if w in demand.index])
fig, ax = plt.subplots(figsize=(9, 3.5))
demand.plot(kind="barh", stacked=True, ax=ax, color=["#e76f51", "#e9c46a", "#2a9d8f"], width=0.6)
for cont in ax.containers:
    ax.bar_label(cont, fmt="%.0f%%", label_type="center", fontsize=9)
ax.set_xlabel("Persentase hari (%)")
ax.set_ylabel("")
ax.invert_yaxis()
ax.legend(title="Tingkat permintaan", frameon=False, bbox_to_anchor=(1.01, 1), loc="upper left")
sns.despine()
st.pyplot(fig)

st.divider()
st.header("Rekomendasi")
st.markdown(
    """
1. Isi ulang stasiun sebelum 07:00 dan 16:00 pada hari kerja, dan siapkan stok di area rekreasi pukul 10:00-15:00 pada akhir pekan.
2. Jadwalkan perawatan armada saat prakiraan hujan/salju atau suhu di bawah 10 C (permintaan turun lebih dari 60%).
3. Fokuskan promosi pada musim panas hingga gugur (suhu 20-30 C) dan beri insentif keanggotaan di musim semi.
"""
)
st.caption("Sumber data: Fanaee-T & Gama (2013), Capital Bikeshare Washington D.C.")

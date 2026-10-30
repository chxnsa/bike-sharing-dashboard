# Proyek Analisis Data: Bike Sharing Dataset

Analisis data penyewaan sepeda Capital Bikeshare (Washington D.C., 2011-2012) beserta dashboard interaktif Streamlit.

## Pertanyaan Bisnis
1. Pada jam berapa penyewaan memuncak pada hari kerja vs akhir pekan/libur, dan berapa porsi penyewaan tiap rentang waktu?
2. Seberapa besar penurunan penyewaan harian saat cuaca mist/berawan dan hujan/salju ringan dibanding cerah, dan pada rentang suhu berapa penyewaan paling tinggi?

## Struktur Direktori
```
submission
├───dashboard
| ├───main_data.csv     (data per jam, sudah bersih)
| ├───day_data.csv      (data harian, sudah bersih)
| └───dashboard.py
├───data
| ├───day.csv
| └───hour.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment
Dengan Anaconda:
```
conda create --name bike-ds python=3.11
conda activate bike-ds
pip install -r requirements.txt
```

Dengan Shell/Terminal:
```
mkdir proyek_analisis_data
cd proyek_analisis_data
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## Menjalankan Dashboard
Dari folder `submission`:
```
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di `http://localhost:8501`.

## Menjalankan Notebook
Buka `notebook.ipynb` di Jupyter/Colab, lalu jalankan semua cell secara berurutan (pastikan folder `data/` ada di samping notebook). Cell terakhir akan menyimpan ulang data bersih ke folder `dashboard/`.

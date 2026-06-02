# ⧫ Ethereum EDA Dashboard

**SAP ID:** 70177906  
**Dataset:** CoinGecko Ethereum History (`ethereum.csv`)  
**Course:** Exploratory Data Analysis  
**Instructor:** Ali Hassan Sherazi  
**Submission Date:** 05-June-2026  

---

## 📁 Project Structure

```
dashboard_project/
├── data/
│   └── ethereum.csv          ← Auto-downloaded on first run
├── notebooks/
│   └── analysis.ipynb        ← EDA notebook
├── app.py                    ← Main Streamlit dashboard
├── charts.py                 ← All 10 chart functions
├── filters.py                ← Data loading & filter logic
├── fetch_data.py             ← CoinGecko API data fetcher
├── requirements.txt          ← Python dependencies
└── README.md                 ← This file
```

---

## ⚙️ Installation & Setup

### 1. Clone / unzip the project
```bash
cd dashboard_project
```

### 2. Create virtual environment (optional but recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Fetch the dataset
```bash
python fetch_data.py
```
This downloads ETH daily price, market cap, and volume from CoinGecko and saves it as `data/ethereum.csv`.  
> If the API is unavailable, realistic synthetic demo data is generated automatically.

### 5. Launch the dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`

---

## 📊 Dashboard Features

### KPI Cards (Top)
- Total Records, Average Price, All-Time High, All-Time Low
- Best Day Return, Worst Day Return

### Charts (All 10 Required)
| # | Chart | Purpose |
|---|-------|---------|
| 1 | Line Chart | ETH price trend + MA-7/30/90 |
| 2 | Histogram | Daily return distribution |
| 3 | Bar Chart | Average price by year |
| 4 | Scatter Plot | Volume vs Price (colored by year) |
| 5 | Box Plot | Price distribution per year |
| 6 | Heatmap | Feature correlation matrix |
| 7 | Area Chart | Market cap over time |
| 8 | Pie Chart | Volume share by year |
| 9 | Count Plot | Trading days per quarter |
| 10 | Violin Plot | Daily return density by year |
| 🎁 | Pair Plot | Bonus pairwise feature relationships |

### Interactive Filters (Sidebar)
- **Date Range Filter** — Select start & end date
- **Year Multi-Select** — Choose specific years
- **Quarter Multi-Select** — Filter by Q1/Q2/Q3/Q4
- **Price Range Slider** — Filter by ETH price
- **Volume Range Slider** — Filter by trading volume
- **Text Search** — Search by date keyword (e.g. "2021-11")
- **Reset Button** — Clear all filters instantly

> All charts update simultaneously when any filter changes.

---

## 🔑 Key Insights

1. **ETH was virtually worthless in 2015–2016**, trading under $15.
2. **2017 was the first major bull run**, with ETH reaching ~$1,400.
3. **2021 saw the all-time high** of ~$4,800 driven by DeFi & NFT demand.
4. **2022 saw a massive crash** (−70%) due to macro tightening and FTX collapse.
5. **Daily returns are heavy-tailed** — far more extreme moves than traditional assets.
6. **Price and market cap are perfectly correlated** (supply is roughly stable daily).
7. **Volume spikes during volatile periods** — fear and greed both drive trading activity.
8. **Q4 historically shows higher average prices** (holiday rally effect).

---

## 🛠️ Tech Stack
- **Python 3.x** — Core language
- **Pandas** — Data loading, cleaning, filtering, aggregation
- **NumPy** — Numerical operations
- **Matplotlib** — Core plotting
- **Seaborn** — Statistical visualizations
- **Streamlit** — Interactive dashboard frontend
- **Requests** — CoinGecko API calls

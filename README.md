# Findwise

Professional product discovery powered by a Kaggle catalogue, TF-IDF similarity, and live product data.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-web%20app-000000?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-2b8375)

## Contents

- [What it does](#what-it-does)
- [Quick start](#quick-start)
- [How it works](#how-it-works)
- [Live data](#live-data)
- [Routes](#routes)
- [Project layout](#project-layout)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## What it does

Findwise helps users discover related products through a clean, responsive storefront.

- Content-based recommendations from the supplied Walmart/Kaggle product data.
- Live product cards with images, prices, ratings, and stock counts.
- Automatic live refresh every 60 seconds plus a manual Refresh button.
- Professional Home, Why Us, Contact, and recommendation result pages.
- Theme toggle, brand/category filters, saved-item buttons, and responsive layouts.
- Offline fallback to the local catalogue when the live API is unavailable.

## Quick start

### 1. Create an environment

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Run the website

```bash
python -m flask --app app run --debug --port 5000
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser.

## How it works

1. `clean_data.csv` is loaded and product tags are converted into TF-IDF vectors.
2. A selected product is compared with the full catalogue using cosine similarity.
3. The closest products are ranked and rendered as recommendation cards.
4. The home page separately fetches current products from a free live API.
5. If that API fails, the live section displays local Kaggle-derived products.

## Live data

The default source is the free [DummyJSON products API](https://dummyjson.com/docs/products). Change it without editing code:

PowerShell:

```powershell
$env:LIVE_PRODUCTS_URL = "https://your-api.example/products"
python -m flask --app app run --debug --port 5000
```

The endpoint should return a JSON object containing a `products` array with fields such as `title`, `brand`, `category`, `price`, `rating`, `stock`, and `thumbnail`.

## Routes

| Route | Purpose |
| --- | --- |
| `/` | Home page and live product discovery |
| `/recommendations?prod=<name>&nbr=8` | Similar product results |
| `/why-us` | Product and recommendation explanation |
| `/contact` | Contact form |
| `/api/live-products` | JSON live product feed |

## Project layout

```text
app.py                 Flask routes and recommendation engine
clean_data.csv         Kaggle-derived recommendation catalogue
trending_products.csv  Kaggle-derived trending products
templates/             Home, results, Why Us, Contact, and card templates
style.css              Responsive visual system
ui.js                  Theme, filters, saved items, and live refresh
requirements.txt       Python dependencies
LICENSE                MIT license
```

## Troubleshooting

**The live section says unavailable**

The app is still working. The API timed out or returned an error, so Findwise is showing local catalogue data. Check your network connection or set `LIVE_PRODUCTS_URL` to another compatible endpoint.

**PowerShell blocks activation**

Run the project with the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m flask --app app run --debug --port 5000
```

**The port is busy**

```bash
python -m flask --app app run --debug --port 5001
```

## License

Released under the [MIT License](LICENSE).

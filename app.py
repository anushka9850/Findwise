from pathlib import Path
import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

from flask import Flask, jsonify, request, render_template
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR), static_url_path="/assets")

trending_products = pd.read_csv(BASE_DIR / "trending_products.csv").fillna("")
train_data = pd.read_csv(BASE_DIR / "clean_data.csv").fillna("")
train_data["Name"] = train_data["Name"].astype(str)
train_data["Tags"] = train_data["Tags"].astype(str)
train_data["Brand"] = train_data["Brand"].astype(str)
train_data["Category"] = train_data["Category"].astype(str)

vectorizer = TfidfVectorizer(stop_words="english", max_features=40000)
tfidf_matrix = vectorizer.fit_transform(train_data["Tags"])
LIVE_PRODUCTS_URL = os.getenv(
    "LIVE_PRODUCTS_URL",
    "https://dummyjson.com/products?limit=8&select=title,brand,category,price,rating,stock,thumbnail",
)


# Recommendations functions============================================================================================
# Function to truncate product name
def first_image(value):
    images = str(value).split(" | ")
    return images[0] if images and images[0].startswith("http") else ""


def product_record(row, score=None):
    rating = pd.to_numeric(row.get("Rating", 0), errors="coerce")
    reviews = pd.to_numeric(row.get("ReviewCount", 0), errors="coerce")
    return {
        "name": str(row.get("Name", "Unnamed product")),
        "brand": str(row.get("Brand", "Independent")) or "Independent",
        "category": str(row.get("Category", "")),
        "rating": float(rating) if pd.notna(rating) else 0,
        "reviews": int(float(reviews)) if pd.notna(reviews) else 0,
        "image": first_image(row.get("ImageURL", "")),
        "price": None,
        "stock": None,
        "source": "Kaggle catalogue",
        "score": round(float(score) * 100) if score is not None else None,
    }


def fetch_live_products(limit=8):
    request = Request(LIVE_PRODUCTS_URL, headers={"User-Agent": "Findwise/1.0"})
    try:
        with urlopen(request, timeout=4) as response:
            payload = json.loads(response.read().decode("utf-8"))
        products = []
        for item in payload.get("products", [])[:limit]:
            products.append({
                "name": item.get("title", "Live product"),
                "brand": item.get("brand", "Independent") or "Independent",
                "category": item.get("category", "").replace("-", " ").title(),
                "rating": float(item.get("rating", 0) or 0),
                "reviews": 0,
                "image": item.get("thumbnail", ""),
                "price": float(item.get("price", 0) or 0),
                "stock": int(item.get("stock", 0) or 0),
                "source": "Live API",
                "score": None,
            })
        return products, "Live now · DummyJSON product API"
    except (URLError, TimeoutError, ValueError, OSError):
        return get_trending(limit), "Live feed unavailable · showing Kaggle catalogue"


def get_trending(limit=8):
    return [product_record(row) for _, row in trending_products.head(limit).iterrows()]


def get_catalog_options():
    brands = sorted({value for value in train_data["Brand"] if value})
    categories = sorted({value.split(",")[0].strip().title() for value in train_data["Category"] if value})
    return brands, categories


@app.template_filter("short_name")
def short_name(value, length=58):
    value = str(value)
    return value if len(value) <= length else f"{value[:length].rstrip()}..."


@app.template_filter("format_number")
def format_number(value):
    return f"{int(value):,}"


def content_based_recommendations(item_name, top_n=8):
    matches = train_data[train_data["Name"].str.lower() == item_name.lower()]
    if matches.empty:
        return []

    item_index = matches.index[0]
    similarities = cosine_similarity(tfidf_matrix[item_index], tfidf_matrix).ravel()
    ranked_indices = similarities.argsort()[::-1]
    recommendations = []
    for index in ranked_indices:
        if index == item_index:
            continue
        recommendations.append(product_record(train_data.iloc[index], similarities[index]))
        if len(recommendations) == top_n:
            break
    return recommendations


@app.route("/")
@app.route("/index")
def index():
    brands, categories = get_catalog_options()
    live_products, live_status = fetch_live_products()
    return render_template("index.html", trending_products=get_trending(), brands=brands,
                           categories=categories, product_count=len(train_data),
                           live_products=live_products, live_status=live_status)

@app.route("/main")
def main():
    return index()


@app.route("/why-us")
def why_us():
    return render_template("why-us.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html", submitted=request.method == "POST")


@app.route("/api/live-products")
def live_products_api():
    products, status = fetch_live_products()
    return jsonify({"products": products, "status": status})

@app.route("/recommendations", methods=["POST", "GET"])
def recommendations():
    product_name = request.values.get("prod", "").strip()
    try:
        count = min(max(int(request.values.get("nbr", 8)), 3), 16)
    except (TypeError, ValueError):
        count = 8
    recommendations = content_based_recommendations(product_name, count) if product_name else []
    brands, categories = get_catalog_options()
    return render_template("main.html", recommendations=recommendations,
                           selected_product=product_name, count=count, brands=brands,
                           categories=categories, trending_products=get_trending(4),
                           product_count=len(train_data))


if __name__=='__main__':
    app.run(debug=True)
import pandas as pd
from sqlalchemy import create_engine

# load parsers 
from parsers.colours import parse_colours
from parsers.price import parse_price
from parsers.ratings import parse_rating
from parsers.weights import parse_weight_grams

# Load data for json
print("Loading JSON data...")
df = pd.read_json(
    "./data/marketing_sample_for_amazon_com-amazon_fashion_products__20200201_20200430__30k_data.ldjson",
    lines=True,
)

cat_cols = df.select_dtypes(include=["object", "category"]).columns
num_cols = df.select_dtypes(include=["number"]).columns

df[cat_cols] = df[cat_cols].fillna("unknown")
df[num_cols] = df[num_cols].fillna(0)

# 2. Clean numeric features
print("Clean the data...")
df["sales_price"] = df["sales_price"].apply(parse_price)
df["weight"] = df["weight"].apply(parse_weight_grams)
df["nurating"] = df["rating"].apply(parse_rating)
df["colour"] = df["colour"].apply(parse_colours)

print("Selecting relevant columns...")
df_with_selected_cols = df[
    [
        "uniq_id",
        "product_name",
        "brand",
        "colour",
        "sales_price",
        "weight",
        "rating",
        "image_urls__small",
    ]
]

f = open("/tmp/clean_data_info.log", "w")
print(df_with_selected_cols.info(), file=f)
f.close()

# PostgreSQL connection details
username = "postgres"
password = "postgres"
host = "localhost"
port = "5432"
database = "products_db"

# Connection to database
print("Connecting to PostgreSQL database...")
try:

    engine = create_engine(
        f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database}"
    )

    # Write the selected columns to the PostgreSQL table
    df_with_selected_cols.to_sql("products", engine, if_exists="replace", index=False)
    print("Data successfully written to the PostgreSQL table.")

except Exception as e:
    print(f"An error occurred: {e}")

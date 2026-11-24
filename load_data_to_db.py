import pandas as pd
from sqlalchemy import create_engine

# Load data for json
print("Loading JSON data...")
df = pd.read_json(
    "./data/marketing_sample_for_amazon_com-amazon_fashion_products__20200201_20200430__30k_data.ldjson",
    lines=True,
)

cat_cols = df.select_dtypes(include=["object", "category"]).columns
num_cols = df.select_dtypes(include=["number"]).columns

df[cat_cols] = df[cat_cols].fillna("")
df[num_cols] = df[num_cols].fillna(0)

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
    df_with_selected_cols.to_sql("products_original", engine, if_exists="replace", index=False)
    print("Data successfully written to the PostgreSQL table.")

except Exception as e:
    print(f"An error occurred: {e}")

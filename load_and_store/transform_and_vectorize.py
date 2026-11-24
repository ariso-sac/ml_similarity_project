import re
import numpy as np
import pandas as pd
import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, normalize


# PostgreSQL connection details
username = "postgres"
password = "postgres"
host = "localhost"
port = "5432"
database = "products_db"

DB_DSN = f"postgresql://{username}:{password}@{host}:{port}/{database}"
TABLE_NAME = "products"

# Configurable weights between numeric attributes and categorical/text attributes
SVD_DIMS = 64  # Total vector dim = 4 + 64 = 68


def build_and_store_embeddings():
    # 1. Fetch raw columns from Postgres
    with psycopg.connect(DB_DSN) as conn:
        query = f"""
            SELECT uniq_id, product_name, brand, colour, sales_price, weight, rating, image_urls__small
            FROM {TABLE_NAME}
            WHERE uniq_id IS NOT NULL
        """
        df = pd.read_sql(query, conn)

    print(f"Loaded {len(df)} products from Postgres.")

    num_cols = ["sales_price", "weight", "rating"]
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()

    X_num = scaler.fit_transform(imputer.fit_transform(df[num_cols]))
    X_num = normalize(X_num, norm="l2")

    # 3. Encode categorical / text attributes + Dimensionality Reduction (SVD)
    df["text_blob"] = (
        "brand_"
        + df["brand"].fillna("unknown").astype(str).str.lower().str.strip()
        + " color_"
        + df["colour"]
        .fillna("unknown")
        .astype(str)
        .str.lower()
        .str.strip()
        + " has_img_"
        + df["image_urls__small"].notna().astype(str)
    )

    tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_tfidf = tfidf.fit_transform(df["text_blob"])

    svd = TruncatedSVD(n_components=SVD_DIMS, random_state=42)
    X_text = svd.fit_transform(X_tfidf)
    X_text = normalize(X_text, norm="l2")

    # 4. Combine & L2-normalize final vector for Cosine Similarity
    embeddings = np.concatenate([np.asarray(X_num), np.asarray(X_text)], axis=1).astype(
        np.float32
    )
    embeddings = normalize(embeddings, norm="l2", axis=1)

    # 6. Store embeddings
    dimension = embeddings.shape[1]

    with psycopg.connect(DB_DSN) as conn:

        register_vector(conn)

        with conn.cursor() as cur:

            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

            query = f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS embedding vector({dimension})"
            cur.execute(query)

            update_query = (
                f"""UPDATE {TABLE_NAME} SET embedding = %s WHERE uniq_id = %s"""
            )

            records = [
                (embedding, uniq_id)
                for uniq_id, embedding in zip(df["uniq_id"], embeddings)
            ]

            cur.executemany(update_query, records)

        conn.commit()

    print(
        f"Successfully stored {len(embeddings)} "
        f"embeddings ({dimension} dimensions)."
    )

    print("Successfully stored embeddings in Postgres!")


if __name__ == "__main__":
    build_and_store_embeddings()

from functools import lru_cache
from typing import List
import psycopg
from pgvector.psycopg import register_vector

# PostgreSQL connection details
username = "postgres"
password = "postgres"
host = "localhost"
port = "5432"
database = "products_db"

DB_DSN = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# Reuse a persistent connection (or psycopg_pool.ConnectionPool in production)
_conn = psycopg.connect(DB_DSN)
register_vector(_conn)


@lru_cache(maxsize=2048)
def _cached_similarity_search(product_id: str, num_similar: int) -> tuple[str, ...]:
    """
    Cached inner implementation. Uses HNSW approximate nearest neighbor search
    in Postgres, with deterministic tie-breaking on rating and sales_price.
    """
    if num_similar <= 0:
        return ()

    with _conn.cursor() as cur:
        # 1. Retrieve target product's embedding via unique index on uniq_id
        cur.execute(
            "SELECT embedding FROM products WHERE uniq_id = %s",
            (product_id,),
        )
        row = cur.fetchone()
        if not row or row[0] is None:
            raise ValueError(
                f"Product ID '{product_id}' not found or has no embedding."
            )

        target_vec = row[0]

        # 2. Ensure HNSW ef_search >= num_similar for high recall
        ef_search = max(40, num_similar * 3)
        cur.execute(f"SET LOCAL hnsw.ef_search = {int(ef_search)}")

        # Over-fetch slightly (+1 for self, +extra for clean tie-breaking at boundary)
        candidate_k = num_similar + 15

        # 3. Inner CTE uses HNSW index; outer query filters self & applies tie-breakers
        cur.execute(
            """
            WITH candidates AS (
                SELECT
                    uniq_id,
                    (embedding <=> %s) AS distance,
                    rating,
                    sales_price
                FROM products
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s
                LIMIT %s
            )
            SELECT uniq_id
            FROM candidates
            WHERE uniq_id != %s
            ORDER BY
                ROUND(distance::numeric, 6) ASC,
                rating DESC NULLS LAST,
                sales_price ASC NULLS LAST
            LIMIT %s;
            """,
            (target_vec, target_vec, candidate_k, product_id, num_similar),
        )
        results = [r[0] for r in cur.fetchall()]
        _conn.commit()
        return tuple(results)


def find_similar_products(product_id: str, num_similar: int) -> List[str]:
    """
    Retrieve top num_similar product IDs similar to product_id.
    """
    return list(_cached_similarity_search(product_id, num_similar))


if __name__ == "__main__":
    print("Welcome to search for similar products !!")
    sample_id = input("Enter a reference product id :-\t")
    number_of_samples = int(input("Enter number of similar products to fetch :-\t"))

    similar_products = find_similar_products(sample_id, number_of_samples)
    print(f"Top {number_of_samples} similar to {sample_id}:", similar_products)

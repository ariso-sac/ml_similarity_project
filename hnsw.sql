-- HNSW Query

CREATE EXTENSION IF NOT EXISTS vector;

CREATE INDEX IF NOT EXISTS idx_products_embedding_hnsw
ON products
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

ANALYZE products;
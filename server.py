
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from search_similar_and_retervive import find_similar_products

app = FastAPI(title="Similar Products API")


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

    <div class="container mt-5">
        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0">Similar Products Search</h4>
            </div>

            <div class="card-body">
                <form action="/similar-products" method="get">

                    <div class="mb-3">
                        <label class="form-label">Product ID</label>
                        <input type="text" name="product_id"
                               class="form-control" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Number of Similar Products</label>
                        <input type="number" name="num_similar"
                               class="form-control" value="5" min="1">
                    </div>

                    <button type="submit" class="btn btn-primary">
                        Search
                    </button>

                </form>
            </div>
        </div>
    </div>
    """


@app.get("/similar-products", response_class=HTMLResponse)
def get_similar_products(
    product_id: str = Query(...),
    num_similar: int = Query(5, gt=0)
):
    try:
        results = find_similar_products(product_id, num_similar)

        result_html = "".join(
            f'<li class="list-group-item">{i}. {product}</li>'
            for i, product in enumerate(results, 1)
        )

        return f"""
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

        <div class="container mt-5">
            <div class="card shadow-sm">
                <div class="card-header bg-success text-white">
                    <h4 class="mb-0">Similar Products</h4>
                </div>

                <div class="card-body">
                    <p><strong>Reference Product:</strong> {product_id}</p>
                    <p><strong>Results Found:</strong> {len(results)}</p>

                    <ul class="list-group mb-3">
                        {result_html or '<li class="list-group-item">No similar products found.</li>'}
                    </ul>

                    <a href="/" class="btn btn-primary">
                        Search Again
                    </a>
                </div>
            </div>
        </div>
        """

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
SitWise FastAPI uygulaması — giriş noktası.
SW-015: API v1 router'larını kayıt eder; /docs ile OpenAPI arayüzü aktif.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.router import api_v1_router

# ---------------------------------------------------------------------------
# Uygulama nesnesi (main dalındaki temel ayarlar korunarak)
# ---------------------------------------------------------------------------

app = FastAPI(title="SitWise Server", version="0.1.0")

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Router kayıtları
# ---------------------------------------------------------------------------

app.include_router(api_v1_router)


# ---------------------------------------------------------------------------
# Sağlık kontrolü
# ---------------------------------------------------------------------------


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "sitwise-server"}


# ---------------------------------------------------------------------------
# Doğrudan çalıştırma (geliştirme)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

"""
SitWise FastAPI uygulaması — giriş noktası.
SW-015: API v1 router'larını kayıt eder; /docs ile OpenAPI arayüzü aktif.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.router import api_v1_router

# ---------------------------------------------------------------------------
# Uygulama nesnesi
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SitWise API",
    description=(
        "SitWise Ergonomi Asistanı arka uç servisi.\n\n"
        "**Gizlilik notu:** Kamera kareleri asla iletilmez; "
        "yalnızca sayısal ergonomi özetleri gönderilir."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# Ara katman — CORS
# Masaüstü uygulamasının (Electron) sunucuya sorunsuz bağlanabilmesi için
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Sunucunun ayakta olup olmadığını kontrol eden uç nokta."""
    return {"status": "healthy", "service": "SitWise API", "version": "1.0.0"}


# ---------------------------------------------------------------------------
# Doğrudan çalıştırma (geliştirme)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    # Sunucuyu yerel makinede 8000 portunda başlatıyoruz
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

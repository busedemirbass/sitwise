from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPI uygulamasını başlatıyoruz
app = FastAPI(
    title="SitWise API",
    description="SitWise Ergonomi Asistanı Backend Servisi",
    version="0.1.0",
)

# Masaüstü uygulamasının (Electron) sunucuya sorunsuz bağlanabilmesi için CORS izni
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    """Sunucunun ayakta olup olmadığını kontrol eden uç nokta."""
    return {"status": "healthy", "service": "SitWise API", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    # Sunucuyu yerel makinede 8000 portunda başlatıyoruz
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

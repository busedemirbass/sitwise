# SitWise — masaüstü istemci

Electron + React + Vite + TypeScript. Kamera görüntüsü MediaPipe ile bu bilgisayarda işlenir; görüntü kaydedilmez.

## Kurulum

```bash
cd apps/desktop
npm install
npm run dev
```

Node 22+ gerekir.

## Komutlar

| Komut               | Ne yapar                                          |
| ------------------- | ------------------------------------------------- |
| `npm run dev`       | Geliştirme modunda açar (kod değişince yenilenir) |
| `npm run typecheck` | TypeScript tip kontrolü                           |
| `npm run lint`      | ESLint                                            |
| `npm run format`    | Prettier ile biçimlendirir                        |
| `npm run build`     | Tip kontrolü + üretim derlemesi (`out/`)          |

## SW-007 — iskelet

- Pencere kapatılınca uygulama kapanmaz, tepsiye iner; kamera arka planda sürer (`backgroundThrottling: false`).
- Tepsi menüsü: aç · izlemeyi duraklat/devam · bilgisayar açılınca başlat · çıkış.
- Duraklatınca kamera tamamen kapanır (ışık söner).
- Otomatik başlama Windows ve macOS'ta; oturum açılışında pencere göstermeden başlar (`--hidden`).
- Tek örnek: ikinci kez açılırsa mevcut pencere öne gelir.
- Kamera izni yalnızca kendi arayüzümüze, yalnızca görüntü (ses yok).
- Üretimde arayüz `app://sitwise` protokolünden sıkı bir CSP ile sunulur.

## Klasörler

```
src/main       Electron ana süreç: pencere, tepsi, izinler, IPC
src/preload    contextBridge ile arayüze açılan dar API (window.sitwise)
src/shared     main ↔ renderer IPC kanalları ve tipleri
src/renderer   React arayüzü
resources/     tepsi ve uygulama simgeleri
```

## Bilinen sınırlar

- Linux'ta otomatik başlatma yok (Electron desteklemiyor).
- Kurulum dosyası (electron-builder) SW-063'te eklenecek.

# AGENTS.md — SitWise

Bu dosya, repoda çalışan tüm yapay zekâ ajanları (Cursor, Antigravity vb.) ve insanlar için ortak kurallardır. Ajan bu dosyayı her görevde okur.

## Proje

SitWise, standart bir webcam ile duruşu ve göz yorgunluğunu izleyen, gizlilik öncelikli bir masaüstü ergonomi asistanıdır. Manisa Celal Bayar Üniversitesi Bilgisayar Mühendisliği mezuniyet projesidir (2 kişi, Ekim 2026 – Ocak 2027).

## Klasör yapısı

```
apps/desktop   Electron + React + Vite + TypeScript istemci (Alan A)
apps/server    Python + FastAPI + PostgreSQL sunucu (Alan B)
docs/          vision.md, api/contract.md, adr/, uml/, meetings/
```

## Değişmez kurallar

1. **Görüntü asla kaydedilmez ve gönderilmez.** Kamera kareleri yalnızca bellekte işlenir. Diske, loga, sunucuya yalnızca sayısal özetler gider. Bu kuralı çiğneyen bir PR birleştirilmez.
2. **CDN yok.** MediaPipe wasm ve modelleri uygulamanın içinden yüklenir.
3. **Electron güvenliği:** `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`. Arayüz Node'a doğrudan erişmez; yeni bir yetenek preload üzerinden dar bir fonksiyonla eklenir.
4. **Ajan yalnızca alınan kartın dosyalarına dokunur.** Kartla ilgisi olmayan dosyaları yeniden biçimlendirmez, yeniden adlandırmaz, "temizlemez".
5. **PR'lar küçük tutulur:** bir kart = bir branch = bir PR.
6. **Sırlar repoya girmez.** Şifreler ve anahtarlar `.env` dosyasında durur; repoda yalnızca `.env.example` bulunur.

## Git ve iş akışı

- Branch: `tip/SW-id-kisa-ad` (ör. `feat/SW-024-blink-detector`). `main` korumalı, doğrudan push yok.
- Commit: Conventional Commits, sonunda kart numarası. Ör. `feat(client): add EAR-based blink counter (SW-024)`.
- Kapsamlar: `client`, `server`, `docs`, `ci`.
- PR açıklaması: ne değişti, nasıl test edildi, ekran görüntüsü. Diğer kişi onaylayınca merge edilir.
- Büyük mimari kararlar `docs/adr/ADR-00X-*.md` olarak yazılır.

## Kod stili

- Biçimlendirme repodaki ayarlardan gelir; elle tartışılmaz:
  - İstemci: Prettier + ESLint (`npm run lint`, `npm run format`).
  - Sunucu: black + flake8 (`apps/server/.flake8`, satır uzunluğu 88).
  - Hepsi: `.editorconfig`; satır sonları `.gitattributes` ile LF; dosyalar UTF-8.
- TypeScript `strict`. `any` yerine doğru tip ya da `unknown`.
- Kod, tanımlayıcılar ve commit mesajları İngilizce; kullanıcıya görünen metinler ve açıklayıcı yorumlar Türkçe olabilir.
- Ölçüm/analiz kodu React'ten bağımsız saf TypeScript olarak yazılır ki test edilebilsin.

## Bitti tanımı

Kart ancak şunlar sağlanınca "Bitti"ye geçer: PR main'e birleşti ve CI yeşil · kartın kabul kriteri karşılandı · gerekiyorsa UML/tablo güncellendi · Geliştirme Günlüğü'ne satır yazıldı.
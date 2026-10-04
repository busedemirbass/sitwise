import { useEffect, useState } from 'react';
import type { AppSettings } from '../../shared/ipc';
import { useCamera } from './hooks/useCamera';

/**
 * SW-007: iskelet arayüzü. Kamera önizlemesi, izleme durumu ve arka plan ayarları.
 * MediaPipe ölçümleri SW-008'de bu ekrana eklenecek.
 */
export function App() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const paused = settings?.paused ?? false;
  const { videoRef, status: cameraStatus, error: cameraError, resolution } = useCamera(!paused);

  useEffect(() => {
    void window.sitwise.getSettings().then(setSettings);
    return window.sitwise.onPausedChanged((p) => setSettings((s) => (s ? { ...s, paused: p } : s)));
  }, []);

  const togglePause = async () => setSettings(await window.sitwise.setPaused(!paused));
  const toggleAutoStart = async () => settings && setSettings(await window.sitwise.setAutoStart(!settings.autoStart));

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="logo" aria-hidden>
            ◉
          </span>
          SitWise <span className="muted">· geliştirici görünümü</span>
        </div>
        <div className="topbar-actions">
          <span className={`pill ${paused ? 'pill-warn' : 'pill-ok'}`}>{paused ? 'Duraklatıldı' : 'İzleniyor'}</span>
          <button onClick={togglePause}>{paused ? 'Devam et' : 'Duraklat'}</button>
        </div>
      </header>

      <main className="layout">
        <section className="stage">
          <div className="video-wrap">
            <video ref={videoRef} className="mirror" playsInline muted />
            {cameraStatus !== 'live' && (
              <div className="video-placeholder">
                {paused && 'İzleme duraklatıldı — kamera kapalı.'}
                {!paused && cameraStatus === 'starting' && 'Kamera açılıyor…'}
                {cameraStatus === 'denied' && 'Kamera izni verilmedi. Sistem ayarlarından SitWise’a kamera izni verin.'}
                {cameraStatus === 'error' && `Kamera açılamadı: ${cameraError}`}
              </div>
            )}
          </div>
          <p className="privacy">
            Görüntü yalnızca bu bilgisayarda, bellekte işlenir. Hiçbir kare kaydedilmez veya gönderilmez.
          </p>
        </section>

        <aside className="side">
          <section className="card">
            <h2>Kamera</h2>
            <dl className="metrics">
              <dt>Durum</dt>
              <dd>{cameraStatus}</dd>
              <dt>Çözünürlük</dt>
              <dd>{resolution || '—'}</dd>
              <dt>Platform</dt>
              <dd>{settings?.platform ?? '—'}</dd>
            </dl>
          </section>
          <section className="card">
            <h2>Arka plan</h2>
            <p className="muted small">
              Pencereyi kapatınca SitWise tepside çalışmaya devam eder. Tamamen kapatmak için tepsi simgesi → Çıkış.
            </p>
            <label className="row">
              <input
                type="checkbox"
                checked={settings?.autoStart ?? false}
                disabled={!settings?.autoStartSupported}
                onChange={toggleAutoStart}
              />
              Bilgisayar açılınca başlat
              {settings && !settings.autoStartSupported && <span className="muted small"> (bu platformda yok)</span>}
            </label>
          </section>
        </aside>
      </main>
    </div>
  );
}

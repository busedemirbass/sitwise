/**
 * Ana süreç (main) ile arayüz (renderer) arasındaki IPC kanalları ve tipleri.
 * Kanal adları tek yerde durur; iki taraf da buradan içe aktarır.
 */
export const IPC = {
  getSettings: 'settings:get',
  setAutoStart: 'settings:set-auto-start',
  setPaused: 'monitoring:set-paused',
  pausedChanged: 'monitoring:paused-changed',
} as const;

export interface AppSettings {
  autoStart: boolean;
  /** Otomatik başlatma bu platformda destekleniyor mu (Linux'ta değil). */
  autoStartSupported: boolean;
  paused: boolean;
  /** Uygulama oturum açılışında gizli başlatıldı mı. */
  startedHidden: boolean;
  platform: string;
}

/** preload'ın window.sitwise üzerinden açtığı güvenli API. */
export interface SitWiseApi {
  getSettings(): Promise<AppSettings>;
  setAutoStart(enabled: boolean): Promise<AppSettings>;
  setPaused(paused: boolean): Promise<AppSettings>;
  onPausedChanged(listener: (paused: boolean) => void): () => void;
}

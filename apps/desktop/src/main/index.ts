/**
 * SitWise ana süreç (SW-007).
 *
 * - Tek örnek (single instance): ikinci açılış mevcut pencereyi öne getirir.
 * - Pencere kapatılınca uygulama kapanmaz, tepsiye iner; kamera çalışmaya devam eder.
 * - Tepsi menüsü: göster, duraklat/devam, otomatik başlat, çıkış.
 * - Otomatik başlama: oturum açılışında gizli (--hidden) başlar.
 * - Kamera izni yalnızca kendi arayüzümüze verilir; görüntü hiçbir yere gönderilmez.
 */
import {
  app,
  BrowserWindow,
  ipcMain,
  nativeImage,
  net,
  protocol,
  session,
  systemPreferences,
  Tray,
  Menu,
} from 'electron';
import { join, normalize, sep } from 'node:path';
import { existsSync } from 'node:fs';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { IPC, type AppSettings } from '../shared/ipc';

const here = fileURLToPath(new URL('.', import.meta.url));

const APP_SCHEME = 'app';
const APP_HOST = 'sitwise';
const HIDDEN_FLAG = '--hidden';
const isDev = !app.isPackaged && Boolean(process.env['ELECTRON_RENDERER_URL']);
const autoStartSupported = process.platform === 'win32' || process.platform === 'darwin';

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
let isQuitting = false;
let paused = false;
const startedHidden =
  process.argv.includes(HIDDEN_FLAG) || (process.platform === 'darwin' && app.getLoginItemSettings().wasOpenedAtLogin);

// Üretimde arayüzü file:// yerine app:// ile sunuyoruz: MediaPipe wasm ve model
// dosyalarını fetch() ile yükler ve Chromium file:// üzerinde fetch'e izin vermez.
protocol.registerSchemesAsPrivileged([
  { scheme: APP_SCHEME, privileges: { standard: true, secure: true, supportFetchAPI: true, stream: true } },
]);

if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on('second-instance', () => showWindow());
  app
    .whenReady()
    .then(onReady)
    .catch((err) => {
      console.error('[main] başlatma hatası', err);
      app.quit();
    });
}

async function onReady(): Promise<void> {
  if (!isDev) registerAppProtocol();
  setupPermissions();
  registerIpc();

  if (process.platform === 'darwin') {
    // macOS kamera iznini sistem düzeyinde ister; reddedilirse arayüz hata gösterir.
    await systemPreferences.askForMediaAccess('camera').catch(() => false);
    app.dock?.hide();
  }

  createWindow();
  createTray();
}

function rendererDir(): string {
  return join(here, '../renderer');
}

function registerAppProtocol(): void {
  const root = rendererDir();
  protocol.handle(APP_SCHEME, (request) => {
    const url = new URL(request.url);
    const relative = decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname);
    const filePath = normalize(join(root, relative));
    // Kök dizinin dışına çıkmaya çalışan istekleri reddet.
    if (filePath !== root && !filePath.startsWith(root + sep)) {
      return new Response('Not found', { status: 404 });
    }
    if (!existsSync(filePath)) return new Response('Not found', { status: 404 });
    return net.fetch(pathToFileURL(filePath).toString());
  });
}

function isOwnOrigin(origin: string): boolean {
  if (isDev) return origin.startsWith(process.env['ELECTRON_RENDERER_URL'] ?? '\0');
  return origin.startsWith(`${APP_SCHEME}://${APP_HOST}`);
}

function setupPermissions(): void {
  const ses = session.defaultSession;
  // Yalnızca kamera (media) izni, yalnızca kendi arayüzümüze.
  ses.setPermissionRequestHandler((webContents, permission, callback, details) => {
    const origin = details.requestingUrl || webContents.getURL();
    const wantsOnlyVideo =
      permission === 'media' && !(details as { mediaTypes?: string[] }).mediaTypes?.includes('audio');
    callback(wantsOnlyVideo && isOwnOrigin(origin));
  });
  ses.setPermissionCheckHandler((_wc, permission, requestingOrigin) => {
    return permission === 'media' && isOwnOrigin(requestingOrigin);
  });
}

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 760,
    minWidth: 800,
    minHeight: 560,
    show: false,
    title: 'SitWise',
    autoHideMenuBar: true,
    icon: trayImage(),
    webPreferences: {
      preload: join(here, '../preload/index.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      // Pencere gizliyken de zamanlayıcılar ve kamera kısılmadan çalışsın.
      backgroundThrottling: false,
    },
  });

  mainWindow.once('ready-to-show', () => {
    if (!startedHidden) mainWindow?.show();
  });

  // Kapat = tepsiye in. Gerçek çıkış yalnızca tepsi menüsünden.
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow?.hide();
    }
  });

  // Dış bağlantılar uygulama içinde açılmasın.
  mainWindow.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!isOwnOrigin(url)) event.preventDefault();
  });

  if (isDev) {
    void mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL']!);
  } else {
    void mainWindow.loadURL(`${APP_SCHEME}://${APP_HOST}/index.html`);
  }
}

function showWindow(): void {
  if (!mainWindow) return;
  if (mainWindow.isMinimized()) mainWindow.restore();
  mainWindow.show();
  mainWindow.focus();
}

function trayImage(): Electron.NativeImage {
  // Paketlenmiş uygulamada resources/ klasörü extraResources ile kopyalanır.
  const base = app.isPackaged ? process.resourcesPath : join(here, '../../resources');
  const file = process.platform === 'win32' ? 'tray.ico' : 'tray.png';
  const img = nativeImage.createFromPath(join(base, file));
  return img.isEmpty() ? nativeImage.createFromPath(join(base, 'tray.png')) : img;
}

function createTray(): void {
  const img = trayImage();
  tray = new Tray(process.platform === 'darwin' ? img.resize({ width: 16, height: 16 }) : img);
  tray.setToolTip('SitWise');
  tray.on('click', () => showWindow());
  refreshTrayMenu();
}

function refreshTrayMenu(): void {
  if (!tray) return;
  const settings = currentSettings();
  tray.setToolTip(paused ? 'SitWise — duraklatıldı' : 'SitWise — izleniyor');
  tray.setContextMenu(
    Menu.buildFromTemplate([
      { label: 'SitWise’ı aç', click: () => showWindow() },
      { type: 'separator' },
      {
        label: paused ? 'İzlemeye devam et' : 'İzlemeyi duraklat',
        click: () => setPaused(!paused),
      },
      {
        label: 'Bilgisayar açılınca başlat',
        type: 'checkbox',
        checked: settings.autoStart,
        enabled: settings.autoStartSupported,
        click: (item) => setAutoStart(item.checked),
      },
      { type: 'separator' },
      {
        label: 'Çıkış',
        click: () => {
          isQuitting = true;
          app.quit();
        },
      },
    ]),
  );
}

function currentSettings(): AppSettings {
  return {
    autoStart: autoStartSupported && app.getLoginItemSettings().openAtLogin,
    autoStartSupported,
    paused,
    startedHidden,
    platform: process.platform,
  };
}

function setAutoStart(enabled: boolean): AppSettings {
  if (autoStartSupported) {
    app.setLoginItemSettings({
      openAtLogin: enabled,
      // Windows: --hidden ile başlar. macOS: wasOpenedAtLogin ile anlaşılır.
      args: [HIDDEN_FLAG],
    });
  }
  refreshTrayMenu();
  return currentSettings();
}

function setPaused(value: boolean): AppSettings {
  paused = value;
  mainWindow?.webContents.send(IPC.pausedChanged, paused);
  refreshTrayMenu();
  return currentSettings();
}

function registerIpc(): void {
  ipcMain.handle(IPC.getSettings, () => currentSettings());
  ipcMain.handle(IPC.setAutoStart, (_e, enabled: unknown) => setAutoStart(enabled === true));
  ipcMain.handle(IPC.setPaused, (_e, value: unknown) => setPaused(value === true));
}

app.on('before-quit', () => {
  isQuitting = true;
});

// Tüm pencereler gizli olsa bile uygulama tepside yaşamaya devam eder.
app.on('window-all-closed', () => {
  /* bilerek boş: çıkış yalnızca tepsiden */
});

app.on('activate', () => showWindow());

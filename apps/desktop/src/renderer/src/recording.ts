/** About five rows a second while a command is on screen. */
export const SAMPLE_INTERVAL_MS = 200;

/**
 * Feature names from docs/ml/features.md.
 * neckRatio, shoulderTilt and distanceCm are computed on this branch.
 * The others stay empty until their own cards are on main. This file does not add a formula.
 */
export const FEATURE_COLUMNS = [
  'neckRatio',
  'shoulderTilt',
  'distanceCm',
  'noseShoulderDrop',
  'earShoulderDrop',
  'headPitch',
  'EAR',
  'blinksPerMinute',
  'PERCLOS',
  'MAR',
  'headDrop',
] as const;

const CSV_HEADER = [
  'person_code',
  'session',
  't_s',
  ...FEATURE_COLUMNS,
  'label',
  'distance_cm',
  'camera',
  'glasses',
  'light',
];

export type SessionMeta = {
  personCode: string;
  session: string;
  camera: 'laptop' | 'harici';
  glasses: 'var' | 'yok';
  light: 'iyi' | 'zayif';
};

export type RecordingStep = {
  prompt: string;
  durationMs: number;
  label: string;
  /** Ruler distance. Filled only while the person sits at 40, 60 or 80 cm. */
  rulerCm: number | null;
};

export type ComputedFeatures = {
  neckRatio: number | null;
  shoulderTilt: number | null;
  distanceCm: number | null;
};

export type RecordingRow = {
  tSeconds: number;
  features: ComputedFeatures;
  label: string;
  rulerCm: number | null;
};

/** The command script. The durations add up to 7 minutes 35 seconds. */
export const RECORDING_STEPS: readonly RecordingStep[] = [
  { prompt: 'Dik otur ve ekrana bak.', durationMs: 5_000, label: 'kalibrasyon', rulerCm: null },
  { prompt: 'Dik otur. Normal yaz ve oku.', durationMs: 60_000, label: 'dik', rulerCm: null },
  { prompt: 'Başını öne eğ.', durationMs: 45_000, label: 'one_egik', rulerCm: null },
  { prompt: 'Kambur otur, omuzlarını düşür.', durationMs: 45_000, label: 'kambur', rulerCm: null },
  { prompt: 'Sağa yasıl.', durationMs: 30_000, label: 'yana_yatik', rulerCm: null },
  { prompt: 'Sola yasıl.', durationMs: 30_000, label: 'yana_yatik', rulerCm: null },
  { prompt: 'Cetvelle ekrana 40 cm otur.', durationMs: 20_000, label: 'mesafe_cm', rulerCm: 40 },
  { prompt: 'Cetvelle ekrana 60 cm otur.', durationMs: 20_000, label: 'mesafe_cm', rulerCm: 60 },
  { prompt: 'Cetvelle ekrana 80 cm otur.', durationMs: 20_000, label: 'mesafe_cm', rulerCm: 80 },
  { prompt: 'Serbest çalış. Komut yok.', durationMs: 180_000, label: 'serbest', rulerCm: null },
];

export function sessionDurationMs(): number {
  return RECORDING_STEPS.reduce((sum, step) => sum + step.durationMs, 0);
}

export function stepAt(elapsedMs: number): { index: number; step: RecordingStep; done: boolean } {
  let cursor = 0;
  for (let index = 0; index < RECORDING_STEPS.length; index += 1) {
    const step = RECORDING_STEPS[index];
    if (elapsedMs < cursor + step.durationMs) return { index, step, done: false };
    cursor += step.durationMs;
  }
  const last = RECORDING_STEPS.length - 1;
  return { index: last, step: RECORDING_STEPS[last], done: true };
}

export function secondsLeftInStep(elapsedMs: number): number {
  let cursor = 0;
  for (const step of RECORDING_STEPS) {
    const end = cursor + step.durationMs;
    if (elapsedMs < end) return Math.max(0, Math.ceil((end - elapsedMs) / 1000));
    cursor = end;
  }
  return 0;
}

export function recordingFilename(meta: SessionMeta, day: string): string {
  return `${meta.personCode}_${meta.session}_${day}.csv`;
}

export function localDay(now: Date): string {
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
}

function cell(value: number | null, digits: number): string {
  if (value == null || !Number.isFinite(value)) return '';
  return value.toFixed(digits);
}

function csvCell(value: string): string {
  if (/[",\n\r]/.test(value)) return `"${value.replaceAll('"', '""')}"`;
  return value;
}

/** One CSV row. Uncomputed features and the ruler column are empty, never a made-up zero. */
export function rowCells(meta: SessionMeta, row: RecordingRow): string[] {
  return [
    meta.personCode,
    meta.session,
    row.tSeconds.toFixed(1),
    cell(row.features.neckRatio, 4),
    cell(row.features.shoulderTilt, 4),
    cell(row.features.distanceCm, 1),
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    row.label,
    row.rulerCm == null ? '' : String(row.rulerCm),
    meta.camera,
    meta.glasses,
    meta.light,
  ];
}

export function toCsv(meta: SessionMeta, rows: readonly RecordingRow[]): string {
  const lines = [CSV_HEADER.join(',')];
  for (const row of rows) lines.push(rowCells(meta, row).map(csvCell).join(','));
  return `${lines.join('\n')}\n`;
}

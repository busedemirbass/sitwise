/** One summary row about every 10 seconds. Camera frames are never stored here. */
export const SUMMARY_WINDOW_MS = 10_000;

const MAX_BATCH = 500;

export type FrameReading = {
  atMs: number;
  neckRatio: number;
  shoulderTilt: number;
  distanceCm: number;
  /**
   * Blinks in the last minute from SW-026.
   * Null means the counter was not running. A measured zero stays zero.
   */
  blinksPerMin: number | null;
};

/** One row of the data contract. `blinks_per_min` stays null when it was not measured. */
export type MetricSample = {
  ts: string;
  neck_ratio: number;
  shoulder_tilt: number;
  distance_cm: number;
  blinks_per_min: number | null;
  state: 'ok' | 'warn';
};

export type MetricsBuffer = {
  readings: FrameReading[];
  pending: MetricSample[];
  windowStartMs: number | null;
};

export function createMetricsBuffer(): MetricsBuffer {
  return { readings: [], pending: [], windowStartMs: null };
}

function mean(values: readonly number[]): number {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function round(value: number, digits: number): number {
  return Number(value.toFixed(digits));
}

function summarize(readings: readonly FrameReading[], endMs: number): MetricSample | null {
  if (readings.length === 0) return null;
  const neck = mean(readings.map((reading) => reading.neckRatio));
  const shoulder = mean(readings.map((reading) => reading.shoulderTilt));
  const distance = mean(readings.map((reading) => reading.distanceCm));
  if (neck < 0 || neck > 2 || shoulder < -90 || shoulder > 90 || distance < 10 || distance > 200) return null;
  const blinks = [...readings].reverse().find((reading) => reading.blinksPerMin != null)?.blinksPerMin ?? null;
  if (blinks != null && (!Number.isInteger(blinks) || blinks < 0 || blinks > 60)) return null;
  return {
    ts: new Date(endMs).toISOString(),
    neck_ratio: round(neck, 4),
    shoulder_tilt: round(shoulder, 4),
    distance_cm: round(distance, 1),
    blinks_per_min: blinks,
    state: 'ok',
  };
}

/** Adds one live reading. A finished 10-second window becomes one queued row. */
export function addReading(buffer: MetricsBuffer, reading: FrameReading): MetricsBuffer {
  const windowStartMs = buffer.windowStartMs ?? reading.atMs;
  const readings = [...buffer.readings, reading];
  if (reading.atMs - windowStartMs < SUMMARY_WINDOW_MS) {
    return { ...buffer, readings, windowStartMs };
  }
  const sample = summarize(readings, reading.atMs);
  return {
    readings: [],
    pending: sample ? [...buffer.pending, sample] : buffer.pending,
    windowStartMs: reading.atMs,
  };
}

/** Drops an unfinished window. Rows already queued stay. */
export function discardOpenWindow(buffer: MetricsBuffer): MetricsBuffer {
  return { ...buffer, readings: [], windowStartMs: null };
}

export function nextBatch(buffer: MetricsBuffer): MetricSample[] {
  return buffer.pending.filter((sample) => sample.blinks_per_min != null).slice(0, MAX_BATCH);
}

/** Removes the samples the server accepted. Rows that were not in the batch stay. */
export function dropAccepted(buffer: MetricsBuffer, batch: readonly MetricSample[], accepted: number): MetricsBuffer {
  if (accepted <= 0) return buffer;
  const remove = new Set(batch.slice(0, accepted));
  return { ...buffer, pending: buffer.pending.filter((sample) => !remove.has(sample)) };
}

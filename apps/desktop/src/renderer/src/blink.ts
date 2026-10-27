import type { LandmarkPoint } from './posture';

/**
 * Soukupová and Čech, 2016. A blink is an EAR drop below this value
 * and a rise back above it. SW-027 will replace this with the personal baseline.
 */
export const EAR_BLINK_THRESHOLD = 0.2;

const BLINK_WINDOW_MS = 60_000;

/** p1 outer, p2 upper, p3 upper-inner, p4 inner, p5 lower-inner, p6 lower. */
const LEFT_EYE = [33, 160, 158, 133, 153, 144] as const;
const RIGHT_EYE = [362, 385, 387, 263, 373, 380] as const;

export type BlinkMemory = {
  closed: boolean;
  eventsMs: number[];
};

export const emptyBlinkMemory: BlinkMemory = { closed: false, eventsMs: [] };

function distance(a: LandmarkPoint, b: LandmarkPoint): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function earOfEye(landmarks: LandmarkPoint[], indices: readonly number[]): number | null {
  const points = indices.map((index) => landmarks[index]);
  if (points.some((point) => point == null)) return null;
  const [p1, p2, p3, p4, p5, p6] = points as [
    LandmarkPoint,
    LandmarkPoint,
    LandmarkPoint,
    LandmarkPoint,
    LandmarkPoint,
    LandmarkPoint,
  ];
  const horizontal = distance(p1, p4);
  if (horizontal < 1e-4) return null;
  return (distance(p2, p6) + distance(p3, p5)) / (2 * horizontal);
}

/** Mean EAR of the eyes that have all six points. Null when both eyes are missing. */
export function earFromFace(landmarks: LandmarkPoint[] | undefined): number | null {
  if (!landmarks) return null;
  const ears = [LEFT_EYE, RIGHT_EYE]
    .map((indices) => earOfEye(landmarks, indices))
    .filter((ear): ear is number => ear != null);
  if (ears.length === 0) return null;
  return ears.reduce((sum, ear) => sum + ear, 0) / ears.length;
}

/**
 * Updates the blink memory for one frame.
 * A blink is recorded when the eye was closed and EAR rises to the threshold or above.
 * A missing face keeps the closed flag and does not add a blink.
 */
export function observeBlink(memory: BlinkMemory, ear: number | null, nowMs: number): BlinkMemory {
  const eventsMs = memory.eventsMs.filter((at) => nowMs - at <= BLINK_WINDOW_MS);
  if (ear == null) return { closed: memory.closed, eventsMs };
  const closed = ear < EAR_BLINK_THRESHOLD;
  const opened = memory.closed && !closed;
  return {
    closed,
    eventsMs: opened ? [...eventsMs, nowMs] : eventsMs,
  };
}

export function blinksInLastMinute(memory: BlinkMemory): number {
  return memory.eventsMs.length;
}

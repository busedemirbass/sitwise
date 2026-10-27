/** A 2D image point. x and y are normalized to 0–1. y grows downward. */
export type LandmarkPoint = {
  x: number;
  y: number;
  visibility?: number;
};

export type PostureMetrics = {
  neckRatio: number | null;
  shoulderTilt: number | null;
  noseShoulderDrop: number | null;
};

const NOSE = 0;
const LEFT_SHOULDER = 11;
const RIGHT_SHOULDER = 12;
const MIN_VISIBILITY = 0.5;

const empty: PostureMetrics = { neckRatio: null, shoulderTilt: null, noseShoulderDrop: null };

function visible(point: LandmarkPoint | undefined): point is LandmarkPoint {
  return point != null && (point.visibility == null || point.visibility >= MIN_VISIBILITY);
}

/**
 * SW-018: ratio-based posture from a front camera.
 * neckRatio is how far the nose sits from the shoulder midpoint, divided by shoulder width.
 * shoulderTilt is the shoulder height difference, divided by the same width. Near 0 means level.
 * noseShoulderDrop is the vertical gap from the shoulders up to the nose, divided by the same width.
 * y grows downward, so a slouch shrinks this gap.
 */
export function postureFromLandmarks(landmarks: LandmarkPoint[] | undefined): PostureMetrics {
  if (!landmarks || landmarks.length <= RIGHT_SHOULDER) return empty;

  const nose = landmarks[NOSE];
  const left = landmarks[LEFT_SHOULDER];
  const right = landmarks[RIGHT_SHOULDER];
  if (!visible(nose) || !visible(left) || !visible(right)) return empty;

  const shoulderWidth = Math.hypot(left.x - right.x, left.y - right.y);
  if (shoulderWidth < 1e-4) return empty;

  const midX = (left.x + right.x) / 2;
  const midY = (left.y + right.y) / 2;
  return {
    neckRatio: Math.abs(nose.x - midX) / shoulderWidth,
    shoulderTilt: (left.y - right.y) / shoulderWidth,
    noseShoulderDrop: (midY - nose.y) / shoulderWidth,
  };
}

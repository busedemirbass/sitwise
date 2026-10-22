import type { LandmarkPoint } from './posture';

/** Average adult iris diameter, in millimetres. */
const IRIS_DIAMETER_MM = 11.7;

/**
 * Assumed horizontal field of view of a laptop webcam, in degrees.
 * Sit 60 cm from the camera with a ruler: if the card does not read about 60,
 * change this number and check again.
 */
const HORIZONTAL_FOV_DEG = 60;

/** Face Landmarker iris edges: left eye (left, right), right eye (left, right). */
const LEFT_IRIS_EDGES = [471, 469] as const;
const RIGHT_IRIS_EDGES = [476, 474] as const;

function edgeDistancePx(a: LandmarkPoint, b: LandmarkPoint, width: number, height: number): number {
  const dx = (a.x - b.x) * width;
  const dy = (a.y - b.y) * height;
  return Math.hypot(dx, dy);
}

/**
 * SW-019: screen distance in centimetres from the iris size.
 * A near face makes a wide iris, so the result gets smaller.
 * Returns null when the iris is not visible.
 */
export function distanceCmFromFace(
  landmarks: LandmarkPoint[] | undefined,
  videoWidth: number,
  videoHeight: number,
): number | null {
  if (!landmarks || videoWidth < 2 || videoHeight < 2) return null;

  const diameters = [LEFT_IRIS_EDGES, RIGHT_IRIS_EDGES]
    .map(([left, right]) => {
      const a = landmarks[left];
      const b = landmarks[right];
      if (!a || !b) return null;
      const px = edgeDistancePx(a, b, videoWidth, videoHeight);
      return px >= 2 ? px : null;
    })
    .filter((px): px is number => px != null);

  if (diameters.length === 0) return null;

  const irisPx = diameters.reduce((sum, px) => sum + px, 0) / diameters.length;
  const fovRad = (HORIZONTAL_FOV_DEG * Math.PI) / 180;
  const focalPx = videoWidth / 2 / Math.tan(fovRad / 2);
  const distanceMm = (IRIS_DIAMETER_MM * focalPx) / irisPx;
  return distanceMm / 10;
}

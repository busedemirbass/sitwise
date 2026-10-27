import { distanceCmFromFace } from './distance';
import { postureFromLandmarks, type LandmarkPoint, type PostureMetrics } from './posture';

/** One frame of the numbers the rest of the app reads. */
export type FrameFeatures = PostureMetrics & {
  distanceCm: number | null;
};

/**
 * SW-025: posture and distance from a single call.
 * SW-027 reads noseShoulderDrop from the same posture result to judge an upright calibration.
 * The formulas stay in posture.ts and distance.ts.
 */
export function featuresFromFrame(
  poseLandmarks: LandmarkPoint[] | undefined,
  faceLandmarks: LandmarkPoint[] | undefined,
  videoWidth: number,
  videoHeight: number,
): FrameFeatures {
  const posture = postureFromLandmarks(poseLandmarks);
  return {
    neckRatio: posture.neckRatio,
    shoulderTilt: posture.shoulderTilt,
    noseShoulderDrop: posture.noseShoulderDrop,
    distanceCm: distanceCmFromFace(faceLandmarks, videoWidth, videoHeight),
  };
}

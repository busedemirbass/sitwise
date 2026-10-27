/** Five upright seconds. The profile is the mean and spread of those samples. */
export const CALIBRATION_MS = 5_000;

/** About one second of readable frames inside the five-second sit. */
export const MIN_CALIBRATION_SAMPLES = 30;

/**
 * Nose-to-shoulder height divided by shoulder width.
 * An upright head keeps the nose well above the shoulders, so the ratio stays larger.
 * A slouch drops the nose toward the shoulders and the ratio shrinks.
 *
 * SitWise cutoff from the 27 Oct 2026 webcam check, not a published constant.
 * Upright sit was about 0.74. A deep slouch fell to 0.18. A milder slouch stayed above 0.45
 * and was accepted, so the line sits just under the upright sit.
 */
export const MIN_UPRIGHT_NOSE_SHOULDER_DROP = 0.65;

const MIN_DISTANCE_CM = 10;
const MAX_DISTANCE_CM = 200;

export type CalibrationSample = {
  neckRatio: number;
  shoulderTilt: number;
  distanceCm: number;
  noseShoulderDrop: number;
};

/** Matches the server calibration profile, plus the upright head height used to reject a slouch. */
export type CalibrationProfile = {
  neckMean: number;
  neckStd: number;
  shoulderMean: number;
  shoulderStd: number;
  distanceCm: number;
  noseShoulderDropMean: number;
};

export type CalibrationRejection = 'slouch' | 'incomplete';

export type CalibrationOutcome =
  { ok: true; profile: CalibrationProfile } | { ok: false; reason: CalibrationRejection };

function mean(values: readonly number[]): number {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function sampleStd(values: readonly number[], avg: number): number {
  if (values.length < 2) return 0;
  const squareSum = values.reduce((sum, value) => sum + (value - avg) ** 2, 0);
  return Math.sqrt(squareSum / (values.length - 1));
}

/**
 * Builds the personal upright profile, or rejects the sit.
 * A slouch is a low nose-to-shoulder height. Too few readable frames, or a distance
 * outside the server's 10–200 cm range, leaves the previous profile untouched.
 */
export function finishCalibration(samples: readonly CalibrationSample[]): CalibrationOutcome {
  if (samples.length < MIN_CALIBRATION_SAMPLES) return { ok: false, reason: 'incomplete' };

  const distanceCm = mean(samples.map((sample) => sample.distanceCm));
  const noseShoulderDropMean = mean(samples.map((sample) => sample.noseShoulderDrop));
  if (noseShoulderDropMean < MIN_UPRIGHT_NOSE_SHOULDER_DROP) return { ok: false, reason: 'slouch' };
  if (distanceCm < MIN_DISTANCE_CM || distanceCm > MAX_DISTANCE_CM) return { ok: false, reason: 'incomplete' };

  const neck = samples.map((sample) => sample.neckRatio);
  const shoulder = samples.map((sample) => sample.shoulderTilt);
  const neckMean = mean(neck);
  const shoulderMean = mean(shoulder);
  return {
    ok: true,
    profile: {
      neckMean,
      neckStd: sampleStd(neck, neckMean),
      shoulderMean,
      shoulderStd: sampleStd(shoulder, shoulderMean),
      distanceCm,
      noseShoulderDropMean,
    },
  };
}

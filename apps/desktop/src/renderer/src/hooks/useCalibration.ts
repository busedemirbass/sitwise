import { useEffect, useRef, useState } from 'react';
import {
  CALIBRATION_MS,
  finishCalibration,
  type CalibrationProfile,
  type CalibrationRejection,
  type CalibrationSample,
} from '../calibration';

export type CalibrationPhase = 'idle' | 'running' | 'saved' | 'rejected';

/**
 * Collects live samples for five seconds, then keeps the profile only when the sit is upright.
 * A rejected sit does not replace a profile that was already saved.
 */
export function useCalibration(live: boolean, sample: CalibrationSample | null, frameSeq: number) {
  const samplesRef = useRef<CalibrationSample[]>([]);
  const sampleRef = useRef(sample);
  const timerRef = useRef<number | null>(null);
  const [phase, setPhase] = useState<CalibrationPhase>('idle');
  const [profile, setProfile] = useState<CalibrationProfile | null>(null);
  const [reason, setReason] = useState<CalibrationRejection | null>(null);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [now, setNow] = useState(0);

  sampleRef.current = sample;

  const stopTimer = () => {
    if (timerRef.current != null) {
      window.clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  useEffect(() => stopTimer, []);

  useEffect(() => {
    if (phase !== 'running') return;
    setNow(performance.now());
    const id = window.setInterval(() => setNow(performance.now()), 200);
    return () => window.clearInterval(id);
  }, [phase]);

  useEffect(() => {
    if (phase !== 'running' || !live) return;
    const current = sampleRef.current;
    if (current) samplesRef.current.push(current);
  }, [phase, live, frameSeq]);

  const start = () => {
    stopTimer();
    samplesRef.current = [];
    setReason(null);
    setPhase('running');
    const started = performance.now();
    setStartedAt(started);
    setNow(started);
    timerRef.current = window.setTimeout(() => {
      timerRef.current = null;
      const outcome = finishCalibration(samplesRef.current);
      samplesRef.current = [];
      setStartedAt(null);
      if (outcome.ok) {
        setProfile(outcome.profile);
        setReason(null);
        setPhase('saved');
      } else {
        setReason(outcome.reason);
        setPhase('rejected');
      }
    }, CALIBRATION_MS);
  };

  const cancel = () => {
    stopTimer();
    samplesRef.current = [];
    setStartedAt(null);
    setReason(null);
    setPhase(profile ? 'saved' : 'idle');
  };

  const elapsed = startedAt == null || phase !== 'running' ? 0 : Math.min(CALIBRATION_MS, Math.max(0, now - startedAt));

  return {
    phase,
    profile,
    reason,
    secondsLeft: phase === 'running' ? Math.ceil((CALIBRATION_MS - elapsed) / 1000) : 0,
    progress: elapsed / CALIBRATION_MS,
    start,
    cancel,
  };
}

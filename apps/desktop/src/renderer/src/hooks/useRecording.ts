import { useEffect, useRef, useState } from 'react';
import {
  RECORDING_STEPS,
  SAMPLE_INTERVAL_MS,
  localDay,
  recordingFilename,
  secondsLeftInStep,
  stepAt,
  toCsv,
  type ComputedFeatures,
  type RecordingRow,
  type SessionMeta,
} from '../recording';

export type RecordingPhase = 'idle' | 'running' | 'saved';

/**
 * Shows one protocol command at a time and keeps about five numeric rows a second.
 * The CSV is written once, at the end. Cancelling writes nothing. No camera frame is included.
 */
export function useRecording(live: boolean, features: ComputedFeatures | null) {
  const featuresRef = useRef(features);
  const rowsRef = useRef<RecordingRow[]>([]);
  const startedRef = useRef<number | null>(null);
  const savingRef = useRef(false);
  const [phase, setPhase] = useState<RecordingPhase>('idle');
  const [personCode, setPersonCode] = useState('P01');
  const [session, setSession] = useState('S01');
  const [camera, setCamera] = useState<SessionMeta['camera']>('laptop');
  const [glasses, setGlasses] = useState<SessionMeta['glasses']>('yok');
  const [light, setLight] = useState<SessionMeta['light']>('iyi');
  const [elapsedMs, setElapsedMs] = useState(0);
  const [savedPath, setSavedPath] = useState<string | null>(null);
  const [rowCount, setRowCount] = useState(0);
  const [note, setNote] = useState('Kayıt bitince tek bir CSV yazılır. Görüntü yazılmaz.');

  featuresRef.current = features;
  const place = stepAt(elapsedMs);

  const meta = (): SessionMeta => ({ personCode: personCode.trim(), session: session.trim(), camera, glasses, light });

  const finishRef = useRef<() => Promise<void>>(async () => {});
  finishRef.current = async () => {
    if (savingRef.current) return;
    savingRef.current = true;
    const rows = rowsRef.current;
    const current = meta();
    const filename = recordingFilename(current, localDay(new Date()));
    try {
      const saved = await window.sitwise.saveRecording(filename, toCsv(current, rows));
      setSavedPath(saved.path);
      setRowCount(rows.length);
      setPhase('saved');
      setNote('Kayıt duruyor. Cetvel adımında 40, 60 ve 80 yazıldı. Dosyada görüntü yok.');
    } catch (err) {
      savingRef.current = false;
      setPhase('idle');
      setNote(err instanceof Error ? err.message : 'Kayıt yazılamadı.');
    }
  };

  useEffect(() => {
    if (phase !== 'running') return;
    const id = window.setInterval(() => {
      const started = startedRef.current;
      if (started == null) return;
      const elapsed = Date.now() - started;
      const current = stepAt(elapsed);
      if (current.done) {
        window.clearInterval(id);
        void finishRef.current();
        return;
      }
      const reading = featuresRef.current;
      rowsRef.current.push({
        tSeconds: elapsed / 1000,
        features: {
          neckRatio: reading?.neckRatio ?? null,
          shoulderTilt: reading?.shoulderTilt ?? null,
          distanceCm: reading?.distanceCm ?? null,
        },
        label: current.step.label,
        rulerCm: current.step.rulerCm,
      });
      setElapsedMs(elapsed);
    }, SAMPLE_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [phase]);

  const start = () => {
    const current = meta();
    if (!/^P\d+$/.test(current.personCode) || !/^S\d+$/.test(current.session)) {
      setNote('Kişi kodu P01, oturum S01 biçiminde olmalı. İsim yazılmaz.');
      return;
    }
    rowsRef.current = [];
    startedRef.current = Date.now();
    savingRef.current = false;
    setSavedPath(null);
    setRowCount(0);
    setElapsedMs(0);
    setPhase('running');
    setNote('Komut ekrandayken satırlar bellekte birikir.');
  };

  const cancel = () => {
    startedRef.current = null;
    rowsRef.current = [];
    savingRef.current = false;
    setElapsedMs(0);
    setPhase('idle');
    setNote('Kayıt iptal edildi. Dosya yazılmadı.');
  };

  const removeSaved = async () => {
    if (!savedPath) return;
    const filename = savedPath.split(/[/\\]/).pop();
    if (!filename) return;
    await window.sitwise.deleteRecording(filename);
    setSavedPath(null);
    setRowCount(0);
    setPhase('idle');
    setNote('Oturum dosyası silindi. Bu kayıt kullanılmayacak.');
  };

  return {
    phase,
    personCode,
    setPersonCode,
    session,
    setSession,
    camera,
    setCamera,
    glasses,
    setGlasses,
    light,
    setLight,
    step: place.step,
    stepNumber: place.index + 1,
    stepCount: RECORDING_STEPS.length,
    secondsLeft: secondsLeftInStep(elapsedMs),
    savedPath,
    rowCount,
    note,
    start,
    cancel,
    removeSaved,
    canStart: live && phase !== 'running',
  };
}

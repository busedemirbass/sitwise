import { useEffect, useRef, useState } from 'react';
import { login, sendMetrics, startSession, DEFAULT_API_BASE } from '../apiClient';
import {
  addReading,
  createMetricsBuffer,
  discardOpenWindow,
  dropAccepted,
  nextBatch,
  type FrameReading,
  type MetricsBuffer,
} from '../metricsBuffer';

export type LiveMetrics = Omit<FrameReading, 'atMs'>;

/**
 * Turns live numbers into 10-second rows and keeps those rows until the server accepts them.
 * A missing network does not delete the queue. The queue holds numbers only.
 */
export function useMetricsUpload(live: boolean, reading: LiveMetrics | null, frameSeq: number) {
  const bufferRef = useRef<MetricsBuffer>(createMetricsBuffer());
  const readingRef = useRef(reading);
  const tokenRef = useRef<string | null>(null);
  const sessionRef = useRef<string | null>(null);
  const baseUrlRef = useRef(DEFAULT_API_BASE);
  const sendingRef = useRef(false);
  const holdRef = useRef(false);
  const [baseUrl, setBaseUrlState] = useState(DEFAULT_API_BASE);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [pending, setPending] = useState(0);
  const [signedIn, setSignedIn] = useState(false);
  const [note, setNote] = useState('Her 10 saniyede bir sayı satırı oluşur. Görüntü gönderilmez.');

  readingRef.current = reading;

  const syncPending = () => setPending(bufferRef.current.pending.length);

  const flushRef = useRef<() => Promise<void>>(async () => {});
  flushRef.current = async () => {
    if (sendingRef.current || holdRef.current) return;
    const batch = nextBatch(bufferRef.current);
    const waiting = bufferRef.current.pending.length;
    if (waiting === 0) return;
    if (batch.length === 0) {
      setNote('Satırlar kuyrukta. Kırpma ölçülmediği için uydurma 0 gönderilmiyor.');
      return;
    }
    const token = tokenRef.current;
    if (!token) {
      setNote(`Giriş yok. ${waiting} satır kuyrukta bekliyor.`);
      return;
    }
    sendingRef.current = true;
    try {
      if (!sessionRef.current) {
        const opened = await startSession(baseUrlRef.current, token);
        if (!opened.ok) {
          if (opened.unauthorized) {
            tokenRef.current = null;
            sessionRef.current = null;
            setSignedIn(false);
          }
          if (!opened.retry) holdRef.current = true;
          setNote(`${opened.message} ${waiting} satır kuyrukta.`);
          return;
        }
        sessionRef.current = opened.id;
      }
      const sent = await sendMetrics(baseUrlRef.current, token, sessionRef.current, batch);
      if (!sent.ok) {
        if (sent.unauthorized) {
          tokenRef.current = null;
          sessionRef.current = null;
          setSignedIn(false);
        }
        if (!sent.retry) holdRef.current = true;
        setNote(`${sent.message} ${bufferRef.current.pending.length} satır kuyrukta.`);
        return;
      }
      bufferRef.current = dropAccepted(bufferRef.current, batch, sent.accepted);
      syncPending();
      setNote(`${sent.accepted} satır sunucuya gitti. Kuyrukta ${bufferRef.current.pending.length} satır var.`);
    } finally {
      sendingRef.current = false;
    }
  };

  useEffect(() => {
    if (!live) {
      bufferRef.current = discardOpenWindow(bufferRef.current);
      return;
    }
    const current = readingRef.current;
    if (!current) return;
    bufferRef.current = addReading(bufferRef.current, { ...current, atMs: Date.now() });
    syncPending();
    if (bufferRef.current.pending.length > 0) void flushRef.current();
  }, [live, frameSeq]);

  useEffect(() => {
    const onOnline = () => void flushRef.current();
    window.addEventListener('online', onOnline);
    const id = window.setInterval(() => void flushRef.current(), 5_000);
    return () => {
      window.removeEventListener('online', onOnline);
      window.clearInterval(id);
    };
  }, []);

  const setBaseUrl = (value: string) => {
    baseUrlRef.current = value;
    setBaseUrlState(value);
  };

  const signIn = async () => {
    holdRef.current = false;
    const result = await login(baseUrlRef.current, email, password);
    setPassword('');
    if (!result.ok) {
      setNote(result.message);
      return;
    }
    tokenRef.current = result.token;
    sessionRef.current = null;
    setSignedIn(true);
    setNote('Giriş yapıldı. Bekleyen satırlar gönderilecek.');
    void flushRef.current();
  };

  return { baseUrl, setBaseUrl, email, setEmail, password, setPassword, pending, signedIn, note, signIn };
}

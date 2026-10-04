import { useEffect, useRef, useState } from 'react';

export type CameraStatus = 'idle' | 'starting' | 'live' | 'denied' | 'error';

/**
 * Webcam akışını açar/kapatır. active=false olduğunda akış tamamen durdurulur
 * (kamera ışığı söner) — duraklatma gerçekten kamerayı kapatır.
 */
export function useCamera(active: boolean) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [status, setStatus] = useState<CameraStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [resolution, setResolution] = useState<string>('');

  useEffect(() => {
    if (!active) {
      setStatus('idle');
      return;
    }
    let stream: MediaStream | null = null;
    let cancelled = false;
    const video = videoRef.current;
    setStatus('starting');
    setError(null);

    navigator.mediaDevices
      .getUserMedia({
        audio: false,
        video: { width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 30 }, facingMode: 'user' },
      })
      .then(async (s) => {
        if (cancelled) {
          s.getTracks().forEach((t) => t.stop());
          return;
        }
        stream = s;
        if (!video) return;
        video.srcObject = s;
        await video.play();
        const settings = s.getVideoTracks()[0]?.getSettings();
        setResolution(
          settings ? `${settings.width}×${settings.height} @ ${Math.round(settings.frameRate ?? 0)} fps` : '',
        );
        setStatus('live');
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const name = err instanceof DOMException ? err.name : '';
        setStatus(name === 'NotAllowedError' ? 'denied' : 'error');
        setError(err instanceof Error ? `${err.name}: ${err.message}` : String(err));
      });

    return () => {
      cancelled = true;
      stream?.getTracks().forEach((t) => t.stop());
      if (video) video.srcObject = null;
    };
  }, [active]);

  return { videoRef, status, error, resolution };
}

import { useEffect, useRef, useState, type RefObject } from 'react';
import { FaceLandmarker, FilesetResolver, PoseLandmarker } from '@mediapipe/tasks-vision';
import { postureFromLandmarks } from '../posture';

const WASM_BASE = 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.0.1/wasm';
const FACE_MODEL =
  'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task';
const POSE_MODEL =
  'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task';

export type MediaPipeState = {
  fps: number;
  inferenceTimeMs: number;
  faceDetected: boolean;
  poseDetected: boolean;
  neckRatio: number | null;
  shoulderTilt: number | null;
  ready: boolean;
  error: string | null;
};

const initialState: MediaPipeState = {
  fps: 0,
  inferenceTimeMs: 0,
  faceDetected: false,
  poseDetected: false,
  neckRatio: null,
  shoulderTilt: null,
  ready: false,
  error: null,
};

/**
 * SW-008: FaceLandmarker + PoseLandmarker (GPU) ile canlı kare ölçümü.
 * Modeller bir kez yüklenir; döngü yalnızca kamera canlıyken döner.
 */
export function useMediaPipe(videoRef: RefObject<HTMLVideoElement | null>, enabled: boolean): MediaPipeState {
  const [state, setState] = useState<MediaPipeState>(initialState);
  const faceRef = useRef<FaceLandmarker | null>(null);
  const poseRef = useRef<PoseLandmarker | null>(null);

  useEffect(() => {
    const created: { face: FaceLandmarker | null; pose: PoseLandmarker | null } = { face: null, pose: null };
    let cancelled = false;

    const load = async () => {
      try {
        const vision = await FilesetResolver.forVisionTasks(WASM_BASE);
        if (cancelled) return;

        const face = await FaceLandmarker.createFromOptions(vision, {
          baseOptions: { modelAssetPath: FACE_MODEL, delegate: 'GPU' },
          runningMode: 'VIDEO',
          numFaces: 1,
        });
        if (cancelled) {
          face.close();
          return;
        }
        created.face = face;

        const pose = await PoseLandmarker.createFromOptions(vision, {
          baseOptions: { modelAssetPath: POSE_MODEL, delegate: 'GPU' },
          runningMode: 'VIDEO',
          numPoses: 1,
        });
        if (cancelled) {
          pose.close();
          return;
        }
        created.pose = pose;

        faceRef.current = face;
        poseRef.current = pose;
        setState((s) => ({ ...s, ready: true, error: null }));
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        console.error('[mediapipe]', message);
        if (!cancelled) setState((s) => ({ ...s, ready: false, error: message }));
      }
    };

    void load();

    return () => {
      cancelled = true;
      created.face?.close();
      created.pose?.close();
      faceRef.current = null;
      poseRef.current = null;
      setState(initialState);
    };
  }, []);

  useEffect(() => {
    const face = faceRef.current;
    const pose = poseRef.current;
    if (!enabled || !face || !pose) return;

    let raf = 0;
    let frames = 0;
    let inferenceSum = 0;
    let windowStart = performance.now();
    let lastTimestamp = -1;

    const tick = () => {
      raf = requestAnimationFrame(tick);
      const video = videoRef.current;
      if (!video) return;

      try {
        let started = performance.now();
        if (started <= lastTimestamp) started = lastTimestamp + 0.001;
        lastTimestamp = started;

        const faceResult = face.detectForVideo(video, started);
        const poseResult = pose.detectForVideo(video, started);
        const elapsed = performance.now() - started;

        frames += 1;
        inferenceSum += elapsed;

        const now = performance.now();
        const posture = postureFromLandmarks(poseResult.landmarks[0]);
        setState((s) => ({
          ...s,
          fps: frames > 0 ? (frames * 1000) / (now - windowStart) : 0,
          inferenceTimeMs: frames > 0 ? inferenceSum / frames : 0,
          faceDetected: faceResult.faceLandmarks.length > 0,
          poseDetected: poseResult.landmarks.length > 0,
          neckRatio: posture.neckRatio,
          shoulderTilt: posture.shoulderTilt,
        }));
        if (now - windowStart >= 1000) {
          frames = 0;
          inferenceSum = 0;
          windowStart = now;
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        console.error('[mediapipe]', message);
        setState((s) => ({ ...s, error: message }));
      }
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [enabled, state.ready, videoRef]);

  return state;
}

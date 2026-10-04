import type { SitWiseApi } from '../shared/ipc';

declare global {
  interface Window {
    sitwise: SitWiseApi;
  }
}

export {};

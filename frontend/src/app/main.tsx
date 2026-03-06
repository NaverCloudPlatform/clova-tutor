/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import './styles/index.css';

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import App from './App.tsx';

async function enableMocking() {
  const searchParams = new URLSearchParams(window.location.search);
  const hasScenario = searchParams.get('scenario') !== null;

  if (import.meta.env.DEV && hasScenario) {
    try {
      const { worker } = await import('~/mocks/browser.ts');
      return worker.start({ onUnhandledRequest: 'bypass' });
    } catch (error) {
      console.error('Failed to import mocks/browser.ts', error);
    }
  }
}

if (typeof global === 'undefined') {
  window.global = window;
}

const root = document.getElementById('root');
if (!root) throw new Error('Root element not found');

enableMocking().then(() => {
  createRoot(root).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
});

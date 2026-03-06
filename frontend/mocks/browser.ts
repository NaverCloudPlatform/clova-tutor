/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { setupWorker } from 'msw/browser';
import { isValidScenario, loadScenarioHandlers } from './handlers/network-log-scenario.handlers';
import { log } from '@/shared/core/log';

export const worker = setupWorker();

const scenarioName = new URLSearchParams(window.location.search).get('scenario');

if (scenarioName && isValidScenario(scenarioName)) {
  log.info(`[MSW] 시나리오 활성화: ${scenarioName}`);

  loadScenarioHandlers(scenarioName)
    .then((handlers) => {
      worker.use(...handlers);
      log.info(`[MSW] 시나리오 핸들러 적용 완료: ${scenarioName}`);
    })
    .catch((error) => {
      log.error(`[MSW] 시나리오 핸들러 로드 실패: ${scenarioName}`, error);
    });
} else if (scenarioName) {
  log.warn(`[MSW] 유효하지 않은 시나리오: ${scenarioName}`);
}

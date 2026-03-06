/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { chromium, test as setup } from '@playwright/test';

const AUTH_FILE = 'playwright/.auth/token.json';

setup('authenticate', async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  const userId = '452395d2-8832-41d5-976f-857e9ad2dcb8';

  await page.goto('/');
  await page.evaluate((id) => {
    localStorage.setItem('userId', id);
  }, userId);
  await page.evaluate(() => {
    localStorage.setItem(
      'react-resizable-panels:/_student/$subject/$chat_id_resizable-panel-group',
      `{"{"minSize":30},study-area-panel":{"expandToSizes":{},"layout":[54.7017255167,45.2982744833]}}`,
    );
  });

  // sidebar_state 쿠키 설정
  await page.context().addCookies([
    {
      name: 'sidebar_state',
      value: 'true',
      domain: 'localhost',
      path: '/',
    },
  ]);

  console.log(`로컬스토리지에 userId가 설정되었습니다: ${userId}`);
  console.log('쿠키 sidebar_state가 true로 설정되었습니다');

  await page.context().storageState({ path: AUTH_FILE });

  await page.close();
  await context.close();
  await browser.close();
});

/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { defineConfig, devices } from '@playwright/test';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

export default defineConfig({
  testDir: './playwright',
  fullyParallel: true,
  retries: 0,
  workers: undefined,
  reporter: [
    ['html', { outputFolder: './playwright/reporters' }],
    ['json', { outputFile: './playwright/reporters/results.json' }],
    [
      require.resolve('@jjades/e2e-autogen/playwright/reporter'),
      {
        outputFile: './playwright/reporters/e2e-autogen-report.json',
      },
    ],
  ],
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on',
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'setup',
      testMatch: '**/auth.setup.ts',
      use: {
        storageState: undefined,
      },
    },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: './playwright/.auth/token.json' },
      testMatch: '**/e2e/**/*.spec.ts',
      dependencies: ['setup'],
    },

    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },

    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },

    /* Test against mobile viewports. */
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },

    /* Test against branded browsers. */
    // {
    //   name: 'Microsoft Edge',
    //   use: { ...devices['Desktop Edge'], channel: 'msedge' },
    // },
    // {
    //   name: 'Google Chrome',
    //   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    // },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'VITE_API_MOCKING=enabled yarn dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
  },
});
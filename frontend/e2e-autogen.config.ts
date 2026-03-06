/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { defineConfig } from "@jjades/e2e-autogen";

export default defineConfig({
  sheetsUrl: "https://docs.google.com/spreadsheets/d/1XLSwVLph3tIQcDUzazokn4ABbX0T-sUteDMe2-Z_oFk/edit?usp=sharing",
  framework: "playwright",
  stubOutputFolder: "./playwright/__generated-stub__",
  jsonReporterFile: "./playwright/reporters/e2e-autogen-report.json",
  credentialsFile: "./playwright/.auth/credentials.json",
  googleSheetColumns: {
    scenarioId: "A",
    scenarioDescription: "B",
    uiPath: "C",
    action: "D",
    expected: "E",
    testId: "F",
    tag: "G",
    comment: "H"
  }
});

/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { InputCodegenConfig } from "swagger-client-autogen";

export const config: Partial<InputCodegenConfig> = {
  uri: "http://localhost:8000/api/v1/openapi.json",
  username: 'edu',
  password: 'edu1234'
};
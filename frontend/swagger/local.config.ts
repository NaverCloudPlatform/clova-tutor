/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { InputCodegenConfig } from 'swagger-client-autogen';

export const config: InputCodegenConfig = {
  uri: "swagger/be.yml",
  createSchema: true,
  createQueryHook: false,
  customOutput: {
    aliasInfo: {
      aliasMap: {
        "@": "src",
      },
      aliasMapDepth: 2,
    },
    pathInfo: {
      api: "src/entities/{moduleName}/__generated__/api/index.ts",
      apiInstance: "src/entities/{moduleName}/__generated__/api/instance.ts",
      queries: "src/entities/{moduleName}/__generated__/api/queries.ts",
      mutations: "src/entities/{moduleName}/__generated__/api/mutations.ts",
      dto: "src/shared/api/__generated__/dto.ts",
      schema: "src/shared/api/__generated__/schema.ts",
      apiUtils: "src/shared/api/__generated__/utils.ts",
      typeGuards: "src/shared/api/__generated__/type-guards.ts",
      streamUtils: "src/shared/api/__generated__/stream-utils.ts",
      globalMutationEffectType: "src/shared/api/__generated__/global-mutation-effect.type.ts",
    }
  }
};
# API 클라이언트 자동 생성

Swagger 스펙으로부터 TypeScript API 클라이언트 코드를 자동으로 생성하는 가이드입니다.

## 목차

- [개요](#개요)
- [사용법](#사용법)
- [생성된 파일 구조](#생성된-파일-구조)
- [사용 예시](#사용-예시)
- [워크플로우](#워크플로우)
- [참고 자료](#참고-자료)

## 개요

`swagger-client-autogen` 도구를 사용하여 백엔드 API의 Swagger/OpenAPI 스펙으로부터 타입 안전한 API 클라이언트를 자동 생성합니다.

### 장점

- **타입 안정성**: TypeScript 타입이 자동 생성
- **동기화**: 백엔드 API 변경사항 자동 반영
- **생산성**: 수동으로 API 함수 작성 불필요
- **에러 감소**: 컴파일 타임에 API 호출 오류 발견
- **Query Key 관리**: TanStack Query key 자동 생성
- **통합 관리**: Global mutation effect를 통한 invalidate 통합 관리 및 타입 추론

## 사용법

```bash
# API 클라이언트 생성
yarn api:generate
```

이 명령어는 다음 작업을 수행합니다:
1. [swagger.config.ts](../swagger.config.ts) 기반으로 코드 생성
2. Biome으로 포맷팅

## 생성된 파일 구조

### 공통 파일 (src/shared/api/\_\_generated\_\_)

```
src/shared/api/__generated__/
├── dto.ts                          # 모든 DTO 타입 정의
├── schema.ts                       # Zod 스키마
├── utils.ts                        # 유틸리티 함수
├── stream-utils.ts                 # 스트리밍 유틸리티
├── type-guards.ts                  # 타입 가드
└── global-mutation-effect.type.ts  # 전역 뮤테이션 핸들러 설정 타입
```

### 엔티티별 API 파일 (src/entities/\*/\_\_generated\_\_/api)

```
src/entities/
├── chats/__generated__/api/
│   ├── index.ts        # 엔티티에 대한 API 엔드포인트별 요청 함수 클래스
│   ├── instance.ts     # 엔티티 클래스의 인스턴스, ky 인스턴스가 이곳에서 주입됨
│   ├── queries.ts      # Query options
│   └── mutations.ts    # Mutation hooks (useMutation)
├── users/__generated__/api/
│   ├── index.ts
│   ├── instance.ts
│   ├── queries.ts
│   └── mutations.ts
├── problems/__generated__/api/
│   ├── index.ts
│   ├── instance.ts
│   ├── queries.ts
│   └── mutations.ts
└── ...
```

## 사용 예시

### Query 사용

채팅 메시지 목록을 조회하는 예시:

```typescript
import { useSuspenseQuery } from '@tanstack/react-query';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';

export const useGetChatMessages = (chatId: number) => {
  return useSuspenseQuery({
    ...chatsQueries.getChatsByChatIdMessages({ chatId }),
    staleTime: Number.POSITIVE_INFINITY,
  });
};
```

### Mutation 사용

채팅 제목을 수정하는 예시 (Optimistic Update 포함):

```typescript
import { useQueryClient } from '@tanstack/react-query';
import { usePatchChatsByChatIdMutation } from '@/entities/chats/__generated__/api/mutations';
import { CHATS_QUERY_KEY } from '@/entities/chats/__generated__/api/queries';
import type { ChatResponseDto } from '@/shared/api/__generated__/dto';

export function ChatTitleEdit({ chatId, initialTitle }: Props) {
  const queryClient = useQueryClient();

  const { mutate: updateChatTitle } = usePatchChatsByChatIdMutation({
    onMutate: async (variables) => {
      queryClient.setQueryData(chatsQueries.getChatsByChatId({ chatId }).queryKey, (old) =>
        old ? { ...old, title: variables.payload.title } : old,
      );
    },
    onError: () => {
      queryClient.invalidateQueries({
        queryKey: CHATS_QUERY_KEY.GET_CHATS(),
      });
    },
  });

  const handleUpdate = (newTitle: string) => {
    updateChatTitle({
      chatId,
      payload: { title: newTitle },
    });
  };

  // ...
}
```

### Global Mutation Effects 사용

특정 Mutation 성공 시 자동으로 관련 Query를 무효화하는 전역 효과를 정의할 수 있습니다.

#### 1. Global Mutation Effects 정의

[src/shared/api/global-mutation-effects.ts](../src/shared/api/global-mutation-effects.ts):

```typescript
import type { QueryClient } from '@tanstack/react-query';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import type { TChatsGlobalMutationEffects } from './__generated__/global-mutation-effect.type';

export const globalMutationEffects = (queryClient: QueryClient) => ({
  ...chatGlobalMutationEffects(queryClient),
});

function chatGlobalMutationEffects(queryClient: QueryClient): TChatsGlobalMutationEffects {
  return {
    // 문제 제출 시 관련 Query 무효화
    postChatsByChatIdProblemsByProblemIdSubmit: {
      onSuccess: {
        invalidate: (_data, variables) => {
          // 문제 목록 무효화
          queryClient.invalidateQueries({
            queryKey: chatsQueries.getChatsByChatIdProblems({ chatId: variables.chatId }).queryKey,
            exact: true,
          });

          // 특정 문제 상세 무효화
          queryClient.invalidateQueries({
            queryKey: chatsQueries.getChatsByChatIdProblemsByProblemId({
              chatId: variables.chatId,
              problemId: variables.problemId,
            }).queryKey,
            exact: true,
          });
        },
      },
    },
  };
}
```

#### 2. QueryClient에서 자동 실행

[src/app/provider/tanstack-query.tsx](../src/app/provider/tanstack-query.tsx):

```typescript
import { MutationCache, QueryClient } from '@tanstack/react-query';
import { globalMutationEffects, isGlobalMutationEffectKey } from '@/shared/api/global-mutation-effects';

export const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onSuccess: async (_data, _variables, _context, mutation) => {
      const mutationFnName = mutation.options.meta?.mutationFnName;

      // Global Mutation Effect가 등록된 경우 자동 실행
      if (isGlobalMutationEffectKey(mutationFnName)) {
        const invalidate = globalMutationEffects(queryClient)[mutationFnName]?.onSuccess.invalidate;

        if (invalidate) {
          invalidate(_data, _variables, _context, mutation);
          return; // 전역 효과 실행 후 엔티티 단위 invalidate 스킵
        }
      }

      // 기본 동작: 엔티티 단위 invalidate
      if (!mutationKey) return;
      await queryClient.invalidateQueries({
        queryKey: [mutationKey?.at(0)],
        exact: false,
      });
    },
  }),
});
```

#### 3. 장점

- **중앙 집중 관리**: Invalidation 로직이 한 곳에 모여 유지보수 용이
- **타입 안전성**: `TChatsGlobalMutationEffects` 타입으로 자동 완성 및 검증
- **일관성**: 모든 Mutation에서 동일한 방식으로 동작
- **재사용성**: 여러 컴포넌트에서 동일한 Mutation 사용 시 중복 코드 제거

## 워크플로우

### 개발 중 API 변경 시

1. 백엔드 API 변경됨
2. Swagger 스펙 업데이트
3. 프론트엔드에서 `yarn api:generate` 실행
4. 타입 에러 확인 및 코드 수정

### 권장 사항

- ✅ API 변경 후 즉시 재생성
- ✅ 생성된 파일은 Git에 커밋
- ✅ PR 리뷰 시 API 변경사항 확인
- ⚠️ 생성된 파일 직접 수정 금지 (재생성 시 덮어써짐)

## 참고 자료

- [swagger-client-autogen](https://github.com/4jades/swagger-client-autogen)
- [swagger-typescript-api](https://acacode.github.io/swagger-typescript-api/)

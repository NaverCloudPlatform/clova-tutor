import type { DefaultError, Mutation, QueryClient } from '@tanstack/react-query';

import type { chatsMutations } from '@/entities/chats/__generated__/api/mutations';
import type { goalsMutations } from '@/entities/goals/__generated__/api/mutations';
import type { problemBookmarksMutations } from '@/entities/problem-bookmarks/__generated__/api/mutations';
import type { problemsMutations } from '@/entities/problems/__generated__/api/mutations';
import type { uploadMutations } from '@/entities/upload/__generated__/api/mutations';
import type { usersMutations } from '@/entities/users/__generated__/api/mutations';

// biome-ignore lint/suspicious/noExplicitAny: 타입 제약을 위해 any 사용
type AnyMutationFn = (variables: any) => any;

type MutationFactory = () => {
  mutationFn: AnyMutationFn;
  mutationKey: readonly unknown[];
};

export type MutationMap = Record<string, MutationFactory>;

type ExtractMutationDef<M extends MutationMap, K extends keyof M> = ReturnType<M[K]>;

type ExtractMutationFn<M extends MutationMap, K extends keyof M> = ExtractMutationDef<M, K>['mutationFn'];

type ExtractMutationVariables<M extends MutationMap, K extends keyof M> = Parameters<ExtractMutationFn<M, K>>[0];

type ExtractMutationData<M extends MutationMap, K extends keyof M> = Awaited<ReturnType<ExtractMutationFn<M, K>>>;

export type GlobalMutationEffectMap<M extends MutationMap> = Partial<{
  [K in keyof M]: {
    onSuccess: {
      invalidate: (
        data: ExtractMutationData<M, K>,
        variables: ExtractMutationVariables<M, K>,
        context: unknown,
        mutation: Mutation<ExtractMutationData<M, K>, DefaultError, ExtractMutationVariables<M, K>, unknown>,
      ) => void;
    };
  };
}>;

export type TChatsGlobalMutationEffects = GlobalMutationEffectMap<typeof chatsMutations>;
export type TProblemsGlobalMutationEffects = GlobalMutationEffectMap<typeof problemsMutations>;
export type TUploadGlobalMutationEffects = GlobalMutationEffectMap<typeof uploadMutations>;
export type TUsersGlobalMutationEffects = GlobalMutationEffectMap<typeof usersMutations>;
export type TGoalsGlobalMutationEffects = GlobalMutationEffectMap<typeof goalsMutations>;
export type TProblemBookmarksGlobalMutationEffects = GlobalMutationEffectMap<typeof problemBookmarksMutations>;

export type TGlobalMutationEffectFactory = (
  queryClient: QueryClient,
) => Partial<
  TChatsGlobalMutationEffects &
    TProblemsGlobalMutationEffects &
    TUploadGlobalMutationEffects &
    TUsersGlobalMutationEffects &
    TGoalsGlobalMutationEffects &
    TProblemBookmarksGlobalMutationEffects
>;

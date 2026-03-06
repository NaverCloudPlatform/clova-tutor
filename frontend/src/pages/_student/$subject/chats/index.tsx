/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { createFileRoute } from '@tanstack/react-router';
import { zodValidator } from '@tanstack/zod-adapter';
import { z } from 'zod';
import { useSubject } from '@/entities/chats/hooks/use-subject';
import { ScrollArea } from '@/shared/ui/scroll-area';
import { ChatOnboarding } from '@/widgets/chat-onboarding/ui/chat-onboarding';
import { OnboardingTutorChatInput } from '@/widgets/tutor-chat-input/ui/onboarding-tutor-chat-input';

const searchSchema = z.object({});

export const Route = createFileRoute('/_student/$subject/chats/')({
  component: RouteComponent,
  validateSearch: zodValidator(searchSchema),
  head: ({ params: { subject } }) => {
    const title = `${subject === 'math' ? '수학' : '영어'} 튜터`;

    return {
      meta: [
        {
          title,
        },
      ],
    };
  },
});

function RouteComponent() {
  const { subject } = useSubject();

  return (
    <>
      <div className="flex-1 overflow-hidden w-full">
        <ScrollArea className="h-full" componentProps={{ viewport: { className: '[&>div]:h-full' } }}>
          <div className="@lg:max-w-3xl mx-auto h-full">
            <ChatOnboarding subject={subject} />
          </div>
        </ScrollArea>
      </div>

      <div className="pt-2 pb-2 px-4 bg-card rounded-b-xl @lg:max-w-3xl w-full mx-auto">
        <OnboardingTutorChatInput />
      </div>
    </>
  );
}

type SearchSchema = z.infer<typeof searchSchema>;

export { searchSchema as studentChatIndexSearchSchema, type SearchSchema as StudentChatIndexSearchSchema };

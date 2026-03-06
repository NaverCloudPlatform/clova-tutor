/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { RocketIcon } from 'lucide-react';
import type { ChatProblemDetailResponseDto } from '@/shared/api/__generated__/dto';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/shared/ui/accordion';

type ProblemHintProps = {
  hint: ChatProblemDetailResponseDto['problem_info']['content']['hint'];
};

export function ProblemHint({ hint }: ProblemHintProps) {
  return (
    <Accordion type="single" collapsible>
      <AccordionItem value="item-1">
        <AccordionTrigger className="hover:bg-secondary py-1.5 px-2" headerProps={{ className: 'w-fit' }}>
          <div className="flex items-center gap-2 text-muted-foreground">
            <RocketIcon className="size-3.5" />
            <p className="text-sm">힌트 보기</p>
          </div>
        </AccordionTrigger>
        <AccordionContent className="py-2">
          <div className="bg-secondary rounded-lg py-3 px-4 text-muted-foreground">{hint}</div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}

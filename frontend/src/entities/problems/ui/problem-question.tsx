/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { MarkdownBase } from '@/packages/markdown/ui/markdown-base';
import type { ChatProblemDetailResponseDto } from '@/shared/api/__generated__/dto';

type SingleChoiceProblemProps = {
  problem: ChatProblemDetailResponseDto['problem_info']['content']['problem'];
};

export function ProblemQuestion({ problem }: SingleChoiceProblemProps) {
  return <MarkdownBase>{problem}</MarkdownBase>;
}

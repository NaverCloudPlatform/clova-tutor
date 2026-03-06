/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

'use client';

import { useSuspenseQuery } from '@tanstack/react-query';
import React from 'react';
import { Label, PolarAngleAxis, PolarRadiusAxis, RadialBar, RadialBarChart } from 'recharts';
import { chatsQueries } from '@/entities/chats/__generated__/api/queries';
import { type ChartConfig, ChartContainer } from '@/shared/ui/chart';
import { Skeleton } from '@/shared/ui/skeleton';

const chartConfig = {
  progress: { label: 'Progress', color: 'var(--chart-3)' },
} satisfies ChartConfig;

type GoalProgressStatusProps = {
  chatId: number;
};

export const GoalProgressStatus = React.memo(GoalProgressStatusContent);

function GoalProgressStatusContent({ chatId }: GoalProgressStatusProps) {
  const { data: activeGoal } = useSuspenseQuery({
    ...chatsQueries.getChatsByChatId({ chatId }),
    select: (data) => {
      return data.active_goal;
    },
  });

  if (!activeGoal) return null;

  const progress = Math.round((activeGoal.solved_count / activeGoal.goal_count) * 100);
  const chartData = [{ progress }];

  return (
    <div className="h-9 w-12 flex-1 overflow-hidden ms-1">
      <ChartContainer config={chartConfig} className="aspect-square">
        <RadialBarChart data={chartData} startAngle={200} endAngle={-20} innerRadius={21} outerRadius={35}>
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />

          <PolarRadiusAxis tick={false} tickLine={false} axisLine={false}>
            <Label
              content={({ viewBox }) => {
                if (viewBox && 'cx' in viewBox && 'cy' in viewBox) {
                  return (
                    <text x={viewBox.cx} y={viewBox.cy} textAnchor="middle">
                      <tspan x={viewBox.cx} y={viewBox.cy} className="fill-primary text-xs font-bold">
                        {progress}%
                      </tspan>
                    </text>
                  );
                }
                return null;
              }}
            />
          </PolarRadiusAxis>

          <RadialBar
            dataKey="progress"
            cornerRadius={999}
            className="fill-primary"
            background={{
              className: '!fill-border',
            }}
          />
        </RadialBarChart>
      </ChartContainer>
    </div>
  );
}

export function GoalProgressStatusSkeleton() {
  return (
    <div className="h-9 w-12 flex-1 ms-1">
      <Skeleton className="h-9 w-12" />
    </div>
  );
}

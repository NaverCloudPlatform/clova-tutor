/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { AlertCircleIcon, InfoIcon, TriangleAlertIcon } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/shared/ui/alert';
import { Button } from '@/shared/ui/button';

type Props = {
  message: string;
  type: 'error' | 'warning' | 'info';
  button?: {
    label: string;
    onClick: () => void;
  };
};

export function ChatAlert({ message, type, button }: Props) {
  const variants = {
    error: {
      icon: <AlertCircleIcon className="h-4 w-4 stroke-destructive" />,
      title: 'Error',
    },
    warning: {
      icon: <TriangleAlertIcon className="h-4 w-4 stroke-accent-yellow-700" />,
      title: 'Warning',
    },
    info: {
      icon: <InfoIcon className="h-4 w-4 stroke-primary" />,
      title: 'Info',
    },
  } as const;
  const variant = variants[type];

  return (
    <Alert variant="default" className="mt-4 mb-4">
      {variant.icon}
      <AlertTitle>{variant.title}</AlertTitle>
      <AlertDescription>{message}</AlertDescription>

      {button && (
        <Button
          variant="outline"
          size="sm"
          className="absolute right-3 top-1/2 -translate-y-1/2"
          onClick={button.onClick}
        >
          {button.label}
        </Button>
      )}
    </Alert>
  );
}

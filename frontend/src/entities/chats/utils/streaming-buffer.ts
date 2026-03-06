/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

interface StreamingBufferOptions<T> {
  interval?: number;
  onTokenUpdate: (token: T) => void;
  onAllTokensProcessed?: () => void;
}

export class StreamingBuffer<T> {
  private pendingTokens: T[] = [];
  private isProcessing = false;
  private isStreamComplete = false;
  private intervalId: NodeJS.Timeout | null = null;
  private interval: number;
  private onTokenUpdate: (token: T) => void;
  private onAllTokensProcessed?: () => void;

  constructor(options: StreamingBufferOptions<T>) {
    this.onTokenUpdate = options.onTokenUpdate;
    this.interval = options.interval ?? 30;
    this.onAllTokensProcessed = options.onAllTokensProcessed;
  }

  private startProcessing() {
    if (this.isProcessing) return;

    this.isProcessing = true;
    this.intervalId = setInterval(() => {
      if (this.pendingTokens.length === 0) {
        this.stopProcessing();

        if (this.isStreamComplete) {
          this.onAllTokensProcessed?.();
        }

        return;
      }

      this.processToken();
    }, this.interval);
  }

  private stopProcessing() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.isProcessing = false;
  }

  private processToken() {
    const token = this.pendingTokens.shift();
    if (token) {
      this.onTokenUpdate(token);
    }
  }

  completeStream() {
    this.isStreamComplete = true;

    if (this.pendingTokens.length === 0 && this.isProcessing) {
      this.stopProcessing();
      this.onAllTokensProcessed?.();
    }
  }

  addToken(token: T) {
    this.pendingTokens.push(token);
    this.startProcessing();
  }

  flush(onFlushComplete?: () => void) {
    if (this.pendingTokens.length === 0) {
      onFlushComplete?.();
      this.onAllTokensProcessed?.();
      return;
    }

    this.stopProcessing();
    this.intervalId = setInterval(
      () => {
        if (this.pendingTokens.length === 0) {
          this.stopProcessing();
          onFlushComplete?.();
          this.onAllTokensProcessed?.();
          return;
        }

        this.processToken();
      },
      Math.floor(this.interval / 2),
    );
  }

  abort() {
    this.stopProcessing();
    this.pendingTokens = [];
    this.isStreamComplete = false;
    this.isProcessing = false;
  }
}

/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import type { QueryClient } from '@tanstack/react-query';
import { format, isToday } from 'date-fns';
import { produce } from 'immer';
import type {
  ChatMessageCreateRequestBodyDto,
  ChatMessageResponseDto,
  SystemMessageResponseDto,
} from '@/shared/api/__generated__/dto';
import { chatsQueries } from '../__generated__/api/queries';
import {
  ASSISTANT_STREAMING_MESSAGE_ID,
  DATE_STREAMING_MESSAGE_ID,
  USER_STREAMING_MESSAGE_ID,
} from '../constants/streaming';
import type { MessageDeltaData } from '../types/stream';

export class ChatQueryCacheService {
  private readonly queryClient: QueryClient;
  private readonly chatId: number;

  constructor(queryClient: QueryClient, chatId: number) {
    this.chatId = chatId;
    this.queryClient = queryClient;
  }

  private addDateMessageToQueryClient() {
    const lastMessageCreatedAt = this.queryClient
      .getQueryData(chatsQueries.getChatsByChatIdMessages({ chatId: this.chatId }).queryKey)
      ?.data.at(-1)?.created_at;
    const isLastMessageCreatedToday = lastMessageCreatedAt && isToday(lastMessageCreatedAt);

    if (isLastMessageCreatedToday) return;

    const dateMessage: SystemMessageResponseDto = {
      id: DATE_STREAMING_MESSAGE_ID,
      chat_id: this.chatId,
      created_at: format(new Date(), "yyyy-MM-dd'T'HH:mm:ssXXX"),
      type: 'system',
      author: {
        role: 'system',
      },
      contents: [
        {
          m_type: 'date',
          value: {
            text: format(new Date(), 'yyyy-MM-dd'),
          },
        },
      ],
      metadata: {},
    };

    this.queryClient.setQueryData(chatsQueries.getChatsByChatIdMessages({ chatId: this.chatId }).queryKey, (old) => {
      if (!old) return { data: [dateMessage] };
      return {
        ...old,
        data: [...old.data, dateMessage],
      };
    });
  }

  private addUserMessageToQueryClient(payload: ChatMessageCreateRequestBodyDto) {
    const userMessage: ChatMessageResponseDto = {
      id: USER_STREAMING_MESSAGE_ID,
      chat_id: this.chatId,
      created_at: format(new Date(), "yyyy-MM-dd'T'HH:mm:ssXXX"),
      type: 'chat',
      author: {
        role: 'user',
      },
      contents: payload.contents,
      metadata: payload.metadata,
    };

    this.queryClient.setQueryData(chatsQueries.getChatsByChatIdMessages({ chatId: this.chatId }).queryKey, (old) => {
      if (!old) return { data: [userMessage] };
      return {
        ...old,
        data: [...old.data, userMessage],
      };
    });
  }

  private addModelMessageToQueryClient() {
    const modelMessage: ChatMessageResponseDto = {
      id: ASSISTANT_STREAMING_MESSAGE_ID,
      chat_id: this.chatId,
      created_at: format(new Date(), "yyyy-MM-dd'T'HH:mm:ssXXX"),
      type: 'chat',
      author: {
        role: 'assistant',
      },
      contents: [{ m_type: 'text', value: { text: '' } }],
      metadata: {},
    };

    this.queryClient.setQueryData(chatsQueries.getChatsByChatIdMessages({ chatId: this.chatId }).queryKey, (old) => {
      if (!old) return { data: [modelMessage] };
      return {
        ...old,
        data: [...old.data, modelMessage],
      };
    });
  }

  private replaceLastAssistantMessage(data: ChatMessageResponseDto) {
    this.queryClient.setQueryData(chatsQueries.getChatsByChatIdMessages({ chatId: this.chatId }).queryKey, (old) => {
      if (!old) return { data: [data] };

      return produce(old, (draft) => {
        const lastMessageIndex = draft.data.findLastIndex(
          (message) => message.type === 'chat' && message.author.role === 'assistant',
        );

        if (lastMessageIndex !== -1) {
          draft.data[lastMessageIndex] = data;
        }
      });
    });
  }

  private addTextToLastAssistantMessage(token: MessageDeltaData) {
    this.queryClient.setQueryData(chatsQueries.getChatsByChatIdMessages({ chatId: this.chatId }).queryKey, (old) => {
      if (!old) return { data: [] };

      return produce(old, (draft) => {
        const lastMessage = draft.data.findLast(
          (message) => message.type === 'chat' && message.author.role === 'assistant',
        );

        if (!lastMessage) return;

        const textContent = lastMessage.contents.findLast((content) => content.m_type === 'text');

        if (textContent) {
          textContent.value.text += token.text;
        }
      });
    });
  }

  private filterEmptyAssistantMessage(data: ChatMessageResponseDto) {
    const filteredData = produce(data, (draft) => {
      draft.contents = draft.contents.filter((content) => {
        if (content.m_type === 'text') {
          return content.value.text.trim() !== '';
        }

        return true;
      });
    });

    return filteredData;
  }

  private removeModelMessages() {
    this.queryClient.setQueryData(chatsQueries.getChatsByChatIdMessages({ chatId: this.chatId }).queryKey, (old) => {
      if (!old) return old;

      return produce(old, (draft) => {
        draft.data = draft.data.filter((message) => {
          return message.id !== ASSISTANT_STREAMING_MESSAGE_ID;
        });
      });
    });
  }

  private removeUserMessage() {
    this.queryClient.setQueryData(chatsQueries.getChatsByChatIdMessages({ chatId: this.chatId }).queryKey, (old) => {
      if (!old) return old;

      return produce(old, (draft) => {
        draft.data = draft.data.filter((message) => {
          return message.id !== USER_STREAMING_MESSAGE_ID;
        });
      });
    });
  }

  /**
   * 메시지 전송 시 초기 메시지 추가
   */
  initializeStreamingMessages(payload: ChatMessageCreateRequestBodyDto) {
    this.addDateMessageToQueryClient();
    this.addUserMessageToQueryClient(payload);
    this.addModelMessageToQueryClient(); // MessasgeStreamSuspense에서 로딩 컴포넌트를 표시하기 위해 텍스트가 비어있는 모델 메시지 캐시를 추가합니다.
  }

  /**
   * message_start 스트리밍 이벤트 수신 시 모델 메시지 교체
   */
  updateAssistantMessage(data: ChatMessageResponseDto) {
    this.replaceLastAssistantMessage(data);
  }

  /**
   * StreamingBatchProcessor 에서 토큰 수신 시 모델 메시지 텍스트 추가
   */
  updateAssistantMessageTextContent(token: MessageDeltaData) {
    this.addTextToLastAssistantMessage(token);
  }

  /**
   * message_end 스트리밍 이벤트 수신 시 모델 메시지 교체
   */
  updateFinalAssistantMessage(data: ChatMessageResponseDto) {
    this.replaceLastAssistantMessage(this.filterEmptyAssistantMessage(data));
  }

  /**
   * 스트리밍 복구 시 모델 메시지 초기화
   */
  initializeStreamingMessagesResume() {
    this.addModelMessageToQueryClient();
  }

  /**
   * 에러 발생 시 낙관적으로 추가한 메시지들을 롤백
   */
  rollbackStreamingMessages() {
    this.removeModelMessages();
  }

  /**
   * 재전송 시 낙관적으로 추가한 유저 메시지를 제거
   */
  retryUserMessage() {
    this.removeUserMessage();
  }
}

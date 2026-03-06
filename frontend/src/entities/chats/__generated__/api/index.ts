import type { KyInstance, Options } from 'ky';
import { z } from 'zod';

import type {
  ChatCreateRequestBodyDto,
  ChatDetailResponseDto,
  ChatMessageCreateRequestBodyDto,
  ChatMessageStopResponseDto,
  ChatProblemDetailResponseDto,
  ChatProblemResponseDto,
  ChatProblemSubmitRequestBodyDto,
  ChatProblemSubmitResponseDto,
  ChatResponseDto,
  ChatStreamStatusResponseDto,
  ChatTitleUpdateRequestBodyDto,
  CursorPaginateResponseChatResponseDto,
  GetChatsChatsGetQueryParams,
  MessageListResponseDto,
} from '@/shared/api/__generated__/dto';
import {
  chatCreateRequestBodyDtoSchema,
  chatDetailResponseDtoSchema,
  chatMessageCreateRequestBodyDtoSchema,
  chatMessageStopResponseDtoSchema,
  chatProblemDetailResponseDtoSchema,
  chatProblemResponseDtoSchema,
  chatProblemSubmitRequestBodyDtoSchema,
  chatProblemSubmitResponseDtoSchema,
  chatResponseDtoSchema,
  chatStreamStatusResponseDtoSchema,
  chatTitleUpdateRequestBodyDtoSchema,
  cursorPaginateResponseChatResponseDtoSchema,
  messageListResponseDtoSchema,
} from '@/shared/api/__generated__/schema';
import { createSearchParams, validateSchema } from '@/shared/api/__generated__/utils';
import {
  type ChatsByChatIdMessagesStreamCallbacks,
  ChatsByChatIdMessagesStreamHandler,
  type ChatsByChatIdResumeStreamCallbacks,
  ChatsByChatIdResumeStreamHandler,
} from '../../api/stream-handlers';

export class ChatsApi {
  private readonly instance: KyInstance;

  constructor(instance: KyInstance) {
    this.instance = instance;
  }

  /**
   * @tags chats
   * @summary Get Chats
   * @request GET:/chats
   */
  async getChats({ params, kyInstance, options }: TChatsApiRequestParameters['getChats']) {
    const instance = kyInstance ?? this.instance;

    const urlSearchParams = createSearchParams(params);
    const response = await instance
      .get<CursorPaginateResponseChatResponseDto>(`chats`, {
        searchParams: urlSearchParams,
        ...options,
      })
      .json();

    const validateResponse = validateSchema(cursorPaginateResponseChatResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags chats
   * @summary Create Chat
   * @request POST:/chats
   */
  async postChats({ payload, kyInstance, options }: TChatsApiRequestParameters['postChats']) {
    const instance = kyInstance ?? this.instance;
    const validatedPayload = validateSchema(chatCreateRequestBodyDtoSchema, payload);

    const response = await instance
      .post<ChatResponseDto>(`chats`, {
        json: validatedPayload,
        ...options,
      })
      .json();

    const validateResponse = validateSchema(chatResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags chats
   * @summary Get Chat
   * @request GET:/chats/{chat_id}
   */
  async getChatsByChatId({ chatId, kyInstance, options }: TChatsApiRequestParameters['getChatsByChatId']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .get<ChatDetailResponseDto>(`chats/${chatId}`, {
        ...options,
      })
      .json();

    const validateResponse = validateSchema(chatDetailResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags chats
   * @summary Update Chat Title
   * @request PATCH:/chats/{chat_id}
   */
  async patchChatsByChatId({ chatId, payload, kyInstance, options }: TChatsApiRequestParameters['patchChatsByChatId']) {
    const instance = kyInstance ?? this.instance;
    const validatedPayload = validateSchema(chatTitleUpdateRequestBodyDtoSchema, payload);

    const response = await instance
      .patch<ChatResponseDto>(`chats/${chatId}`, {
        json: validatedPayload,
        ...options,
      })
      .json();

    const validateResponse = validateSchema(chatResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags chats
   * @summary Delete Chat
   * @request DELETE:/chats/{chat_id}
   */
  async deleteChatsByChatId({ chatId, kyInstance, options }: TChatsApiRequestParameters['deleteChatsByChatId']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .delete<void>(`chats/${chatId}`, {
        ...options,
      })
      .json();

    return response;
  }

  /**
   * @tags chats
   * @summary Get Chat Stream Status
   * @request GET:/chats/{chat_id}/stream-status
   */
  async getChatsByChatIdStreamStatus({
    chatId,
    kyInstance,
    options,
  }: TChatsApiRequestParameters['getChatsByChatIdStreamStatus']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .get<ChatStreamStatusResponseDto>(`chats/${chatId}/stream-status`, {
        ...options,
      })
      .json();

    const validateResponse = validateSchema(chatStreamStatusResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags chats
   * @summary Resume Chat Stream
   * @request POST:/chats/{chat_id}/resume
   *
   * @todo 1. ReadableStreamHandler를 상속받아 "./stream-handlers" 경로에 ChatsByChatIdResumeStreamHandler 클래스를 구현해주세요
   * @see 구현 가이드: https://github.com/dhlab-org/swagger-client-autogen/blob/main/.docs/stream-handler-guide.md
   *
   * @todo 2. 스트리밍 응답은 TanStack Query hook 코드를 자동으로 생성하지 않기 때문에 직접 훅을 구현해서 사용해야 합니다.
   * @see TanStack Query 통합 가이드: https://github.com/dhlab-org/swagger-client-autogen/blob/main/.docs/tanstack-query-stream.md
   */
  async postChatsByChatIdResume({
    chatId,
    kyInstance,
    options,
    callbacks,
  }: TChatsApiRequestParameters['postChatsByChatIdResume'] & {
    callbacks: ChatsByChatIdResumeStreamCallbacks;
  }) {
    const instance = kyInstance ?? this.instance;

    const response = await instance.post<string>(`chats/${chatId}/resume`, {
      ...options,
    });

    return new ChatsByChatIdResumeStreamHandler(response, callbacks);
  }

  /**
   * @tags chats
   * @summary Stop Stream
   * @request POST:/chats/{chat_id}/stop-conversation
   */
  async postChatsByChatIdStopConversation({
    chatId,
    kyInstance,
    options,
  }: TChatsApiRequestParameters['postChatsByChatIdStopConversation']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .post<ChatMessageStopResponseDto>(`chats/${chatId}/stop-conversation`, {
        ...options,
      })
      .json();

    const validateResponse = validateSchema(chatMessageStopResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags chats
   * @summary Get Messages
   * @request GET:/chats/{chat_id}/messages
   */
  async getChatsByChatIdMessages({
    chatId,
    kyInstance,
    options,
  }: TChatsApiRequestParameters['getChatsByChatIdMessages']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .get<MessageListResponseDto>(`chats/${chatId}/messages`, {
        ...options,
      })
      .json();

    const validateResponse = validateSchema(messageListResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags chats
   * @summary Send Message
   * @request POST:/chats/{chat_id}/messages
   *
   * @todo 1. ReadableStreamHandler를 상속받아 "./stream-handlers" 경로에 ChatsByChatIdMessagesStreamHandler 클래스를 구현해주세요
   * @see 구현 가이드: https://github.com/dhlab-org/swagger-client-autogen/blob/main/.docs/stream-handler-guide.md
   *
   * @todo 2. 스트리밍 응답은 TanStack Query hook 코드를 자동으로 생성하지 않기 때문에 직접 훅을 구현해서 사용해야 합니다.
   * @see TanStack Query 통합 가이드: https://github.com/dhlab-org/swagger-client-autogen/blob/main/.docs/tanstack-query-stream.md
   */
  async postChatsByChatIdMessages({
    chatId,
    payload,
    kyInstance,
    options,
    callbacks,
  }: TChatsApiRequestParameters['postChatsByChatIdMessages'] & {
    callbacks: ChatsByChatIdMessagesStreamCallbacks;
  }) {
    const instance = kyInstance ?? this.instance;
    const validatedPayload = validateSchema(chatMessageCreateRequestBodyDtoSchema, payload);

    const response = await instance.post<string>(`chats/${chatId}/messages`, {
      json: validatedPayload,
      ...options,
    });

    return new ChatsByChatIdMessagesStreamHandler(response, callbacks);
  }

  /**
   * @tags chats
   * @summary Get Chat Problems
   * @request GET:/chats/{chat_id}/problems
   */
  async getChatsByChatIdProblems({
    chatId,
    kyInstance,
    options,
  }: TChatsApiRequestParameters['getChatsByChatIdProblems']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .get<ChatProblemResponseDto[]>(`chats/${chatId}/problems`, {
        ...options,
      })
      .json();

    const validateResponse = validateSchema(z.array(chatProblemResponseDtoSchema), response);
    return validateResponse;
  }

  /**
   * @tags chats
   * @summary Get Chat Problem
   * @request GET:/chats/{chat_id}/problems/{problem_id}
   */
  async getChatsByChatIdProblemsByProblemId({
    chatId,
    problemId,
    kyInstance,
    options,
  }: TChatsApiRequestParameters['getChatsByChatIdProblemsByProblemId']) {
    const instance = kyInstance ?? this.instance;

    const response = await instance
      .get<ChatProblemDetailResponseDto>(`chats/${chatId}/problems/${problemId}`, {
        ...options,
      })
      .json();

    const validateResponse = validateSchema(chatProblemDetailResponseDtoSchema, response);
    return validateResponse;
  }

  /**
   * @tags chats
   * @summary Submit Chat Problem
   * @request POST:/chats/{chat_id}/problems/{problem_id}/submit
   */
  async postChatsByChatIdProblemsByProblemIdSubmit({
    chatId,
    problemId,
    payload,
    kyInstance,
    options,
  }: TChatsApiRequestParameters['postChatsByChatIdProblemsByProblemIdSubmit']) {
    const instance = kyInstance ?? this.instance;
    const validatedPayload = validateSchema(chatProblemSubmitRequestBodyDtoSchema, payload);

    const response = await instance
      .post<ChatProblemSubmitResponseDto>(`chats/${chatId}/problems/${problemId}/submit`, {
        json: validatedPayload,
        ...options,
      })
      .json();

    const validateResponse = validateSchema(chatProblemSubmitResponseDtoSchema, response);
    return validateResponse;
  }
}

export type TChatsApiRequestParameters = {
  getChats: {
    params?: GetChatsChatsGetQueryParams;
    kyInstance?: KyInstance;
    options?: Options;
  };
  postChats: {
    payload: ChatCreateRequestBodyDto;
    kyInstance?: KyInstance;
    options?: Options;
  };
  getChatsByChatId: {
    chatId: number;
    kyInstance?: KyInstance;
    options?: Options;
  };
  patchChatsByChatId: {
    chatId: number;
    payload: ChatTitleUpdateRequestBodyDto;
    kyInstance?: KyInstance;
    options?: Options;
  };
  deleteChatsByChatId: {
    chatId: number;
    kyInstance?: KyInstance;
    options?: Options;
  };
  getChatsByChatIdStreamStatus: {
    chatId: number;
    kyInstance?: KyInstance;
    options?: Options;
  };
  postChatsByChatIdResume: {
    chatId: number;
    kyInstance?: KyInstance;
    options?: Options;
  };
  postChatsByChatIdStopConversation: {
    chatId: number;
    kyInstance?: KyInstance;
    options?: Options;
  };
  getChatsByChatIdMessages: {
    chatId: number;
    kyInstance?: KyInstance;
    options?: Options;
  };
  postChatsByChatIdMessages: {
    chatId: number;
    payload: ChatMessageCreateRequestBodyDto;
    kyInstance?: KyInstance;
    options?: Options;
  };
  getChatsByChatIdProblems: {
    chatId: number;
    kyInstance?: KyInstance;
    options?: Options;
  };
  getChatsByChatIdProblemsByProblemId: {
    chatId: number;
    problemId: string;
    kyInstance?: KyInstance;
    options?: Options;
  };
  postChatsByChatIdProblemsByProblemIdSubmit: {
    chatId: number;
    problemId: string;
    payload: ChatProblemSubmitRequestBodyDto;
    kyInstance?: KyInstance;
    options?: Options;
  };
};

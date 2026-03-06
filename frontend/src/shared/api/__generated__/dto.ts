/**
 * SystemHint
 * 시스템 힌트 플래그를 정의하는 열거형 클래스입니다.
 *
 */
export type SystemHintDto = 'translation_button';

/** SubjectEnum */
export type SubjectEnumDto = 'math' | 'english';

/** StopResponseStatusValue */
export type StopResponseStatusValueDto = 'ok';

/** ReActModelToolType */
export type ReActModelToolTypeDto =
  | 'translation'
  | 'eng_voca'
  | 'eng_grammar'
  | 'table_fetch'
  | 'answer_included'
  | 'math_concept'
  | 'stepwise_solution'
  | 'solution_demonstration'
  | 'recommend_problem'
  | 'default_chat';

/** ProblemStatus */
export type ProblemStatusDto = '풀지 않음' | '정답' | '오답' | '복습 완료';

/** ProblemDuplicateStatus */
export type ProblemDuplicateStatusDto = 'duplicate' | 'unique';

/**
 * MessageRole
 * 메시지 작성자의 역할을 정의하는 열거형 클래스입니다.
 *
 * Attributes:
 *     USER: 사용자가 작성한 메시지
 *     ASSISTANT: AI 어시스턴트가 작성한 메시지
 *     SYSTEM: 시스템이 작성한 메시지
 */
export type MessageRoleDto = 'user' | 'assistant' | 'system';

/** ChatStreamStatus */
export type ChatStreamStatusDto = 'IS_STREAMING' | 'COMPLETE';

/** ProblemResponse */
export type ProblemResponseDto =
  | ({
      type: '다중선택 객관식';
    } & MultipleChoiceProblemResponseDto)
  | ({
      type: '다중응답 주관식';
    } & MultipleShortAnswerProblemResponseDto)
  | ({
      type: '단일선택 객관식';
    } & SingleChoiceProblemResponseDto)
  | ({
      type: '단일응답 주관식';
    } & SingleShortAnswerProblemResponseDto);

/** ActiveGoalResponse */
export type ActiveGoalResponseDto = {
  /** Id */
  id: number;
  /** Goal Count */
  goal_count: number;
  /** Solved Count */
  solved_count: number;
};

/** ChatCreateRequestBody */
export type ChatCreateRequestBodyDto = {
  /** Title */
  title: string;
  /** Grade */
  grade: string;
  /** Subject */
  subject: string;
};

/** ChatDetailResponse */
export type ChatDetailResponseDto = {
  /** Id */
  id: number;
  /** Title */
  title: string;
  /** Subject */
  subject: string;
  /** Has Problem */
  has_problem: boolean;
  /** Has Active Goal */
  has_active_goal: boolean;
  active_goal: ActiveGoalResponseDto | null;
};

/** ChatMessageCreateRequestBody */
export type ChatMessageCreateRequestBodyDto = {
  /** Contents */
  contents: (
    | ({
        m_type: 'images';
      } & ImagesContentDto)
    | ({
        m_type: 'problem_link';
      } & ProblemLinkContentDto)
    | ({
        m_type: 'problem_recommended';
      } & ProblemRecommendedContentDto)
    | ({
        m_type: 'quote';
      } & QuoteContentDto)
    | ({
        m_type: 'text';
      } & TextContentDto)
  )[];
  metadata: ChatMessageMetadataRequestDto;
};

/** ChatMessageMetadataRequest */
export type ChatMessageMetadataRequestDto = {
  /** System Hints */
  system_hints?: SystemHintDto[];
};

/** ChatMessageResponse */
export type ChatMessageResponseDto = {
  /** Id */
  id: number;
  /** Chat Id */
  chat_id: number;
  /**
   * Created At
   * @format date-time
   */
  created_at: string;
  /** Type */
  type: 'chat';
  author: MessageAuthorDto;
  /** Contents */
  contents: (
    | ({
        m_type: 'images';
      } & ImagesContentDto)
    | ({
        m_type: 'problem_link';
      } & ProblemLinkContentDto)
    | ({
        m_type: 'problem_recommended';
      } & ProblemRecommendedContentDto)
    | ({
        m_type: 'quote';
      } & QuoteContentDto)
    | ({
        m_type: 'text';
      } & TextContentDto)
  )[];
  metadata: MessageMetadataResponseDto;
};

/** ChatMessageStopResponse */
export type ChatMessageStopResponseDto = {
  status: StopResponseStatusValueDto;
};

/** ChatProblemDetailResponse */
export type ChatProblemDetailResponseDto = {
  /** Number */
  number: number;
  status: ProblemStatusDto;
  /** Last Answer */
  last_answer: string | null;
  /** Is Bookmarked */
  is_bookmarked: boolean;
  problem_info: ProblemResponseDto;
};

/** ChatProblemResponse */
export type ChatProblemResponseDto = {
  /** Id */
  id: string;
  /** Number */
  number: number;
  status: ProblemStatusDto;
  /** Category */
  category?: string;
  /** Grade */
  grade: number;
  /** Level */
  level: number;
};

/** ChatProblemSubmitRequestBody */
export type ChatProblemSubmitRequestBodyDto = {
  /** Answer */
  answer:
    | ({
        type: '다중선택 객관식';
      } & MultipleChoiceAnswerDto)
    | ({
        type: '다중응답 주관식';
      } & MultipleShortAnswerDto)
    | ({
        type: '단일선택 객관식';
      } & SingleChoiceAnswerDto)
    | ({
        type: '단일응답 주관식';
      } & SingleShortAnswerDto);
};

/** ChatProblemSubmitResponse */
export type ChatProblemSubmitResponseDto = {
  /** Is Correct */
  is_correct: boolean;
  active_goal: ActiveGoalResponseDto | null;
};

/** ChatQuoteSource */
export type ChatQuoteSourceDto = {
  /** Type */
  type: 'chat';
  /** Chat Id */
  chat_id: number;
};

/** ChatResponse */
export type ChatResponseDto = {
  /** Id */
  id: number;
  /** Title */
  title: string;
  /** Subject */
  subject: string;
  /** Has Problem */
  has_problem: boolean;
  /** Has Active Goal */
  has_active_goal: boolean;
  /**
   * Latest Used At
   * @format date-time
   */
  latest_used_at: string;
};

/** ChatStreamStatusResponse */
export type ChatStreamStatusResponseDto = {
  status: ChatStreamStatusDto;
};

/** ChatTitleUpdateRequestBody */
export type ChatTitleUpdateRequestBodyDto = {
  /** Title */
  title: string;
};

/** ChoiceProblemContent */
export type ChoiceProblemContentDto = {
  /** Subject */
  subject: string;
  /** Grade */
  grade: number;
  /** Semester */
  semester: number | null;
  /** Level */
  level: number;
  /** Primary */
  primary: string | null;
  /** Secondary */
  secondary: string | null;
  /** Specific */
  specific: string | null;
  /** Category */
  category: string | null;
  /** Problem */
  problem: string;
  /** Tags */
  tags?: string[];
  /** Hint */
  hint: string | null;
  /** Explanation */
  explanation: string | null;
  /**
   * Choices
   * @default []
   */
  choices?: ProblemChoiceDto[];
};

/** CursorPaginateResponse[ChatResponse] */
export type CursorPaginateResponseChatResponseDto = {
  /** Items */
  items: ChatResponseDto[];
  /** Next Cursor */
  next_cursor: string | null;
};

/** CursorPaginateResponse[ProblemBookmarkResponse] */
export type CursorPaginateResponseProblemBookmarkResponseDto = {
  /** Items */
  items: ProblemBookmarkResponseDto[];
  /** Next Cursor */
  next_cursor: string | null;
};

/** DateContent */
export type DateContentDto = {
  /** M Type */
  m_type: 'date';
  value: DateValueDto;
};

/** DateValue */
export type DateValueDto = {
  /** Text */
  text: string;
};

/** ErrorResponse */
export type ErrorResponseDto = {
  /** Message */
  message: string;
  /** Detail */
  detail?: Record<string, any>;
};

/** GoalCreateRequestBody */
export type GoalCreateRequestBodyDto = {
  /** Chat Id */
  chat_id: number;
  /** Goal Count */
  goal_count: number;
};

/** GoalResponse */
export type GoalResponseDto = {
  /** Id */
  id: number;
  /** Goal Count */
  goal_count: number;
  /** Solved Count */
  solved_count: number;
};

/** HTTPValidationError */
export type HTTPValidationErrorDto = {
  /** Detail */
  detail?: ValidationErrorDto[];
};

/** ImagesContent */
export type ImagesContentDto = {
  /** M Type */
  m_type: 'images';
  value: ImagesValueDto;
};

/** ImagesValue */
export type ImagesValueDto = {
  /** Sources */
  sources: string[];
};

/** MessageAuthor */
export type MessageAuthorDto = {
  /**
   * 메시지 작성자의 역할을 정의하는 열거형 클래스입니다.
   *
   * Attributes:
   *     USER: 사용자가 작성한 메시지
   *     ASSISTANT: AI 어시스턴트가 작성한 메시지
   *     SYSTEM: 시스템이 작성한 메시지
   */
  role: MessageRoleDto;
};

/** MessageListResponse */
export type MessageListResponseDto = {
  /** Data */
  data: (
    | ({
        type: 'chat';
      } & ChatMessageResponseDto)
    | ({
        type: 'system';
      } & SystemMessageResponseDto)
  )[];
};

/** MessageMetadataResponse */
export type MessageMetadataResponseDto = {
  /**
   * Tools
   * @default []
   */
  tools?: ToolInfoDto[];
  /** System Hints */
  system_hints?: SystemHintDto[];
};

/** MultipleChoiceAnswer */
export type MultipleChoiceAnswerDto = {
  /** Type */
  type: '다중선택 객관식';
  /** Answer */
  answer: number[];
};

/** MultipleChoiceProblemResponse */
export type MultipleChoiceProblemResponseDto = {
  /** Id */
  id: string;
  /** Type */
  type: '다중선택 객관식';
  content: ChoiceProblemContentDto;
};

/** MultipleShortAnswer */
export type MultipleShortAnswerDto = {
  /** Type */
  type: '다중응답 주관식';
  /** Answer */
  answer: string[];
};

/** MultipleShortAnswerProblemResponse */
export type MultipleShortAnswerProblemResponseDto = {
  /** Id */
  id: string;
  /** Type */
  type: '다중응답 주관식';
  content: ShortAnswerProblemContentDto;
};

/** ProblemBookmarkChatProblemResponse */
export type ProblemBookmarkChatProblemResponseDto = {
  /** Number */
  number: number;
  status: ProblemStatusDto;
  /** Last Answer */
  last_answer: string | null;
  problem_info: ProblemResponseDto;
};

/** ProblemBookmarkChatResponse */
export type ProblemBookmarkChatResponseDto = {
  /** Id */
  id: number;
  /** Has Active Goal */
  has_active_goal: boolean;
};

/** ProblemBookmarkCheckResponse */
export type ProblemBookmarkCheckResponseDto = {
  status: ProblemDuplicateStatusDto;
};

/** ProblemBookmarkCreateRequestBody */
export type ProblemBookmarkCreateRequestBodyDto = {
  /** Chat Id */
  chat_id: number;
  /** Problem Id */
  problem_id: string;
  /** Is Bookmarked */
  is_bookmarked: boolean;
  /** Bookmarked At */
  bookmarked_at?: string;
};

/** ProblemBookmarkCreateResponse */
export type ProblemBookmarkCreateResponseDto = {
  /** Id */
  id: number;
  /** Chat Id */
  chat_id: number;
  /** Problem Id */
  problem_id: string;
  /** Is Bookmarked */
  is_bookmarked: boolean;
  /** Bookmarked At */
  bookmarked_at: string | null;
};

/** ProblemBookmarkResponse */
export type ProblemBookmarkResponseDto = {
  /**
   * Bookmarked At
   * @format date-time
   */
  bookmarked_at: string;
  chat: ProblemBookmarkChatResponseDto;
  problem: ProblemBookmarkChatProblemResponseDto;
};

/** ProblemChoice */
export type ProblemChoiceDto = {
  /** No */
  no: number;
  /** Inst */
  inst: string;
};

/** ProblemCreateAnswerRequest */
export type ProblemCreateAnswerRequestDto = {
  /** Answer */
  answer: string;
  /** Accepted Answers */
  accepted_answers?: string[];
};

/** ProblemCreateChoiceRequest */
export type ProblemCreateChoiceRequestDto = {
  /** No */
  no: number;
  /** Inst */
  inst: string;
};

/** ProblemCreateRequest */
export type ProblemCreateRequestDto = {
  /** Id */
  id: string;
  /** Subject */
  subject: string;
  /** Grade */
  grade: number;
  /** Type */
  type: string;
  /** Level */
  level: number;
  /** Url */
  url: string | null;
  /** Semester */
  semester: number | null;
  /** Primary */
  primary: string | null;
  /** Secondary */
  secondary: string | null;
  /** Specific */
  specific: string | null;
  /** Category */
  category: string | null;
  /** Problem */
  problem: string;
  /** Choices */
  choices: ProblemCreateChoiceRequestDto[] | null;
  /** Correct Answers */
  correct_answers: ProblemCreateAnswerRequestDto[];
  /** Explanation */
  explanation: string | null;
  /** Hint */
  hint: string | null;
  /** Tags */
  tags: string[] | null;
};

/** ProblemCreateRequestBody */
export type ProblemCreateRequestBodyDto = {
  /** Problems */
  problems: ProblemCreateRequestDto[];
};

/** ProblemCreateResponse */
export type ProblemCreateResponseDto = {
  /** Ids */
  ids: string[];
};

/** ProblemLinkContent */
export type ProblemLinkContentDto = {
  /** M Type */
  m_type: 'problem_link';
  value: ProblemLinkValueDto;
};

/** ProblemLinkValue */
export type ProblemLinkValueDto = {
  /** Problem Id */
  problem_id: string;
};

/** ProblemQuoteSource */
export type ProblemQuoteSourceDto = {
  /** Type */
  type: 'problem';
  /** Problem Id */
  problem_id: string;
};

/** ProblemRecommendedContent */
export type ProblemRecommendedContentDto = {
  /** M Type */
  m_type: 'problem_recommended';
  value: ProblemRecommendedValueDto;
};

/** ProblemRecommendedValue */
export type ProblemRecommendedValueDto = {
  /** Problem Id */
  problem_id: string;
  /** Category */
  category: string | null;
  status: ProblemStatusDto;
};

/** QuoteContent */
export type QuoteContentDto = {
  /** M Type */
  m_type: 'quote';
  value: QuoteValueDto;
};

/** QuoteValue */
export type QuoteValueDto = {
  /** Text */
  text: string;
  /** Source */
  source: ProblemQuoteSourceDto | ChatQuoteSourceDto;
};

/** ShortAnswerProblemContent */
export type ShortAnswerProblemContentDto = {
  /** Subject */
  subject: string;
  /** Grade */
  grade: number;
  /** Semester */
  semester: number | null;
  /** Level */
  level: number;
  /** Primary */
  primary: string | null;
  /** Secondary */
  secondary: string | null;
  /** Specific */
  specific: string | null;
  /** Category */
  category: string | null;
  /** Problem */
  problem: string;
  /** Tags */
  tags?: string[];
  /** Hint */
  hint: string | null;
  /** Explanation */
  explanation: string | null;
};

/** SingleChoiceAnswer */
export type SingleChoiceAnswerDto = {
  /** Type */
  type: '단일선택 객관식';
  /** Answer */
  answer: number;
};

/** SingleChoiceProblemResponse */
export type SingleChoiceProblemResponseDto = {
  /** Id */
  id: string;
  /** Type */
  type: '단일선택 객관식';
  content: ChoiceProblemContentDto;
};

/** SingleShortAnswer */
export type SingleShortAnswerDto = {
  /** Type */
  type: '단일응답 주관식';
  /** Answer */
  answer: string;
};

/** SingleShortAnswerProblemResponse */
export type SingleShortAnswerProblemResponseDto = {
  /** Id */
  id: string;
  /** Type */
  type: '단일응답 주관식';
  content: ShortAnswerProblemContentDto;
};

/** SystemMessageResponse */
export type SystemMessageResponseDto = {
  /** Id */
  id: number;
  /** Chat Id */
  chat_id: number;
  /**
   * Created At
   * @format date-time
   */
  created_at: string;
  /** Type */
  type: 'system';
  author: MessageAuthorDto;
  /** Contents */
  contents: ({
    m_type: 'date';
  } & DateContentDto)[];
  metadata: MessageMetadataResponseDto;
};

/** TextContent */
export type TextContentDto = {
  /** M Type */
  m_type: 'text';
  value: TextValueDto;
};

/** TextValue */
export type TextValueDto = {
  /** Text */
  text: string;
};

/** ToolInfo */
export type ToolInfoDto = {
  name: ReActModelToolTypeDto;
  value: ToolValueDictDto;
};

/** ToolValueDict */
export type ToolValueDictDto = {
  /** Translation Button Visible */
  translation_button_visible?: boolean;
};

/** UnknownConceptCreateRequestBody */
export type UnknownConceptCreateRequestBodyDto = {
  /** Subject */
  subject: string;
  /** Key Concept */
  key_concept: string;
  /** Unknown Concept */
  unknown_concept: string;
  /** Unknown Concept Reason */
  unknown_concept_reason?: string;
};

/** UnknownConceptResponse */
export type UnknownConceptResponseDto = {
  /** Id */
  id: number;
  /** Subject */
  subject: string;
  /** Key Concept */
  key_concept: string;
  /** Unknown Concept */
  unknown_concept: string;
  /** Unknown Concept Reason */
  unknown_concept_reason?: string;
  /**
   * Created At
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * @format date-time
   */
  updated_at: string;
};

/** UploadUrlRequest */
export type UploadUrlRequestDto = {
  /** Mime Type */
  mime_type: string;
};

/** UploadUrlResponse */
export type UploadUrlResponseDto = {
  /** Presigned Url */
  presigned_url: string;
  /** File Url */
  file_url: string;
};

/** UserCreateRequestBody */
export type UserCreateRequestBodyDto = {
  /** Name */
  name: string;
  /** Grade */
  grade: number;
  /** Memo */
  memo?: string;
};

/** UserCreateResponse */
export type UserCreateResponseDto = {
  /**
   * Id
   * @format uuid
   */
  id: string;
  /** Name */
  name: string;
  /** Grade */
  grade: number;
  /** Memo */
  memo: string | null;
};

/** UserResponse */
export type UserResponseDto = {
  /**
   * Id
   * @format uuid
   */
  id: string;
  /** Name */
  name: string;
  /** Grade */
  grade: number;
  /** Memo */
  memo: string | null;
  /**
   * Created At
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * @format date-time
   */
  updated_at: string;
};

/** UserUpdateRequestBody */
export type UserUpdateRequestBodyDto = {
  /** Name */
  name?: string;
  /** Grade */
  grade?: number;
  /** Memo */
  memo?: string;
};

/** UserUpdateResponse */
export type UserUpdateResponseDto = {
  /**
   * Id
   * @format uuid
   */
  id: string;
  /** Name */
  name: string;
  /** Grade */
  grade: number;
  /** Memo */
  memo: string | null;
};

/** ValidationError */
export type ValidationErrorDto = {
  /** Location */
  loc: (string | number)[];
  /** Message */
  msg: string;
  /** Error Type */
  type: string;
};

export type GetChatsChatsGetQueryParams = {
  /** Subject */
  subject?: SubjectEnumDto[];
  /** Cursor */
  cursor?: string;
  /**
   * Size
   * @min 1
   * @max 100
   * @default 10
   */
  size?: number;
};

export type CreateProblemsProblemsPostHeaders = {
  /** X-Api-Key */
  'x-api-key'?: string;
};

export type UploadFileUploadsKeyPutQueryParams = {
  /** Expires */
  expires: number;
  /** Signature */
  signature: string;
  /** Mime */
  mime: string;
};

export type GetProblemBookmarksProblemBookmarksGetQueryParams = {
  subject: SubjectEnumDto;
  /**
   * Status
   * @default []
   */
  status?: ProblemStatusDto[];
  /** Cursor */
  cursor?: string;
  /**
   * Size
   * @min 1
   * @max 100
   * @default 10
   */
  size?: number;
};

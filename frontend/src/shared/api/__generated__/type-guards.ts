import type {
  ActiveGoalResponseDto,
  ChatCreateRequestBodyDto,
  ChatDetailResponseDto,
  ChatMessageCreateRequestBodyDto,
  ChatMessageMetadataRequestDto,
  ChatMessageResponseDto,
  ChatMessageStopResponseDto,
  ChatProblemDetailResponseDto,
  ChatProblemResponseDto,
  ChatProblemSubmitRequestBodyDto,
  ChatProblemSubmitResponseDto,
  ChatQuoteSourceDto,
  ChatResponseDto,
  ChatStreamStatusDto,
  ChatStreamStatusResponseDto,
  ChatTitleUpdateRequestBodyDto,
  ChoiceProblemContentDto,
  CreateProblemsProblemsPostHeaders,
  CursorPaginateResponseChatResponseDto,
  CursorPaginateResponseProblemBookmarkResponseDto,
  DateContentDto,
  DateValueDto,
  ErrorResponseDto,
  GetChatsChatsGetQueryParams,
  GetProblemBookmarksProblemBookmarksGetQueryParams,
  GoalCreateRequestBodyDto,
  GoalResponseDto,
  ImagesContentDto,
  ImagesValueDto,
  MessageAuthorDto,
  MessageListResponseDto,
  MessageMetadataResponseDto,
  MessageRoleDto,
  MultipleChoiceAnswerDto,
  MultipleChoiceProblemResponseDto,
  MultipleShortAnswerDto,
  MultipleShortAnswerProblemResponseDto,
  ProblemBookmarkChatProblemResponseDto,
  ProblemBookmarkChatResponseDto,
  ProblemBookmarkCheckResponseDto,
  ProblemBookmarkCreateRequestBodyDto,
  ProblemBookmarkCreateResponseDto,
  ProblemBookmarkResponseDto,
  ProblemChoiceDto,
  ProblemCreateAnswerRequestDto,
  ProblemCreateChoiceRequestDto,
  ProblemCreateRequestBodyDto,
  ProblemCreateRequestDto,
  ProblemCreateResponseDto,
  ProblemDuplicateStatusDto,
  ProblemLinkContentDto,
  ProblemLinkValueDto,
  ProblemQuoteSourceDto,
  ProblemRecommendedContentDto,
  ProblemRecommendedValueDto,
  ProblemResponseDto,
  ProblemStatusDto,
  QuoteContentDto,
  QuoteValueDto,
  ReActModelToolTypeDto,
  ShortAnswerProblemContentDto,
  SingleChoiceAnswerDto,
  SingleChoiceProblemResponseDto,
  SingleShortAnswerDto,
  SingleShortAnswerProblemResponseDto,
  StopResponseStatusValueDto,
  SubjectEnumDto,
  SystemHintDto,
  SystemMessageResponseDto,
  TextContentDto,
  TextValueDto,
  ToolInfoDto,
  ToolValueDictDto,
  UnknownConceptCreateRequestBodyDto,
  UnknownConceptResponseDto,
  UploadFileUploadsKeyPutQueryParams,
  UploadUrlRequestDto,
  UploadUrlResponseDto,
  UserCreateRequestBodyDto,
  UserCreateResponseDto,
  UserResponseDto,
  UserUpdateRequestBodyDto,
  UserUpdateResponseDto,
  ValidationErrorDto,
} from './dto';
import {
  activeGoalResponseDtoSchema,
  chatCreateRequestBodyDtoSchema,
  chatDetailResponseDtoSchema,
  chatMessageCreateRequestBodyDtoSchema,
  chatMessageMetadataRequestDtoSchema,
  chatMessageResponseDtoSchema,
  chatMessageStopResponseDtoSchema,
  chatProblemDetailResponseDtoSchema,
  chatProblemResponseDtoSchema,
  chatProblemSubmitRequestBodyDtoSchema,
  chatProblemSubmitResponseDtoSchema,
  chatQuoteSourceDtoSchema,
  chatResponseDtoSchema,
  chatStreamStatusDtoSchema,
  chatStreamStatusResponseDtoSchema,
  chatTitleUpdateRequestBodyDtoSchema,
  choiceProblemContentDtoSchema,
  createProblemsProblemsPostHeadersSchema,
  cursorPaginateResponseChatResponseDtoSchema,
  cursorPaginateResponseProblemBookmarkResponseDtoSchema,
  dateContentDtoSchema,
  dateValueDtoSchema,
  errorResponseDtoSchema,
  getChatsChatsGetQueryParamsSchema,
  getProblemBookmarksProblemBookmarksGetQueryParamsSchema,
  goalCreateRequestBodyDtoSchema,
  goalResponseDtoSchema,
  imagesContentDtoSchema,
  imagesValueDtoSchema,
  messageAuthorDtoSchema,
  messageListResponseDtoSchema,
  messageMetadataResponseDtoSchema,
  messageRoleDtoSchema,
  multipleChoiceAnswerDtoSchema,
  multipleChoiceProblemResponseDtoSchema,
  multipleShortAnswerDtoSchema,
  multipleShortAnswerProblemResponseDtoSchema,
  problemBookmarkChatProblemResponseDtoSchema,
  problemBookmarkChatResponseDtoSchema,
  problemBookmarkCheckResponseDtoSchema,
  problemBookmarkCreateRequestBodyDtoSchema,
  problemBookmarkCreateResponseDtoSchema,
  problemBookmarkResponseDtoSchema,
  problemChoiceDtoSchema,
  problemCreateAnswerRequestDtoSchema,
  problemCreateChoiceRequestDtoSchema,
  problemCreateRequestBodyDtoSchema,
  problemCreateRequestDtoSchema,
  problemCreateResponseDtoSchema,
  problemDuplicateStatusDtoSchema,
  problemLinkContentDtoSchema,
  problemLinkValueDtoSchema,
  problemQuoteSourceDtoSchema,
  problemRecommendedContentDtoSchema,
  problemRecommendedValueDtoSchema,
  problemResponseDtoSchema,
  problemStatusDtoSchema,
  quoteContentDtoSchema,
  quoteValueDtoSchema,
  reActModelToolTypeDtoSchema,
  shortAnswerProblemContentDtoSchema,
  singleChoiceAnswerDtoSchema,
  singleChoiceProblemResponseDtoSchema,
  singleShortAnswerDtoSchema,
  singleShortAnswerProblemResponseDtoSchema,
  stopResponseStatusValueDtoSchema,
  subjectEnumDtoSchema,
  systemHintDtoSchema,
  systemMessageResponseDtoSchema,
  textContentDtoSchema,
  textValueDtoSchema,
  toolInfoDtoSchema,
  toolValueDictDtoSchema,
  unknownConceptCreateRequestBodyDtoSchema,
  unknownConceptResponseDtoSchema,
  uploadFileUploadsKeyPutQueryParamsSchema,
  uploadUrlRequestDtoSchema,
  uploadUrlResponseDtoSchema,
  userCreateRequestBodyDtoSchema,
  userCreateResponseDtoSchema,
  userResponseDtoSchema,
  userUpdateRequestBodyDtoSchema,
  userUpdateResponseDtoSchema,
  validationErrorDtoSchema,
} from './schema';

export const isSystemHintDto = (data: unknown): data is SystemHintDto => {
  return systemHintDtoSchema.safeParse(data).success;
};

export const isSubjectEnumDto = (data: unknown): data is SubjectEnumDto => {
  return subjectEnumDtoSchema.safeParse(data).success;
};

export const isStopResponseStatusValueDto = (data: unknown): data is StopResponseStatusValueDto => {
  return stopResponseStatusValueDtoSchema.safeParse(data).success;
};

export const isReActModelToolTypeDto = (data: unknown): data is ReActModelToolTypeDto => {
  return reActModelToolTypeDtoSchema.safeParse(data).success;
};

export const isProblemStatusDto = (data: unknown): data is ProblemStatusDto => {
  return problemStatusDtoSchema.safeParse(data).success;
};

export const isProblemDuplicateStatusDto = (data: unknown): data is ProblemDuplicateStatusDto => {
  return problemDuplicateStatusDtoSchema.safeParse(data).success;
};

export const isMessageRoleDto = (data: unknown): data is MessageRoleDto => {
  return messageRoleDtoSchema.safeParse(data).success;
};

export const isChatStreamStatusDto = (data: unknown): data is ChatStreamStatusDto => {
  return chatStreamStatusDtoSchema.safeParse(data).success;
};

export const isProblemResponseDto = (data: unknown): data is ProblemResponseDto => {
  return problemResponseDtoSchema.safeParse(data).success;
};

export const isActiveGoalResponseDto = (data: unknown): data is ActiveGoalResponseDto => {
  return activeGoalResponseDtoSchema.safeParse(data).success;
};

export const isChatCreateRequestBodyDto = (data: unknown): data is ChatCreateRequestBodyDto => {
  return chatCreateRequestBodyDtoSchema.safeParse(data).success;
};

export const isChatDetailResponseDto = (data: unknown): data is ChatDetailResponseDto => {
  return chatDetailResponseDtoSchema.safeParse(data).success;
};

export const isChatMessageCreateRequestBodyDto = (data: unknown): data is ChatMessageCreateRequestBodyDto => {
  return chatMessageCreateRequestBodyDtoSchema.safeParse(data).success;
};

export const isChatMessageMetadataRequestDto = (data: unknown): data is ChatMessageMetadataRequestDto => {
  return chatMessageMetadataRequestDtoSchema.safeParse(data).success;
};

export const isChatMessageResponseDto = (data: unknown): data is ChatMessageResponseDto => {
  return chatMessageResponseDtoSchema.safeParse(data).success;
};

export const isChatMessageStopResponseDto = (data: unknown): data is ChatMessageStopResponseDto => {
  return chatMessageStopResponseDtoSchema.safeParse(data).success;
};

export const isChatProblemDetailResponseDto = (data: unknown): data is ChatProblemDetailResponseDto => {
  return chatProblemDetailResponseDtoSchema.safeParse(data).success;
};

export const isChatProblemResponseDto = (data: unknown): data is ChatProblemResponseDto => {
  return chatProblemResponseDtoSchema.safeParse(data).success;
};

export const isChatProblemSubmitRequestBodyDto = (data: unknown): data is ChatProblemSubmitRequestBodyDto => {
  return chatProblemSubmitRequestBodyDtoSchema.safeParse(data).success;
};

export const isChatProblemSubmitResponseDto = (data: unknown): data is ChatProblemSubmitResponseDto => {
  return chatProblemSubmitResponseDtoSchema.safeParse(data).success;
};

export const isChatQuoteSourceDto = (data: unknown): data is ChatQuoteSourceDto => {
  return chatQuoteSourceDtoSchema.safeParse(data).success;
};

export const isChatResponseDto = (data: unknown): data is ChatResponseDto => {
  return chatResponseDtoSchema.safeParse(data).success;
};

export const isChatStreamStatusResponseDto = (data: unknown): data is ChatStreamStatusResponseDto => {
  return chatStreamStatusResponseDtoSchema.safeParse(data).success;
};

export const isChatTitleUpdateRequestBodyDto = (data: unknown): data is ChatTitleUpdateRequestBodyDto => {
  return chatTitleUpdateRequestBodyDtoSchema.safeParse(data).success;
};

export const isChoiceProblemContentDto = (data: unknown): data is ChoiceProblemContentDto => {
  return choiceProblemContentDtoSchema.safeParse(data).success;
};

export const isCursorPaginateResponseChatResponseDto = (
  data: unknown,
): data is CursorPaginateResponseChatResponseDto => {
  return cursorPaginateResponseChatResponseDtoSchema.safeParse(data).success;
};

export const isCursorPaginateResponseProblemBookmarkResponseDto = (
  data: unknown,
): data is CursorPaginateResponseProblemBookmarkResponseDto => {
  return cursorPaginateResponseProblemBookmarkResponseDtoSchema.safeParse(data).success;
};

export const isDateContentDto = (data: unknown): data is DateContentDto => {
  return dateContentDtoSchema.safeParse(data).success;
};

export const isDateValueDto = (data: unknown): data is DateValueDto => {
  return dateValueDtoSchema.safeParse(data).success;
};

export const isErrorResponseDto = (data: unknown): data is ErrorResponseDto => {
  return errorResponseDtoSchema.safeParse(data).success;
};

export const isGoalCreateRequestBodyDto = (data: unknown): data is GoalCreateRequestBodyDto => {
  return goalCreateRequestBodyDtoSchema.safeParse(data).success;
};

export const isGoalResponseDto = (data: unknown): data is GoalResponseDto => {
  return goalResponseDtoSchema.safeParse(data).success;
};

export const isImagesContentDto = (data: unknown): data is ImagesContentDto => {
  return imagesContentDtoSchema.safeParse(data).success;
};

export const isImagesValueDto = (data: unknown): data is ImagesValueDto => {
  return imagesValueDtoSchema.safeParse(data).success;
};

export const isMessageAuthorDto = (data: unknown): data is MessageAuthorDto => {
  return messageAuthorDtoSchema.safeParse(data).success;
};

export const isMessageListResponseDto = (data: unknown): data is MessageListResponseDto => {
  return messageListResponseDtoSchema.safeParse(data).success;
};

export const isMessageMetadataResponseDto = (data: unknown): data is MessageMetadataResponseDto => {
  return messageMetadataResponseDtoSchema.safeParse(data).success;
};

export const isMultipleChoiceAnswerDto = (data: unknown): data is MultipleChoiceAnswerDto => {
  return multipleChoiceAnswerDtoSchema.safeParse(data).success;
};

export const isMultipleChoiceProblemResponseDto = (data: unknown): data is MultipleChoiceProblemResponseDto => {
  return multipleChoiceProblemResponseDtoSchema.safeParse(data).success;
};

export const isMultipleShortAnswerDto = (data: unknown): data is MultipleShortAnswerDto => {
  return multipleShortAnswerDtoSchema.safeParse(data).success;
};

export const isMultipleShortAnswerProblemResponseDto = (
  data: unknown,
): data is MultipleShortAnswerProblemResponseDto => {
  return multipleShortAnswerProblemResponseDtoSchema.safeParse(data).success;
};

export const isProblemBookmarkChatProblemResponseDto = (
  data: unknown,
): data is ProblemBookmarkChatProblemResponseDto => {
  return problemBookmarkChatProblemResponseDtoSchema.safeParse(data).success;
};

export const isProblemBookmarkChatResponseDto = (data: unknown): data is ProblemBookmarkChatResponseDto => {
  return problemBookmarkChatResponseDtoSchema.safeParse(data).success;
};

export const isProblemBookmarkCheckResponseDto = (data: unknown): data is ProblemBookmarkCheckResponseDto => {
  return problemBookmarkCheckResponseDtoSchema.safeParse(data).success;
};

export const isProblemBookmarkCreateRequestBodyDto = (data: unknown): data is ProblemBookmarkCreateRequestBodyDto => {
  return problemBookmarkCreateRequestBodyDtoSchema.safeParse(data).success;
};

export const isProblemBookmarkCreateResponseDto = (data: unknown): data is ProblemBookmarkCreateResponseDto => {
  return problemBookmarkCreateResponseDtoSchema.safeParse(data).success;
};

export const isProblemBookmarkResponseDto = (data: unknown): data is ProblemBookmarkResponseDto => {
  return problemBookmarkResponseDtoSchema.safeParse(data).success;
};

export const isProblemChoiceDto = (data: unknown): data is ProblemChoiceDto => {
  return problemChoiceDtoSchema.safeParse(data).success;
};

export const isProblemCreateAnswerRequestDto = (data: unknown): data is ProblemCreateAnswerRequestDto => {
  return problemCreateAnswerRequestDtoSchema.safeParse(data).success;
};

export const isProblemCreateChoiceRequestDto = (data: unknown): data is ProblemCreateChoiceRequestDto => {
  return problemCreateChoiceRequestDtoSchema.safeParse(data).success;
};

export const isProblemCreateRequestDto = (data: unknown): data is ProblemCreateRequestDto => {
  return problemCreateRequestDtoSchema.safeParse(data).success;
};

export const isProblemCreateRequestBodyDto = (data: unknown): data is ProblemCreateRequestBodyDto => {
  return problemCreateRequestBodyDtoSchema.safeParse(data).success;
};

export const isProblemCreateResponseDto = (data: unknown): data is ProblemCreateResponseDto => {
  return problemCreateResponseDtoSchema.safeParse(data).success;
};

export const isProblemLinkContentDto = (data: unknown): data is ProblemLinkContentDto => {
  return problemLinkContentDtoSchema.safeParse(data).success;
};

export const isProblemLinkValueDto = (data: unknown): data is ProblemLinkValueDto => {
  return problemLinkValueDtoSchema.safeParse(data).success;
};

export const isProblemQuoteSourceDto = (data: unknown): data is ProblemQuoteSourceDto => {
  return problemQuoteSourceDtoSchema.safeParse(data).success;
};

export const isProblemRecommendedContentDto = (data: unknown): data is ProblemRecommendedContentDto => {
  return problemRecommendedContentDtoSchema.safeParse(data).success;
};

export const isProblemRecommendedValueDto = (data: unknown): data is ProblemRecommendedValueDto => {
  return problemRecommendedValueDtoSchema.safeParse(data).success;
};

export const isQuoteContentDto = (data: unknown): data is QuoteContentDto => {
  return quoteContentDtoSchema.safeParse(data).success;
};

export const isQuoteValueDto = (data: unknown): data is QuoteValueDto => {
  return quoteValueDtoSchema.safeParse(data).success;
};

export const isShortAnswerProblemContentDto = (data: unknown): data is ShortAnswerProblemContentDto => {
  return shortAnswerProblemContentDtoSchema.safeParse(data).success;
};

export const isSingleChoiceAnswerDto = (data: unknown): data is SingleChoiceAnswerDto => {
  return singleChoiceAnswerDtoSchema.safeParse(data).success;
};

export const isSingleChoiceProblemResponseDto = (data: unknown): data is SingleChoiceProblemResponseDto => {
  return singleChoiceProblemResponseDtoSchema.safeParse(data).success;
};

export const isSingleShortAnswerDto = (data: unknown): data is SingleShortAnswerDto => {
  return singleShortAnswerDtoSchema.safeParse(data).success;
};

export const isSingleShortAnswerProblemResponseDto = (data: unknown): data is SingleShortAnswerProblemResponseDto => {
  return singleShortAnswerProblemResponseDtoSchema.safeParse(data).success;
};

export const isSystemMessageResponseDto = (data: unknown): data is SystemMessageResponseDto => {
  return systemMessageResponseDtoSchema.safeParse(data).success;
};

export const isTextContentDto = (data: unknown): data is TextContentDto => {
  return textContentDtoSchema.safeParse(data).success;
};

export const isTextValueDto = (data: unknown): data is TextValueDto => {
  return textValueDtoSchema.safeParse(data).success;
};

export const isToolInfoDto = (data: unknown): data is ToolInfoDto => {
  return toolInfoDtoSchema.safeParse(data).success;
};

export const isToolValueDictDto = (data: unknown): data is ToolValueDictDto => {
  return toolValueDictDtoSchema.safeParse(data).success;
};

export const isUnknownConceptCreateRequestBodyDto = (data: unknown): data is UnknownConceptCreateRequestBodyDto => {
  return unknownConceptCreateRequestBodyDtoSchema.safeParse(data).success;
};

export const isUnknownConceptResponseDto = (data: unknown): data is UnknownConceptResponseDto => {
  return unknownConceptResponseDtoSchema.safeParse(data).success;
};

export const isUploadUrlRequestDto = (data: unknown): data is UploadUrlRequestDto => {
  return uploadUrlRequestDtoSchema.safeParse(data).success;
};

export const isUploadUrlResponseDto = (data: unknown): data is UploadUrlResponseDto => {
  return uploadUrlResponseDtoSchema.safeParse(data).success;
};

export const isUserCreateRequestBodyDto = (data: unknown): data is UserCreateRequestBodyDto => {
  return userCreateRequestBodyDtoSchema.safeParse(data).success;
};

export const isUserCreateResponseDto = (data: unknown): data is UserCreateResponseDto => {
  return userCreateResponseDtoSchema.safeParse(data).success;
};

export const isUserResponseDto = (data: unknown): data is UserResponseDto => {
  return userResponseDtoSchema.safeParse(data).success;
};

export const isUserUpdateRequestBodyDto = (data: unknown): data is UserUpdateRequestBodyDto => {
  return userUpdateRequestBodyDtoSchema.safeParse(data).success;
};

export const isUserUpdateResponseDto = (data: unknown): data is UserUpdateResponseDto => {
  return userUpdateResponseDtoSchema.safeParse(data).success;
};

export const isValidationErrorDto = (data: unknown): data is ValidationErrorDto => {
  return validationErrorDtoSchema.safeParse(data).success;
};

export const isGetChatsChatsGetQueryParams = (data: unknown): data is GetChatsChatsGetQueryParams => {
  return getChatsChatsGetQueryParamsSchema.safeParse(data).success;
};

export const isCreateProblemsProblemsPostHeaders = (data: unknown): data is CreateProblemsProblemsPostHeaders => {
  return createProblemsProblemsPostHeadersSchema.safeParse(data).success;
};

export const isUploadFileUploadsKeyPutQueryParams = (data: unknown): data is UploadFileUploadsKeyPutQueryParams => {
  return uploadFileUploadsKeyPutQueryParamsSchema.safeParse(data).success;
};

export const isGetProblemBookmarksProblemBookmarksGetQueryParams = (
  data: unknown,
): data is GetProblemBookmarksProblemBookmarksGetQueryParams => {
  return getProblemBookmarksProblemBookmarksGetQueryParamsSchema.safeParse(data).success;
};

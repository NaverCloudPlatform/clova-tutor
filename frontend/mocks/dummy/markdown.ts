/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

export const MARKDOWN_DUMMY = `
## 근의 공식 증명

일반적인 이차방정식은 다음과 같습니다:

$$ ax^2 + bx + c = 0 $$

여기서 $$a \\neq 0$$ 입니다.

이 방정식의 근을 구하기 위해, 먼저 방정식을 $$ x $$에 대한 식으로 정리해야 합니다.

1. 우선 방정식을 $$ a $$로 나누어 정리합니다:
   
   $$ x^2 + \\frac{b}{a}x + \\frac{c}{a} = 0 $$

2. 이차항의 계수가 1이 되도록 조정한 다음, $$ x $$의 계수의 절반의 제곱을 더하고 뺍니다. 이를 완전제곱식으로 만들기 위함입니다:
   
   $$ x^2 + \\frac{b}{a}x + \\left(\\frac{b}{2a}\\right)^2 - \\left(\\frac{b}{2a}\\right)^2 + \\frac{c}{a} = 0 $$

3. 위 식을 재정리하여 완전제곱식을 만들고, 나머지 항을 우측으로 이동시킵니다:
   
   $$ \\left(x + \\frac{b}{2a}\\right)^2 = \\left(\\frac{b}{2a}\\right)^2 - \\frac{c}{a} $$

4. 양변의 제곱근을 취합니다:
   
   $$ x + \\frac{b}{2a} = \\pm \\sqrt{\\left(\\frac{b}{2a}\\right)^2 - \\frac{c}{a}} $$

5. 마지막으로, $$ x $$에 대해 풀면 근의 공식을 얻습니다:
   
   $$ x = -\\frac{b}{2a} \\pm \\sqrt{\\left(\\frac{b}{2a}\\right)^2 - \\frac{c}{a}} $$

   이를 좀 더 간단하게 표현하면:

   $$ x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a} $$

위 식이 바로 이차방정식의 근을 구하는 공식, 즉 근의 공식입니다.
`;

export const TRANSLATION_DUMMY = `
직독직해로 해석해줄게

\`\`\`json
{
   "type": "translation",
   "content": [
     { "en": "Some laws, *policies*, and practices", "ko": "\`일부 법률\`, \`정책\`, 그리고 \`관행\`은" },
     { "en": "are ~~developed~~", "ko": "만들어진다" },
     { "en": "without a <u>conscious intent to discriminate</u>", "ko": "**차별하려는 의식적인 의도** 없이" },
     { "en": "and may appear", "ko": "그리고 보일 수도 있다" },
     { "en": "ethnically neutral and impersonal", "ko": "인종적으로 중립적이고 비인격적인 것으로" }
   ]
}
\`\`\`
`;

export const CALLOUT_DUMMY = `
> [!quote]+ 직독직해로 해석해줄게
> 짜잔 직독직해야!
>\`\`\`json
>{
>   "type": "translation",
>   "content": [
>     { "en": "Some laws, *policies*, and practices", "ko": "\`일부 법률\`, \`정책\`, 그리고 \`관행\`은" },
>     { "en": "are ~~developed~~", "ko": "만들어진다" },
>     { "en": "without a <u>conscious intent to discriminate</u>", "ko": "**차별하려는 의식적인 의도** 없이" },
>     { "en": "and may appear", "ko": "그리고 보일 수도 있다" },
>     { "en": "ethnically neutral and impersonal", "ko": "인종적으로 중립적이고 비인격적인 것으로" }
>   ]
>}
>\`\`\`
>
>| sdfsdfs | sdfsdf |
>|---------|--------|
>| sdfsdf  | sdfsdf |
>| sdfsdf  | sdfsdf |
>> [!note]- 중첩된 콜아웃도 가능!
>> sdfasfsfsdf
>> dfsdfds
>
`;

export const MARKDOWN_DUMMY_JSON = `
직독직해로 해석해줄게

\`\`\`json
{
   "type": "translation",
   "content": [
     { "en": "Some laws, *policies*, and practices", "ko": "\`일부 법률\`, \`정책\`, 그리고 \`관행\`은" },
     { "en": "are ~~developed~~", "ko": "만들어진다" },
     { "en": "without a <u>conscious intent to discriminate</u>", "ko": "**차별하려는 의식적인 의도** 없이" },
     { "en": "and may appear", "ko": "그리고 보일 수도 있다" },
     { "en": "ethnically neutral and impersonal", "ko": "인종적으로 중립적이고 비인격적인 것으로" }
   ]
}
\`\`\`

| sdfsdfs | sdfsdf |
|---------|--------|
| sdfsdf  | sdfsdf |
| sdfsdf  | sdfsdf |

> [!{tool_name}]+
> 짜잔 직독직해야!
>\`\`\`json
>{
>   "type": "translation",
>   "content": [
>     { "en": "Some laws, *policies*, and practices", "ko": "\`일부 법률\`, \`정책\`, 그리고 \`관행\`은" },
>     { "en": "are ~~developed~~", "ko": "만들어진다" },
>     { "en": "without a <u>conscious intent to discriminate</u>", "ko": "**차별하려는 의식적인 의도** 없이" },
>     { "en": "and may appear", "ko": "그리고 보일 수도 있다" },
>     { "en": "ethnically neutral and impersonal", "ko": "인종적으로 중립적이고 비인격적인 것으로" }
>   ]
>}
>\`\`\`
>
>| sdfsdfs | sdfsdf |
>|---------|--------|
>| sdfsdf  | sdfsdf |
>| sdfsdf  | sdfsdf |
>> [!note]- 참고
>> sdfasfsfsdf
>> dfsdfds
>

\`inline code\`
  
좀 이해가 되니?
`;

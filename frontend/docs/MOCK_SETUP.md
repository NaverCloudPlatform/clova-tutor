# MSW Mock 데이터 설정

HAR 파일을 MSW(Mock Service Worker) 형식으로 변환하여 API Mocking을 설정하는 가이드입니다.

## 목차

- [개요](#개요)
- [HAR 파일이란](#har-파일이란)
- [빠른 시작](#빠른-시작)
- [HAR 파일 수집](#har-파일-수집)
- [Mock 변환](#mock-변환)
- [시나리오 사용](#시나리오-사용)
- [작동 원리](#작동-원리)
- [고급 사용법](#고급-사용법)
- [트러블슈팅](#트러블슈팅)

## 개요

MSW를 사용하여 실제 백엔드 없이도 프론트엔드 개발과 테스트를 진행할 수 있습니다. HAR 파일을 변환하여 실제 API 응답을 재현합니다.

### 장점

- **백엔드 독립**: 백엔드 서버 없이도 개발 가능
- **안정적인 테스트**: 일관된 데이터로 E2E 테스트
- **시나리오 재현**: 특정 케이스를 반복 테스트

## HAR 파일이란

[HAR](http://www.softwareishard.com/blog/har-12-spec/)은 웹 브라우저와 서버 간의 HTTP 통신을 기록한 JSON 형식의 파일입니다.

## 빠른 시작

### 1. HAR 파일 수집

Chrome DevTools에서 네트워크 활동을 HAR로 저장:

```bash
# Chrome DevTools (F12) 열기
# Network 탭 선택
# 원하는 작업 수행 (예: 로그인, 채팅)
# 우클릭 > "Save all as HAR with content"
```

### 2. Mock 변환

```bash
# HAR 파일을 mocks/__data__/network-logs/에 저장
cp ~/Downloads/example.har mocks/__data__/network-logs/

# Mock 데이터로 변환
yarn mock:convert
```

### 3. 시나리오 활성화

network-log-scenario.handlers.ts에 데이터 등록  
URL에 시나리오 파라미터 추가:

```
http://localhost:5173?scenario=TC-4.6
```

## HAR 파일 수집

### Chrome DevTools 사용

1. **DevTools 열기**: `F12` 또는 `Cmd+Option+I` (Mac)
2. **Network 탭** 선택
3. **Preserve log** 체크 ✅ (페이지 이동 시에도 로그 유지)
4. **녹화 시작**: 빨간 점이 활성화되어 있는지 확인
5. **작업 수행**: 테스트하려는 시나리오 실행
6. **HAR 저장**:
   - Network 탭에서 우클릭
   - **"Save all as HAR with content"** 선택
   - 파일명: `tc-4.6.har` (테스트 케이스 번호 사용)

### 파일 저장 위치

```bash
mocks/__data__/network-logs/tc-4.6.har
```

### 네이밍 규칙

테스트 케이스 번호를 파일명으로 사용:

```
TC-1.2.har   # 로그인 테스트
TC-4.6.har   # 채팅 입력 테스트
TC-7.1.har   # 문제 콘텐츠 테스트
```

## Mock 변환

### 변환 스크립트 실행

```bash
yarn mock:convert
```

### 변환된 파일 구조

```json
[
  {
    "id": "uuid",
    "version": "1.1",
    "request": {
      "method": "POST",
      "url": "http://localhost:8000/api/v1/chats/314/messages",
      "headers": { "content-type": "application/json" },
      "payload": { "text": "안녕하세요" },
      "timestamp": 1765728503524
    },
    "response": {
      "mode": "single",  // 또는 "event-stream"
      "status": 200,
      "headers": { "content-type": "application/json" },
      "body": { "id": 1, "text": "안녕하세요" },
      "timestamp": 1765728503600
    }
  }
]
```

## 시나리오 사용

### 시나리오 등록

`mocks/__handlers__/network-log-scenario.handlers.ts`에 추가:

```typescript
const SCENARIO_JSON_MAP = {
  'TC-4.6': () => import('../__data__/network-logs/tc-4.6.json').then((m) => m.default),
  'TC-7.1': () => import('../__data__/network-logs/tc-7.1.json').then((m) => m.default),
};
```

### 브라우저에서 활성화

URL 쿼리 파라미터로 시나리오 지정:

```
http://localhost:5173?scenario=TC-4.6
```

### DevTools 확인

MSW가 활성화되면 콘솔에 다음 메시지 표시:

```
[MSW] 시나리오 활성화: TC-4.6
[MSW] 시나리오 로드 완료: TC-4.6 (10개 핸들러)
[MSW] Mocking enabled.
```

### Network 탭 확인

MSW가 가로채는 요청은 다음과 같이 표시됩니다:

```
Status: 200 OK (from ServiceWorker)
X-Call-Count: 1/5  // 동일 엔드포인트 호출 횟수
```

## 고급 사용법

### 1. 시나리오 커스터마이징

특정 응답을 수정하려면 JSON 파일을 직접 편집:

```json
{
  "response": {
    "mode": "single",
    "body": {
      "id": 999,
      "text": "커스텀 응답"  // 수정
    }
  }
}
```

### 2. E2E 테스트와 통합

Playwright 테스트에서 시나리오 활성화:

```typescript
test('채팅 입력 테스트', async ({ page }) => {
  // 시나리오 활성화
  await page.goto('http://localhost:5173?scenario=TC-4.6');
  
  // 테스트 수행
  await page.fill('textarea', '안녕하세요');
  await page.click('button[type="submit"]');
  
  // Mock 데이터로 응답 확인
  await expect(page.locator('.message')).toContainText('안녕하세요');
});
```

## 참고 자료

- [MSW 공식 문서](https://mswjs.io/)
- [HAR 스펙](http://www.softwareishard.com/blog/har-12-spec/)
- [Chrome DevTools Network](https://developer.chrome.com/docs/devtools/network/)


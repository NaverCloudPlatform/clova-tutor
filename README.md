<div align="center">

<img src="./docs/static/img/title-logo.svg" height="60"/>

# CLOVA Tutor

**초·중등 학습자를 위한 대화형 AI 튜터 데모 프로젝트**

[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)

[**Documentation**](https://your-docs-url.com) · [**Quick Start**](#quick-start) · [**Demo**](#demo)

</div>

---

![CLOVA Tutor Hero](./docs/static/img/hero-img.png)

## About

**CLOVA Tutor**는 Naver Cloud의 HCX-005 모델을 기반으로 한 **대화 중심 AI 튜터 데모 프로젝트**입니다.

하나의 채팅 인터페이스에서 수학·영어 문제 풀이, 개념 설명, 학습 목표 설정, 복습 관리를 통합적으로 경험할 수 있습니다.

> 본 프로젝트는 **대화 기반 학습 경험과 AI 튜터 UX 구조를 탐구하기 위한 오픈소스 데모**입니다.

---

## Demo

### 📐 수학 튜터

<table>
<tr>
<td width="50%" align="center">

**개념 설명 & 문제 추천**

![수학 개념 설명과 문제 추천](./docs/static/img/수학%20개념%20설명과%20문제추천.gif)

</td>
<td width="50%" align="center">

**문제 풀이 & 단계적 교수**

![수학 문제 풀이와 단계적 교수](./docs/static/img/수학%20문제%20풀이와%20단계적%20교수.gif)

</td>
</tr>
</table>

### 📖 영어 튜터

<table>
<tr>
<td width="50%" align="center">

**단어 설명 & 직독직해**

![영어 단어 설명과 직독직해](./docs/static/img/영어%20단어%20설명과%20직독직해.gif)

</td>
<td width="50%" align="center">

**문법 설명 & 문제 추천**

![영어 문법 설명과 문제 추천](./docs/static/img/영어%20문법%20설명과%20문제추천.gif)

</td>
</tr>
</table>

### 🎯 학습 관리

- **학습 목표 설정 & 달성**: 채팅방에서 목표를 정하면 튜터가 그에 맞는 피드백을 제공합니다.
- **학습 노트 저장**: 풀이와 해설을 저장해 복습하고, 다시 풀기·원본 대화로 이동할 수 있습니다.

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) / [Docker Compose](https://docs.docker.com/compose/install/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### 1. 환경 설정

```bash
cp .env.example .env
# .env 파일에서 필수 환경 변수 설정 (HCX_API_KEY, CLOVA_STUDIO_* 등)
```

### 2. 서비스 시작

```bash
docker compose up -d
cd backend && make init
cd model-server && make setup
```

### 3. 접속

- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

> 상세한 설정 방법은 [Documentation](https://your-docs-url.com)을 참고하세요.

---

## Documentation

자세한 내용은 문서를 참고하세요:

- [프로젝트 개요](https://your-docs-url.com/docs/introduction/overview)
- [사용자 가이드](https://your-docs-url.com/docs/user-guide/start)
- [개발자 가이드](https://your-docs-url.com/docs/dev-guide/quick-start)
- [환경 변수 설정](https://your-docs-url.com/docs/dev-guide/environment-variables)

---

## License

This project is licensed under the [MIT License](LICENSE).

```
CLOVA Tutor
Copyright (c) 2026-present NAVER Cloud Corp.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

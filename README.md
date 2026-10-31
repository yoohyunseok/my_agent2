# 💱 실시간 환율 챗봇

[Frankfurter Exchange Rates API](https://frankfurter.dev/)와 Streamlit으로 만든 환율 조회 챗봇입니다.
"100달러는 원화로 얼마야?"처럼 자연어로 질문하면 최신 환율을 조회해 환산 결과를 알려줍니다.

## 주요 기능

- 자연어 질문을 OpenAI 모델(`gpt-5.4-mini`)이 해석해 통화 코드와 금액을 추출 (function calling)
- 질문할 때마다 Frankfurter API로 최신 일별 기준 환율 조회
- 환산 금액은 모델이 아닌 코드에서 계산해 숫자 오류 방지
- 기준 통화, 대상 통화, 1단위 환율, 환산 금액, 환율 기준일을 정리해서 답변
- 이전 대화 맥락을 유지하는 채팅 UI

> Frankfurter 환율은 실시간 금융시장 체결가가 아니라 **최신 일별 기준 환율**입니다.

## 질문 예시

- 100달러는 원화로 얼마야?
- 1유로는 엔화로 얼마야?

## 기술 스택

| 구분 | 사용 기술 |
| --- | --- |
| UI | Streamlit |
| LLM | OpenAI API (`gpt-5.4-mini`) |
| 환율 데이터 | Frankfurter API (`https://api.frankfurter.dev/v1/latest`) |
| 환경 변수 | python-dotenv |

## 프로젝트 구조

```
my_agent2/
├── app.py                 # 챗봇 앱 (환율 조회 도구 + OpenAI 호출 + UI)
├── requirements.txt       # 패키지 의존성
├── .streamlit/
│   └── config.toml        # 테마 설정 (라이트 모드, 초록 강조색)
├── .env                   # API Key (Git에 올라가지 않음)
└── .gitignore
```

## 실행 방법

### 1. 가상환경 생성 및 활성화

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. API Key 설정

프로젝트 루트에 `.env` 파일을 만들고 OpenAI API Key를 넣습니다. Frankfurter API는 키가 필요 없습니다.

```
OPENAI_API_KEY=sk-...
```

`.env`는 `.gitignore`에 포함되어 있어 GitHub에 올라가지 않습니다.

### 4. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`이 열립니다.

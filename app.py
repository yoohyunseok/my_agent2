import json

import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = "gpt-5.4-mini"
FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"

SYSTEM_PROMPT = """너는 환율 안내 챗봇이다. 환율이나 환산 질문이 오면 반드시 get_exchange_rate 도구로 최신 환율을 조회한 뒤 답한다.
- 통화는 ISO 4217 코드로 변환한다 (달러→USD, 원→KRW, 엔→JPY, 유로→EUR, 위안→CNY 등).
- 금액이 없으면 amount=1로 조회한다.
- 답변 형식(마크다운):
  첫 줄: "{금액}{통화명}({코드})는 **{환산금액}{통화명}({코드})** 입니다."
  이어서 목록: 기준 통화, 대상 통화, 1 {기준} 환율, 환산 금액, 환율 기준일
  마지막 줄: "참고로 Frankfurter 환율은 실시간 체결가가 아니라 **최신 일별 기준 환율**입니다."
- 도구 결과의 숫자만 사용하고 직접 계산하거나 추측하지 않는다.
- 환율과 무관한 질문에는 환율 관련 질문만 도와줄 수 있다고 짧게 안내한다."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Frankfurter API로 최신 일별 기준 환율을 조회하고 금액을 환산한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base": {"type": "string", "description": "기준 통화 ISO 코드 (예: USD)"},
                    "target": {"type": "string", "description": "대상 통화 ISO 코드 (예: KRW)"},
                    "amount": {"type": "number", "description": "환산할 금액"},
                },
                "required": ["base", "target", "amount"],
            },
        },
    }
]


def get_exchange_rate(base: str, target: str, amount: float) -> dict:
    base, target = base.upper(), target.upper()
    resp = requests.get(FRANKFURTER_URL, params={"base": base, "symbols": target}, timeout=10)
    if resp.status_code != 200:
        return {"error": f"환율 조회 실패 ({resp.status_code}): {resp.text}"}
    data = resp.json()
    rate = data["rates"][target]
    return {
        "base": base,
        "target": target,
        "rate": rate,
        "amount": amount,
        "converted": round(amount * rate, 2),
        "date": data["date"],
    }


def answer(messages: list[dict]) -> str:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    while True:
        response = client.chat.completions.create(model=MODEL, messages=msgs, tools=TOOLS)
        msg = response.choices[0].message
        if not msg.tool_calls:
            return msg.content
        msgs.append(msg)
        for call in msg.tool_calls:
            result = get_exchange_rate(**json.loads(call.function.arguments))
            msgs.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result, ensure_ascii=False)})


CSS = """
<style>
@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");
html, body, .stMarkdown, textarea { font-family: "Pretendard", sans-serif !important; }
header[data-testid="stHeader"] { background: transparent; }
.block-container, [data-testid="stBottomBlockContainer"] { max-width: 480px; }
.block-container { padding-top: 2.5rem; }

.steps { display: flex; align-items: center; margin-bottom: 28px; }
.steps span { width: 24px; height: 24px; border-radius: 50%; background: #03A94E; color: #fff;
  font-size: 13px; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.steps i { width: 20px; height: 2px; background: #03A94E; }
.title { font-size: 26px; font-weight: 800; line-height: 1.45; color: #111; margin: 0 0 12px; }
.subtitle { font-size: 16px; line-height: 1.6; color: #8B8F97; margin-bottom: 28px; }
.notice { display: flex; gap: 12px; align-items: flex-start; background: #F0F1F4; border-radius: 16px;
  padding: 18px 20px; margin-bottom: 12px; font-size: 15px; line-height: 1.6; color: #222; }
.notice b.icon { flex: none; width: 22px; height: 22px; border-radius: 50%; background: #111; color: #fff;
  font-size: 13px; display: flex; align-items: center; justify-content: center; margin-top: 1px; }
.notice code { background: #fff; color: #03A94E; border-radius: 6px; padding: 1px 6px; }

[data-testid="stChatMessage"] { background: #F7F8FA; border-radius: 16px; padding: 16px; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) { background: #fff; border: 1px solid #E5E7EB; }
[data-testid="stChatInput"] { border-radius: 16px; }
[data-testid="stChatInputSubmitButton"] { background: #03A94E !important; color: #fff !important; border-radius: 12px; }
</style>
"""

st.set_page_config(page_title="실시간 환율 챗봇", page_icon="💱", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(
    """
    <div class="steps"><span>$</span><i></i><span>₩</span><i></i><span>¥</span></div>
    <div class="title">궁금한 환율을<br>바로 알려드릴게요</div>
    <div class="subtitle">질문할 때마다 Frankfurter의<br>최신 일별 기준 환율을 조회해요.</div>
    <div class="notice"><b class="icon">!</b><div>이렇게 물어보세요<br><code>100달러는 원화로 얼마야?</code> <code>1유로는 엔화로 얼마야?</code></div></div>
    <div class="notice"><b class="icon">!</b><div>실시간 금융시장 체결가가 아니라<br>하루 단위 기준 환율이에요.</div></div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("환율이나 환산할 금액을 질문해 보세요."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("환율 조회 중..."):
            reply = answer(st.session_state.messages)
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

# Day2

에이전틱 AI 기술 기반 시스템 구축 및 운영 전문 과정

---

# 강의 노트

| 교시 | 시간 | 파일 | 주제 | 상태 |
|------|------|------|------|------|
| 1교시 | 09:30 | [Hour0930.md](Hour0930.md) | Microsoft Agent Framework 입문 | 완료 |
| 2교시 | 10:30 | [Hour1030.md](Hour1030.md) | Agent의 기억과 Tool Calling | 완료 |
| 3교시 | 11:30 | [Hour1130.md](Hour1130.md) | Session과 Multi-turn Conversation | 완료 |

---

# 실습 코드

| 파일 | 내용 |
|------|------|
| [src/hello_agent.py](src/hello_agent.py) | 첫 Agent 생성과 기본 실행 |
| [src/add_tools.py](src/add_tools.py) | 날씨 Tool 등록과 Tool Calling |
| [src/multi_turn.py](src/multi_turn.py) | Session 기반 Multi-turn과 Multi Tool Calling |

---

# 현재까지 진행 내용

## Hour0930

- Data Types: Markdown, JSON, CSV, XML
- Microsoft Agent Framework 개념
- AutoGen + Semantic Kernel
- LangChain, n8n, LangGraph 비교
- Agent Framework 설치
- `hello_agent.py` 기본 골격 작성

## Hour1030

- LLM은 Stateless
- AgentSession과 Memory
- InMemoryChatHistoryProvider / CustomChatHistoryProvider
- Context Window 한계
- Tool Calling
- `get_weather()` Tool 구현
- Tool 결과 신뢰와 Tool 품질의 중요성

## Hour1130

- Session을 이용한 Multi-turn Conversation
- AI Debt 개념
- 주요 AI 코딩 도구
- Multi Tool Calling
- `get_exchange_money()` 환율 Tool 구현
- 날씨와 환율을 결합한 복합 질문 처리

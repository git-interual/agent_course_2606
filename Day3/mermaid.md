# AI Agent 기반 SaaS 플랫폼 설계 문서

## 1. 프로젝트 개요

프로젝트명: AI Agent Workflow Studio

목표:
- 자연어 기반 Workflow 생성
- Agent 자동 연결
- Tool Calling 지원
- SaaS 형태 서비스 제공

주요 기술:
- GPT-5
- Microsoft Agent Framework
- n8n
- PostgreSQL
- Node.js
- Azure OpenAI

---

# 2. 프로젝트 구조 (Mindmap)

```mermaid
mindmap
  root((AI Agent Workflow Studio))
    Frontend
      React
      Tailwind
      Mermaid
    Backend
      Node.js
      Express
      PostgreSQL
    AI
      GPT-5
      Embedding
      RAG
      Tool Calling
    Agent
      Planner
      Executor
      Reviewer
    Infra
      Azure
      Docker
      Nginx
```

---

# 3. 사용자 Workflow

```mermaid
flowchart TD

A[사용자 요청] --> B[Workflow 생성]

B --> C{기존 템플릿 존재?}

C -->|Yes| D[템플릿 로드]
C -->|No| E[새 Workflow 생성]

D --> F[Agent 실행]
E --> F

F --> G[Tool 호출]

G --> H{성공?}

H -->|Yes| I[결과 반환]
H -->|No| J[재시도]

J --> G
```

---

# 4. Agent 호출 Sequence

```mermaid
sequenceDiagram

participant User
participant Planner
participant Executor
participant Tool
participant DB

User->>Planner: 보고서 작성

Planner->>Executor: 계획 전달

Executor->>Tool: 데이터 조회

Tool->>DB: SQL 실행

DB-->>Tool: 데이터 반환

Tool-->>Executor: 결과

Executor-->>Planner: 완료

Planner-->>User: 최종 보고서
```

---

# 5. 상태 전이도

```mermaid
stateDiagram-v2

[*] --> Draft

Draft --> Reviewing
Reviewing --> Approved
Reviewing --> Rejected

Rejected --> Draft

Approved --> Published

Published --> Archived

Archived --> [*]
```

---

# 6. 클래스 구조

```mermaid
classDiagram

class Agent {
    +id
    +name
    +execute()
}

class PlannerAgent {
    +plan()
}

class ExecutorAgent {
    +run()
}

class ReviewAgent {
    +review()
}

Agent <|-- PlannerAgent
Agent <|-- ExecutorAgent
Agent <|-- ReviewAgent
```

---

# 7. 데이터베이스 설계

```mermaid
erDiagram

USER ||--o{ PROJECT : owns
PROJECT ||--o{ WORKFLOW : contains
WORKFLOW ||--o{ AGENT : executes
AGENT ||--o{ EXECUTION_LOG : creates

USER {
    int id
    string email
    string name
}

PROJECT {
    int id
    string title
    datetime created_at
}

WORKFLOW {
    int id
    string workflow_name
}

AGENT {
    int id
    string type
}

EXECUTION_LOG {
    int id
    datetime executed_at
    string result
}
```

---

# 8. 고객 여정

```mermaid
journey

title AI Agent Workflow Studio 사용자 경험

section 가입
회원가입: 5: 사용자
이메일인증: 4: 사용자

section 프로젝트 생성
프로젝트 생성: 5: 사용자
Workflow 생성: 5: 사용자

section Agent 실행
실행: 5: 사용자
결과확인: 5: 사용자

section SaaS 결제
결제: 4: 사용자
구독유지: 5: 사용자
```

---

# 9. 개발 일정

```mermaid
gantt

title AI Agent SaaS 개발 일정

dateFormat YYYY-MM-DD

section 기획
요구사항 분석 :done, a1, 2026-06-01, 7d
화면설계 :done, a2, after a1, 5d

section 개발
Backend :active, b1, 2026-06-15, 20d
Frontend :b2, 2026-06-20, 15d
AI Agent :b3, 2026-06-25, 20d

section 테스트
통합테스트 :c1, after b3, 10d

section 배포
Azure 배포 :c2, after c1, 5d
```

---

# 10. SaaS 매출 구성

```mermaid
pie title 2026년 예상 매출

"구독형 SaaS" : 55
"SI 구축" : 20
"컨설팅" : 10
"교육" : 10
"기술지원" : 5
```

---

# 11. Git Flow

```mermaid
gitGraph

commit id:"v1.0"

branch develop

checkout develop

commit id:"API"

commit id:"Agent"

branch feature-ui

checkout feature-ui

commit id:"Dashboard"

commit id:"Workflow"

checkout develop

merge feature-ui

checkout main

merge develop

commit id:"Release 1.1"
```

---

# 12. 요구사항

```mermaid
requirementDiagram

requirement login {
    id: R1
    text: OAuth 로그인 지원
    risk: low
    verifymethod: test
}

requirement workflow {
    id: R2
    text: Workflow 생성
    risk: medium
    verifymethod: demo
}

requirement agent {
    id: R3
    text: Agent 실행
    risk: high
    verifymethod: test
}

login - contains -> workflow
workflow - contains -> agent
```

---

# 13. 서비스 발전 Timeline

```mermaid
timeline

title AI Agent Workflow Studio

2025
    아이디어 기획

2026
    MVP 개발
    SaaS 베타

2027
    글로벌 출시
    Agent Marketplace

2028
    AI Workflow Ecosystem 구축

2029
    IPO 검토
```

---

# 14. 경쟁사 비교

```mermaid
quadrantChart

title AI Workflow 플랫폼 비교

x-axis 저비용 --> 고비용
y-axis 저성능 --> 고성능

Zapier:[0.6,0.5]
n8n:[0.4,0.7]
LangGraph:[0.7,0.9]
AI Agent Workflow Studio:[0.5,0.95]
```

---

# 15. 시스템 컨텍스트 (C4)

```mermaid
C4Context

title AI Agent Workflow Studio

Person(user, "사용자")

System(platform, "Workflow Platform")

System_Ext(openai, "Azure OpenAI")

System_Ext(postgres, "PostgreSQL")

Rel(user, platform, "사용")
Rel(platform, openai, "LLM 호출")
Rel(platform, postgres, "데이터 저장")
```

---

# 16. 배포 아키텍처

```mermaid
flowchart LR

User --> Nginx

Nginx --> Frontend

Nginx --> Backend

Backend --> PostgreSQL

Backend --> AzureOpenAI

Backend --> AgentFramework

AgentFramework --> ToolServer
```

---

# 17. 결론

본 시스템은

- AI Agent
- Workflow 자동화
- SaaS 플랫폼
- Tool Calling
- RAG
- Multi-Agent

를 통합한 차세대 업무 자동화 플랫폼을 목표로 한다.
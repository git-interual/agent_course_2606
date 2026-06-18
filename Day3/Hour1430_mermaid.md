# 4~5교시 Mermaid 다이어그램 모음

## 1. Azure AI Search 전체 구조

```mermaid
flowchart LR

    DS["Data Source<br/>(PDF, DB, Files)"]

    IDXER["Indexer"]

    IDX["Index"]

    USER["User"]

    DS --> IDXER
    IDXER --> IDX
    USER --> IDX
```

---

## 2. Azure AI Search + RAG 구조

```mermaid
flowchart LR

    PDF["PDF 문서"]

    CHUNK["Chunking"]

    EMB["Embedding Model"]

    VECTOR["Vector Store"]

    PDF --> CHUNK
    CHUNK --> EMB
    EMB --> VECTOR
```

---

## 3. PDF → Chunk → Vector 생성 과정

```mermaid
flowchart LR

    PDF["PDF"]

    C1["Chunk 1"]
    C2["Chunk 2"]
    C3["Chunk 3"]

    EMB["Embedding Model"]

    V1["Vector"]
    V2["Vector"]
    V3["Vector"]

    PDF --> C1
    PDF --> C2
    PDF --> C3

    C1 --> EMB
    C2 --> EMB
    C3 --> EMB

    EMB --> V1
    EMB --> V2
    EMB --> V3
```

---

## 4. 문서 등록 과정

```mermaid
flowchart LR

    PDF["PDF 문서"]

    CHUNK["Chunking<br/>1024 Tokens"]

    EMB["text-embedding-3-small"]

    VECTOR["1536차원 Vector"]

    INDEX["Azure AI Search Index"]

    PDF --> CHUNK
    CHUNK --> EMB
    EMB --> VECTOR
    VECTOR --> INDEX
```

---

## 5. 검색(Query) 과정

```mermaid
flowchart LR

    USER["사용자 질문"]

    EMB["text-embedding-3-small"]

    QUERYV["Query Vector"]

    VECTOR["Vector Store"]

    RESULT["관련 Chunk"]

    USER --> EMB
    EMB --> QUERYV
    QUERYV --> VECTOR
    VECTOR --> RESULT
```

---

## 6. Embedding Model은 운영 중에도 사용

```mermaid
flowchart LR

    PDF["문서"]

    EMB["Embedding Model"]

    VS["Vector Store"]

    QUERY["사용자 질문"]

    PDF --> EMB
    EMB --> VS

    QUERY --> EMB
    EMB --> VS
```

설명:

- 문서 등록 시 사용
- 사용자 검색 시 사용
- 운영 중에도 계속 필요

---

## 7. Vector DB (Vector Store)

```mermaid
flowchart LR

    PDF["PDF"]

    CHUNK["Chunk"]

    EMB["Embedding"]

    VECTOR["Vector"]

    STORE["Vector Store"]

    PDF --> CHUNK
    CHUNK --> EMB
    EMB --> VECTOR
    VECTOR --> STORE
```

---

## 8. Azure AI Search + Azure OpenAI 연동

```mermaid
flowchart LR

    PDF["Tesla + 대동 매뉴얼"]

    SEARCH["Azure AI Search"]

    OPENAI["Azure OpenAI"]

    PDF --> SEARCH

    OPENAI --> SEARCH
```

---

## 9. 최종 Vector Search 구조

```mermaid
flowchart LR

    PDF["PDF"]

    CHUNK["Chunking<br/>1024 Tokens"]

    EMB["text-embedding-3-small<br/>1536 Dimensions"]

    VECTOR["Vector Store"]

    PDF --> CHUNK
    CHUNK --> EMB
    EMB --> VECTOR
```

---

## 10. 이미지 벡터화(Image Vectorization)

Google Photos 예시

```mermaid
flowchart LR

    IMG["이미지"]

    EMB["Image Embedding Model"]

    VS["Vector Store"]

    QUERY["검색어"]

    IMG --> EMB
    EMB --> VS

    QUERY --> EMB
    EMB --> VS
```

예)

- 비행기
- 개
- 밤
- 판교
- 뉴욕

---

## 11. Azure Data Box

```mermaid
flowchart LR

    A["회사 데이터센터"]

    B["Azure Data Box"]

    C["Microsoft 데이터센터"]

    D["Azure Storage"]

    A -->|데이터 복사| B
    B -->|택배 발송| C
    C --> D
```

대용량 데이터(수십~수백 TB)를 물리 장비로 이전하는 방식

---

## 12. Azure AI Search 전체 RAG 파이프라인

```mermaid
flowchart LR

    PDF["PDF 문서"]

    CHUNK["Chunking"]

    EMB["text-embedding-3-small"]

    VECTOR["Vector Index"]

    QUERY["사용자 질문"]

    PDF --> CHUNK
    CHUNK --> EMB
    EMB --> VECTOR

    QUERY --> EMB
    EMB --> VECTOR
```

설명:

- PDF와 질문 모두 동일한 Embedding 모델 사용
- Vector Search 수행
- RAG의 핵심 구조
```
:::

특히 **12번 다이어그램**이 오늘 5교시의 핵심입니다. 강의 전체를 한 장으로 요약하면 사실상 저 그림 하나로 표현할 수 있습니다. PDF → Chunking → Embedding → Vector Index, 그리고 사용자 질문도 같은 Embedding을 거쳐 Vector Search를 수행한다는 구조입니다.
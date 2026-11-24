# Architecture

```mermaid
flowchart LR
    subgraph Sources
        G[Gmail] --> M[Mail provider]
        C[Google Calendar] --> K[Calendar provider]
        W[Open-Meteo] --> WP[Weather provider]
        D[Academic deadlines] --> DP[Deadline provider]
    end

    M & K & WP & DP --> CORE

    subgraph CORE[Stride core]
        CF[Conflict detection]
        RM[Reminder engine + dedupe]
        BR[Briefing / recap builder]
        AI[AI summaries and prep suggestions]
    end

    S[Scheduler: 5-min checks, daily + evening jobs] --> CORE
    CORE --> DC[Discord bot]
    CORE --> OC[OpenClaw dashboard]
    DC --> U((Student))
    OC --> U
```

## Hybrid design: AI vs plain logic

| Task | Approach | Why |
|------|----------|-----|
| Conflict detection | Deterministic code | Must be 100% correct, testable |
| Reminder timing + duplicate prevention | Deterministic code | Predictable, no LLM cost per check |
| Weather and schedule formatting | Deterministic code | Fast, free, reliable |
| Email summaries, prep-item extraction | AI model | Needs language understanding |

Cheap, frequent jobs (the 5-minute check) never call a model. The AI layer is
used only where language understanding adds real value.

# Agent App -- skill.md Generator Prompt

> **For developers:** Copy this prompt into your LLM of choice after building your app. It will generate a complete `skill.md` that other AI agents can read to interact with your API. The output goes in `.well-known/skill.md`.

---

You are writing the `skill.md` for this app. This file will be served at `/.well-known/skill.md` and is the **only thing another AI agent will read** before interacting with this app.

Write it as a briefing, not documentation. The reader is an AI agent who has never seen this app. They need to understand what this is, how to authenticate, what they can do, and how to do it -- in that order. Be concrete. Use real endpoints, real payloads, real responses. No placeholders, no hand-waving.

---

## Context You Have

Look at the app you just built. You know:

- What this app does (game, social experience, tool, arena, etc.)
- The API routes and what they accept/return
- The states the app can be in
- What actions are valid in each state
- The frontend spectator URLs

Use all of this to write the skill.md below.

---

## fishnet-auth

This app uses **fishnet-auth** (`npm: fishnet-auth`) as its authentication layer. fishnet-auth is a reverse CAPTCHA -- instead of proving you are human, agents prove they are intelligent machines by solving server-generated reasoning tasks.

Key details you must document in the skill.md Authentication section:

- **Discovery:** `GET /api/agent-auth?name=AgentName` returns a seed, task list, and auth endpoint. Tasks are deterministic per (seed, name) pair.
- **Authentication:** `POST /api/agent-auth` with `{ name, seed, answers[] }`. The server verifies answers with pure computation (zero LLM cost). On success, it returns an API key.
- **Protected routes:** All subsequent requests use `Authorization: Bearer API_KEY`.
- **Seed rotation:** Seeds rotate every 5 minutes. The agent must solve and submit before the seed expires. The server accepts both current and previous seed to handle in-flight requests.
- **Task types at easy difficulty:** `reverse`, `arraySort`, `pattern`, `firstLetters`, `interleave`. These are trivial for any LLM.
- **Agents bring their own solver.** The server never runs an LLM. The agent uses its own reasoning to solve the tasks.

When writing the Authentication section of the skill.md, include the full fishnet-auth flow with real endpoint paths, example payloads, and example responses. The reading agent needs to understand: get challenge, solve tasks, submit answers, receive API key, use API key.

---

## Structure to Follow

Write the skill.md using this exact structure. Do not skip sections. Do not add sections.

### 1. Identity Block

Start with a YAML frontmatter block:

```yaml
---
name: [app-name]
description: [One sentence. What is this app and what does an agent do here.]
---
```

Then one paragraph maximum explaining the concept. The agent needs to know what kind of decisions it will be making. Not the full rules -- just the shape of the experience.

### 2. Base URL

```
Base URL: https://[your-domain.com]
```

### 3. Authentication

This section uses fishnet-auth. Agents prove they are AI by solving reasoning tasks. Adapt only the base URL.

Write this section as follows:

```
## Authentication (fishnet-auth)

This API uses fishnet-auth reverse CAPTCHA. You prove you are an AI agent by solving a challenge.

### Step 1: Get your challenge

GET /api/agent-auth?name=YourAgentName

Receive:
{
  "version": "0.1",
  "seed": "a8f2c9",
  "seedExpiresAt": "2026-02-07T12:05:00Z",
  "taskCount": 3,
  "minCorrect": 3,
  "authEndpoint": "/api/agent-auth",
  "tasks": [
    { "type": "reverse", "instruction": "Reverse this string exactly.", "input": "xK9mQ2nL" }
  ]
}

### Step 2: Solve the tasks and submit answers

Use your reasoning capability to solve each task. Submit all answers in order:

POST /api/agent-auth

Send:
{
  "name": "YourAgentName",
  "seed": "a8f2c9",
  "answers": ["Ln2Qm9Kx", ...]
}

Receive:
{
  "agentId": "ag_k8x2m9f1",
  "apiKey": "agent_a8Kx92mN...",
  "expiresAt": "2026-02-08T12:00:00Z"
}

### Step 3: Use your API key

All subsequent requests use the API key as a Bearer token:

  Authorization: Bearer YOUR_API_KEY
```

### 4. Quick Start

Write a numbered sequence of the **minimum steps** to go from unauthenticated to actively participating. This is not the full loop -- it is "do these 3-5 things right now and you are in."

Example shape (adapt to your app):

```
1. Get challenge   --> GET /api/agent-auth?name=YourName
2. Solve and auth  --> POST /api/agent-auth
3. Join a session  --> POST /api/sessions/join
4. Get state       --> GET /api/sessions/{id}/state
5. Submit action   --> POST /api/sessions/{id}/action
```

Keep it tight. The agent should be able to follow this mechanically.

### 5. The Loop

Describe the repeating interaction cycle specific to this app. Every app has one. Frame it from the agent's perspective:

- What triggers the start of a cycle
- What information the agent receives
- What decisions the agent needs to make
- How the agent submits its decision
- What happens next
- How the agent knows it is over

Write this as prose, not a table. The agent needs to understand the rhythm, not just the steps.

### 6. Actions

For each action the agent can take, define it as:

```
### [Action Name]

[When to use this -- one sentence]

[METHOD] /api/path

Send:
{
  "field": "value"
}

Receive:
{
  "field": "value"
}
```

Include **every** action. Include a realistic example for each one showing actual values, not schema types. The agent will pattern-match off these examples.

Order the actions in the sequence the agent is most likely to use them.

### 7. State Shape

Define the standard response envelope the agent will see on every game/session response:

```json
{
  "sessionId": "string",
  "status": "waiting | active | complete",
  "state": { },
  "availableActions": [],
  "spectatorUrl": "https://domain.com/watch/SESSION_ID",
  "result": null
}
```

Then describe what goes inside `state` for THIS specific app. Be concrete -- show a real mid-game state, not a schema.

Explain what each value of `status` means:
- `waiting` -- what the agent should do
- `active` -- what the agent should do
- `complete` -- what the agent should do

Explain `availableActions` -- this array tells the agent exactly what moves are valid RIGHT NOW. The agent should never guess -- it should always check this array.

### 8. Constraints

List anything that will cause the agent to fail, get rejected, or get removed:

- Rate limits (requests per second/minute)
- Timeout rules (how long before a turn is forfeited)
- Invalid action behavior (what happens if you send a bad move)
- Concurrency rules (can you be in multiple sessions)
- Seed expiration (seeds rotate every 5 minutes, solve before it expires)

Be specific with numbers. "Don't send too many requests" is useless. "Max 2 requests per second" is useful.

### 9. Spectator

One short section:

```
Your human can watch at: https://[domain]/watch/{sessionId}

Share this URL with the human who asked you to play.
```

---

## Writing Rules

- Write for an AI agent, not a human developer
- Use imperative voice: "Send this", "Wait for", "Check the status"
- Include one realistic example per endpoint with actual values
- Never say "see documentation" -- this IS the documentation
- Never explain HTTP basics -- the agent knows how to make requests
- Never explain the game rules exhaustively -- just enough to make good decisions
- Keep the total length under 400 lines -- context window is shared space
- If the app has complex rules, put the essentials in the skill.md and link to a `/rules` endpoint the agent can fetch if needed

---

## What NOT to Include

- Implementation details (database, framework, hosting)
- Human onboarding flows
- Frontend component descriptions
- Changelog or version history
- Setup or installation instructions
- Anything the agent does not directly use to interact with the API

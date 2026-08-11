# Testing Guide

## Prerequisites

```bash
npm install
cp .env.example .env.local
npm run dev
```

## Agent Authentication Flow

### 1. Get a challenge

```bash
curl "http://localhost:3000/api/agent-auth?name=TestAgent"
```

You will receive reasoning tasks (reverse strings, sort arrays, etc.) along with a `seed` value.

### 2. Solve and authenticate

Submit your answers in order, referencing the `seed` from step 1:

```bash
curl -X POST "http://localhost:3000/api/agent-auth" \
  -H "Content-Type: application/json" \
  -d '{"name":"TestAgent","seed":"YOUR_SEED","answers":["answer1","answer2"]}'
```

On success you receive an `apiKey` (bearer token).

### 3. Test your token

```bash
curl -X POST "http://localhost:3000/api/test" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"test":"hello"}'
```

### 4. Join a session

```bash
curl -X POST "http://localhost:3000/api/sessions/join" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 5. Check session state

```bash
curl "http://localhost:3000/api/sessions/SESSION_ID/state" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 6. Verify skill.md

```bash
curl http://localhost:3000/.well-known/skill.md
curl http://localhost:3000/skill.md
```

Both endpoints should return the same skill documentation.

## Automated Test with Claude

`test-anthropic.sh` runs the full fishnet-auth flow end-to-end using Claude as the solver. It fetches a challenge, sends the tasks to the Anthropic API, submits the answers, and verifies protected route access.

### Prerequisites

- `jq` installed (`brew install jq` on macOS)
- `curl` installed (comes with macOS/Linux)
- An [Anthropic API key](https://console.anthropic.com/settings/keys)
- The dev server running (`npm run dev`)

### Setup

Set your Anthropic API key in `.env.local` or export it directly:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Usage

```bash
# Make the script executable (first time only)
chmod +x test-anthropic.sh

# Run against local dev server (default)
./test-anthropic.sh

# Run against a custom URL with a custom agent name
./test-anthropic.sh https://your-app.vercel.app MyAgent
```

### What the script does

| Step | Description |
|------|-------------|
| 1 | Fetches a fishnet-auth challenge (`GET /api/agent-auth`) |
| 2 | Sends the reasoning tasks to Claude (claude-sonnet-4-5) via the Anthropic API |
| 3 | Submits Claude's answers back to the server (`POST /api/agent-auth`) |
| 4 | Tests a protected GET route with the issued bearer token |
| 5 | Verifies that the same route returns 401 without a token |
| 6 | Tests a protected POST route with the bearer token |
| 7 | Verifies that the POST route returns 401 without a token |

A successful run means the full auth flow -- challenge, solve, authenticate, and use protected routes -- works end-to-end.

## Automated Demo (Browser)

Visit http://localhost:3000/demo/fishnet to run the full authentication flow interactively in the browser. This page lets you step through challenge retrieval, solving, and token verification without curl.

## Checklist

- [ ] Agent can discover the service via `/.well-known/skill.md`
- [ ] Challenge endpoint returns reasoning tasks
- [ ] Correct answers produce a valid bearer token
- [ ] Protected endpoints reject requests without a valid token
- [ ] Session join and state endpoints work with a valid token
- [ ] Health endpoint responds at `/api/health`
- [ ] Landing page loads at `/`

## Production Checklist

- [ ] `FISHNET_AUTH_SECRET` set to a strong random value
- [ ] `NEXT_PUBLIC_BASE_URL` set to production URL
- [ ] Base URL updated in `public/skill-content.md`
- [ ] In-memory storage replaced with a persistent database
- [ ] Rate limiting configured
- [ ] Monitoring and logging enabled

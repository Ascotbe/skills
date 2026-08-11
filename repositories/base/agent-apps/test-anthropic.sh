#!/usr/bin/env bash
set -euo pipefail

# Usage: ./test-anthropic.sh [BASE_URL] [AGENT_NAME]
#
# Tests the full fishnet auth flow using Claude as the solver.
# Requires ANTHROPIC_API_KEY env var.

ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:?Set ANTHROPIC_API_KEY env var}"
BASE_URL="${1:-http://localhost:3000}"
AGENT_NAME="${2:-TestAgent}"

echo "=== fishnet auth test ==="
echo "Server: $BASE_URL"
echo "Agent:  $AGENT_NAME"
echo ""

# ── Step 1: Discovery ───────────────────────────────────────────────
echo "1. Fetching challenge..."
DISCOVERY=$(curl -s "${BASE_URL}/api/agent-auth?name=${AGENT_NAME}")
SEED=$(echo "$DISCOVERY" | jq -r '.seed')
TASKS=$(echo "$DISCOVERY" | jq -c '.tasks')
TASK_COUNT=$(echo "$DISCOVERY" | jq '.taskCount')

echo "   Seed: $SEED"
echo "   Tasks: $TASK_COUNT"
echo ""
echo "   Task details:"
echo "$TASKS" | jq -r 'to_entries[] | "   [\(.key + 1)] \(.value.type): \(.value.instruction | split("\n")[0]) | input: \(.value.input | tostring | .[0:80])"'
echo ""

# ── Step 2: Solve with Claude ──────────────────────────────────────
echo "2. Sending tasks to Claude..."

# Build the prompt with strict formatting rules per task type
PROMPT="You are solving authentication challenge tasks. Follow each instruction EXACTLY.

For each task, use the \"work\" field to show your step-by-step reasoning BEFORE writing the answer. This is critical for character-level tasks like interleave, reverse, and transform.

CRITICAL formatting rules:
- reverse: Return the reversed string, nothing else.
- nthWord: Return just the word (lowercase).
- jsonBuild: Return compact JSON with no spaces, e.g. {\"a\":1,\"b\":2}. Keys sorted alphabetically, values are character counts (integers).
- arraySort: Return comma-separated with NO spaces between words.
- charCount: Return just the number.
- pattern: Return comma-separated next elements with NO spaces.
- transform: Apply each step in order. Return the exact final string.
- firstLetters: Concatenate first letters into a single string (lowercase).
- wordLengths: Return comma-separated numbers with NO spaces.
- filterWords: Return matching words sorted alphabetically, comma-separated, NO spaces.
- interleave: Take first[0], second[0], first[1], second[1], first[2], second[2], ... Return the single combined string. Example: first="ab", second="cd" → "acbd".

Here are the tasks:
$(echo "$TASKS" | jq -r 'to_entries[] | "Task \(.key + 1) [type: \(.value.type)]: \(.value.instruction)\nInput: \(.value.input | tostring)\n"')"

# Build the JSON schema — let Claude show work before committing each answer
SCHEMA=$(jq -n '{
  type: "object",
  properties: {
    solutions: {
      type: "array",
      items: {
        type: "object",
        properties: {
          work: { type: "string" },
          answer: { type: "string" }
        },
        required: ["work", "answer"],
        additionalProperties: false
      }
    }
  },
  required: ["solutions"],
  additionalProperties: false
}')

# Call Claude API with structured outputs
CLAUDE_RESPONSE=$(curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: ${ANTHROPIC_API_KEY}" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d "$(jq -n \
    --arg prompt "$PROMPT" \
    --argjson schema "$SCHEMA" \
    '{
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 1024,
      messages: [{role: "user", content: $prompt}],
      output_config: {
        format: {
          type: "json_schema",
          schema: $schema
        }
      }
    }')")

# Extract answers from solutions array
SOLUTIONS=$(echo "$CLAUDE_RESPONSE" | jq -r '.content[0].text')
ANSWERS=$(echo "$SOLUTIONS" | jq -c '[.solutions[].answer]')

echo "   Answers per task:"
paste <(echo "$TASKS" | jq -r '.[].type') <(echo "$ANSWERS" | jq -r '.[]') | while IFS=$'\t' read -r type answer; do
  echo "   [$type] → $answer"
done
echo ""

if [ -z "$ANSWERS" ] || [ "$ANSWERS" = "null" ]; then
  echo "ERROR: Failed to get answers from Claude."
  echo "$CLAUDE_RESPONSE" | jq .
  exit 1
fi

# ── Step 3: Authenticate ───────────────────────────────────────────
echo "3. Submitting answers..."

AUTH_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/agent-auth" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg name "$AGENT_NAME" \
    --arg seed "$SEED" \
    --argjson answers "$ANSWERS" \
    '{name: $name, seed: $seed, answers: $answers}')")

echo "   Response: $AUTH_RESPONSE"
echo ""

# Check if we got an API key
API_KEY=$(echo "$AUTH_RESPONSE" | jq -r '.apiKey // empty')
if [ -z "$API_KEY" ]; then
  echo "FAILED: Authentication failed."
  echo "$AUTH_RESPONSE" | jq .
  exit 1
fi

AGENT_ID=$(echo "$AUTH_RESPONSE" | jq -r '.agentId')
echo "   Agent ID: $AGENT_ID"
echo "   API Key:  ${API_KEY:0:20}..."
echo ""

# ── Step 4: Test protected route (with auth) ──────────────────────
echo "4. Testing protected route with agent auth..."
PROTECTED_AUTH=$(curl -s "${BASE_URL}/api/agent-auth/protected" \
  -H "Authorization: Bearer ${API_KEY}")
echo "   $PROTECTED_AUTH" | jq .
echo ""

# ── Step 5: Test protected route WITHOUT auth (should 401) ────────
echo "5. Testing protected route without auth (should 401)..."
NO_AUTH=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/agent-auth/protected")
echo "   Status: $NO_AUTH"
echo ""

# ── Step 6: Test protected POST route (as agent) ──────────────────
echo "6. Testing protected POST route as agent..."
PROTECTED_POST=$(curl -s -X POST "${BASE_URL}/api/agent-auth/protected" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"action": "test"}')
echo "   $PROTECTED_POST" | jq .
echo ""

# ── Step 7: Test protected POST route (no auth, should 401) ───────
echo "7. Testing protected POST route without auth (should 401)..."
NO_AUTH_POST=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE_URL}/api/agent-auth/protected")
echo "   Status: $NO_AUTH_POST"
echo ""

echo "=== done ==="
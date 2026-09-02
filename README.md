# gtm-ticket-triage
GTM ticket triage agent built using Claude SDK for architect cert prep


# GTM Ticket Triage Agent — CCA-F Exam Prep

A small agentic project built to cover all 5 domains of the Claude Certified Architect – Foundations exam:
Agentic Architecture (27%), Tool Design & MCP (18%), Claude Code Workflows (20%), Prompt Engineering & Structured Output (20%), Context Management & Reliability (15%).

## Week 1 — Core loop + tools (Domain 1 & 2 foundations)

- [ ] Set up repo, venv, `anthropic` SDK, `.env` for API key
- [ ] Build a mock ticket dataset (15-20 rows: subject, body, sender, urgency signals) as CSV
- [ ] Write a raw agent loop using `messages.create` — no SDK helpers: send ticket, inspect `stop_reason`, handle `tool_use` by executing a Python function and feeding `tool_result` back, loop until `end_turn`
- [ ] Define 3 tools (`lookup_account`, `create_task`, `escalate_to_human`) with strict JSON schemas — practice writing schemas that prevent ambiguous calls
- [ ] Add a confidence check: if the model's triage confidence is low, force a call to `escalate_to_human` instead of auto-resolving

## Week 2 — MCP + structured output (Domain 2 & 4)

- [ ] Install the MCP Python SDK, wrap `lookup_account` as a standalone MCP server (stdio transport is simplest)
- [ ] Swap that one tool from inline `tool_use` to an MCP client call — note what changes in your loop code
- [ ] Define a JSON schema for the final triage decision (category, priority, confidence, next_action)
- [ ] Force structured output via tool-call schema; add a repair loop that retries on invalid JSON (cap retries, log failures)
- [ ] Run the 3-4 hardest tickets with extended thinking on vs off, compare triage accuracy/confidence

## Week 3 — Claude Code config + Agent SDK (Domain 1 & 3)

- [ ] Write a `CLAUDE.md` describing project conventions, tool contracts, and escalation rules
- [ ] Add a custom slash command (e.g. `/triage-batch` to run the pipeline over a CSV)
- [ ] Add a pre-tool-use hook that blocks `create_task` if the payload fails schema validation
- [ ] Set up a permissions config restricting which tools can run without confirmation
- [ ] Rebuild Week 1's raw loop using the Claude Agent SDK; split into a router agent + one subagent (hub-and-spoke) and compare against your hand-rolled version

## Week 4 — Context/reliability + exam prep (Domain 5 + review)

- [ ] Add prompt caching on the system prompt and tool definitions; confirm cache hits in the response usage stats
- [ ] Convert one code path to streaming; handle partial JSON during a stream
- [ ] Add retry-with-backoff for rate-limit errors
- [ ] Run the full ticket backlog through the Batches API instead of synchronous calls
- [ ] Do 2-3 full practice exams, weighting review time to match domain %: most time on Domain 1 (27%), least on Domain 5 (15%)
- [ ] Re-read the official exam guide once, end to end, as a final pass

## Notes

If a week runs long, Week 3's Claude Code config tasks are the easiest to compress — they're mostly file-writing, not debugging.

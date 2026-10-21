# Herdr-native delivery

Read this when Herdr is the selected runtime. Follow the parent skill's role,
lane and review decisions. Keep deployment-specific commands, endpoints and
policy in the owning project's instructions, rather than in this shared skill.

## Establish the contract

1. Record the installed Herdr version, selected server/session, native agent
   integration and approved provider/model. Read the official
   [agent automation](https://herdr.dev/docs/agent-automation/),
   [CLI](https://herdr.dev/docs/cli-reference/) and
   [socket API](https://herdr.dev/docs/socket-api/) documentation for that version.
   Export the installed contract with `herdr api schema --json`. Compare docs,
   schema and server capabilities before using a newer feature.
2. Obtain the project's admitted execution binding before creating layout. Bind
   task, attempt/generation, source revision, control machine, workload identity,
   environment class, egress policy and scoped execution capability. Herdr panes
   and worktrees organize terminals and source; they do not enforce isolation.
   When Incus is the deployment boundary, place the coordinator and every model
   agent inside Incus, with baseline worktrees and Docker inside Incus and
   dedicated minimal/full VMs as admitted. A host lifecycle helper is trusted
   infrastructure, not a model agent. Maintain resource admission and preserve
   existing sessions, guests and keys.
3. Separate the model/control boundary from the enclosed workload. Keep the
   coordinator's required internet and repository access while an independent
   authority enforces each worker's full/whitelist/isolated policy. An isolated
   workload has no concealed inference route. An online model may control it
   only through an externally restricted execution capability: disable or
   confine alternative shell, file, network, proxy and tool paths. Verify that
   restriction empirically; a prompt instruction is not enforcement. If the
   provider cannot support it, report the inspected blocker and keep that
   acceptance cell blocked rather than silently changing mode. Keep workloads
   unable to reach the coordinator's Herdr socket, saved connection registry,
   Docker socket or management credentials. Socket file permissions protect an
   OS account boundary; same-user panes do not gain separate capabilities merely
   by using different named sessions.

Done when the installed contract and admitted binding agree, including source
identity and enforcement. Carry immutable-reference-only repository exclusions
into each author, reviewer and operator brief before any repository discovery.

## Dispatch through native primitives

Use the admitted control machine/session for every operation. A pane in an
already-open terminal keeps its original target even if the TUI changes machine.
For remote API commands, the documented `--machine` selector targets an enabled
saved profile, not an arbitrary SSH hostname. Resolve target identity before
mutating; never fall back to a local server when remote control fails.

Create layout only in an owned admitted source directory. `workspace create`
returns `.result.root_pane.pane_id`; `pane split` returns `.result.pane.pane_id`.
Capture those values from successful JSON responses. Start an agent only in an
available shell pane, using `agent start` with the chosen `--kind`, `--pane` and
explicit provider arguments after `--`. Read provider flags from that installed
provider's contract; do not infer them from Herdr's examples. A successful start
confirms recognized readiness, not provider authentication or task completion.

Before submitting, persist the brief and its task/attempt/source binding through
the project's verified durable task channel. Include the exact authorized result
and question route, permitted files, acceptance tests and read-only exclusions.
Use `agent prompt` for an agent's prompt and `pane run` for a shell command.
Use explicit targets and bounded timeouts. Submit only when the prior assignment
is reconciled: `agent prompt --wait` observes lifecycle, not a particular turn.
Record the submission response or uncertainty durably before taking the next
side effect. Native CLI names are not task/attempt identities.

Herdr's `idle` and `done` states can both mean ready for input. Treat them as
wake signals to check the bound result. `blocked` calls for a deliberate response
to the assigned agent's UI; `unknown` requires investigation. Use native waits
for actionable state, and correlate the returned identity with the assignment.
On timeout or `agent_prompt_stalled`, input may already have been sent. Reconcile
receipts, current authorized worker state and artifacts before any retry.

Done when the exact attempt produced a durable result and independent evidence
establishes the requested outcome. A terminal badge, matched historical text,
start receipt or author claim is insufficient. Harvest artifacts before closing
owned layout; preserve user-owned sessions and settle uncertain attempts first.

## Recover without replaying uncertain work

Read [session state](https://herdr.dev/docs/session-state/) and
[persistence/remote access](https://herdr.dev/docs/persistence-remote/) before
reconnect, restart or update. Detach preserves live processes; server restart
restores layout and eligible native agent sessions rather than arbitrary running
commands. Screen history is sensitive and is not task state. Validate installed
integrations and a disposable restore test before claiming conversation recovery.
Eligible native sessions resume after a client attaches with terminal size/theme;
include an actual attach-before-resume check rather than assuming headless server
startup alone resumes the conversation.

Treat event subscriptions as live signals, not a durable mailbox. Following
reconnect, subscribe and reconcile authoritative state plus the project's durable
task/attempt records. Fence obsolete attempts before reassignment; reconcile
uncertain side effects before creating a new attempt. Obtain task-level replay,
receipt and recovery behavior from the verified project adapter, not imagined
Herdr task, Run, mailbox or acknowledgement commands.

Updates use the project's reviewed versioned artifact and durable upgrade job.
Keep the coordinator alive or provide tested independent supervision and recovery;
record status and rollback outside a process that may be replaced. Experimental
Herdr handoff is not a guarantee of process preservation. Never stop a shared
server to test restore, install integrations into private agent homes, or accept
an automatic remote install/restart without deployment authority and continuity
checks.

## Prepare owner entry

Resolve the coordinator's required placement from the owning project's admitted
execution binding. Have the operator verify that placement and supply its SSH
route and selected named Herdr session. When the project requires Incus, verify
that the coordinator and every model agent reside inside their admitted Incus
VMs. Prepare an exact `herdr --remote TARGET --session SESSION` command with real
values, or the verified SSH-then-Herdr alternative. Neither command proves
placement; retain the operator's separate placement evidence.
Remote bootstrap can install/update software, so use the reviewed installation
and check compatibility before a connection that could prompt for changes.

Deliver a durable context handoff containing objective, role ownership,
acceptance, exact source/skill revisions, task/attempt evidence, unresolved work
and rollback. Transfer only selected non-secret context. Establish a conversation
with the intended coordinator, execute a bounded server task, detach, resume and
verify its durable result. Record mobile/Moshi behavior separately when available.
A context handoff does not import the original chat or its private state.

Return the tested entry/resume commands, endpoint/session identity, provenance,
actual pass/block evidence and recovery instructions. Label Mac/bootstrap,
fixture, parser and source-only checks by their limits; server deployment and
provider-backed acceptance require actual server invocation.

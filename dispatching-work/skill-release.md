# Release skills to coordinators and agents

Use when installing or upgrading canonical skills across agent environments.
The output is a reviewable manifest, an operator procedure and invocation
receipts; preparing them does not itself install anything.

1. **Pin source.** Resolve the owning repository's current base, isolated author
   branch, reviewed commit/tree and required exact-head checks. Reconcile
   overlapping drafts by behavior rather than merging them wholesale. Identify
   the relevant skills and every linked reference they require. Edit the owning
   branch; preserve live global symlinks and unrelated skills.
2. **Map destinations.** Inventory only deployment-owned skill directories and
   existing link identities. Determine the installed agent's discovery mechanism
   from its official contract. For every coordinator and agent role, record the
   exact VM, user, immutable release path, discovery path and selected skill set.
   Include future agent/template destinations so new workers receive the same
   release. Unknown destinations remain explicitly unresolved; never substitute
   a guessed home, a host-global path or an author's local workspace.
3. **Build a manifest.** Record source repository/commit/tree, approved review
   and CI evidence, relative files with SHA256, bundle SHA256, destinations and
   ownership/modes, old release/link identity, activation method, rollback target
   and the expected invocation for each role. Keep environment-specific values
   in the deployment record outside this portable skill. Exclude credentials,
   private sessions and unrelated home directories. Validate that links resolve
   only within the selected release and that every disclosed reference exists.
4. **Validate before effects.** Export from the exact commit, stage in a fresh
   directory and verify hashes and referenced paths. Check discovery and skill
   invocation using the actual installed agent/runtime contract in a disposable
   environment. Exercise role routing, native dispatch, ambiguous submission,
   reconnect, read-only exclusions and completion evidence. Record both tested
   outcomes and limits: text assertions and CLI parsing do not prove model
   compliance, deployment or provider-backed server execution.
5. **Hand off for independent review.** The operational PM commissions reviewers
   and owns the merge/deployment gate; the author supplies reproducible checks
   without choosing its own reviewers. Rebuild and re-review changed deltas;
   bind approval and required checks to the exact artifact source revision.
6. **Deploy through the authorized operator.** First establish current session
   continuity and exact old discovery/link identities. Stage immutable bytes,
   verify remote hashes, preserve a rollback copy and switch only approved
   discovery entries. Reject an unexpected existing entry or unresolved target.
   Keep deployment status durable across disconnect; preserve existing guests,
   sessions, keys and unrelated skill links. Avoid automatic agent/server
   restarts; test fresh disposable agents before changing active sessions.
7. **Prove invocation on the server.** Record deployed file hashes, source
   revision, VM/user identity and actual discovery/invocation receipts for the
   coordinator and each agent role. Run one bounded task through the native
   workflow and verify addressed result provenance, reconnect and unchanged
   exclusions. Have an independent verifier assess those receipts. A copied
   directory is not proof of invocation. If any required role remains untested,
   report it pending or blocked rather than marking the release deployed.
8. **Retain rollback.** Restore only the deployment-owned discovery entries to
   their recorded previous identities; preserve the failed release and its
   evidence. Verify restored hashes and a disposable invocation. Keep old
   releases until session/dependency continuity permits removal.

Complete with one manifest and evidence index mapping each required role from
canonical source hash to destination hash to invocation outcome. Return exact
entry/resume and rollback commands only once the operator has established their
real values and tested them; identify remaining dependencies explicitly.

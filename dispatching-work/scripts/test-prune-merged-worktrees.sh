#!/usr/bin/env bash
# test-prune-merged-worktrees.sh — scenario tests + mutation tests for
# prune-merged-worktrees.sh.
#
# Each test builds an isolated git repository in a temp sandbox with worktrees
# in known states (merged / open / local-only / dirty / protected / live
# session / detached / PR states), runs the script under test, and asserts the
# outcome. Mutation tests apply single behavioral mutations to a copy of the
# script and require the suite to catch each one (killed = the suite fails on
# the mutant).
#
# Usage: test-prune-merged-worktrees.sh [script-under-test]
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
UNDER_TEST="${1:-$HERE/prune-merged-worktrees.sh}"
SANDBOX="$(mktemp -d "${TMPDIR:-/tmp}/prune-test.XXXXXX")"
mkdir -p "$SANDBOX/home"

PASS=0
FAIL=0
FAILED_NAMES=""
MUT_KILLED=0
MUT_SURVIVED=0
GH_FAKE=""   # global: set by run_suite, read by mutate_and_test; must exist under set -u

ok()   { PASS=$((PASS + 1)); echo "ok   - $1"; }
fail() { FAIL=$((FAIL + 1)); FAILED_NAMES="$FAILED_NAMES
  $1"; echo "FAIL - $1"; }

# run the script under test in a stripped environment:
# PATH without orca (forces the git fallback), isolated HOME (session dirs),
# no gh unless the test sets GH_FAKE.
runcap() { # runcap <cwd> <args...>  -> sets OUT, RC
  local cwd=$1; shift
  OUT="$(cd "$cwd" && env -i PATH="/usr/bin:/bin" HOME="$SANDBOX/home" \
    TMPDIR="$SANDBOX" GH_BIN="${GH_FAKE:-/nonexistent-gh}" \
    bash "$UNDER_TEST" "$@" 2>&1)"
  RC=$?
}

# ---------- repo builders ----------
build_repo() { # build_repo <test-dir>  -> fresh $T/repo; wipes stale state so mutation tests can't inherit leftovers
  T=$1
  R="$T/repo"
  rm -rf "${T:?}"   # full reset: a leftover backup dir from a previous run would mask a removed backup call
  git init -q -b main "$R"
  git -C "$R" config user.email t@t.test
  git -C "$R" config user.name tester
  echo base > "$R/base.txt"
  git -C "$R" add -A
  git -C "$R" commit -qm base
}

add_worktree() { # add_worktree <name> [branch] — branch defaults to feat-<name>
  git -C "$R" worktree add -q -b "feat-$1" "$T/wt-$1"
}

merge_branch() { # merge_branch <name> — merge feat-<name> into main
  git -C "$R" merge -q --no-edit "feat-$1"
}

commit_in_wt() { # commit_in_wt <name> <text> — write and commit one file
  echo "$2" > "$T/wt-$1/$1.txt"
  git -C "$T/wt-$1" add -A
  git -C "$T/wt-$1" commit -qm "$1"
}

# ---------- assertions ----------
assert_dir_absent()  { [ ! -d "$1" ] && ok "$2" || fail "$2 (dir still present: $1)"; }
assert_dir_present() { [ -d "$1" ]  && ok "$2" || fail "$2 (dir missing: $1)"; }
assert_file_present(){ [ -f "$1" ]  && ok "$2" || fail "$2 (file missing: $1)"; }
assert_file_absent() { [ ! -f "$1" ] && ok "$2" || fail "$2 (file exists: $1)"; }
assert_contains()    { case "$OUT" in *"$1"*) ok "$2";; *) fail "$2 (output missing: $1)";; esac; }
assert_rc_zero()     { [ "$RC" -eq 0 ] && ok "$1" || fail "$1 (rc=$RC) OUT=$OUT"; }
assert_rc_nonzero()  { [ "$RC" -ne 0 ] && ok "$1" || fail "$1 (rc=$RC, expected failure) OUT=$OUT"; }
assert_branch_gone() {
  git -C "$R" show-ref --verify --quiet "refs/heads/$1" \
    && fail "$2 (branch $1 still exists)" || ok "$2"
}
assert_branch_present() {
  git -C "$R" show-ref --verify --quiet "refs/heads/$1" \
    && ok "$2" || fail "$2 (branch $1 missing)"
}

# ---------- shared fixture: merged + open + local-only ----------
build_standard_fixture() {
  build_repo "$SANDBOX/fix-$1"
  add_worktree merged
  commit_in_wt merged m1
  merge_branch merged
  add_worktree open
  commit_in_wt open o1
  add_worktree local
  commit_in_wt local l1
}

# =====================================================================
# Scenario tests
# =====================================================================

t01_dry_run_default_writes_nothing() {
  build_standard_fixture "t01"
  runcap "$SANDBOX" --repo "$R"
  assert_rc_zero "t01 dry run exits 0"
  assert_dir_present "$T/wt-merged" "t01 dry run keeps merged worktree"
  assert_dir_present "$T/wt-open" "t01 dry run keeps open worktree"
  assert_dir_present "$T/wt-local" "t01 dry run keeps local worktree"
  assert_contains "DRY-RUN" "t01 dry run says DRY-RUN"
  assert_contains "merged / clean" "t01 classifies merged wt"
  assert_contains "local-only" "t01 classifies local-only wt"
  assert_dir_absent "$T/worktree-backups" "t01 dry run creates no backup dir"
  [ -z "$(git -C "$R" status --porcelain)" ] && ok "t01 dry run leaves repo clean" \
    || fail "t01 dry run left repo dirty"
}

t02_apply_removes_merged_keeps_unmerged() {
  build_standard_fixture "t02"
  runcap "$SANDBOX" --repo "$R" --apply
  assert_rc_zero "t02 apply exits 0"
  assert_dir_absent "$T/wt-merged" "t02 apply removes merged worktree"
  assert_dir_present "$T/wt-open" "t02 apply keeps open worktree"
  assert_dir_present "$T/wt-local" "t02 apply keeps local-only worktree"
  assert_branch_gone "feat-merged" "t02 deletes merged branch"
  assert_branch_present "feat-open" "t02 keeps open branch"
  assert_branch_present "feat-local" "t02 keeps local-only branch"
}

t03_backup_captures_untracked_ignored_and_patch() {
  T="$SANDBOX/t03"; build_repo "$T"
  add_worktree dirty
  echo edit > "$T/wt-dirty/tracked.txt"
  echo untracked > "$T/wt-dirty/untracked.txt"
  mkdir -p "$T/wt-dirty/sub/deep"
  echo keepme > "$T/wt-dirty/sub/deep/keep.txt"
  echo ignored > "$T/wt-dirty/ignored.log"
  echo "*.log" > "$T/wt-dirty/.gitignore"
  head -c 11000000 /dev/zero > "$T/wt-dirty/big.bin"
  git -C "$T/wt-dirty" add tracked.txt .gitignore
  git -C "$T/wt-dirty" commit -qm dirty
  echo more >> "$T/wt-dirty/tracked.txt"   # dirty tracked change after commit
  merge_branch dirty
  runcap "$SANDBOX" --repo "$R" --apply
  assert_rc_zero "t03 apply exits 0"
  assert_dir_absent "$T/wt-dirty" "t03 dirty merged wt removed"
  B="$(ls -d "$T/worktree-backups"/feat-dirty-* 2>/dev/null | head -1)"
  if [ -z "$B" ]; then
    fail "t03 backup dir created outside repo"
    return
  fi
  ok "t03 backup dir created outside repo"
  assert_file_present "$B/untracked.txt" "t03 backup has untracked file"
  assert_file_present "$B/ignored.log" "t03 backup has ignored file (unique state)"
  assert_file_present "$B/sub/deep/keep.txt" "t03 backup preserves relative dirs"
  assert_file_present "$B/dirty-tracked.patch" "t03 backup has dirty patch"
  grep -q "tracked.txt" "$B/dirty-tracked.patch" && ok "t03 patch contains tracked edit" \
    || fail "t03 patch missing tracked edit"
  assert_file_absent "$B/big.bin" "t03 backup skips oversized file"
  assert_dir_absent "$R/worktree-backups" "t03 no backups inside the repo"
}

t04_protected_list_skips_branch_and_path() {
  T="$SANDBOX/t04"; build_repo "$T"
  add_worktree protected
  commit_in_wt protected p
  merge_branch protected
  add_worktree protected2
  commit_in_wt protected2 q
  merge_branch protected2
  printf '# comment\n\nfeat-protected\n%s\n' "$T/wt-protected2" > "$T/prot.list"
  runcap "$SANDBOX" --repo "$R" --config "$T/prot.list" --apply
  assert_rc_zero "t04 apply exits 0"
  assert_dir_present "$T/wt-protected" "t04 protected branch skipped"
  assert_dir_present "$T/wt-protected2" "t04 protected path skipped"
  assert_branch_present "feat-protected" "t04 protected branch kept"
  assert_branch_present "feat-protected2" "t04 protected path branch kept"
  assert_contains "[SKIPPED: PROTECTED]" "t04 reports protected skip"
}

t05_live_session_skipped_but_stale_and_override_not() {
  T="$SANDBOX/t05"; build_repo "$T"
  add_worktree live
  commit_in_wt live v
  merge_branch live
  add_worktree stale
  commit_in_wt stale s
  merge_branch stale
  local munged
  munged="$(cd "$T" && pwd -P)"   # canonical form, matching git's porcelain paths
  munged="${munged//\//-}"
  mkdir -p "$SANDBOX/home/.claude/projects/--${munged}-wt-live--"
  echo session > "$SANDBOX/home/.claude/projects/--${munged}-wt-live--/sess.jsonl"
  mkdir -p "$SANDBOX/home/.claude/projects/--${munged}-wt-stale--"
  echo old > "$SANDBOX/home/.claude/projects/--${munged}-wt-stale--/old.jsonl"
  touch -t 202001010000 "$SANDBOX/home/.claude/projects/--${munged}-wt-stale--/old.jsonl"
  runcap "$SANDBOX" --repo "$R" --live-minutes 60 --apply
  assert_rc_zero "t05 apply exits 0"
  assert_dir_present "$T/wt-live" "t05 fresh session skipped"
  assert_contains "[SKIPPED: LIVE SESSION]" "t05 reports live skip"
  assert_dir_absent "$T/wt-stale" "t05 stale session removed"
  add_worktree live2
  commit_in_wt live2 w
  merge_branch live2
  mkdir -p "$SANDBOX/home/.claude/projects/--${munged}-wt-live2--"
  echo fresh > "$SANDBOX/home/.claude/projects/--${munged}-wt-live2--/fresh.jsonl"
  runcap "$SANDBOX" --repo "$R" --no-skip-live --apply
  assert_dir_absent "$T/wt-live2" "t05 --no-skip-live removes despite session"
}

t06_live_checkout_guard_refuses_and_confirms() {
  build_standard_fixture "t06"
  runcap "$R" --repo "$R" --apply
  assert_rc_nonzero "t06 --apply from live checkout refused"
  assert_contains "live checkout" "t06 refusal names the live checkout"
  assert_dir_present "$T/wt-merged" "t06 refusal removes nothing"
  runcap "$R" --repo "$R" --apply --confirm-live-checkout
  assert_rc_zero "t06 --confirm-live-checkout proceeds"
  assert_dir_absent "$T/wt-merged" "t06 confirmed apply removes merged wt"
  assert_dir_present "$R" "t06 primary checkout untouched"
}

t07_current_working_tree_never_removed() {
  build_standard_fixture "t07"
  add_worktree merged2
  commit_in_wt merged2 m2
  merge_branch merged2
  runcap "$T/wt-merged" --repo "$R" --apply
  assert_rc_zero "t07 apply from inside a worktree exits 0"
  assert_dir_present "$T/wt-merged" "t07 cwd worktree not removed"
  assert_contains "[SKIPPED: CURRENT WORKING TREE]" "t07 reports cwd skip"
  assert_dir_absent "$T/wt-merged2" "t07 other merged wt removed"
}

t08_gh_states_pr_merged_open_closed() {
  T="$SANDBOX/t08"; build_repo "$T"
  GH_FAKE="$T/fake-gh"
  cat > "$GH_FAKE" <<'EOF'
#!/usr/bin/env bash
branch=""
prev=""
for a in "$@"; do
  [ "$prev" = "--head" ] && branch="$a"
  prev="$a"
done
case "$branch" in
  feat-pr-merged) echo MERGED ;;
  feat-closed)    echo CLOSED ;;
  feat-open-pr)   echo OPEN ;;
  *)              echo "" ;;
esac
EOF
  chmod +x "$GH_FAKE"
  git init -q --bare "$T/origin.git"
  git -C "$R" remote add origin "$T/origin.git"
  git -C "$R" push -q origin main
  for name in pr-merged closed open-pr; do
    add_worktree "$name"
    commit_in_wt "$name" "$name"
    git -C "$T/wt-$name" push -q origin "feat-$name"
  done
  runcap "$SANDBOX" --repo "$R"
  assert_contains "pr-merged / clean" "t08 gh MERGED classified pr-merged"
  assert_contains "closed / clean" "t08 gh CLOSED classified closed"
  assert_contains "open / clean" "t08 gh OPEN classified open"
  runcap "$SANDBOX" --repo "$R" --apply
  assert_dir_absent "$T/wt-pr-merged" "t08 pr-merged removed"
  assert_dir_present "$T/wt-closed" "t08 closed kept by default"
  assert_dir_present "$T/wt-open-pr" "t08 open kept"
  runcap "$SANDBOX" --repo "$R" --apply --include-closed
  assert_dir_absent "$T/wt-closed" "t08 --include-closed removes closed"
  GH_FAKE=""
}

t09_backup_dir_inside_repo_refused() {
  build_standard_fixture "t09"
  runcap "$SANDBOX" --repo "$R" --backup-dir "$R/backups" --apply
  assert_rc_nonzero "t09 backup dir inside repo refused"
  assert_dir_absent "$R/backups" "t09 nothing written inside repo"
}

t10_primary_only_unknown_args_explicit_base() {
  T="$SANDBOX/t10"; build_repo "$T"
  runcap "$SANDBOX" --repo "$R"
  assert_rc_zero "t10 primary-only repo exits 0"
  assert_contains "PRIMARY / LIVE CHECKOUT" "t10 primary never a candidate"
  runcap "$SANDBOX" --repo "$R" --bogus
  assert_rc_nonzero "t10 unknown argument refused"
  assert_contains "unknown argument" "t10 names the bad argument"
  build_standard_fixture "t10b"
  runcap "$SANDBOX" --repo "$R" --base main
  assert_contains "merged / clean" "t10 --base main classifies merged"
}

t11_detached_head_merged_removed_without_branch_delete() {
  T="$SANDBOX/t11"; build_repo "$T"
  add_worktree detached
  commit_in_wt detached d
  merge_branch detached
  git -C "$T/wt-detached" checkout -q --detach HEAD
  runcap "$SANDBOX" --repo "$R" --apply
  assert_rc_zero "t11 apply exits 0"
  assert_dir_absent "$T/wt-detached" "t11 detached merged wt removed"
  assert_branch_present "feat-detached" "t11 no branch delete for detached record"
}

t12_open_and_local_only_kept_without_gh() {
  T="$SANDBOX/t12"; build_repo "$T"
  git init -q --bare "$T/origin.git"
  git -C "$R" remote add origin "$T/origin.git"
  git -C "$R" push -q origin main
  add_worktree open
  commit_in_wt open o1
  git -C "$T/wt-open" push -q origin feat-open
  add_worktree local
  commit_in_wt local l1
  runcap "$SANDBOX" --repo "$R" --apply
  assert_contains "open / clean" "t12 pushed unmerged wt classified open"
  assert_contains "local-only" "t12 unpushed wt classified local-only"
  assert_dir_present "$T/wt-open" "t12 open wt kept"
  assert_dir_present "$T/wt-local" "t12 local-only wt kept"
}

# =====================================================================
# Mutation tests: each mutant must be caught by the suite
# =====================================================================
run_suite() {
  GH_FAKE=""
  t01_dry_run_default_writes_nothing
  t02_apply_removes_merged_keeps_unmerged
  t03_backup_captures_untracked_ignored_and_patch
  t04_protected_list_skips_branch_and_path
  t05_live_session_skipped_but_stale_and_override_not
  t06_live_checkout_guard_refuses_and_confirms
  t07_current_working_tree_never_removed
  t08_gh_states_pr_merged_open_closed
  t09_backup_dir_inside_repo_refused
  t10_primary_only_unknown_args_explicit_base
  t11_detached_head_merged_removed_without_branch_delete
  t12_open_and_local_only_kept_without_gh
}

# replace the first line containing <old> with <new> (plain substring, no regex)
replace_line() { # replace_line <file> <old-substring> <new-line>
  local file=$1 old=$2 new=$3
  local out="${file}.new"
  local line found=0
  : > "$out"
  while IFS= read -r line || [ -n "$line" ]; do
    if [ "$found" -eq 0 ] && [ "${line#*"$old"}" != "$line" ]; then
      printf '%s\n' "$new" >> "$out"
      found=1
    else
      printf '%s\n' "$line" >> "$out"
    fi
  done < "$file"
  if [ "$found" -eq 1 ]; then mv "$out" "$file"; return 0; fi
  rm -f "$out"
  return 1
}

mutate_and_test() { # mutate_and_test <name> <old-substring> <new-line> <tests...>
  local name=$1 old=$2 new=$3; shift 3
  local mut="$SANDBOX/mutant-$name.sh"
  cp "$HERE/prune-merged-worktrees.sh" "$mut"
  if ! replace_line "$mut" "$old" "$new"; then
    echo "SKIP - mutation $name: pattern not found (harness bug)"
    MUT_SURVIVED=$((MUT_SURVIVED + 1))
    return
  fi
  if ! bash -n "$mut" 2>/dev/null; then
    ok "mutation $name: killed (mutant does not parse)"
    MUT_KILLED=$((MUT_KILLED + 1))
    return
  fi
  local save_under="$UNDER_TEST" save_gh="$GH_FAKE"
  UNDER_TEST="$mut"
  GH_FAKE=""
  PASS=0; FAIL=0; FAILED_NAMES=""
  local fn
  for fn in "$@"; do "$fn"; done
  UNDER_TEST="$save_under"
  GH_FAKE="$save_gh"
  if [ "$FAIL" -gt 0 ]; then
    ok "mutation $name: killed (caught by suite)"
    MUT_KILLED=$((MUT_KILLED + 1))
  else
    fail "mutation $name: SURVIVED (suite did not catch it)"
    MUT_SURVIVED=$((MUT_SURVIVED + 1))
  fi
}

run_mutations() {
  # backup step removed -> backup assertions must fail
  mutate_and_test no-backup \
    'backup_worktree "${wt}" "${branch}"' \
    '  : # mutation: backup removed' \
    t03_backup_captures_untracked_ignored_and_patch
  # dry run writes -> dry-run assertions must fail
  mutate_and_test dry-run-writes \
    'APPLY=false' 'APPLY=true' \
    t01_dry_run_default_writes_nothing
  # live-session skip removed -> live wt removed
  mutate_and_test no-live-skip \
    'if is_live "${wt}"; then' 'if false; then' \
    t05_live_session_skipped_but_stale_and_override_not
  # protected-list skip removed -> protected wt removed
  mutate_and_test no-protected-skip \
    'if is_protected "${branch}" || is_protected "${wt}"; then' 'if false; then' \
    t04_protected_list_skips_branch_and_path
  # live-checkout write guard removed -> --apply from live checkout succeeds
  mutate_and_test no-live-guard \
    '   && [ "${CWD_TOP}" = "${PRIMARY}" ] && [ "${CONFIRM_LIVE}" = false ]; then' \
    '   && [ "${CWD_TOP}" = "${PRIMARY}" ] && [ "${CONFIRM_LIVE}" = "never" ]; then' \
    t06_live_checkout_guard_refuses_and_confirms
  # branch deletion removed -> merged branch survives apply
  mutate_and_test no-branch-delete \
    'if "${GIT[@]}" branch -d "${branch}" 2>/dev/null; then' \
    'if false; then' \
    t02_apply_removes_merged_keeps_unmerged
  # open branches misclassified as merged -> open wt removed
  mutate_and_test open-as-merged \
    '    echo open; return' \
    '    echo merged; return' \
    t12_open_and_local_only_kept_without_gh
  # remote-existence check removed -> pushed branch looks local-only
  mutate_and_test no-remote-check \
    '  if "${GIT[@]}" ls-remote --exit-code --heads origin "refs/heads/${branch}" >/dev/null 2>&1; then' \
    '  if false; then' \
    t12_open_and_local_only_kept_without_gh
  # cwd skip removed -> script tries to remove its own working tree
  mutate_and_test no-cwd-skip \
    'if [ -n "${CWD_TOP}" ] && [ "${CWD_TOP}" = "${wt}" ]; then' \
    'if false; then' \
    t07_current_working_tree_never_removed
  # backup-inside-repo guard removed -> backups written into the repo
  mutate_and_test no-backup-guard \
    '  "${REPO_DIR:?}"/*) die "--backup-dir must live outside the repository (${REPO_DIR:?}), not inside it" ;;' \
    '  "${REPO_DIR:?}"/*) : ;;' \
    t09_backup_dir_inside_repo_refused
  # primary detection removed -> primary becomes a removal candidate
  mutate_and_test no-primary-detect \
    '  if [ -d "${wt}/.git" ]; then PRIMARY="${wt}"; break; fi' \
    '  if [ -d "${wt}/.git" ]; then PRIMARY=""; break; fi' \
    t06_live_checkout_guard_refuses_and_confirms
}

# ---------- main ----------
echo "== scenario tests against $UNDER_TEST =="
run_suite
echo
echo "scenario: pass=$PASS fail=$FAIL"
if [ "$FAIL" -gt 0 ]; then
  echo "FAILED:$FAILED_NAMES"
  echo "== stopping: fix scenarios before running mutations =="
  exit 1
fi

echo
echo "== mutation tests =="
run_mutations

echo
echo "mutation: killed=$MUT_KILLED survived=$MUT_SURVIVED"
if [ "$MUT_SURVIVED" -gt 0 ]; then
  echo "FAILED:$FAILED_NAMES"
  exit 1
fi
echo "ALL PASS"

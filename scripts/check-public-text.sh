#!/usr/bin/env bash
# The plugin's Done-when grep: words the shipped files and the self-check's
# output must never contain. Run from anywhere: bash scripts/check-public-text.sh
# Exit status 1 when any check finds something; each hit is printed.
set -u
cd "$(dirname "$0")/.." || exit 2
fail=0

# The renderer holds the self-check's own deny list, so it is not searched
# for the words it refuses (unless INCLUDE_RENDERER is set). ALLOW (an
# extended regex) drops known-good hits.
check() { # label, extended regex, paths...
  local label=$1 pattern=$2
  shift 2
  local hits
  if [ -n "${INCLUDE_RENDERER:-}" ]; then
    hits=$(grep -rnIE -- "$pattern" "$@" 2>/dev/null)
  else
    hits=$(grep -rnIE --exclude=render_report.py -- "$pattern" "$@" 2>/dev/null)
  fi
  if [ -n "${ALLOW:-}" ] && [ -n "$hits" ]; then
    hits=$(printf '%s\n' "$hits" | grep -vE -- "$ALLOW")
  fi
  if [ -n "$hits" ]; then
    printf '%s\n' "$hits"
    echo "FAIL: $label"
    fail=1
  else
    echo "ok:   $label"
  fi
}

# 1. Retired score-era words, wherever users read (README, skills, commands).
check "score-era words" '0–100|reproducibility score|free trial|trial runs|Level [0-9N] of 3' \
  README.md skills commands

# 2. The self-check's sources: written only from RepoReady's public guides.
#    No account or pricing words, no thresholds in the instructions.
SELF_CHECK="skills/reproducibility-self-check commands/self-check.md"
#    The optional signed-in mode (signed-in.md) tells the credits of an
#    official fix check by design: it is left out of the credits word here
#    and checked below for every other pricing word.
SIGNED_IN=skills/reproducibility-self-check/signed-in.md
ALLOW="^$SIGNED_IN:" check "self-check: account and pricing words" \
  'free trial|own (API |OpenRouter )?key|OpenRouter|(^|[^a-z])credits?([^a-z]|$)|\$[0-9]|about \$' \
  $SELF_CHECK
check "self-check signed-in mode: no dollars, own keys or trials" \
  'free trial|own (API |OpenRouter )?key|OpenRouter|\$[0-9]|about \$|[Uu][Ss][Dd]|dollar' \
  $SIGNED_IN
check "self-check: thresholds in the instructions" \
  '[0-9]+ ?%|>= ?[0-9]|≥ ?[0-9]' \
  skills/reproducibility-self-check/SKILL.md commands/self-check.md

# 3. The self-check's output: the template and freshly rendered example
#    reports never carry a badge, badge Markdown, a certification claim or a
#    score.
out=$(mktemp -d)
for f in tests/fixtures/*.findings.json; do
  python3 skills/reproducibility-self-check/scripts/render_report.py "$f" --no-previous --out-dir "$out" >/dev/null || {
    echo "FAIL: render $f"
    fail=1
  }
done
check "self-check output: no badge, score or certification claim" \
  '[Bb]adge|shields\.io|!\[|[Cc]ertified|reproducibility score|[0-9]+ ?/ ?100' \
  skills/reproducibility-self-check/assets/report-template.html "$out"
rm -rf "$out"

# 4. A public repository: no local paths, non-production hosts or scratch
#    folders (the guides' own example path /Users/you/data is fine).
ALLOW='/Users/you/' check "local paths and non-production hosts" \
  '/Users/[a-z]|/private/tmp|localhost' \
  README.md CHANGELOG.md AGENTS.md CLAUDE.md skills commands docs .claude-plugin .mcp.json tests

# 5. The self-check has one version, v0.1. The rubric is
#    the skill's and has no version of its own; no text names another skill
#    version or a revision number. The plugin's own version (2.1.0) is
#    fine. The renderer is searched too (its SKILL_VERSION). On the skill's next release, raise SKILL_V together with the
#    renderer's SKILL_VERSION, SKILL.md and the reference headers.
SKILL_V=0.1
PUBLIC="README.md CHANGELOG.md skills commands .claude-plugin tests docs"
INCLUDE_RENDERER=1 check "self-check: no rubric version, rubric bump or revision number" \
  '[Rr]ubric[ _-]?\(?(v|version )?[0-9]|[Rr]ubric_version|RUBRIC_VERSION|[Rr]ubric bump|[Rr]evision [0-9]|\(rev\. ?[0-9]|earlier versions' \
  $PUBLIC
# Every place that names the self-check's version: the text labels, the
# findings.json field and the renderer's constant. Each must be SKILL_V.
skill_v_re=$(printf '%s' "$SKILL_V" | sed 's/\./\\./g')
hits=$(grep -rnoIE -- '[Ss]elf-check( skill)?( version)? v?[0-9]+(\.[0-9]+)+|[Ss]kill( version)? v?[0-9]+(\.[0-9]+)+|"skill_version": *"[^"]*"|SKILL_VERSION *= *"[^"]*"' \
  $PUBLIC 2>/dev/null | grep -vE -- "(v|[ \"])${skill_v_re}\"?\$")
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  echo "FAIL: self-check: every skill version is v$SKILL_V"
  fail=1
else
  echo "ok:   self-check: every skill version is v$SKILL_V"
fi

exit $fail

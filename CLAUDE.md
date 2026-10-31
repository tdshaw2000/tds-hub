# tds-hub

Home page for tds-hub.duckdns.org, linking the apps on the owner's OCI VM. Static site in
`site/` (the app list is `site/apps.json`), served by an nginx container behind the shared edge
Caddy that lives in the scramble-challenge repo's `edge/`. See README.md for layout and deploys.

Merging to `main` deploys to the live site within a minute (`.github/workflows/deploy.yml`).

## Checks

`python3 scripts/check_site.py` and `python3 -m unittest discover -s tests`. Standard library
only. CI runs both on every PR, plus `docker compose -f deploy/compose.yaml config -q`. New
behaviour in `scripts/` gets a test. For changes to the page itself, load it in a browser
(`python3 -m http.server -d site 8000`) and check there are no console errors.

## Review loop

Open PRs as drafts. Once review and CI pass, Claude marks the PR ready and merges it with a
merge commit (never squash or rebase). The owner is told what shipped but does not merge.

Every PR is reviewed by the `reviewer` subagent (.claude/agents/reviewer.md) before it is marked
ready or merged. A hook (.claude/hooks/review_gate.py, copied from scramble-challenge) enforces
this. It blocks opening a PR that isn't a draft, and blocks marking ready or merging until the
pushed HEAD commit has a passing review. It also blocks merges that aren't merge commits of that
exact commit, auto-merge, --admin merges and merges through gh api. Verdicts live in
.git/claude-review/, one file per branch, never committed; to restart a branch's round count
(only when the owner says so), delete its file, with any / in the branch name written as __.

1. Finish the work, commit, push, and open the PR as a draft.
2. Run the `reviewer` subagent (subagent_type exactly `reviewer`). Give it the PR number and one
   line on what the change is for. Don't tell it what to conclude.
3. **Blocking findings**: fix each one, push, and run the reviewer again. After three rounds
   with blocking findings, stop, leave the PR unmerged, and tell the owner what is blocking.
4. **Once it passes**, post the suggestions as one PR review with event COMMENT and one inline
   comment per suggestion. Don't act on suggestions unless they are trivial.
5. **Judgment calls** take the reviewer's recommendation. List each one, with the choice made,
   in the PR review body and in the message to the owner.
6. Wait for CI to be green on the reviewed commit, then mark the PR ready and merge it with
   merge_method "merge" and expectedHeadSha set to the reviewed commit.
7. Check the Deploy run on `main` is green before saying anything shipped.

## The live server

The owner runs every server command; Claude has no access. The VM has no GitHub login: every
repo it pulls is public and cloned over https. Give clone commands as https URLs.

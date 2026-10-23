# Brain Live: security and participant-readiness review

**Reviewed:** 23 October 2026 (Europe/Berlin)  
**Repository:** `romius/sample-agents`, branch `brain-dashboard`  
**Code baseline:** [`dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22`](https://github.com/romius/sample-agents/commit/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22)  
**Scope:** documentation and recommendations; the application changes proposed below are not implemented by this review.

## 1. Recommendation

**Offer the idea to the Brain community, with a small opt-in pilot as the next step. The current branch is a useful private monitor, but it is not ready to become a general hosted dashboard for every participant.**

The strongest product proposition is a clear operational view of the shared lab: what is queued, what is running, what finished, which result belongs to a selected participant, and how it relates to the public leaderboard. The implementation already separates best and latest runs, distinguishes execution errors from low scores, shows simultaneous running jobs, and preserves timestamps when a source becomes unavailable.

The credential findings are reassuring within the reviewed scope: no embedded credential was found in the tracked text files, the associated Site stores `BRAIN_MCP_URL` as a secret, and the browser does not receive that configured URL. The main release risks are authorization, publication of account-accessible data, hardcoded participant identity, cache isolation, and upstream read volume.

| Distribution model | Readiness | Required next step |
| --- | --- | --- |
| Existing private owner deployment | Appropriate for continued personal use, subject to the limitations below | Keep its restricted audience; verify the deployed HTTP access boundary and operational controls |
| Private installation per participant | Closest to the present architecture; suitable for a pilot after changes | Remove personal constants, document private hosting, and require each operator's own server-held connection |
| One shared participant dashboard | Best low-friction community experience, conditional on an approved shared feed | Agree publishable fields with BitGN, use a dedicated collector, and enforce the intended audience |
| Hosted service with each participant's own credential | Not ready | Implement authentication, credential lifecycle, tenant isolation, scoped caches, and deletion/revocation |

For broad adoption, prefer **one organizer-approved shared feed with a participant selector** when all displayed information can be shared. A selector should say **Selected participant** unless the viewer's identity has actually been authenticated and mapped. Collecting everyone's personal key adds a substantial trust and operations burden and is unnecessary for an approved common overview.

## 2. Challenge and participant context

The platform is **BitGN (`bitgn.com`)**; its collaborative workspace is **`brain.bitgn.com`**.

The original ECOM1 competition took place on 30 May 2026. Its Hall of Fame is frozen, while DEV and PROD remain available for practice. At the review date, the Brain homepage describes an ECOM2 collaborative sandbox using ECOM1 production tasks. The product should describe its actual workspace and benchmark, rather than imply that the original competition is still running. [O1], [O2]

There are two distinct onboarding paths:

| Path | Credentials and workflow | Relationship to Brain Live |
| --- | --- | --- |
| Standard ECOM1 sample agent | Sign in to BitGN, obtain `BITGN_API_KEY`, configure a model-provider key, run the Python sample, inspect feedback and My runs | Executes benchmark tasks; this dashboard does not use those sample-agent keys |
| Shared Brain workspace | Create a Brain agent configuration and follow the official connection instructions; the connection page refers to an `agt-…` agent key | Brain Live expects the complete configured Brain MCP connection URL in `BRAIN_MCP_URL` |

Public connection material does not establish the exact permissions, expiry, rotation behavior, or availability of a truly read-only credential. These must be confirmed with BitGN. No real key was retrieved or used during this review. [O3], [O4]

The official site already provides a progress view, a workspace, account run details, and public leaderboards. The value proposition is **bringing operational questions into one understandable view**, not claiming the platform has no progress reporting. The live Brain UI and authenticated onboarding were not visually tested. [O1], [O5]

### Interpret scores and rankings correctly

The PROD live leaderboard chooses the best evaluated run per account, ordered by `total_trials × score`. Its `xN` suffix counts positive-scoring evaluated submissions. It is not a stream of every attempt. The quickstart distinguishes summed trial durations from elapsed wall-clock time. [O6], [O3]

Brain Live filters that public HTML table for names beginning with `Brain `. This is a naming heuristic: it cannot prove membership, completeness, or ownership. An account whose best public run has a different name can disappear from this subset even while its Brain activity exists.

Scores reflect graded outcomes, policies, required evidence, and output contracts; they are not simply percentages of perfectly solved tasks. Short evaluations, diagnostic carriers, and complete 100-trial runs need separate interpretation. New practice results do not change the historical Hall of Fame. [O7], [O2]

## 3. Credential and data-flow audit

### 3.1 What was verified

| Location or mechanism | Observed behavior | Assessment |
| --- | --- | --- |
| Tracked repository text | Pattern scan of all 146 tracked text files found no literal Brain agent key, common provider token, private-key block, JWT-like secret, or literal credential assignment | No embedded credential found within this scope; not a complete historical secret-scanner certification |
| Dashboard path history | The GitHub history query for `brain-dashboard/` returned its single introducing commit | The current snapshot covers that returned path history; other branches, deleted files elsewhere, and binary assets were not audited |
| Associated Site runtime settings | `BRAIN_MCP_URL` exists with `is_secret: true`; the API returns a redacted value | Secret storage confirmed by metadata, without retrieving the value |
| Associated Site access settings | `custom` audience, one allowlisted account, no groups or external visitors | Restricted audience confirmed by metadata; not an anonymous HTTP or alternate-origin penetration test |
| `.openai/hosting.json` | Contains a Site project ID and null D1/R2 bindings | A project ID identifies a resource; it is not the Brain credential |
| Browser network path | The page fetches same-origin `/api/live` | Reviewed response construction does not return the configured endpoint or MCP session identifiers |
| Browser storage | The normalized snapshot is written to `sessionStorage` under `brain-live:last-success:v1` | Challenge data is stored in the tab, although the credential is not |
| Server storage | Successful source values are retained in module memory; no dashboard database persistence is implemented | Cache lifetime depends on the Worker instance; no durable history is guaranteed |

Site configuration is a dated operational observation. It is not encoded by this Git branch, and the deployed build was not proven byte-for-byte identical to the reviewed commit. Credentials, access-policy identities, and deployment tokens are deliberately omitted.

### 3.2 How the key is used

1. The browser sends `GET /api/live`.
2. `worker/index.ts` reads `env.BRAIN_MCP_URL` and passes it to `getLiveSnapshot`.
3. `lib/live-service.mjs` uses that value directly as the destination for server-side JSON-RPC `POST` requests.
4. The server calls `initialize`, then `brain_start`, then `brain_run` with the fixed Python collector from `lib/live-data.mjs`.
5. The collector selects workspace `w1`, reads queue/history/results and the baseline, prints compact JSON, and calls `brain.discard()` on the successful path.
6. The Worker returns normalized challenge data and timestamps. Separately, it fetches the public PROD leaderboard over HTTPS without a participant credential.

**There is no explicit `Authorization: Bearer …` or `X-API-Key` header in this client.** Its headers are `Content-Type`, `Accept`, and, when supplied by initialization, `Mcp-Session-Id`. The complete connection URL must be treated as a capability-bearing secret. This review did not inspect its real path/query format or independently establish the provider's authentication implementation. [S1], [S2], [S3]

The Brain route does not use the starter's generic Sites connector binding or the unused ChatGPT authentication helper. Those files being present does not add authorization to `/api/live`. [S1], [S5]

The sibling Python sample has a different flow: `ecom-py/main.py` reads `BITGN_API_KEY` and passes it in `StartRunRequest.api_key`. A model-provider key is used by the sample agent, not the dashboard collector. These credentials are not interchangeable. [S9]

### 3.3 Existing protections

- The fixed collector does not submit/cancel evaluations or create/edit/commit documents.
- The browser cannot choose an endpoint, tool name, Python program, or workspace through the current API. This is not an arbitrary public MCP proxy.
- The endpoint and session identifiers are not included in the response. Upstream errors become generic messages.
- The active page uses React text rendering for names and parsed leaderboard text, without raw HTML insertion.
- Success responses use `Cache-Control: private, no-store` and `X-Content-Type-Options: nosniff`.
- Git excludes local environment files, Worker state, generated builds, and common package-manager logs. Local tooling defaults Wrangler telemetry and file logging off.
- Local environment injection into Worker variables is conditional on `serve`; the configuration does not intentionally embed the runtime credential in production builds.
- Source deadlines, original successful-update timestamps, and stale fallback are implemented. The cache deliberately avoids sharing pending Worker I/O across requests. [S1], [S2], [S4], [S6], [S8]

These properties do not prove the absence of credentials in production logs, source maps, previous deployments, operator machines, screenshots, or monitoring.

## 4. Prioritized recommendations

**P0** means a blocker for the affected sharing model, not a confirmed active breach. **P1** means required for a dependable participant release. **P2** means subsequent hardening or usability work.

### R01 · P0 for shared hosting: enforce the intended audience

**Evidence:** `/api/live` checks the HTTP method and reads with the deployment's credential. It has no user, membership, or role check. The auth helper is not called. The currently restricted Site gateway is the operative access boundary. [S1], [S5]

**Change:** Decide whether the response is public, member-only, or private per operator. For protected data, enforce that boundary before upstream work through a trusted gateway and/or application authorization. Protect the API and all deployment aliases as well as the HTML page. Do not trust caller-supplied identity headers on an unprotected standalone Worker.

**Acceptance:** Anonymous/nonmember requests to protected data fail without contacting Brain; authorized requests succeed. A deliberately public endpoint returns only the approved public response. Changing the Site audience cannot silently expose personal data.

### R02 · P0 for broad distribution: verify credential privileges and lifecycle

**Evidence:** `brain-live-readonly` and the read-only task description express intent. They do not constrain provider permissions; the connection invokes generic `brain_run`. [S2], [S3]

**Change:** Prefer a BitGN-supported read-only API/feed or dedicated scoped service credential. If unavailable, agree the residual risk of a fixed server-side read adapter and protect the broader credential accordingly. Document the operator, rotation/revocation, and redaction of URL-bearing logs. A service accepting personal keys must disclose that its backend operator processes those credentials.

**Acceptance:** Actual capability restrictions are demonstrated, or compensating controls and remaining privileges are explicitly accepted. Revocation removes access and invalidates relevant cached data. No arbitrary tool/source input is accepted.

### R03 · P0 for shared hosting: publish an explicit field allowlist

**Evidence:** JSON includes job/document/run IDs, authors, names, timestamps, scores, failures, model-call counts, costs, completeness flags, and up to 650 characters of baseline text. Some fields are not displayed. Hiding another participant's link in React does not remove its `runId` from the response. [S3], [S4]

**Change:** Agree publishable fields with BitGN and construct a dedicated public/member response on the server. Omit unused baseline prose, costs, and internal IDs unless their publication is intended. Collaboration is not blanket approval to redistribute every credential-accessible response; platform policies publish artifacts according to the applicable rules. [O8], [O9]

**Acceptance:** Raw responses contain only approved fields. Documentation explains audience, source, retention, and links. Hidden-but-delivered private fields are not used as an access-control mechanism.

### R04 · P0 before multiple credentials: isolate caches and stale fallback

**Evidence:** `createLiveReader` closes over one `cached`, `lastBrain`, and `lastPublic`, without an endpoint/identity/workspace key. The exported reader is a singleton. [S2]

Offline probes against the exact implementation, with fake readers and no network, reproduced:

| Sequence | Observed response |
| --- | --- |
| Successful A, then B inside the cache TTL | A's snapshot; B's reader is never called |
| Successful A, then failing B with `cacheMs: 0` | A's stale snapshot |
| Successful A, then no configured endpoint | A's stale snapshot |

This does not demonstrate a current cross-user leak in a deployment with one fixed secret. It is a concrete blocker to per-user credentials or runtime account switching.

**Change:** Key fresh and stale data by an opaque credential identity, workspace, and authorization scope. Invalidate on configuration changes and revocation. A public common feed may deliberately use a common cache, but it must never mix with private responses.

**Acceptance:** Tests prove A cannot receive B's fresh or stale data, including failures, logout, credential removal, and rotation. Raw secrets are not exposed in cache keys or logs.

### R05 · P0 for participant rollout: remove personal assumptions and fix ownership

**Evidence:** `romius` is hardcoded in normalization, collection, labels, and filters. Workspace `w1`, baseline document `d7`, and a historical watched job are fixed. Only `romius` receives additional history from the 100-job window. [S3], [S4]

Leaderboard ownership uses a case-insensitive `romius` substring in the **run name**, whereas queue/history use exact author identity. A public run by another participant crediting `(romius)` in its title is an actual counterexample: it is incorrectly treated as yours. [S4], [O6]

**Change:** Introduce validated participant/workspace configuration or a neutral selector. Map Brain author identity to a stable BitGN account ID. Parse that ID separately from its `xN` display suffix. Make baseline links and watched jobs configurable, with the pin optional. These proposed fields are not currently implemented environment variables.

**Acceptance:** Two participants can use their queue, latest/best cards, filters, and links without editing source. Contributor mentions do not imply ownership; an owned run without the participant's name remains attributed correctly. History coverage is consistent.

### R06 · P1: bound upstream load independently of visitor count

**Evidence:** Each uncached request initializes a Brain session and collects results. The 30-second cache belongs to one Worker instance, not the deployment; concurrent cold requests can repeat work. If the public HTML leaderboard fails, the combined result is not cached even when Brain succeeds. Manual browser refresh is also available. [S2], [S4]

**Change:** For a common dashboard, use a scheduled or durably coordinated collector with source-specific caches, rate limits, bounded concurrency, backoff/jitter, and source-freshness monitoring. Agree a polling budget with BitGN. Do not reintroduce a pending promise shared across unrelated Worker request lifetimes.

**Acceptance:** A defined concurrent-viewer target produces a bounded upstream read rate. A leaderboard outage does not trigger repeated full Brain collections. Retained data carries its original timestamp.

### R07 · P1: make partial collection and cleanup robust

**Evidence:** A failure reading the pinned job, any result, or the baseline can abort the whole Python snapshot. `brain.discard()` is at the end, not in `finally`. A transport failure retries `brain_run` with the same session/sequence; the client alone cannot establish idempotence. [S2], [S3]

**Change:** Isolate optional enrichments and report per-source/per-job availability. Make the pin optional. Confirm BitGN's sequence, retry, cleanup, and MCP-version contract. Use supported cleanup in a `finally` path where appropriate.

**Acceptance:** Missing pin/baseline/result data leaves unrelated queue data usable. A timeout cannot duplicate unintended work or abandon a session indefinitely. Incomplete values remain unavailable rather than silently becoming zero.

### R08 · P1: align browser retention with the access model

**Evidence:** The normalized snapshot is saved in `sessionStorage` with a fixed key and no identity namespace or logout cleanup. HTTP `no-store` does not disable JavaScript storage. [S4]

**Change:** State this behavior accurately. For private/personal data, remove unnecessary persistence or scope it by identity/workspace and clear it when access changes. Provide a clear-data action if retention remains. Treat screenshots/copied JSON as exports.

**Acceptance:** User changes/logout cannot display prior-user snapshots. Documentation distinguishes server-held credentials from browser-held data. Sensitive fields are minimized before storage.

### R09 · P1 before credential-entry onboarding: validate the endpoint

**Evidence:** The server fetches the configured URL directly without a restrictive redirect policy. Today it is administrator-managed, so this is not a demonstrated visitor-controlled SSRF vulnerability. [S2]

**Change:** Before accepting submitted URLs, require HTTPS and approved Brain hosts/paths, reject URL userinfo and internal destinations, and reject or validate redirects. Never echo credential-bearing URLs in validation errors or telemetry. Keep keys out of dashboard query strings and client-visible environment variables.

**Acceptance:** Malformed, HTTP, unexpected-host, private-network, and untrusted-redirect cases fail before secrets reach an unintended destination.

### R10 · P1: make coverage, scores, and ranking semantics precise

**Evidence:** Collection includes the active queue, 25 recent nonqueue jobs from the latest 100, additional `romius` jobs within that 100, and one pin. The main heading nevertheless says all Brain runs. Best selection is correctly limited to an evaluated completed full100 in loaded data. Queue progress substitutes unknown counts with zero. The public subset uses the `Brain ` prefix. [S3], [S4], [S7]

**Change:** Label the page Brain activity; show the history window and distinguish best in available history from all-time best. Separate official global rank from the derived subset position. Use indeterminate progress for unknown counts and processed when counts include failures. Explain normalized short-test scores. Prefer explicit diagnostic metadata: the current classifier treats every 100-trial job as full before checking its name.

**Acceptance:** Users can explain missing leaderboard entries, different short/full coverage, and missing history. Zero scores do not imply crashes; unknown values stay unknown. If queue ETA is added, label its assumptions; the current `estimateMinutes` calculation is not rendered.

### R11 · P1 for adoption: provide neutral English onboarding

**Evidence:** The UI uses Russian labels, `ru-RU`, Berlin time, and personal wording. There is no participant configuration flow. [S4]

**Change:** Provide English by default, optional RU, and a visible timezone setting. Explain Brain versus the benchmark/Hall of Fame, the tabs, timestamps, and viewing versus running an agent. Add Where is my run?, setup diagnostics, and an unofficial-project notice.

**Acceptance:** A new English-speaking participant can find their run, understand state/coverage, and open official details without reading implementation code. Missing connections yield actionable guidance without exposing a key.

### R12 · P1 release gate, then P2 improvements: verify distribution and maintenance

**Change:** Before wider distribution, run the production build, type checking, linting, a current dependency advisory scan, and a secret scan of generated artifacts/source maps with a harmless sentinel. Verify gateway/API protection, HTTPS/security headers, log redaction, and actual mobile/keyboard behavior. Add targeted authorization, payload-allowlist, cache-isolation, and identity tests.

The reviewed tree has no top-level project license file. Clarify dashboard reuse licensing and upstream rights before inviting redistribution; preserve bundled third-party notices. Public visibility and `package.json`'s `private: true` are not licensing decisions.

The beta `vinext` dependency is a support/compatibility consideration, not an unverified vulnerability. HTML leaderboard parsing is another maintenance dependency; prefer a supported structured feed, otherwise retain fixtures and a visible unavailable state.

**P2 usability:** Add accessible selected-state semantics to tabs, review small table text/touch targets, and verify screen-reader progress and 200% zoom. Responsive CSS, focus outlines, reduced-motion support, and accessible labels already exist; compliance was not established by source inspection.

**Acceptance:** A reproducible release check records the deployed version, successful checks, known limits, support owner, and rollback procedure. A clean advisory scan is dated, not treated as a permanent guarantee.

## 5. Suggested delivery sequence

| Stage | Deliverable | Exit condition |
| --- | --- | --- |
| 1. Choose the audience | Private installations or an organizer-approved common feed; named operator/data owner | Credential privileges, publishable fields, and request budget understood |
| 2. Remove personal coupling | Account mapping, workspace/baseline configuration, optional pin, accurate labels | Two participants have correct identities and comparable history coverage |
| 3. Protect and stabilize | Audience enforcement, sanitized responses, cache boundaries, retention policy, bounded collection, partial failures | Relevant P0 items and release-critical P1 checks pass |
| 4. Pilot | Two or three consenting participants; English guide and feedback path | Runs are understandable; no unintended disclosure; agreed upstream budget respected |
| 5. Offer broadly | Versioned release, support instructions, license, short demonstration | Pilot issues resolved and actual deployment verified |

Introduce it to organizers as an independent read-only monitoring companion that makes queue state, current progress, recent outcomes, and participant results easier to follow. Confirm the supported integration and shared data contract before changing the private deployment's audience. This review does not send an invitation or claim endorsement.

## 6. Validation performed and limits

| Check | Result |
| --- | --- |
| Source/configuration review | Application, collector, auth scaffolding, tooling, lockfile presence, and structure inspected at the pinned commit |
| Tracked text secret scan | 146 text files scanned; no candidate literal credential found with the documented pattern classes; one binary image excluded |
| Dashboard path history | One introducing commit returned by the path-filtered history query |
| Site configuration | Restricted custom audience and secret-marked, redacted `BRAIN_MCP_URL` verified through read-only metadata |
| Existing test cases | 11 passed: four data/parser assertions, three service cases, four presentation cases |
| Python-backed fixture | Remaining case blocked by `spawnSync python3 EPERM` in the review environment; the standard aggregate command was not green |
| Cache identity probes | Cross-endpoint cache/fallback behavior reproduced offline with fake readers; no real credentials or network calls |
| Official documentation | Lifecycle, onboarding, ranking, scoring, fair play, and publication context checked |
| Not performed | Production build/typecheck/lint, advisory scan, visual/accessibility tests, authenticated Brain/MCP calls, anonymous/alternate-origin HTTP access tests, production bundle/log scan, full all-branch Git-history audit |

The environment did not provide an installed application dependency tree; direct GitHub cloning failed because its network proxy was unavailable. Source was retrieved through the GitHub integration. No runtime fixes were made to manufacture passing checks. These results support the findings, not a claim of production certification.

## 7. Evidence and references

### Reviewed implementation

- [S1 — Worker and API route](https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/worker/index.ts)
- [S2 — MCP transport, deadlines, cache and fallback](https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/lib/live-service.mjs)
- [S3 — Collector, normalization and leaderboard parser](https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/lib/live-data.mjs)
- [S4 — UI, storage, polling and ownership filters](https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/app/page.tsx)
- [S5 — Authentication helper](https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/app/chatgpt-auth.ts)
- [S6 — Local environment binding](https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/vite.config.ts)
- [S7 — Run classification and best/latest selection](https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/lib/run-presentation.mjs)
- [S8 — Git exclusions](https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/.gitignore) and [tool environment](https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/scripts/tool-environment.mjs)
- [S9 — Standard sample credential flow](https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/ecom-py/main.py)

Site access/secret observations came from authenticated settings metadata for the project identified by the reviewed `hosting.json`; no credential values or access-policy identities are reproduced.

### Official sources, checked 23 October 2026

- [O1 — BitGN Brain](https://brain.bitgn.com/)
- [O2 — ECOM1 lifecycle](https://bitgn.com/challenge/ecom)
- [O3 — ECOM1 quickstart](https://bitgn.com/start/ecom)
- [O4 — Brain connections](https://brain.bitgn.com/connect) and [agent configurations](https://bitgn.com/me/agents)
- [O5 — Official progress view](https://brain.bitgn.com/progress)
- [O6 — PROD live leaderboard](https://bitgn.com/l/ecom1-prod)
- [O7 — Scoring specification](https://github.com/bitgn/challenges/blob/main/ecom/04_scoring_penalties_leaderboards.md)
- [O8 — Terms of service](https://bitgn.com/app/doc/terms-of-service)
- [O9 — Privacy policy](https://bitgn.com/app/doc/privacy-policy)
- [O10 — Competition rules](https://github.com/bitgn/challenges/blob/main/ecom/03_competition_rules_fair_play.md)

ECOM1 rules permit collaboration and external observability within the platform contract, prohibit abuse of limits, and prohibit human steering inside active competition runs. Monitoring fits that direction; it does not confer permission to republish all account data or establish future ECOM2 rules. [O10]

[S1]: https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/worker/index.ts
[S2]: https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/lib/live-service.mjs
[S3]: https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/lib/live-data.mjs
[S4]: https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/app/page.tsx
[S5]: https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/app/chatgpt-auth.ts
[S6]: https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/vite.config.ts
[S7]: https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/lib/run-presentation.mjs
[S8]: https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/brain-dashboard/.gitignore
[S9]: https://github.com/romius/sample-agents/blob/dbf1240ef127292ce9ec499cf74d4e7c3f0a5f22/ecom-py/main.py
[O1]: https://brain.bitgn.com/
[O2]: https://bitgn.com/challenge/ecom
[O3]: https://bitgn.com/start/ecom
[O4]: https://brain.bitgn.com/connect
[O5]: https://brain.bitgn.com/progress
[O6]: https://bitgn.com/l/ecom1-prod
[O7]: https://github.com/bitgn/challenges/blob/main/ecom/04_scoring_penalties_leaderboards.md
[O8]: https://bitgn.com/app/doc/terms-of-service
[O9]: https://bitgn.com/app/doc/privacy-policy
[O10]: https://github.com/bitgn/challenges/blob/main/ecom/03_competition_rules_fair_play.md

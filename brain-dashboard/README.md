# Brain Live

Private live view of BitGN ECOM1's shared Brain lab.

- `/api/live` reads the Brain queue, running progress, current baseline and 25 recent jobs through MCP, retaining our other runs from the most recent 100 jobs and the pinned integration. It never edits documents, submits trials or cancels work.
- The public PROD leaderboard is fetched server-side and filtered to names beginning with `Brain `; it contains the best evaluated submission per account, not all executions.
- The page refreshes every 60 seconds while visible. The server caches resolved successful snapshots for 30 seconds. Requests never share pending I/O across Worker invocations. Each source has an 18-second deadline (10 seconds for the public leaderboard); the browser releases a stalled refresh after 25 seconds. Each source has its own successful-update timestamp; failures preserve the last valid source data within the current Worker instance. The browser also retains its last successful snapshot in sessionStorage across reloads, with the original source timestamps and stale-state indicator.
- Separate `romius` cards show the best evaluated completed full100 and the latest submission by creation time, regardless of state or type (including queued/diagnostic jobs). Running jobs have no priority in the latest card. The best result is limited to available Brain history: the latest 100 jobs plus the historical pinned integration. No ungraded run is assigned a score. All simultaneous running/cancelling jobs are listed with individual progress.
- History distinguishes full100, short evaluations and explicitly named diagnostics. Diagnostic carrier scores remain visible as service metadata, rather than agent-quality scores. A completed job with failed trials shows a warning; all-trial failures show a red failure state. Processed counts include failed trials and are labeled accordingly. Unknown failure counts stay unknown. A score of zero alone never implies a runtime crash.
- The median duration uses completed 100-trial jobs within the displayed recent history. Waiting estimates scale that median by queued trial counts and subtract elapsed running time. They are rough estimates, not scheduler promises.

## Runtime secret

Configure `BRAIN_MCP_URL` as a **secret** in Sites environment settings. Never include it in source, browser code, hosting.json or a shared snapshot. The Site is owner-private. Local preview can receive this value through its process environment.

## Commands

```sh
npm run dev
node --test lib/live-data.test.mjs lib/live-service.test.mjs
npx tsc --noEmit
npm run build
```

Sources: https://bitgn.com/l/ecom1-prod and the user's configured BitGN Brain MCP connection. All display times use Europe/Berlin. No local data snapshot or credentials are shipped to the browser; all names are rendered as plain text.

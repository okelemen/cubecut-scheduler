# CubeCut independent trigger

This Cloudflare Worker dispatches the existing GitHub publisher at 09:00 and
16:00 Turkey time. The publisher itself waits for 12:00/19:00 private upload
and 14:00/21:00 public publication. GitHub cron and watchdog remain backups.

The Worker contains no YouTube token, media key, or video. Store a GitHub
fine-grained personal access token with **Actions: write** permission limited
to `okelemen/cubecut-scheduler` as the Worker secret
`GITHUB_DISPATCH_TOKEN`. Never put the token in this repository or in chat.

After connecting a Cloudflare account, run from this directory:

1. `npx wrangler login`
2. `npx wrangler secret put GITHUB_DISPATCH_TOKEN`
3. `npx wrangler deploy`

Check the deployed Worker's Cron Triggers and logs, then trigger a scheduled
handler manually with a mock/test token before relying on it. Cloudflare cron
changes may take up to 15 minutes to propagate. No live deployment has been
performed yet.

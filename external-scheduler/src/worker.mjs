/** Independent early dispatch for the existing CubeCut publisher workflow. */

const REPO = "okelemen/cubecut-scheduler";
const ENDPOINT = `https://api.github.com/repos/${REPO}/actions/workflows/publish.yml/dispatches`;
const SLOTS = new Map([
  ["0 6 * * *", "morning"], // 09:00 Turkey time
  ["0 13 * * *", "evening"], // 16:00 Turkey time
]);

export default {
  async scheduled(controller, env) {
    const slot = SLOTS.get(controller.cron);
    if (!slot) throw new Error(`Unexpected cron: ${controller.cron}`);
    if (!env.GITHUB_DISPATCH_TOKEN) throw new Error("GitHub dispatch token missing");

    const scheduled = new Date(controller.scheduledTime);
    const lag = Date.now() - scheduled.getTime();
    if (lag < -60_000 || lag > 90 * 60_000) {
      throw new Error(`Dispatch outside safe lead window: ${slot} lag=${lag}ms`);
    }

    const date = scheduled.toISOString().slice(0, 10);
    const response = await fetch(ENDPOINT, {
      method: "POST",
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${env.GITHUB_DISPATCH_TOKEN}`,
        "Content-Type": "application/json",
        "User-Agent": "cubecut-external-scheduler",
        "X-GitHub-Api-Version": "2022-11-28",
      },
      body: JSON.stringify({
        ref: "main",
        inputs: { slot, date, dry_run: "false", recovery: "false" },
      }),
    });
    if (response.status !== 204) {
      throw new Error(`GitHub dispatch failed: HTTP ${response.status}`);
    }
    console.log(`CubeCut publisher dispatched: ${date} ${slot}`);
  },
};

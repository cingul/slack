import { getConfig } from "./config.js";
import { FileScheduleStore } from "./services/scheduleStore.js";
import { ScheduleService } from "./services/scheduleService.js";
import { createSlackApp } from "./slack/app.js";

const config = getConfig();

if (!config.SLACK_BOT_TOKEN || !config.SLACK_SIGNING_SECRET) {
  throw new Error(
    "Set SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET before starting the schedule app."
  );
}

const store = new FileScheduleStore(config.SCHEDULE_STORE_PATH);
const service = new ScheduleService(store);
const app = createSlackApp(config, service);

await app.start(config.PORT);
console.log(`Schedule manager is running on port ${config.PORT}.`);

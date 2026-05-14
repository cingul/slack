import { App } from "@slack/bolt";
import type { AppConfig } from "../config.js";
import type { ScheduleService } from "../services/scheduleService.js";
import { registerScheduleCommands } from "./commands.js";

export function createSlackApp(config: AppConfig, service: ScheduleService): App {
  const app = new App({
    token: config.SLACK_BOT_TOKEN,
    signingSecret: config.SLACK_SIGNING_SECRET,
    socketMode: Boolean(config.SLACK_APP_TOKEN),
    appToken: config.SLACK_APP_TOKEN
  });

  registerScheduleCommands(app, service);
  return app;
}

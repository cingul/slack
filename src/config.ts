import path from "node:path";
import { config as loadEnv } from "dotenv";
import { z } from "zod";

loadEnv();

const configSchema = z.object({
  SLACK_BOT_TOKEN: z.string().startsWith("xoxb-").optional(),
  SLACK_SIGNING_SECRET: z.string().min(1).optional(),
  SLACK_APP_TOKEN: z.string().startsWith("xapp-").optional(),
  PORT: z.coerce.number().int().positive().default(3000),
  SCHEDULE_STORE_PATH: z.string().default(path.resolve("data", "schedules.json"))
});

export type AppConfig = z.infer<typeof configSchema>;

export function getConfig(env: NodeJS.ProcessEnv = process.env): AppConfig {
  return configSchema.parse(env);
}

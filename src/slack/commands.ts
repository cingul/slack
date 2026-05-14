import type { App } from "@slack/bolt";
import { formatScheduleEntry } from "../domain/schedule.js";
import type { ScheduleService } from "../services/scheduleService.js";

type ParsedScheduleCommand =
  | { type: "add"; title: string; startAt: Date; endAt?: Date }
  | { type: "list"; date?: string }
  | { type: "remove"; id: string }
  | { type: "help" }
  | { type: "invalid"; message: string };

const helpText = [
  "*Schedule manager commands*",
  "`/schedule add YYYY-MM-DD HH:mm[-HH:mm] Title` - add an item",
  "`/schedule list [YYYY-MM-DD]` - list items for this channel",
  "`/schedule remove ID` - remove an item",
  "`/schedule help` - show this help",
  "",
  "Times are interpreted as UTC in this bootstrap."
].join("\n");

export function registerScheduleCommands(app: App, service: ScheduleService): void {
  app.command("/schedule", async ({ command, ack, respond }) => {
    await ack();

    const parsed = parseScheduleCommand(command.text);

    try {
      if (parsed.type === "help") {
        await respond({ response_type: "ephemeral", text: helpText });
        return;
      }

      if (parsed.type === "invalid") {
        await respond({
          response_type: "ephemeral",
          text: `${parsed.message}\n\n${helpText}`
        });
        return;
      }

      if (parsed.type === "add") {
        const entry = await service.add({
          title: parsed.title,
          startAt: parsed.startAt,
          endAt: parsed.endAt,
          ownerId: command.user_id,
          channelId: command.channel_id
        });

        await respond({
          response_type: "in_channel",
          text: `Scheduled: ${formatScheduleEntry(entry)}`
        });
        return;
      }

      if (parsed.type === "list") {
        const entries = await service.list({
          date: parsed.date,
          channelId: command.channel_id
        });

        await respond({
          response_type: "ephemeral",
          text: entries.length
            ? entries.map(formatScheduleEntry).join("\n")
            : "No scheduled items found for this channel."
        });
        return;
      }

      const removed = await service.remove(parsed.id, command.channel_id);
      await respond({
        response_type: removed ? "in_channel" : "ephemeral",
        text: removed
          ? `Removed: ${formatScheduleEntry(removed)}`
          : `No schedule item found with ID \`${parsed.id}\` in this channel.`
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      await respond({
        response_type: "ephemeral",
        text: `Unable to update the schedule: ${message}`
      });
    }
  });
}

export function parseScheduleCommand(text: string): ParsedScheduleCommand {
  const trimmed = text.trim();

  if (!trimmed || trimmed === "help") {
    return { type: "help" };
  }

  const [action] = trimmed.split(/\s+/, 1);

  if (action === "add") {
    return parseAddCommand(trimmed);
  }

  if (action === "list") {
    return parseListCommand(trimmed);
  }

  if (action === "remove") {
    return parseRemoveCommand(trimmed);
  }

  return {
    type: "invalid",
    message: `Unknown schedule action \`${action}\`.`
  };
}

function parseAddCommand(text: string): ParsedScheduleCommand {
  const match = text.match(
    /^add\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})(?:-(\d{2}:\d{2}))?\s+(.+)$/
  );

  if (!match) {
    return {
      type: "invalid",
      message: "Use `add` with a date, time, and title."
    };
  }

  const [, date, startTime, endTime, title] = match;
  const startAt = parseUtcDateTime(date, startTime);
  const endAt = endTime ? parseUtcDateTime(date, endTime) : undefined;

  if (!startAt || (endTime && !endAt)) {
    return {
      type: "invalid",
      message: "Use valid dates and 24-hour times, for example `2026-05-15 09:00`."
    };
  }

  return { type: "add", title, startAt, endAt };
}

function parseListCommand(text: string): ParsedScheduleCommand {
  const match = text.match(/^list(?:\s+(\d{4}-\d{2}-\d{2}))?$/);

  if (!match) {
    return {
      type: "invalid",
      message: "Use `list` with an optional date, for example `list 2026-05-15`."
    };
  }

  const [, date] = match;

  if (date && !isValidDateOnly(date)) {
    return {
      type: "invalid",
      message: "Use a valid list date in `YYYY-MM-DD` format."
    };
  }

  return { type: "list", date };
}

function parseRemoveCommand(text: string): ParsedScheduleCommand {
  const match = text.match(/^remove\s+([a-zA-Z0-9-]+)$/);

  if (!match) {
    return {
      type: "invalid",
      message: "Use `remove` with the schedule item ID."
    };
  }

  return { type: "remove", id: match[1] };
}

function parseUtcDateTime(date: string, time: string): Date | undefined {
  if (!isValidDateOnly(date) || !isValidTime(time)) {
    return undefined;
  }

  const [year, month, day] = date.split("-").map(Number);
  const [hour, minute] = time.split(":").map(Number);
  const value = new Date(Date.UTC(year, month - 1, day, hour, minute));

  if (
    value.getUTCFullYear() !== year ||
    value.getUTCMonth() !== month - 1 ||
    value.getUTCDate() !== day ||
    value.getUTCHours() !== hour ||
    value.getUTCMinutes() !== minute
  ) {
    return undefined;
  }

  return value;
}

function isValidDateOnly(date: string): boolean {
  const [year, month, day] = date.split("-").map(Number);
  const value = new Date(Date.UTC(year, month - 1, day));

  return (
    value.getUTCFullYear() === year &&
    value.getUTCMonth() === month - 1 &&
    value.getUTCDate() === day
  );
}

function isValidTime(time: string): boolean {
  const [hour, minute] = time.split(":").map(Number);
  return hour >= 0 && hour <= 23 && minute >= 0 && minute <= 59;
}

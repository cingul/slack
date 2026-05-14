import { describe, expect, it } from "vitest";
import { parseScheduleCommand } from "../src/slack/commands.js";

describe("parseScheduleCommand", () => {
  it("parses add commands with an optional end time", () => {
    expect(parseScheduleCommand("add 2026-05-15 09:00-09:30 Morning standup")).toMatchObject({
      type: "add",
      title: "Morning standup",
      startAt: new Date("2026-05-15T09:00:00.000Z"),
      endAt: new Date("2026-05-15T09:30:00.000Z")
    });
  });

  it("parses list commands with an optional date", () => {
    expect(parseScheduleCommand("list 2026-05-15")).toEqual({
      type: "list",
      date: "2026-05-15"
    });
    expect(parseScheduleCommand("list")).toEqual({ type: "list", date: undefined });
  });

  it("parses remove commands", () => {
    expect(parseScheduleCommand("remove abc123")).toEqual({
      type: "remove",
      id: "abc123"
    });
  });

  it("returns help for blank or help commands", () => {
    expect(parseScheduleCommand("")).toEqual({ type: "help" });
    expect(parseScheduleCommand("help")).toEqual({ type: "help" });
  });

  it("rejects invalid dates and times", () => {
    expect(parseScheduleCommand("add 2026-02-31 09:00 Bad date")).toMatchObject({
      type: "invalid"
    });
    expect(parseScheduleCommand("add 2026-05-15 25:00 Bad time")).toMatchObject({
      type: "invalid"
    });
  });
});

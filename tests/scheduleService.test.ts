import { describe, expect, it } from "vitest";
import type { ScheduleEntry } from "../src/domain/schedule.js";
import { ScheduleService } from "../src/services/scheduleService.js";
import type { ScheduleStore } from "../src/services/scheduleStore.js";

class MemoryScheduleStore implements ScheduleStore {
  entries: ScheduleEntry[] = [];

  async list(): Promise<ScheduleEntry[]> {
    return [...this.entries];
  }

  async save(entries: ScheduleEntry[]): Promise<void> {
    this.entries = [...entries];
  }
}

describe("ScheduleService", () => {
  it("adds and lists channel-scoped schedule entries in chronological order", async () => {
    const store = new MemoryScheduleStore();
    const service = new ScheduleService(store);

    await service.add({
      title: "Later",
      startAt: new Date("2026-05-15T17:00:00.000Z"),
      channelId: "C123"
    });
    await service.add({
      title: "Earlier",
      startAt: new Date("2026-05-15T09:00:00.000Z"),
      channelId: "C123"
    });
    await service.add({
      title: "Other channel",
      startAt: new Date("2026-05-15T08:00:00.000Z"),
      channelId: "C999"
    });

    const entries = await service.list({ date: "2026-05-15", channelId: "C123" });

    expect(entries.map((entry) => entry.title)).toEqual(["Earlier", "Later"]);
  });

  it("rejects entries with an end time before the start", async () => {
    const service = new ScheduleService(new MemoryScheduleStore());

    await expect(
      service.add({
        title: "Bad range",
        startAt: new Date("2026-05-15T10:00:00.000Z"),
        endAt: new Date("2026-05-15T09:00:00.000Z")
      })
    ).rejects.toThrow("End time must be after the start time.");
  });

  it("removes entries by id within a channel", async () => {
    const store = new MemoryScheduleStore();
    const service = new ScheduleService(store);
    const entry = await service.add({
      title: "Planning",
      startAt: new Date("2026-05-15T12:00:00.000Z"),
      channelId: "C123"
    });

    await expect(service.remove(entry.id, "C999")).resolves.toBeUndefined();
    await expect(service.remove(entry.id, "C123")).resolves.toMatchObject({
      title: "Planning"
    });
    await expect(service.list({ channelId: "C123" })).resolves.toEqual([]);
  });
});

import { randomUUID } from "node:crypto";
import type {
  CreateScheduleEntry,
  ScheduleEntry,
  ScheduleListFilter
} from "../domain/schedule.js";
import type { ScheduleStore } from "./scheduleStore.js";

export class ScheduleService {
  constructor(private readonly store: ScheduleStore) {}

  async add(input: CreateScheduleEntry): Promise<ScheduleEntry> {
    const entries = await this.store.list();
    const now = new Date().toISOString();
    const title = input.title.trim();

    if (!title) {
      throw new Error("A schedule title is required.");
    }

    if (!isValidDate(input.startAt)) {
      throw new Error("Start time is invalid.");
    }

    if (input.endAt && (!isValidDate(input.endAt) || input.endAt <= input.startAt)) {
      throw new Error("End time must be after the start time.");
    }

    const entry: ScheduleEntry = {
      id: buildShortId(entries),
      title,
      startAt: input.startAt.toISOString(),
      endAt: input.endAt?.toISOString(),
      notes: input.notes?.trim() || undefined,
      ownerId: input.ownerId,
      channelId: input.channelId,
      createdAt: now,
      updatedAt: now
    };

    await this.store.save([...entries, entry]);
    return entry;
  }

  async list(filter: ScheduleListFilter = {}): Promise<ScheduleEntry[]> {
    const entries = await this.store.list();

    return entries
      .filter((entry) => (filter.channelId ? entry.channelId === filter.channelId : true))
      .filter((entry) => (filter.date ? entry.startAt.slice(0, 10) === filter.date : true))
      .sort((left, right) => left.startAt.localeCompare(right.startAt));
  }

  async remove(id: string, channelId?: string): Promise<ScheduleEntry | undefined> {
    const entries = await this.store.list();
    const entry = entries.find(
      (candidate) =>
        candidate.id === id && (channelId ? candidate.channelId === channelId : true)
    );

    if (!entry) {
      return undefined;
    }

    await this.store.save(entries.filter((candidate) => candidate.id !== entry.id));
    return entry;
  }
}

function buildShortId(entries: ScheduleEntry[]): string {
  const existingIds = new Set(entries.map((entry) => entry.id));
  let candidate = randomUUID().slice(0, 8);

  while (existingIds.has(candidate)) {
    candidate = randomUUID().slice(0, 8);
  }

  return candidate;
}

function isValidDate(value: Date): boolean {
  return !Number.isNaN(value.getTime());
}

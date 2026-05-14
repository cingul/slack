import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { z } from "zod";
import type { ScheduleEntry } from "../domain/schedule.js";

const scheduleEntrySchema = z.object({
  id: z.string(),
  title: z.string(),
  startAt: z.string().datetime(),
  endAt: z.string().datetime().optional(),
  notes: z.string().optional(),
  ownerId: z.string().optional(),
  channelId: z.string().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

const scheduleFileSchema = z.array(scheduleEntrySchema);

export interface ScheduleStore {
  list(): Promise<ScheduleEntry[]>;
  save(entries: ScheduleEntry[]): Promise<void>;
}

export class FileScheduleStore implements ScheduleStore {
  constructor(private readonly filePath: string) {}

  async list(): Promise<ScheduleEntry[]> {
    try {
      const contents = await readFile(this.filePath, "utf8");
      return scheduleFileSchema.parse(JSON.parse(contents));
    } catch (error) {
      if (isMissingFile(error)) {
        return [];
      }

      throw error;
    }
  }

  async save(entries: ScheduleEntry[]): Promise<void> {
    await mkdir(path.dirname(this.filePath), { recursive: true });
    await writeFile(this.filePath, `${JSON.stringify(entries, null, 2)}\n`, "utf8");
  }
}

function isMissingFile(error: unknown): boolean {
  return (
    typeof error === "object" &&
    error !== null &&
    "code" in error &&
    (error as NodeJS.ErrnoException).code === "ENOENT"
  );
}

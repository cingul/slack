export type ScheduleEntry = {
  id: string;
  title: string;
  startAt: string;
  endAt?: string;
  notes?: string;
  ownerId?: string;
  channelId?: string;
  createdAt: string;
  updatedAt: string;
};

export type CreateScheduleEntry = {
  title: string;
  startAt: Date;
  endAt?: Date;
  notes?: string;
  ownerId?: string;
  channelId?: string;
};

export type ScheduleListFilter = {
  date?: string;
  channelId?: string;
};

export function formatScheduleEntry(entry: ScheduleEntry): string {
  const start = formatDateTime(entry.startAt);
  const end = entry.endAt ? `-${formatTime(entry.endAt)}` : "";
  const owner = entry.ownerId ? ` by <@${entry.ownerId}>` : "";
  const notes = entry.notes ? ` - ${entry.notes}` : "";

  return `*${entry.id}* ${start}${end} - ${entry.title}${owner}${notes}`;
}

function formatDateTime(value: string): string {
  const date = new Date(value);
  return `${date.toISOString().slice(0, 10)} ${formatTime(value)}`;
}

function formatTime(value: string): string {
  const date = new Date(value);
  return date.toISOString().slice(11, 16);
}

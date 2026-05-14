# Schedule Slack Manager

A TypeScript Slack Bolt bootstrap for managing schedules from a Slack workspace or
channel such as `#schedule`.

## Features

- `/schedule add YYYY-MM-DD HH:mm[-HH:mm] Title` creates a schedule entry.
- `/schedule list [YYYY-MM-DD]` lists entries scoped to the Slack channel.
- `/schedule remove ID` removes an entry from the channel.
- `/schedule help` shows command usage.
- Entries are stored in a local JSON file configured by `SCHEDULE_STORE_PATH`.

Times are interpreted as UTC in this bootstrap. If the workspace needs local
timezone handling, add a timezone field to the parser/service boundary before
storing the entry.

## Local setup

```bash
npm install
cp .env.example .env
npm run dev
```

Set the Slack secrets in `.env` before starting the app:

- `SLACK_BOT_TOKEN`
- `SLACK_SIGNING_SECRET`
- `SLACK_APP_TOKEN` if using Socket Mode

## Slack app setup

1. Create a Slack app for the workspace.
2. Add a bot token scope for slash commands, then install the app.
3. Create a slash command named `/schedule`.
4. If using HTTP mode, point the command request URL to your deployed app.
   If using Socket Mode, set `SLACK_APP_TOKEN` and enable Socket Mode.
5. Invite the bot to the `#schedule` channel and run `/schedule help`.

## Scripts

```bash
npm run dev        # start with tsx watch
npm run build      # compile TypeScript
npm run typecheck  # type-check without emitting
npm test           # run unit tests
```

"""Discord bot: scheduled briefings, recaps, and meeting reminders."""
import asyncio
import logging
from datetime import datetime

import discord
from discord.ext import commands, tasks

from .briefing import evening_recap, morning_briefing, reminder_message
from .conflicts import find_conflicts
from .config import Config
from .dedupe import ReminderTracker
from .integrations.sources import DemoCalendar, DemoDeadlines, DemoMail
from .integrations.weather import get_weather
from .reminders import due_reminders

log = logging.getLogger("stride")


class StrideCog(commands.Cog):
    def __init__(self, bot: commands.Bot, cfg: Config):
        self.bot = bot
        self.cfg = cfg
        self.calendar = DemoCalendar()
        self.mail = DemoMail()
        self.deadlines = DemoDeadlines()
        self.tracker = ReminderTracker("data/sent_reminders.json")

        # Time-of-day loops are built here because the times come from config.
        self.briefing_task = tasks.loop(time=cfg.briefing_time)(self._scheduled_briefing)
        self.recap_task = tasks.loop(time=cfg.recap_time)(self._scheduled_recap)
        self.reminder_task = tasks.loop(minutes=5)(self._reminder_check)
        for t in (self.briefing_task, self.recap_task, self.reminder_task):
            t.before_loop(self.bot.wait_until_ready)
            t.start()

    def cog_unload(self):
        for t in (self.briefing_task, self.recap_task, self.reminder_task):
            t.cancel()

    # ---- helpers ----
    def _now(self) -> datetime:
        return datetime.now(self.cfg.timezone)

    async def _channel(self):
        return self.bot.get_channel(self.cfg.channel_id) or await self.bot.fetch_channel(
            self.cfg.channel_id
        )

    async def _build_morning(self) -> str:
        now = self._now()
        # Weather is a blocking HTTP call, so keep it off the event loop.
        weather = await asyncio.to_thread(get_weather, self.cfg.latitude, self.cfg.longitude)
        return morning_briefing(
            now,
            self.calendar.get_events(now),
            self.mail.get_emails(now),
            self.deadlines.get_deadlines(now),
            weather,
        )

    # ---- scheduled jobs ----
    async def _scheduled_briefing(self):
        await (await self._channel()).send(await self._build_morning())

    async def _scheduled_recap(self):
        now = self._now()
        text = evening_recap(
            now,
            self.calendar.get_events(now),
            self.mail.get_emails(now),
            self.deadlines.get_deadlines(now),
        )
        await (await self._channel()).send(text)

    async def _reminder_check(self):
        now = self._now()
        lead = self.cfg.reminder_lead_minutes
        for event in due_reminders(self.calendar.get_events(now), now, self.tracker, lead):
            await (await self._channel()).send(reminder_message(event, now))
            self.tracker.mark_sent(event.id, lead)  # only after a successful send
            log.info("Sent reminder for %s", event.id)

    # ---- commands ----
    @commands.command(name="briefing")
    async def briefing_cmd(self, ctx: commands.Context):
        """Get today's briefing on demand."""
        await ctx.send(await self._build_morning())

    @commands.command(name="conflicts")
    async def conflicts_cmd(self, ctx: commands.Context):
        """List overlapping events."""
        pairs = find_conflicts(self.calendar.get_events(self._now()))
        if not pairs:
            await ctx.send("No scheduling conflicts found. ✅")
            return
        await ctx.send("\n".join(f"⚠️ {a.title} overlaps {b.title}" for a, b in pairs))


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    cfg = Config.from_env()
    intents = discord.Intents.default()
    intents.message_content = True  # needed for !commands; enable it in the Developer Portal
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def setup_hook():
        await bot.add_cog(StrideCog(bot, cfg))

    @bot.event
    async def on_ready():
        log.info("Stride online as %s", bot.user)

    bot.run(cfg.discord_token)


if __name__ == "__main__":
    main()

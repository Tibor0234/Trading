import discord
from discord.ext import commands
import asyncio
from data.log_handler import make_screenshot


class DiscordBot:
    def __init__(self, token, callback):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.dm_messages = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.token = token
        self.user_id = 454292237090816010
        self.callback = callback

        self.bot.add_listener(self.on_raw_reaction_add)

        # {message_id: {"trade": trade, "task": task, "embed": embed, "msg": msg}}
        self.trades = {}

    def run_bot(self):
        self.bot.run(self.token)

    def run_setup_message(self, trade, html_path):
        img_path = make_screenshot(html_path)
        asyncio.run_coroutine_threadsafe(
            self.send_setup_dm(img_path, trade),
            self.bot.loop
        )

    def run_result_message(self, trade, html_path, result):
        img_path = make_screenshot(html_path)
        asyncio.run_coroutine_threadsafe(
            self.send_result_dm(trade, img_path, result),
            self.bot.loop
        )

    async def send_setup_dm(self, img_path, trade):
        timeout = trade.timeframe_obj.timestamp
        user = await self.bot.fetch_user(self.user_id)

        # alap embed (szürke színnel)
        embed = discord.Embed(
            title="📊 New Trade Setup",
            description="Do you approve this trade?",
            color=discord.Color.light_grey()
        )
        file = discord.File(img_path, filename="trade.png")
        embed.set_image(url="attachment://trade.png")

        msg = await user.send(file=file, embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        # hozzárendeljük az üzenet ID-t a trade-hez
        trade.setup_msg_id = msg.id

        async def expire():
            await asyncio.sleep(timeout)
            if msg.id in self.trades:
                self.trades.pop(msg.id, None)
                # embed színe -> narancs (lejárt)
                embed.color = discord.Color.orange()
                embed.description = "Trade expired"
                await msg.edit(embed=embed)
                self.callback(trade, False)

        task = asyncio.create_task(expire())
        self.trades[msg.id] = {
            "trade": trade,
            "task": task,
            "embed": embed,
            "msg": msg
        }

    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.user_id:
            return

        if payload.message_id not in self.trades:
            return

        entry = self.trades.pop(payload.message_id)
        trade, task, embed, msg = entry["trade"], entry["task"], entry["embed"], entry["msg"]
        task.cancel()

        if str(payload.emoji) == "✅":
            embed.color = discord.Color.green()
            embed.description = "Trade approved"
            await msg.edit(embed=embed)
            self.callback(trade, True)
        elif str(payload.emoji) == "❌":
            embed.color = discord.Color.red()
            embed.description = "Trade denied"
            await msg.edit(embed=embed)
            self.callback(trade, False)

    async def send_result_dm(self, trade, img_path, result):
        user = await self.bot.fetch_user(self.user_id)

        # szín választás
        if result == 1:
            color = discord.Color.green()
            desc = "Trade closed with profit"
        else:
            color = discord.Color.red()
            desc = "Trade closed with loss"

        embed = discord.Embed(
            title="📊 Trade Closed",
            description=desc,
            color=color
        )
        file = discord.File(img_path, filename="result.png")
        embed.set_image(url="attachment://result.png")

        # mindig a trade.setup_msg_id alapján keressük vissza
        setup_msg = None
        if hasattr(trade, "setup_msg_id"):
            try:
                setup_msg = await user.fetch_message(trade.setup_msg_id)
            except discord.NotFound:
                setup_msg = None

        if setup_msg:
            await setup_msg.reply(file=file, embed=embed)
            self.trades.pop(trade.setup_msg_id, None)  # takarítás
        else:
            await user.send(file=file, embed=embed)

import discord
from discord.ext import commands
import os
from PIL import Image
import asyncio
from playwright.async_api import async_playwright

class DiscordBot:
    def __init__(self, token, callback):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.dm_messages = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.token = token
        self.user_id = 454292237090816010

        self.bot.add_listener(self.on_raw_reaction_add)
        self.callback = callback

    def run_bot(self):
        self.bot.run(self.token)

    async def make_screenshot(self, html_path):
        img_path = html_path.replace('.html', '.png')

        try:
            async with async_playwright() as p:
                print('async_playwright runs')
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.set_viewport_size({'width': 1200, 'height': 800})

                url = f'file:///{html_path.replace(os.sep, "/")}'
                print("Opening:", url)
                await page.goto(url)

                await page.screenshot(path=img_path, full_page=False)
                print("Saved screenshot:", img_path, os.path.exists(img_path))

                await browser.close()
        except Exception as e:
            print("Playwright error:", e)
            return None

        try:
            img = Image.open(img_path)
            w, h = img.size
            if w > 40 and h > 40:
                img.crop((20, 20, w-20, h-20)).save(img_path)
        except Exception as e:
            print("PIL error:", e)

        return img_path


    async def send_setup_dm(self, html_path, timeout):
        img_path = await self.make_screenshot(html_path)

        user = await self.bot.fetch_user(self.user_id)
        msg = await user.send("📊 Do you approve this trade?", file=discord.File(img_path))
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        self.active = True  # trade aktív

        async def expire():
            await asyncio.sleep(timeout)
            if self.active:
                self.active = False
                self.callback(False)
                await user.send("⌛ Trade expired")

        asyncio.create_task(expire())

    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.user_id or not getattr(self, "active", False):
            return
        user = await self.bot.fetch_user(self.user_id)

        if str(payload.emoji) == "✅":
            await user.send("✅ Trade approved")
            self.callback(True)
        elif str(payload.emoji) == "❌":
            await user.send("❌ Trade denied")
            self.callback(False)

        self.active = False  # trade lezárva

    async def send_trade_result(self, html_path):
        img_path = await self.make_screenshot(html_path)

        user = await self.bot.fetch_user(self.user_id)
        await user.send("📊 A trade has been closed.", file=discord.File(img_path))
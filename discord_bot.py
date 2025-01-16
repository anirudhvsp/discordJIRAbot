import discord
from discord.ext import commands
import os
import asyncio
import redis
import json
from urllib.parse import urlencode

# Load configuration
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
client_id = config["client_id"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


def run_bot(redis_client):
    bot = commands.Bot(command_prefix='!', intents=intents)

    # Process 1: Discord bot commands
    async def send_issues_to_user(ctx, issues_data):
        if not issues_data:
            await ctx.send("No issues found.")
            return

        embed = discord.Embed(title="Your Recent Jira Issues", color=0x0052CC)
        for issue in issues_data:
            status = issue["fields"]["status"]["name"]
            summary = issue["fields"]["summary"]
            embed.add_field(name=f"{issue['key']} - {status}", value=summary, inline=False)
        await ctx.send(embed=embed)

    @bot.command()
    async def myissues(ctx, limit: int = 5):
        """Fetch user's recent Jira issues using OAuth2 token."""
        access_token = redis_client.get(f"access_token:{ctx.author.id}")
        if not access_token:
            await ctx.send("Please authenticate first using !auth")
            return

        # Simulate fetching issues:
        issues_data = [{"key": "JRA-123", "fields": {"status": {"name": "Open"}, "summary": "Issue Summary"}}]

        # Send issues back to user
        await send_issues_to_user(ctx, issues_data)

    @bot.command()
    async def auth(ctx):
        """Generate OAuth2 authorization link and send it to the user"""
        state = os.urandom(16).hex()  # Generate a random state string to prevent CSRF attacks

        # Prepare the parameters for the OAuth2 authorization URL
        auth_params = {
            "audience": "api.atlassian.com",
            "client_id": config["client_id"],
            "scope": "read:jira-user",  # You can specify more scopes depending on the required permissions
            "redirect_uri": config["redirect_uri"],
            "state": state,
            "response_type": "code",
            "prompt": "consent",
        }

        # Build the authorization URL using urlencode to encode the query parameters
        auth_url = f"{config['oauth2_base_url']}/authorize?" + urlencode(auth_params)

        # Store the state in Redis with user ID
        redis_client.set(f"state:{state}", str(ctx.author.id))

        await ctx.send(f"Click the link to authenticate with Jira: {auth_url}")

    # This function is called when the bot is ready
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')

        # Subscribe to the Redis channel for authentication success messages
        pubsub = redis_client.pubsub()
        pubsub.subscribe("auth_channel")

        async def listen_for_auth():
            while True:
                message = pubsub.get_message()
                if message and message['type'] == 'message':
                    user_id = message['data']
                    user = await bot.fetch_user(user_id)
                    if user:
                        await user.send("You have successfully authenticated with Jira!")
                await asyncio.sleep(1)

        # Run the auth listener in the background
        bot.loop.create_task(listen_for_auth())

    # Run the bot
    bot.run(config["discord_token"])

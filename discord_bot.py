import os
import discord
from discord.ext import commands
import urllib3
urllib3.disable_warnings()

from tiktok_shadowban_checker import TikTokShadowBanClient

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
APIFY_TOKEN = os.environ.get("APIFY_TOKEN")

if not DISCORD_TOKEN or not APIFY_TOKEN:
    print("❌ Missing environment variables")
    exit(1)

client = TikTokShadowBanClient(api_token=APIFY_TOKEN)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connected as {bot.user}")
    print(f"📊 Bot ID: {bot.user.id}")
    print("=" * 50)

# ============================================
#  COMMANDS (NO "help" COMMAND - IT'S BUILT-IN)
# ============================================

@bot.command(name="check")
async def check_video(ctx, url: str = None):
    if not url:
        await ctx.send("❌ Please provide a TikTok video URL.\nExample: `!check https://www.tiktok.com/@username/video/123456789`")
        return

    if not url.startswith("http"):
        await ctx.send("❌ Invalid URL. Please send a valid TikTok video URL.")
        return

    async with ctx.typing():
        try:
            result = client.check_one(url)
            
            embed = discord.Embed(
                title="📊 Shadow Ban Report",
                description=f"**Video:** {url[:60]}...",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="🚫 Shadowbanned",
                value=str(result.get('shadowbanned', 'N/A')),
                inline=True
            )
            embed.add_field(
                name="🏥 Health Score",
                value=f"{result.get('videoHealthScore', 'N/A')}/100",
                inline=True
            )
            embed.add_field(
                name="📈 Engagement Rate",
                value=f"{result.get('engagementRate', 'N/A')}%",
                inline=True
            )
            embed.add_field(
                name="🔥 Viral Potential",
                value=f"{result.get('viralPotentialScore', 'N/A')}/100",
                inline=True
            )
            
            author = result.get('author', {})
            embed.add_field(
                name="👤 Author",
                value=f"@{author.get('uniqueId', 'N/A')}",
                inline=True
            )
            embed.add_field(
                name="📊 Followers",
                value=author.get('followerCount', 'N/A'),
                inline=True
            )
            
            stats = result.get('stats', {})
            embed.add_field(
                name="📊 Stats",
                value=(
                    f"Views: {stats.get('views', 'N/A')}\n"
                    f"Likes: {stats.get('likes', 'N/A')}\n"
                    f"Comments: {stats.get('comments', 'N/A')}"
                ),
                inline=False
            )
            
            if result.get("banReasonHints"):
                reasons = "\n".join(f"• {hint}" for hint in result["banReasonHints"][:3])
                embed.add_field(
                    name="⚠️ Ban Reasons",
                    value=reasons,
                    inline=False
                )
            
            if result.get("recommendations"):
                recs = "\n".join(f"• {rec}" for rec in result["recommendations"][:2])
                embed.add_field(
                    name="💡 Recommendations",
                    value=recs,
                    inline=False
                )
            
            embed.set_footer(text=f"Powered by Apify • $0.01/video")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ **Error:** {str(e)[:200]}")

@bot.command(name="batch")
async def batch_videos(ctx, *urls):
    if not urls:
        await ctx.send("❌ Please provide at least one TikTok URL.\nExample: `!batch url1 url2 url3`")
        return

    if len(urls) > 10:
        await ctx.send("⚠️ Maximum 10 URLs per batch.")
        return

    await ctx.send(f"⏳ Checking {len(urls)} videos...")

    try:
        videos, summary = client.check_urls(list(urls))
        
        embed = discord.Embed(
            title="📊 Batch Summary",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📌 Total Checked",
            value=summary.get('totalChecked', 0),
            inline=True
        )
        embed.add_field(
            name="🚫 Shadowbanned",
            value=f"{summary.get('shadowbannedCount', 0)} ({summary.get('shadowbannedPct', 0)}%)",
            inline=True
        )
        embed.add_field(
            name="🏥 Avg Health",
            value=f"{summary.get('avgHealthScore', 'N/A')}/100",
            inline=True
        )
        embed.add_field(
            name="📈 Avg Engagement",
            value=f"{summary.get('avgEngagementRate', 'N/A')}%",
            inline=True
        )
        embed.add_field(
            name="💡 Verdict",
            value=summary.get('recommendation', 'N/A'),
            inline=False
        )
        
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ **Batch Error:** {str(e)[:150]}")

@bot.command(name="commands")
async def list_commands(ctx):
    embed = discord.Embed(
        title="🤖 TikTok Shadow Ban Checker",
        description="Available commands:",
        color=0x00ff00
    )
    embed.add_field(
        name="📊 Commands",
        value=(
            "`!check <url>` - Check a single video\n"
            "`!batch <url1> <url2> ...` - Check multiple videos\n"
            "`!commands` - Show this message\n"
            "`!help` - Show built-in Discord help"
        ),
        inline=False
    )
    embed.add_field(
        name="💰 Cost",
        value="$0.01 per video (500 free/month)",
        inline=False
    )
    embed.add_field(
        name="📝 Example",
        value="`!check https://www.tiktok.com/@tiktok/video/7480279424202575159`",
        inline=False
    )
    await ctx.send(embed=embed)

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 TIKTOK SHADOW BAN CHECKER - DISCORD BOT")
    print("=" * 50)
    print("📡 Starting bot...")
    bot.run(DISCORD_TOKEN)

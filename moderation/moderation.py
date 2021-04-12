import datetime
import logging

logger = logging.getLogger("Modmail")

import discord
import typing
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


class ModerationPlugin(commands.Cog):
    """
    Moderate ya server using modmail pog
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        print('Moderation by Donny v1.0.1')

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def moderation(self, ctx: commands.Context):
        """
        Settings and stuff
        """
        await ctx.send_help(ctx.command)
        return

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Set the log channel for moderation actions.
        """

        await self.db.find_one_and_update(
            {"_id": "config"}, {"$set": {"channel": channel.id}}, upsert=True
        )

        await ctx.send("Done!")
        return

    def isModmailThread(self, topic):
        if topic is None:
            print('Not modmail thread')
            return False

        components = topic.split(':')

        if components[1] is None:
            print('Not modmail thread')
            return False

        userID = components[1].strip()

        if len(userID) < 17 or len(userID) > 18:
            print('Not modmail thread')
            return False
        else:
            print('Is modmail thread')
            return True

    def getUserId(self, topic):
        if topic is None:
            print('No userID found')
            return None

        components = topic.split(':')

        if components[1] is None:
            print('No userID found')
            return None

        userID = components[1].strip()

        if len(userID) < 17 or len(userID) > 18:
            print('No userID found')
            return None
        else:
            print('UserID found')
            print('UserID:', userID)
            return userID

    @commands.command(aliases=["banhammer"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def ban(
        self,
        ctx: commands.Context,
        member: typing.Union[typing.Optional[discord.User], typing.Optional[str]] = None,
        days: typing.Optional[int] = 0,
        *,
        reason: str = None,
    ):
        """Ban one or more users.
        Usage:
        {prefix}ban @member 10 Advertising their own products
        {prefix}ban Spamming (inside modmail thread)
        """

        config = await self.db.find_one({"_id": "config"})

        if config is None:
            return await ctx.send("There's no configured log channel.")
        else:
            channel = ctx.guild.get_channel(int(config["channel"]))

        if channel is None:
            await ctx.send("There is no configured log channel.")
            return

        print('Member Outer:', member)
        if member is None and self.isModmailThread(ctx.channel.topic):
            userID = self.getUserId(ctx.channel.topic)

            try:
                member = self.bot.get_user(int(userID))
                print('Member:', member)
					
					highestRoleBanee = member.roles[-1]
					highestRoleBanner = ctx.author.roles[-1]
					
					if highestRoleBanee >= highestRoleBanner:
						await ctx.send(f"You cannot ban someone who has the same or higher role than you!")
					else:
						await ctx.guild.ban(member, delete_message_days=days, reason=f"{reason if reason else None}")

                		embed = discord.Embed(
                    	color=discord.Color.red(),
                    	title=f"{member} was banned!",
                    	timestamp=datetime.datetime.utcnow(),
                		)

                		embed.add_field(
                    	name="Moderator",
                    	value=f"{ctx.author}",
                    	inline=False,
                		)

                		if reason:
                    	embed.add_field(name="Reason", value=reason, inline=False)

                		await ctx.send(f"🚫 | {member} is banned!")
                		await channel.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("I don't have the proper permissions to ban people.")

            except Exception as e:
                await ctx.send(
                    "An unexpected error occurred, please check the logs for more details."
                )
                logger.error(e)
                return
        elif member != None and type(member) is str:
            try:
                member = self.bot.get_user(int(member))
                print('Member:', member)

					highestRoleBanee = member.roles[-1]
					highestRoleBanner = ctx.author.roles[-1]
					
					if highestRoleBanee >= highestRoleBanner:
						await ctx.send(f"You cannot ban someone who has the same or higher role than you!")
					else:
                		await ctx.guild.ban(member, delete_message_days=days, reason=f"{reason if reason else None}")

                		embed = discord.Embed(
                    	color=discord.Color.red(),
                    	title=f"{member} was banned!",
                    	timestamp=datetime.datetime.utcnow(),
                		)

                		embed.add_field(
                    	name="Moderator",
                    	value=f"{ctx.author}",
                    	inline=False,
                		)

						if reason:
							embed.add_field(name="Reason", value=reason, inline=False)

                		await ctx.send(f"🚫 | {member} is banned!")
                		await channel.send(embed=embed)
            except discord.Forbidden:
                		await ctx.send("I don't have the proper permissions to ban people.")

            except Exception as e:
                await ctx.send(
                    "An unexpected error occurred, please check the logs for more details."
                )
                logger.error(e)
                return
        elif member != None and type(member) is discord.User:
            try:
                await ctx.guild.ban(member, delete_message_days=days, reason=f"{reason if reason else None}")

                embed = discord.Embed(
                    color=discord.Color.red(),
                    title=f"{member} was banned!",
                    timestamp=datetime.datetime.utcnow(),
                )

                embed.add_field(
                    name="Moderator",
                    value=f"{ctx.author}",
                    inline=False,
                )

                if reason:
                    embed.add_field(name="Reason", value=reason, inline=False)

                await ctx.send(f"🚫 | {member} is banned!")
                await channel.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("I don't have the proper permissions to ban people.")

            except Exception as e:
                await ctx.send(
                    "An unexpected error occurred, please check the logs for more details."
                )
                logger.error(e)
                return
        else:
            await ctx.send("This is not a modmail thread and you have not mentioned anyone.")

    @commands.command(aliases=["getout"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def kick(
        self, ctx, member: typing.Union[typing.Optional[discord.Member], typing.Optional[int]], *, reason: str = None
    ):
        """Kick one or more users.
        Usage:
        {prefix}kick @member Being rude
        {prefix}kick Advertising (inside a modmail thread)
        """

        config = await self.db.find_one({"_id": "config"})

        if config is None:
            return await ctx.send("There's no configured log channel.")
        else:
            channel = ctx.guild.get_channel(int(config["channel"]))

        if channel is None:
            await ctx.send("There is no configured log channel.")
            return

        print('Member Outer:', member)
        if member is None and self.isModmailThread(ctx.channel.topic):
            userID = self.getUserId(ctx.channel.topic)

            try:
                member = self.bot.get_user(int(userID))
                print('Member modmail:', member)
					
					highestRoleBanee = member.roles[-1]
					highestRoleBanner = ctx.author.roles[-1]
					
					if highestRoleBanee >= highestRoleBanner:
						await ctx.send(f"You cannot kick someone who has the same or higher role than you!")
					else:
                		await ctx.guild.kick(member, reason=f"{reason if reason else None}")

                		embed = discord.Embed(
                    	color=discord.Color.red(),
                    	title=f"{member} was kicked!",
                    	timestamp=datetime.datetime.utcnow(),
                		)

                		embed.add_field(
                    	name="Moderator",
                    	value=f"{ctx.author}",
                    	inline=False,
                		)

                		if reason is not None:
                    	embed.add_field(name="Reason", value=reason, inline=False)

                		await ctx.send(f"🦶 | {member} is kicked!")
                		await channel.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("I don't have the proper permissions to kick people.")

            except Exception as e:
                await ctx.send(
                    "An unexpected error occurred, please check the Heroku logs for more details."
                )
                logger.error(e)
                return
        elif member != None and type(member) is str:
            try:
                member = self.bot.get_user(int(userID))
                print('Member not modmail:', member)
					
					highestRoleBanee = member.roles[-1]
					highestRoleBanner = ctx.author.roles[-1]
					
					if highestRoleBanee >= highestRoleBanner:
						await ctx.send(f"You cannot kick someone who has the same or higher role than you!")
					else:
                		await ctx.guild.kick(member, reason=f"{reason if reason else None}")
                		embed = discord.Embed(
                    	color=discord.Color.red(),
                    	title=f"{member} was kicked!",
                    	timestamp=datetime.datetime.utcnow(),
                		)

                		embed.add_field(
                    	name="Moderator",
                    	value=f"{ctx.author}",
                    	inline=False,
                		)

                		if reason is not None:
                    	embed.add_field(name="Reason", value=reason, inline=False)

                		await ctx.send(f"🦶 | {member} is kicked!")
                		await channel.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("I don't have the proper permissions to kick people.")

            except Exception as e:
                await ctx.send(
                    "An unexpected error occurred, please check the Heroku logs for more details."
                )
                logger.error(e)
                return
        elif member != None and type(member) is discord.Member:
            try:
					highestRoleBanee = member.roles[-1]
					highestRoleBanner = ctx.author.roles[-1]
					
					if highestRoleBanee >= highestRoleBanner:
						await ctx.send(f"You cannot kick someone who has the same or higher role than you!")
					else:
                		await member.kick(reason=f"{reason if reason else None}")
                		embed = discord.Embed(
                    	color=discord.Color.red(),
                    	title=f"{member} was kicked!",
                    	timestamp=datetime.datetime.utcnow(),
                		)

                		embed.add_field(
                    	name="Moderator",
                    	value=f"{ctx.author}",
                    	inline=False,
                		)

                		if reason is not None:
                    	embed.add_field(name="Reason", value=reason, inline=False)

                		await ctx.send(f"🦶 | {member} is kicked!")
                		await channel.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("I don't have the proper permissions to kick people.")

            except Exception as e:
                await ctx.send(
                    "An unexpected error occurred, please check the Heroku logs for more details."
                )
                logger.error(e)
                return
        else:
            await ctx.send("This is not a modmail thread and you have not mentioned anyone.")

def setup(bot):
    bot.add_cog(ModerationPlugin(bot))
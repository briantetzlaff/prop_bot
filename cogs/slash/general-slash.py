""""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.1
"""

import json
import os
import platform
import random
import sys

import aiohttp
import disnake
from disnake import ApplicationCommandInteraction, Option, OptionType
from disnake.ext import commands

from helpers import checks, constants

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


class General(commands.Cog, name="general-slash"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="botinfo",
        description="Get some useful (or not) information about the bot.",
    )
    @checks.not_blacklisted()
    async def botinfo(self, interaction: ApplicationCommandInteraction) -> None:
        """
        Get some useful (or not) information about the bot.
        :param interaction: The application command interaction.
        """
        embed = disnake.Embed(
            description="Used [Krypton's](https://krypt0n.co.uk) template",
            color=0x9C84EF
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owner:",
            value="Dexter#0475",
            inline=True
        )
        embed.add_field(
            name="Python Version:",
            value=f"{platform.python_version()}",
            inline=True
        )
        embed.add_field(
            name="Prefix:",
            value=f"/ (Slash Commands) or {config['prefix']} for normal commands",
            inline=False
        )
        embed.set_footer(
            text=f"Requested by {interaction.author}"
        )
        await interaction.send(embed=embed)

    @commands.slash_command(
        name="serverinfo",
        description="Get some useful (or not) information about the server.",
    )
    @checks.not_blacklisted()
    async def serverinfo(self, interaction: ApplicationCommandInteraction) -> None:
        """
        Get some useful (or not) information about the server.
        :param interaction: The application command interaction.
        """
        roles = [role.name for role in interaction.guild.roles]
        if len(roles) > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)

        embed = disnake.Embed(
            title="**Server Name:**",
            description=f"{interaction.guild}",
            color=0x9C84EF
        )
        embed.set_thumbnail(
            url=interaction.guild.icon.url
        )
        embed.add_field(
            name="Server ID",
            value=interaction.guild.id
        )
        embed.add_field(
            name="Member Count",
            value=interaction.guild.member_count
        )
        embed.add_field(
            name="Text/Voice Channels",
            value=f"{len(interaction.guild.channels)}"
        )
        embed.add_field(
            name=f"Roles ({len(interaction.guild.roles)})",
            value=roles
        )
        embed.set_footer(
            text=f"Created at: {interaction.guild.created_at}"
        )
        await interaction.send(embed=embed)

    @commands.slash_command(
        name="invite",
        description="Get the invite link of the bot to be able to invite it.",
    )
    @checks.not_blacklisted()
    async def invite(self, interaction: ApplicationCommandInteraction) -> None:
        """
        Get the invite link of the bot to be able to invite it.
        :param interaction: The application command interaction.
        """
        embed = disnake.Embed(
            description=f"Invite me by clicking [here](https://discordapp.com/oauth2/authorize?&client_id={config['application_id']}&scope=bot+applications.commands&permissions={config['permissions']}).",
            color=0xD75BF4
        )
        try:
            # To know what permissions to give to your bot, please see here: https://discordapi.com/permissions.html and remember to not give Administrator permissions.
            await interaction.author.send(embed=embed)
            await interaction.send("I sent you a private message!")
        except disnake.Forbidden:
            await interaction.send(embed=embed)

    @commands.slash_command(
        name="server",
        description="Get the invite link of the discord server of the bot for some support.",
    )
    @checks.not_blacklisted()
    async def server(self, interaction: ApplicationCommandInteraction) -> None:
        """
        Get the invite link of the discord server of the bot for some support.
        :param interaction: The application command interaction.
        """
        embed = disnake.Embed(
            description=f"Join the support server for the bot by clicking [here](https://discord.gg/mTBrXyWxAF).",
            color=0xD75BF4
        )
        try:
            await interaction.author.send(embed=embed)
            await interaction.send("I sent you a private message!")
        except disnake.Forbidden:
            await interaction.send(embed=embed)

    @commands.slash_command(
        name="8ball",
        description="Ask any question to the bot.",
        options=[
            Option(
                name="question",
                description="The question you want to ask.",
                type=OptionType.string,
                required=True
            )
        ],
    )
    @checks.not_blacklisted()
    async def eight_ball(self, interaction: ApplicationCommandInteraction, question: str) -> None:
        """
        Ask any question to the bot.
        :param interaction: The application command interaction.
        :param question: The question that should be asked by the user.
        """
        answers = ["It is certain.", "It is decidedly so.", "You may rely on it.", "Without a doubt.",
                   "Yes - definitely.", "As I see, yes.", "Most likely.", "Outlook good.", "Yes.",
                   "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
                   "Cannot predict now.", "Concentrate and ask again later.", "Don't count on it.", "My reply is no.",
                   "My sources say no.", "Outlook not so good.", "Very doubtful."]
        embed = disnake.Embed(
            title="**My Answer:**",
            description=f"{random.choice(answers)}",
            color=0x9C84EF
        )
        embed.set_footer(
            text=f"The question was: {question}"
        )
        await interaction.send(embed=embed)

    @commands.slash_command(
        name="props",
        description="Get player props above/below specified odds.",
        options=[
            Option(
                name="sport",
                description="The sport you want to look at.",
                type=OptionType.string,
                required=True
            ),
            Option(
                name="odds",
                description="The odds breakpoint you're looking at",
                type=OptionType.integer,
                required=True
            )
        ],
    )
    @checks.not_blacklisted()
    async def prop_grab(self, interaction: ApplicationCommandInteraction, sport: str, odds: int) -> None:
        """
        Get player props above or under specified odds in specified sport
        """
        sport_value = constants.SPORTS.get(sport.upper())
        for cat, value in constants.NBA.items():
            url = (f"https://sportsbook.draftkings.com//sites/US-SB/api/"\
                    f"v4/eventgroups/88670846/categories/{sport_value}/subcategories/{value}?format=json")
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as request:
                    data = await request.json(content_type="application/json")
                    embed = disnake.Embed(title="Test",
                                          description=f"{data}")
            if data.get('errorStatus').get('code') == 'BET120':
                embed = disnake.Embed(
                    title="Error",
                    description="No player props found :("
                )
                break

        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))

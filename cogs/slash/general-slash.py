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
import pandas as pd
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


def reduce_props(spread: int, subcat: str, df: dict):
    save = pd.DataFrame(columns=['name', 'bet_label', 'line', 'odds'])
    cats = df.get("eventGroup").get("offerCategories")

    # offerCategory == 583 is player props #
    props = next(i for i in cats if i['offerCategoryId'] == 583).get('offerSubcategoryDescriptors')
    for i in props:
        if i.get("subcategoryId") == constants.NBA.get(subcat):
            for offer_list in i.get("offerSubcategory").get("offers"):
                for offer in offer_list:
                    for ou in offer.get("outcomes"):
                        if (int(ou.get("oddsAmerican"))) <= spread:
                            new_row = pd.DataFrame({'name': [offer.get('label')], 'bet_label': [ou.get('label')],
                                                    'line': [ou.get('line')], 'odds': [ou.get('oddsAmerican')]})
                            save = pd.concat([save, new_row], axis=0, ignore_index=True)
    return save


class General(commands.Cog, name="general-slash"):
    def __init__(self, bot):
        self.bot = bot

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
        Get player props under specified odds in specified sport
        """
        sport_value = constants.SPORTS.get(sport.upper())
        if sport.upper() == 'NBA':
            cats = constants.NBA.items()
        else:
            embed = disnake.Embed(
                title="Error",
                description="sport not supported yet"
            )
            await interaction.send(embed=embed)
            return
        for cat, value in cats:
            url = (f"https://sportsbook.draftkings.com//sites/US-SB/api/" \
                   f"v4/eventgroups/88670846/categories/{sport_value}/subcategories/{value}?format=json")
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as request:
                    data = await request.json(content_type="application/json")
                if 'errorStatus' in data.keys():
                    if data.get('errorStatus').get('code') == 'BET120':
                        embed = disnake.Embed(
                            title="Error",
                            description="No player props found :("
                        )
                    else:
                        embed = disnake.Embed(
                            title="Error",
                            description="Unknown error, blame Brian"
                        )
                props = reduce_props(odds, cat, data)
                embed = disnake.Embed(
                    title=cat,
                    description=props.to_string(index=False, header=False)
                )
                await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))

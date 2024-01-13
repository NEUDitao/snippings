#!/usr/bin/env python3

from dataclasses import dataclass

import json

from googleapiclient.errors import HttpError
import discord
import gspread

from typing import List, Optional, Tuple

env = json.load(open('env.json'))

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SAMPLE_SPREADSHEET_ID = env['spreadsheet_id']
SAMPLE_RANGE_NAME = 'B7:U'

names_to_discord_usernames = env["names_to_discord_usernames"]


@dataclass
class Winner:
    faction_index: int
    name: str

index_to_faction = ['cats',
                    'birds',
                    'WA',
                    'vagabond',
                    'lizards',
                    'riverfolk',
                    'moles',
                    'crows',
                    'keepers',
                    'rats']

def find_winners(row) -> List[Winner]:
    """
    Goes through the Google Sheet, and finds who scored 30 or won through dominance
    """
    winners = []

    for index, item in enumerate(row):
        if '30' in item or 'WDOM' in item:
            winners.append(Winner(index, item[1]))

    return winners


def format_winner(winner: Winner) -> Optional[Tuple[str, str]]:
    faction = index_to_faction[winner.faction_index]
    discord_username = names_to_discord_usernames.get(winner.name.lower())
    if discord_username is None:
        return None
    return (faction, discord_username)


def get_sheets_data():
    """Gets the basic root data from the spreadsheet
    """
    gc = gspread.service_account(filename='new_credentials.json')

    try:
        sheet = gc.open_by_key(SAMPLE_SPREADSHEET_ID).get_worksheet(0)
        result = sheet.get(SAMPLE_RANGE_NAME)
    except HttpError as err:
        print(err)
    return result


def get_last_winners():
    """
    Gets the last player(s) who won a Root game
    (In the case of a coalition, there can indeed be multiple winners)
    """
    values = get_sheets_data()

    result_list = []
    for value in values:
        result = [(value[i], value[i + 1]) for i in range(0, len(value), 2)]
        result_list.append(result)

    last_game = result_list[-1]
    winners = find_winners(last_game)
    winners = [format_winner(winner) for winner in winners if winner is not None]
    winners = filter(lambda x: x is not None, winners)
    return winners

def lambda_handler(event, context):
    ### DISCORD STUFF
    # Initialize the bot
    bot = discord.Client(intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print(f'[LIGMA] Logged in as {bot.user.name}')

        print('[LIGMA] getting last winners...')
        last_winners = [winners[1] for winners in get_last_winners()]
        print('[LIGMA] got last winners!')
    
        root_champion_role = env.champion_role
        members = bot.get_all_members()
        for member in members:
            champion_role = discord.utils.get(member.guild.roles, id=root_champion_role)
            if member.name in last_winners:
                await member.add_roles(champion_role)
            elif champion_role:
                await member.remove_roles(champion_role)

        print('exiting!')
        exit()
        

    # Run the bot with your token
    bot.run(env['bot_token'])
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully designated a Root Winner! Probably!')
    }

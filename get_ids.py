"""
Steam script
"""
import logging
import time
import argparse
import configparser
import json
import requests
import re
import unicodedata
import pandas as pd
from pathlib import Path

logger = logging.getLogger()
temps_debut = time.time()


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


def main():
    args = parse_args()
    type = args.type
    user_id = args.user_id
    if not type:
        logger.error("-t/--type argument required. Exiting.")
        exit()
    elif type not in ["all", "owned", "wishlist", "both"]:
        logger.error(f"Type {type} not supported. Exiting.")
        exit()

    logger.debug("Reading config file")
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
    except Exception as e:
        logger.error("No config file found. Be sure you have a config.ini file.")
        exit()
    try:
        api_key = config['steam']['api_key']
    except Exception as e:
        logger.error("No api_key found. Check your config file.")
        exit()

    logger.debug("Reading user_id")
    if user_id:
        user_id = user_id
    else:
        try:
            user_id = config['steam']['user_id']
        except Exception as e:
            logger.error("No user specified. Specify a user_id directive in your config file or use the -u/--user_id flag")
            exit()

    Path("Exports").mkdir(parents=True, exist_ok=True)

    if type == 'all':
        logger.debug("Type : all")
        url = f"http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key={api_key}&format=json"
        json_dict = requests.get(url).json()
        logger.debug("Writing CSV file")
        with open('Exports/ids_all_games.csv', 'w') as f:
            f.write("appid\tName")
            for game in json_dict['applist']['apps']:
                f.write(f"{game['appid']}\t{game['name']}\n")
    elif type == 'owned':
        logger.debug("Type : owned")
        url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={user_id}&format=json"
        json_dict = requests.get(url).json()
        dict_games = []
        for game in json_dict['response']['games']:
            dict_game = {}
            dict_game['appid'] = game['appid']
            dict_game['playtime_forever'] = game['playtime_forever']
            try:
                dict_game['playtime_2weeks'] = game['playtime_2weeks']
            except Exception as e:
                dict_game['playtime_2weeks'] = '0'
            dict_games.append(dict_game)

        df = pd.DataFrame(dict_games)
        df.to_csv(f"Exports/ids_owned_games_{user_id}.csv", sep='\t')
    elif type == 'wishlist':
        logger.debug("Type : wishlist")
        url = f"https://store.steampowered.com/wishlist/profiles/{user_id}/wishlistdata/?p=0"
        json_dict = requests.get(url).json()

        dict_games = []
        for game_id in json_dict:
            dict_game = {}
            dict_game['appid'] = game_id
            game_info = json_dict[game_id]
            dict_game['name'] = slugify(game_info['name'].strip())
            dict_game['review_score'] = game_info['review_score']
            dict_game['review_desc'] = game_info['review_desc']
            dict_game['reviews_total'] = game_info['reviews_total']
            dict_game['reviews_percent'] = game_info['reviews_percent']
            dict_game['release_date'] = game_info['release_date']
            dict_game['release_string'] = game_info['release_string']
            dict_game['review_css'] = game_info['review_css']
            dict_game['priority'] = game_info['priority']
            dict_game['tags'] = game_info['tags']
            try:
                dict_game['win'] = game_info['win']
            except Exception as e:
                dict_game['win'] = '0'
            try:
                dict_game['mac'] = game_info['mac']
            except Exception as e:
                dict_game['mac'] = '0'
            try:
                dict_game['linux'] = game_info['linux']
            except Exception as e:
                dict_game['linux'] = '0'
            dict_games.append(dict_game)

        df = pd.DataFrame(dict_games)
        df.to_csv(f"Exports/wishlist_{user_id}.csv", sep='\t')
    elif type == 'both':
        logger.debug("Type : both")
        url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={user_id}&format=json"
        json_dict = requests.get(url).json()
        dict_games = []
        for game in json_dict['response']['games']:
            dict_game = {}
            dict_game['appid'] = game['appid']
            dict_games.append(dict_game)

        url = f"https://store.steampowered.com/wishlist/profiles/{user_id}/wishlistdata/?p=0"
        json_dict = requests.get(url).json()

        for game_id in json_dict:
            dict_game = {}
            dict_game['appid'] = game_id
            dict_games.append(dict_game)

        df = pd.DataFrame(dict_games)
        df.to_csv(f"Exports/both_{user_id}.csv", sep='\t')

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Steam script')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-t', '--type', help="Type of ids to export (all, owned, wishlist or both (owned and wishlist))", type=str)
    parser.add_argument('-u', '--user_id', help="User id to extract the games info from (steamID64)", type=str)
    parser.set_defaults(boolean_flag=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()

"""
Steam script
"""
import logging
import time
import argparse
import configparser
import json
import requests
import pandas as pd
from pathlib import Path

logger = logging.getLogger()
temps_debut = time.time()


def main():
    args = parse_args()

    logger.debug("Reading config file")
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config['steam']['api_key']

    user_id = '76561198071051035'
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={user_id}&format=json"

    json_dict = requests.get(url).json()

    Path("Exports").mkdir(parents=True, exist_ok=True)

    with open(f'Exports/owned_games_{user_id}', 'w') as f:
        json.dump(json_dict, f)

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
    df.to_csv(f"Exports/owned_games_{user_id}.csv", sep='\t')

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Steam script')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.set_defaults(boolean_flag=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()

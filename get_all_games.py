"""
Steam script
"""
import logging
import time
import argparse
import configparser
import json
import requests
from pathlib import Path

logger = logging.getLogger()
temps_debut = time.time()


def main():
    args = parse_args()

    logger.debug("Reading config file")
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config['steam']['api_key']
    url_all_games = f"http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key={api_key}&format=json"

    logger.debug("Downloading list of all games")
    json_dict = requests.get(url_all_games).json()

    Path("Exports").mkdir(parents=True, exist_ok=True)

    logger.debug("Writing JSON file")
    with open('Exports/steam_all_games.json', 'w') as f:
        json.dump(json_dict, f)

    logger.debug("Writing CSV file")
    with open('Expports/steam_all_games.csv', 'w') as f:
        f.write("appid\tName")
        for game in json_dict['applist']['apps']:
            f.write(f"{game['appid']}\t{game['name']}\n")

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

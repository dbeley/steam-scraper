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
import html
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
    url = f"https://store.steampowered.com/wishlist/profiles/{user_id}/wishlistdata/?p=0"

    json_dict = requests.get(url).json()

    Path("Exports").mkdir(parents=True, exist_ok=True)

    with open(f'Exports/wishlist_{user_id}', 'w') as f:
        json.dump(json_dict, f)

    dict_games = []
    for game_id in json_dict:
        dict_game = {}
        dict_game['appid'] = game_id
        game_info = json_dict[game_id]
        dict_game['name'] = html.unescape(game_info['name'].strip())
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

        # try:
        #     url_info_game = f"http://store.steampowered.com/api/appdetails?appids={game_id}"
        #     info_dict = requests.get(url_info_game).json()
        #     info_dict = info_dict[str(game_id)]['data']

        #     # dict_game['name2'] = html.unescape(info_dict['name'].strip())
        #     dict_game['type2'] = info_dict['type']
        #     dict_game['required_age2'] = info_dict['required_age']
        #     dict_game['is_free2'] = info_dict['is_free']
        #     dict_game['developers2'] = info_dict['developers']
        #     dict_game['publishers2'] = info_dict['publishers']
        #     # dict_game['windows2'] = info_dict['platforms']['windows']
        #     # dict_game['linux2'] = info_dict['platforms']['linux']
        #     # dict_game['mac2'] = info_dict['platforms']['mac']
        #     dict_game['genres2'] = info_dict['genres']
        #     dict_game['release_date2'] = info_dict['release_date']
        #     logger.debug(f"Game {dict_game['name2']} - ID {game_id} : {url_info_game}")
        # except Exception as e:
        #     logger.error(e)
        #     logger.debug(f"ID {game_id} : {url_info_game}")


        # try:
        #     url_reviews = f"https://store.steampowered.com/appreviews/{game_id}?json=1&language=all"
        #     reviews_dict = requests.get(url_reviews).json()
        #     reviews_dict = reviews_dict['query_summary']

        #     dict_game['num_reviews2'] = reviews_dict['num_reviews']
        #     dict_game['review_score2'] = reviews_dict['review_score']
        #     dict_game['review_score_desc2'] = reviews_dict['review_score_desc']
        #     dict_game['total_positive2'] = reviews_dict['total_positive']
        #     dict_game['total_negative2'] = reviews_dict['total_negative']
        #     dict_game['total_reviews2'] = reviews_dict['total_reviews']
        # except Exception as e:
        #     logger.error(e)
        #     logger.debug(f"url_reviews : {url_reviews}")



        dict_games.append(dict_game)

    df = pd.DataFrame(dict_games)
    df.to_csv(f"Exports/wishlist_{user_id}.csv", sep='\t')

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

# steam-scraper

## Requirements

- requests
- pandas
- unicode

Needs a config.ini file with a valid steam api key and a steam id (see config_sample.ini for an example).

- Sample config.ini file :

```
[steam]
api_key=api_key_here
user_id=user_id_ere
```

## get_ids.py

Export the ids of a either all games, the owned games or the wishlisted games of a user.

```
python get_ids.py -h
```

```
usage: get_ids.py [-h] [--debug] [-t TYPE] [-u USER_ID]

export ids of a set of games

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -t TYPE, --type TYPE  Type of ids to export (all, owned, wishlist or both
                        (owned and wishlist))
  -u USER_ID, --user_id USER_ID
                        User id to extract the games info from (steamID64).
                        Default : user in config.ini
```

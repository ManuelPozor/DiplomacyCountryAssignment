import json
from pathlib import Path


class PlayerData():
    ''' Context manager class for loading and storing the player data in a json file. '''
    def __init__(self, player_file):
        player_file = Path(player_file)
        if not player_file.is_file():
            # create empty priority file
            players = [{
                "id": "",
                "name": "Player" + ind,
                "prio1": "",
                "prio2": "",
                "prio3": "",
                "submitted": False
            } for ind in range(7)]
            with open(self.player_file, "r") as file:
                json.dump(players, file, indent=4, sort_keys=True)
        self.player_file = player_file
        self.players = None

    def __enter__(self):
        ''' Read list of players from json file. '''
        with open(self.player_file, "r") as file:
            self.players = [player for player in json.load(file)]
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        ''' Save list of players in json file. '''
        with open(self.player_file, "w") as file:
            json.dump(self.players, file, indent=4, sort_keys=True)

    def get_players(self):
        return self.players

    def set_players(self, players):
        self.players = players

    def get_players_by_id(self):
        ''' Return dict of players with their ID as key. '''
        players_by_id = {p['id']: p for p in self.players}
        return players_by_id

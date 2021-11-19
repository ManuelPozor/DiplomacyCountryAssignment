from flask import (Flask, Response, flash, get_flashed_messages, redirect,
                   render_template, request, url_for)
from pathlib import Path
import json
import uuid

app = Flask(__name__)
players_file = Path("player_priorities.json")

def get_player_by_id(id):
    with open(players_file, "r") as file:
        players = [player for player in json.load(file)]

    player_data = [p for p in players if p["id"] == id]
    if len(player_data) > 0:
        player_data = player_data[0]
    else:
        return None
    return player_data


@app.route("/")
def home():
    return render_template("country_selection.html")



if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Starts a local webserver.')
    # args = parser.parse_args()

    # create player ids in json
    with open(players_file, "r") as file:
        players = [player for player in json.load(file)]
    for p in players:
        if len(p["id"]) == 0:
            p["id"] = str(uuid.uuid4())
    with open(players_file, "w") as file:
        json.dump(players, file, indent=4, sort_keys=True)

    # app.secret_key = os.urandom(24)
    print("Starting webserver ...")
    app.run()

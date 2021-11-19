from flask import (Flask, Response, flash, get_flashed_messages, redirect,
                   render_template, request, url_for)
from pathlib import Path
import json
import uuid

app = Flask(__name__)
players_file = Path("player_priorities.json")

unique_country_tags = ["GB", "FR", "GE", "IT", "AH", "RU", "OE"]
country_names = [
    "Great Britain", "France", "German Empire", "Italy", "Austria-Hungary",
    "Russia", "Ottoman Empire"
]


def get_player_by_id(id):
    with open(players_file, "r") as file:
        players = [player for player in json.load(file)]

    player_data = [p for p in players if p["id"] == id]
    if len(player_data) > 0:
        player_data = player_data[0]
    else:
        return None
    return player_data


@app.route('/result/<id>')
def result(id):
    return 'welcome %s' % id


@app.route("/<id>")
def start(id):
    # check if player id correct
    player = get_player_by_id(id)
    if player is None:
        return 'ERROR: Unknown player'
    # load priorities
    priorities = [player["prio1"], player["prio2"], player["prio3"]]
    already_submitted = player["submitted"]
    # TODO if assignment over redirect straight to result
    return render_template("country_selection.html",
                           id=id,
                           tags=unique_country_tags,
                           country_names=country_names,
                           priorities=priorities,
                           submitted=already_submitted)


@app.route("/")
def home():
    return "Please use your unique access link."


@app.route('/search', methods=['GET'])
def priorities_submitted():
    prio1 = request.args.get('prio1')
    prio2 = request.args.get('prio2')
    prio3 = request.args.get('prio3')
    id = request.args.get('id')

    with open(players_file, "r") as file:
        players = [player for player in json.load(file)]
    # set status to submitted
    for p in players:
        if p["id"] == id:
            p["submitted"] = True
            p["prio1"] = prio1
            p["prio2"] = prio2
            p["prio3"] = prio3
    # save player in json
    with open(players_file, "w") as file:
        json.dump(players, file, indent=4, sort_keys=True)

    # check if all players have submitted
    for p in players:
        if not p["submitted"]:
            # TODO throws error when submitting again
            return redirect(url_for('start', id=id))

    # TODO assignment
    return redirect(url_for('result'), id=id)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Starts a local webserver.')
    # args = parser.parse_args()

    # TODO arg to generate new ids

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

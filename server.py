from priority_assignment import assign_countries_by_priority

from flask import (Flask, redirect, render_template, request, url_for)
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


def get_players():
    with open(players_file, "r") as file:
        players = [player for player in json.load(file)]
    return players


def get_player_by_id(id):
    players = get_players()

    player_data = [p for p in players if p["id"] == id]
    if len(player_data) > 0:
        player_data = player_data[0]
    else:
        return None
    return player_data


@app.route('/result/<id>')
def result(id):
    player_name = get_player_by_id(id)["name"]
    # check if assignment really over, i.e. all players submitted
    all_submited = all(p["submitted"] for p in get_players())
    if not all_submited:
        return redirect(url_for('country_selection', id=id))
    with open("country_distribution.txt", "r") as file:
        for line in file.readlines():
            # remove player number, then separate name from tag
            player_country = line.split(":")[-1]
            p_name, country_tag = player_country.split()
            country_ind = unique_country_tags.index(country_tag)
            if p_name == player_name:
                return render_template("result.html",
                                       player_name=player_name,
                                       country=country_names[country_ind])
    return 'ERROR: Unknown player in results'


@app.route("/<id>")
def country_selection(id):
    # check if player id correct
    player = get_player_by_id(id)
    if player is None:
        return 'ERROR: Unknown player in country selection'
    # load priorities
    priorities = [player["prio1"], player["prio2"], player["prio3"]]
    already_submitted = player["submitted"]

    if already_submitted:
        # check if assignment already over, i.e. all players submitted
        all_submited = all(p["submitted"] for p in get_players())
        if all_submited:
            return redirect(url_for('result', id=id))
    return render_template("country_selection.html",
                           id=id,
                           player_name=player["name"],
                           tags=unique_country_tags,
                           country_names=country_names,
                           priorities=priorities,
                           submitted=already_submitted,
                           zip=zip)


@app.route("/")
def home():
    return "Please use your unique access link."


@app.route('/search', methods=['GET'])
def priorities_submitted():
    prio1 = request.args.get('prio1')
    prio2 = request.args.get('prio2')
    prio3 = request.args.get('prio3')
    id = request.args.get('id')

    # TODO check for duplicate entries, redircet

    players = get_players()
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
            return redirect(url_for('country_selection', id=id))

    # country assignment
    assign_countries_by_priority(players_file)
    print("Countries have been assigned.")
    return redirect(url_for('result', id=id))


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Starts a local webserver.')
    # args = parser.parse_args()

    # TODO arg to generate new ids

    # create player ids in json
    players = get_players()
    for p in players:
        if len(p["id"]) == 0:
            p["id"] = str(uuid.uuid4())
    with open(players_file, "w") as file:
        json.dump(players, file, indent=4, sort_keys=True)

    # app.secret_key = os.urandom(24)
    print("Starting webserver ...")
    app.run()

from priority_assignment import assign_countries_by_priority

from flask import (Flask, redirect, render_template, request, url_for, flash)
import os
from pathlib import Path
import argparse
import json
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)

unique_country_tags = ["GB", "FR", "GE", "IT", "AH", "RU", "OE"]
country_names = [
    "Great Britain", "France", "German Empire", "Italy", "Austria-Hungary",
    "Russia", "Ottoman Empire"
]


def get_players():
    ''' Read list of players from json file. '''
    with open(players_file, "r") as file:
        players = [player for player in json.load(file)]
    return players


def get_players_by_id():
    ''' Return dict of players with their ID as key. '''
    players = get_players()
    players_by_id = {p['id']: p for p in players}
    return players_by_id


@app.route('/result/<id>')
def result(id):
    ''' The result page is shown only once countries have been assigned.
        It tells the players which country has been assigned to them.
    '''
    player_name = get_players_by_id()[id]["name"]
    # check if assignment really over, i.e. all players submitted
    all_submited = all(p["submitted"] for p in get_players())
    if not all_submited:
        return redirect(url_for('country_selection', id=id))

    with open(output_file, "r") as file:
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
    ''' Country selection screen only accesible for each individual player.
        Here, they can submit their priorities.
    '''
    # check if player id correct
    player = get_players_by_id().get(id)
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
    ''' Redirection link that processes the country selection and passes to 
        either the result page or the selection screen.
    '''
    prio1 = request.args.get('prio1')
    prio2 = request.args.get('prio2')
    prio3 = request.args.get('prio3')
    id = request.args.get('id')

    # check for empty or duplicate entries
    priorities = [prio1, prio2, prio3]
    for p in priorities:
        if p == "":
            flash(
                "No country selected, please choose one country for each priority!"
            )
            return redirect(url_for('country_selection', id=id))
        if priorities.count(p) > 1:
            flash(
                "Duplicate entries, please select different countries for each priority!"
            )
            return redirect(url_for('country_selection', id=id))

    players = get_players_by_id()
    # set status to submitted
    players[id]["submitted"] = True
    players[id]["prio1"] = prio1
    players[id]["prio2"] = prio2
    players[id]["prio3"] = prio3
    players = [dict for _, dict in players.items()]

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
    parser = argparse.ArgumentParser(
        description=
        'Starts a local webserver for the diplomacy game country selection.')
    parser.add_argument(
        '--json',
        help='Storage json file for the player data (default: %(default)s)',
        type=str,
        default="player_priorities.json")
    parser.add_argument(
        '--out',
        help='Text file to store the result (default: %(default)s)',
        type=str,
        default="result.txt")
    parser.add_argument('--port',
                        help='Webserver port (default: %(default)s)',
                        type=int,
                        default=5000)
    parser.add_argument('--id-gen',
                        help='Generate new player IDs (default: %(default)s)',
                        action='store_true',
                        default=False)
    parser.add_argument(
        '--reset',
        help=
        'Delete all player selections, make empty country slots instead (default: %(default)s)',
        action='store_true',
        default=False)
    args = parser.parse_args()

    players_file = Path(args.json)
    output_file = Path(args.out)

    # create player ids in json
    players = get_players()
    for p in players:
        if args.reset:
            # reset player choices
            p["prio1"] = ""
            p["prio2"] = ""
            p["prio3"] = ""
            p["submitted"] = False
        if len(p["id"]) == 0 or args.id_gen:
            # generate new player id
            p["id"] = str(uuid.uuid4())

    with open(players_file, "w") as file:
        json.dump(players, file, indent=4, sort_keys=True)

    print("Starting webserver ...")
    app.run(port=args.port, threaded=False, processes=1, host="::")

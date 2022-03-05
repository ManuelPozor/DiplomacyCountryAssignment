from data_processing.player_data import PlayerData

from itertools import product
import random
import argparse

unique_country_tags = ["GB", "FR", "GE", "IT", "AH", "RU", "OE"]


def assign_countries_by_priority(prioritiy_file,
                                 prio1_weight=1,
                                 prio2_weight=2,
                                 prio3_weight=3,
                                 no_prio_weight=5):
    ''' Evaluates the country selections of the players in a given file.
        The countries are assigned by weighting the priorities and determining the combinations resulting in the lowest cost.
        args:
            prioritiy_file: path to the json file with player data
            prio1_weight: weight of getting the first choice
            prio2_weight: weight of getting the second choice
            prio3_weight: weight of getting the third choice
            no_prio_weight: weight of getting an unprioritized country
    '''

    with PlayerData(prioritiy_file) as player_data:
        players = player_data.get_players()

    def tag_validity_check(tag, player_name):
        assert tag in unique_country_tags, "Invalid country tag " + tag + " for player " + player_name + ".\n Valid tags are: " + ", ".join(
            unique_country_tags)

    weighted_priorities = []
    for player in players:
        tag_validity_check(player["prio1"], player["name"])
        tag_validity_check(player["prio2"], player["name"])
        tag_validity_check(player["prio3"], player["name"])
        unwanted_countries = [
            (country, no_prio_weight) for country in unique_country_tags if
            country not in [player["prio1"], player["prio2"], player["prio3"]]
        ]
        # collect priorities with assigned weights
        weighted_priorities.append([(player["prio1"], prio1_weight),
                                    (player["prio2"], prio2_weight),
                                    (player["prio3"], prio3_weight),
                                    *unwanted_countries])

    combinations = list(product(*weighted_priorities))

    best_combinations = []
    # combinations with lowest score are saved
    lowest_score = 7 * no_prio_weight
    for comb in combinations:
        # discard invalid selections, i.e. same countries selected multiple times
        selected_countries = [country for country, prio in comb]
        if len(set(selected_countries)) < len(
                selected_countries):  # if set smaller, duplicates exist
            continue

        # compute score as sum of weights
        score = sum([prio for country, prio in comb])
        if score == lowest_score:
            best_combinations.append(comb)
        if score < lowest_score:
            lowest_score = score
            best_combinations = [comb]

    print(f"best combinations with score {lowest_score}: {best_combinations}")
    if len(best_combinations) > 1:
        best_combination = random.choice(best_combinations)
    else:
        best_combination = best_combinations[0]
    print("randomly selected best:", best_combination)

    with open(output_file, "w") as file:
        for ind, country_weight_tuple in enumerate(best_combination):
            player_name = players[ind]["name"]
            file.write(
                f"Player {ind+1}: {player_name} {country_weight_tuple[0]}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=
        'Assigns countries to players based on their selection stored in a given json file.'
    )
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
    parser.add_argument(
        '--pone',
        help='Penalty for getting the first priority (default: %(default)s)',
        type=int,
        default=1)
    parser.add_argument(
        '--ptwo',
        help='Penalty for getting the second priority (default: %(default)s)',
        type=int,
        default=2)
    parser.add_argument(
        '--pthree',
        help='Penalty for getting the third priority (default: %(default)s)',
        type=int,
        default=3)
    parser.add_argument(
        '--pnone',
        help=
        'Penalty for getting none of the priorities (default: %(default)s)',
        type=int,
        default=5)
    args = parser.parse_args()
    prioritiy_file = args.json
    output_file = args.out
    assign_countries_by_priority(prioritiy_file,
                                 prio1_weight=args.pone,
                                 prio2_weight=args.ptwo,
                                 prio3_weight=args.pthree,
                                 no_prio_weight=args.pnone)

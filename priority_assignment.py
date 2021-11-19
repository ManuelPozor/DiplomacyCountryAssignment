import json
from itertools import product
import random

unique_country_tags = ["GB", "FR", "GE", "IT", "AH", "RU", "OE"]


def assign_countries_by_priority(prioritiy_file):
    with open(prioritiy_file, "r") as file:
        players = [player for player in json.load(file)]

    def tag_validity_check(tag, player_name):
        assert tag in unique_country_tags, "Invalid country tag " + tag + " for player " + player_name + ".\n Valid tags are: " + ", ".join(
            unique_country_tags)

    weighted_priorities = []
    for player in players:
        tag_validity_check(player["prio1"], player["name"])
        tag_validity_check(player["prio2"], player["name"])
        tag_validity_check(player["prio3"], player["name"])
        unwanted_countries = [
            (country, 5) for country in unique_country_tags if country not in
            [player["prio1"], player["prio2"], player["prio3"]]
        ]
        # collect priorities with assigned weights
        weighted_priorities.append([(player["prio1"], 1), (player["prio2"], 2),
                                    (player["prio3"], 3), *unwanted_countries])

    combinations = list(product(*weighted_priorities))

    best_combinations = []
    # combinations with lowest score are saved
    lowest_score = 27
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

    with open("country_distribution.txt", "w") as file:
        for ind, country_weight_tuple in enumerate(best_combination):
            player_name = players[ind]["name"]
            file.write(
                f"Player {ind+1}: {player_name} {country_weight_tuple[0]}\n")


if __name__ == "__main__":
    prioritiy_file = "player_priorities.json"
    assign_countries_by_priority(prioritiy_file)

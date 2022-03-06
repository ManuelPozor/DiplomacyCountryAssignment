# Country assignment for Diplomacy

Assigning countries randomly to the 7 players in the board game Diplomacy often leads to players being unsatisfied with the result.
Instead, players can now anonymously fill in priorities for countries they would like to play.
The algorithm then finds a combination that best fits the preferences of the players and makes the individual result visible to the respective player only.
This can even be done in advance to a live session to give each player more time to choose and prepare, while also retaining an element of surprise with the countries of other players remaining unknown.

Players are provided with a uniquely generated link to an online webform, where they can select their priorities ranking from 1st to 3rd place.
Once all submissions have been collected, the countries are assigned by a deep search which selects one of the country distributions with the lowest combined cost.
The cost of each combination of countries is weighted by the achieved priority in the players' ranking.
That means lower priorities or a country not favored by a player lead to higher penalties and are avoided if possible.


## Usage

The code requires a Python 3 (ideally 3.8+) version and the installation of pipenv through pip.

```bash
# For Linux use 'python3'
python -m pip install --user pipenv
```

As a first step, create a local virtual environment fulfilling the requirements by installing the pipenv.

```bash
# '--deploy' enforces an up to date 'Pipfile.lock'
pipenv install --deploy
```

Now, you can already start a server by simply calling the **server.py**.
It is also possible to specify a JSON file to store the player information or a text file to store the result (optional).

```bash
pipenv run python server.py --json player_priorities.json --out result.txt
```

This starts a local Flask webserver and generates IDs for each player which can be found in the specified JSON file.
Player names can also be adjusted there.
Send each player the server address link followed by "/\<id\>" with the respective ID of the player as a path.
Keep the IDs of players private to ensure anonymity.
The player choices or generated IDs stored in the JSON can be reset by running the server with these flags:

```bash
pipenv run python server.py --reset --id-gen
```

The webinterface allows each player to select their 3 favorite countries.
Once players have submitted their priorities, they will have to wait for others to make their decision but, until then, can change their choice via resubmission.
After all players have submitted, the algorithm determines the best combination.
Player can then see their assigned country using the same link.
The country distribution is also stored in an output text file and printed along with the calculated minimal cost in the console.


### Run from Docker image

The code can also be run inside a Docker container.
Either load or build the Docker image.

```bash
docker build -t diplo .
```

Then, execute the image with the following command:

```bash
docker run diplo
```


### Country assignment optimisation

You can also manually fill in the player choices in the JSON file and run the assignment directly.
Note that the countries are stored as acronyms ["GB", "FR", "GE", "IT", "AH", "RU", "OE"].

```bash
pipenv run python country_assignment.py --json player_priorities.json --out result.txt
```

The algorithm assigns countries by weighting the priorities with low penalties for the top priorities and higher penalties for low priority or unfavored countries.
The weights for the priorities can also be set manually.
A simple search over all possible combinations determines the country distribution resulting in the lowest cost and thus the (hopefully) most agreeable country assignment.

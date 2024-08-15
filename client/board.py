MAP_TEMPLATE = """\
   1  2  3  4  5  6  7  8  9  10
A  .  .  .  .  .  .  .  .  .  .
B  .  .  .  .  .  .  .  .  .  .
C  .  .  .  .  .  .  .  .  .  .
D  .  .  .  .  .  .  .  .  .  .
E  .  .  .  .  .  .  .  .  .  .
F  .  .  .  .  .  .  .  .  .  .
G  .  .  .  .  .  .  .  .  .  .
H  .  .  .  .  .  .  .  .  .  .
I  .  .  .  .  .  .  .  .  .  .
J  .  .  .  .  .  .  .  .  .  .\
"""


class Map:
    """
    Because we are not degenerates, our coordinate
    system operates with the origin at the bottom-left.
    """

    def __init__(self):
        self.map_rows: list[str] = []
        for row in MAP_TEMPLATE.split("\n"):
            self.map_rows.append(row.split())

        self.num_rows = 10
        self.num_cols = 10
        self.row_whitespace = 2  # 2 whitespaces between each row element
        self.col_whitespace = 0

    def is_within_board(self, x: int, y: int) -> bool:
        """
        Determine if the coordinates are within the board
        in a 0-index fashion.
        """
        return 0 <= x <= (self.num_rows - 1) and 0 <= y <= (self.num_cols - 1)

    def transform(self, x: int, y: int):
        """
        Given a pair of battleship coordinates, get the
        row, column that represent the point in our map data structure
        """
        if not self.is_within_board(x, y):
            raise ValueError(f"Coordinates {x=}, {y=} are not within board.")

        row = len(self.map_rows) - y - 1
        col = x + 1
        return row, col

    def get_position(self, x: int, y: int):
        x, y = self.transform(x, y)
        return self.map_rows[x][y]

    def update_position(self, x: int, y: int, repl: str):
        x, y = self.transform(x, y)
        self.map_rows[x][y] = repl

    def place_ship(
        self, size: int, orientation: str, start_position_x: int, start_position_y: int
    ):
        if orientation == "horizontal":
            coords = [(start_position_x + i, start_position_y) for i in range(size)]
        else:
            coords = [(start_position_x, start_position_y + i) for i in range(size)]

        if orientation == "horizontal":
            start_char = "<"
            end_char = ">"
            body = "="
        else:
            start_char = "v"
            end_char = "^"
            body = "|"

        for ind, coord in enumerate(coords):
            if ind == 0:
                char = start_char
            elif ind == len(coords) - 1:
                char = end_char
            else:
                char = body
            x, y = coord
            self.update_position(x, y, char)

    def draw_map(self):
        whitespace = " " * self.row_whitespace
        rows = [whitespace.join(row) for row in self.map_rows]
        # Align the header
        rows[0] = " " * (self.row_whitespace + 1) + rows[0]
        return "\n".join(rows)

    def place_guess(
        self,
        x: int,
        y: int,
        result: str,
    ):
        if result == "hit":
            self.update_position(x, y, "X")
        else:
            self.update_position(x, y, "O")


class Board:
    def __init__(self):
        self.player_map = Map()
        self.enemy_map = Map()

    def add_ships(
        self,
        ships: list[dict],
    ):
        """Draw all of the player's ships."""
        for ship in ships:
            size: int = ship["size"]
            orientation: str = ship["orientation"]
            start_position_x: int = ship["start_position_x"]
            start_position_y: int = ship["start_position_y"]
            self.player_map.place_ship(
                size, orientation, start_position_x, start_position_y
            )

    def add_players_guess_history(self, guesses: list[dict]):
        """Draw all of the guesses that the player has made towards the enemy."""
        for guess in guesses:
            guess_position_x: int = guess["position_x"]
            guess_position_y: int = guess["position_y"]
            result: str = guess["result"]
            self.enemy_map.place_guess(guess_position_x, guess_position_y, result)

    def add_enemys_guess_history(self, guesses: list[dict]):
        """Draw all of the guesses that the enemy has made towards the player."""
        for guess in guesses:
            guess_position_x: int = guess["position_x"]
            guess_position_y: int = guess["position_y"]
            result: str = guess["result"]
            self.player_map.place_guess(guess_position_x, guess_position_y, result)

    def draw_board(self):
        print(self.enemy_map.draw_map())
        print(self.player_map.draw_map())

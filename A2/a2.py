from __future__ import annotations
from typing import Optional
from a2_support import UserInterface, TextInterface
from constants import *

ENTITY = 'E'
MIN_THIRST = 0
MIN_HUNGER = 0
MIN_HEALTH = 0
TILE_DAMAGE = 0
MOVE_DAMAGE = 1
HUNGER_CUMULATE = 1
THIRST_CUMULATE = 1
ITEM_ENTITY = (EMPTY, COIN, POTION, HONEY, APPLE, WATER)
FILE_PROMPT = 'Enter game file: '
MOVE_PROMPT = 'Enter a move: '


# Replace these <strings> with your name, student number and email address.
__author__ = "Shuo Yuan, 46920348"
__email__ = "s4692034@student.uq.edu.au"

# Before submission, update this tag to reflect the latest version of the
# that you implemented, as per the blackboard changelog. 
__version__ = 1.0

# Uncomment this function when you have completed the Level class and are ready
# to attempt the Model class.


def load_game(filename: str) -> list['Level']:
    """ Reads a game file and creates a list of all the levels in order.
    
    Parameters:
        filename: The path to the game file
    
    Returns:
        A list of all Level instances to play in the game
    """
    levels = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('Maze'):
                _, _, dimensions = line[5:].partition(' - ')
                dimensions = [int(item) for item in dimensions.split()]
                levels.append(Level(dimensions))
            elif len(line) > 0 and len(levels) > 0:
                levels[-1].add_row(line)
    return levels


# Write your classes here
class Tile(object):
    """ Represents the floor for a (row, column) position.

    Attributes:
        This class has no public attributes
    """
    def is_blocking(self) -> bool:
        """ A tile is blocking if a player would not be allowed to move onto
            the position it occupies. By default, tile’s are not blocking.

        Returns:
            Returns True iff the tile is blocking.
        """
        return False

    def damage(self) -> int:
        """ For instance, if a tile has a damage of 3, the player’s HP would be
            reduced by 3 if they step onto the tile. By default, tile’s should
            do no damage to a player.

        Returns:
            Returns the damage done to a player if they step on this tile.
        """
        return TILE_DAMAGE

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the tile.
        """
        return ABSTRACT_TILE
    
    def __str__(self) -> str:
        """ Generates an "informal" or well-formed string representation of
            an object

        Returns:
            Returns the string representation for this Tile.
        """
        return self.get_id()

    def __repr__(self) -> str:
        """ Express the object as a string

        Returns:
            Returns the damage done to a player if they step on this tile.
        """
        return '{}()'.format(type(self).__name__)


class Wall(Tile):
    """ Inherits from Tile. Wall is a type of Tile that is blocking.

    Attributes:
        This class has no public attributes
    """
    def is_blocking(self) -> bool:
        """ The player would not be allowed to move onto the position of wall
            occupies.

        Returns:
            Returns True iff the tile is blocking.
        """
        return True

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the tile.
        """
        return WALL


class Empty(Tile):
    """ Inherits from Tile.

    Empty is a type of Tile that does not contain anything special. A player
    can move freely over empty tiles without taking any damage.

    Attributes:
        This class has no public attributes
    """
    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the wall.
        """
        return EMPTY


class Lava(Tile):
    """ Inherits from Tile. Lava is a type of Tile that is not blocking, but
        does a damage of 5 to the player’s HP when stepped on.

    Attributes:
        This class has no public attributes
    """
    def damage(self) -> int:
        """ This damage is in addition to any other damage sustained.

        Returns:
            Returns the damage done to a player if they step on this tile.
        """
        return LAVA_DAMAGE

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the lava.
        """
        return LAVA


class Door(Tile):
    """ Inherits from Tile.

    Door is a type of Tile that starts as locked (blocking). Once the player
    has collected all coins in a given maze, the door is ‘unlocked’ (becomes
    non-blocking and has its ID change to that of an empty tile), and the
    player can move through the square containing the unlocked door to
    complete the level.

    Attributes:
        This class has no public attributes
    """
    def __init__(self) -> None:
        """ Initialize the locked state of the door"""
        self._door_block = True
        self._door_id = DOOR

    def is_blocking(self) -> bool:
        """ The player would not be allowed to move onto the position of door
            occupies if the door is locked.

        Returns:
            Returns True iff the door is locked.
            Returns False iff the door is unlocked
        """
        return self._door_block

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the door.
        """
        return self._door_id

    def unlock(self) -> None:
        """ Unlocks the door, the id would be EMPTY"""
        self._door_block = False
        self._door_id = EMPTY


class Entity(object):
    """ Provides base functionality for all entities in the game.

    Attributes:
        This class has no public attributes
    """
    def __init__(self, position: tuple[int, int]) -> None:
        """ Sets up this entity at the given (row, column) position.

        Args:
            position (tuple[int, int]): position of entity
        """
        self._position = position

    def get_position(self) -> tuple[int, int]:
        """ Returns this entities (row, column) position."""
        return self._position

    def get_name(self) -> str:
        """ Returns the name of the class to which this entity belongs."""
        return type(self).__name__

    def get_id(self) -> str:
        """ For all non-abstract subclasses, this should be a single character
            representing the type of the entity.

        Returns:
            Return the ID of this entity.
        """
        return ENTITY

    def __str__(self) -> str:
        """ Generates an "informal" or well-formed string representation of an
            object

        Returns:
            Return the string representation for this entity (the ID).
        """
        return self.get_id()

    def __repr__(self) -> str:
        """ Express the object as a string

        Returns:
            Return the text that would be required to make a new instance of
            this class that looks identical (where possible) to self.
        """
        return f"{self.get_name()}({self._position})"


class DynamicEntity(Entity):
    """ Inherits from Entity.

    DynamicEntity is an abstract class which provides base functionality
    for special types of Entities that are dynamic (e.g. can move from
    their original position).

    Attributes:
        This class has no public attributes
    """
    def set_position(self, new_position: tuple[int, int]) -> None:
        """ Updates the DynamicEntity’s position to new_position, assuming it
            is a valid position.

        Returns:
            None
        """
        self._position = new_position

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the dynamic entity.
        """
        return DYNAMIC_ENTITY


class Player(DynamicEntity):
    """ Inherits from DynamicEntity.

    Player is a DynamicEntity that is controlled by the user, and must move
    from its original position to the end of each maze. A player has health
    points (HP) which starts at 100, hunger and thirst which both start at 0,
    and an inventory.

    Attributes:
        This class has no public attributes
    """
    def __init__(self, position) -> None:
        """ Sets up the player at the given (row, column) position.

        Args:
            position (tuple[int, int]): position of player
        """
        super().__init__(position)
        self._hunger = MIN_HUNGER
        self._thirst = MIN_THIRST
        self._health = MAX_HEALTH
        self._player_inventory = Inventory([])

    def get_hunger(self) -> int:
        """ Returns the player’s current hunger level."""
        return self._hunger

    def get_thirst(self) -> int:
        """ Returns the player's current thirst level."""
        return self._thirst

    def get_health(self) -> int:
        """ Returns the player's current HP."""
        return self._health

    def change_hunger(self, amount: int) -> None:
        """ Alters the player’s hunger level by the given amount.

        Args:
            amount (int): The amount of hunger needs to be change
        """
        self._hunger += amount
        if self._hunger < MIN_HUNGER:
            self._hunger = MIN_HUNGER
        elif self._hunger > MAX_HUNGER:
            self._hunger = MAX_HUNGER

    def change_thirst(self, amount: int) -> None:
        """ Alters the player’s thirst level by the given amount.

        Args:
            amount (int): The amount of thirst needs to be change
        """
        self._thirst += amount
        if self._thirst < MIN_THIRST:
            self._thirst = MIN_THIRST
        elif self._thirst > MAX_THIRST:
            self._thirst = MAX_THIRST

    def change_health(self, amount: int) -> None:
        """ Alters the player’s HP by the given amount.

        Args:
            amount (int): The amount of HP needs to be change
        """
        self._health += amount
        if self._health < MIN_HEALTH:
            self._health = MIN_HEALTH
        elif self._health > MAX_HEALTH:
            self._health = MAX_HEALTH

    def get_inventory(self) -> Inventory:
        """ Get the player's Inventory.

        Returns:
            Returns the player’s Inventory instance.
        """
        return self._player_inventory

    def add_item(self, item: Item) -> None:
        """ Adds the given item to the player’s Inventory instance.

        Args:
            item (Item): The item to be added to player’s Inventory
        """
        self._player_inventory.add_item(item)


class Item(Entity):
    """ Inherits from Entity. Subclass of Entity which provides base
        functionality for all items in the game.

    Attributes:
        This class has no public attributes
    """
    def apply(self, player: Player) -> None:
        """ Applies the items effect, if any, to the given player.

        Args:
            player (Player): The player instance within the game.
        """
        raise NotImplementedError

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the item.
        """
        return ITEM


class Potion(Item):
    """ Inherits from Item. A potion is an item that increases the player’s
        HP by 20 when applied.

    Attributes:
        This class has no public attributes
    """
    def apply(self, player: Player) -> None:
        """ Applied item effect: Health is restored by 20, if any, for a given
            player.

        Args:
            player (Player): The player instance within the game.
        """
        player.change_health(POTION_AMOUNT)

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the potion.
        """
        return POTION


class Coin(Item):
    """ Inherits from Item. A coin is an item that has no effect when applied
        to a player.

    The purpose of a coin is to be collected and stored in a players inventory.

    Attributes:
        This class has no public attributes
    """
    def apply(self, player: Player) -> None:
        """ The act of adding the coin to the players inventory is not done
            within this class, so we just left the apply method.

        Args:
            player (Player): The player instance within the game.
        """
        pass

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the coin.
        """
        return COIN


class Water(Item):
    """ Inherits from Item. Water is an item that will decrease the player’s
        thirst by 5 when applied.

    Attributes:
        This class has no public attributes
    """
    def apply(self, player: Player) -> None:
        """ Applied item effect: Thirst is restored by 5, if any, for a given
            player.

        Args:
            player (Player): The player instance within the game.
        """
        player.change_thirst(WATER_AMOUNT)

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the water.
        """
        return WATER


class Food(Item):
    """ Inherits from Item. Food is an abstract class.

    Food subclasses implement an apply method that decreases the players
    hunger by a certain amount, depending on the type of food.

        Attributes:
            This class has no public attributes
    """
    def apply(self, player: Player) -> None:
        """ Food is an abstract class, so we just left the apply method.

        Args:
            player (Player): The player instance within the game.
        """
        pass

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the food.
        """
        return FOOD


class Apple(Food):
    """ Inherits from Food. Apple is a type of food that decreases the
        player’s hunger by 1 when applied.

    Attributes:
        This class has no public attributes
    """
    def apply(self, player: Player) -> None:
        """ Applied item effect: Hunger is restored by 1, if any, for a given
            player.

        Args:
            player (Player): The player instance within the game.
        """
        player.change_hunger(APPLE_AMOUNT)

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the apple.
        """
        return APPLE


class Honey(Food):
    """ Inherits from Food. Honey is a type of food that decreases the
        player’s hunger by 5 when applied.

    Attributes:
        This class has no public attributes
    """
    def apply(self, player: Player) -> None:
        """ Applied item effect: Hunger is restored by 5, if any, for a given
            player.

        Args:
            player (Player): The player instance within the game.
        """
        player.change_hunger(HONEY_AMOUNT)

    def get_id(self) -> str:
        """ For non-abstract subclasses, the ID should be a single character
            representing the type of Tile it is

        Returns:
            Returns the ID of the honey.
        """
        return HONEY


class Inventory(object):
    """ An Inventory contains and manages a collection of items.

    Attributes:
        This class has no public attributes
    """
    def __init__(self, initial_items: Optional[list[Item, ...]] = None) -> None:
        """ Sets up initial inventory.

        Args:
            initial_items (Optional[list[Item, ...]]): List of items object
        """
        self._ini_items = initial_items
        self._info = ''

        # If no initial_items is provided, inventory starts with an empty
        # dictionary for the items.
        self._inventory: dict[str, list[str]] = {}

        # Otherwise, the initial dictionary is set up from the initial_items
        # list to be a dictionary mapping item names to a list of item
        # instances with that name.
        if len(initial_items) != 0:
            for items in self._ini_items:
                self.add_item(items)

    def add_item(self, item: Item) -> None:
        """ Adds the given item to this inventory’s collection of items.

        Args:
            item (Item): The item to be added to Inventory instance
        """
        class_type, _, _ = item.__repr__().split('(')
        if class_type in self._inventory.keys():
            self._inventory[class_type].append(item)
        else:
            self._inventory[class_type] = [item]

    def get_items(self) -> dict[str, list[Item, ...]]:
        """ Returns a dictionary mapping the names of all items in the
            inventory to lists containing each instance of the item with
            that name."""
        return self._inventory

    def remove_item(self, item_name: str) -> Optional[Item]:
        """ Removes the first instance of the item with the given
            item_name from the inventory.

        Args:
            item_name (str): The name of item needs to be removed

        Returns:
            Return the first instance of the item with the given item_name
            from the inventory. If no item exists in the inventory with the
            given name, then this method returns None.
        """
        if item_name not in self._inventory.keys():
            return None
        else:
            removed = self._inventory[item_name][0]

            # Remove the first value of given item_name, if no value exists
            # after deletion, delete the key
            self._inventory[item_name] = self._inventory[item_name][1:]
            if not self._inventory[item_name]:
                self._inventory.pop(item_name)
            return removed

    def __str__(self):
        """ Returns a string containing information about quantities of items
            available in the inventory."""
        for items in self._inventory:
            self._info += f'{items}: {len(self._inventory[items])}\n'
        return self._info.strip('\n')

    def __repr__(self):
        """ Returns a string that could be used to construct a new instance of
            Inventory containing the same items as self currently contains."""
        return f"{type(self).__name__}(initial_items={self._ini_items})"


class Maze(object):
    """ A Maze instance represents the space in which a level takes place.

    The maze does not know what entities are placed on it or where the
    entities are; it only knows what tiles it contains and what dimensions
    it has.

    Attributes:
        This class has no public attributes
    """
    def __init__(self, dimensions: tuple[int, int]) -> None:
        """ Sets up an empty maze of given dimensions (a tuple of the number
            of rows and number of columns).

        Args:
            dimensions (tuple[int, int]): The tuple indicates (#rows, #columns)
                                            of this maze.
        """
        self._dimension = dimensions
        self._row_info = ''
        self._tiles = []
        self._door = Door()

    def get_dimensions(self) -> tuple[int, int]:
        """ Returns the (#rows, #columns) in the maze."""
        return self._dimension

    def add_row(self, row: str) -> None:
        """ Adds a row of tiles to the maze. Each character in row is a Tile
            ID which can be used to construct the appropriate Tile instance to
            place in that position of the row of tiles.

        Args:
            row (str): The collection string of tile IDs in a row
        """
        for ID in row:
            if ID not in (WALL, DOOR, LAVA, WATER, APPLE, HONEY, POTION):
                self._row_info += EMPTY
            else:
                self._row_info += ID
        self._row_info += '\n'

        # Each time add_row is called, we need to reassign to null to prevent
        # self._tiles from retaining the contents of the previous call
        processed = []
        self._tiles = []
        for ID in self._row_info:
            if ID == WALL:
                processed.append(Wall())
            elif ID == DOOR:
                processed.append(self._door)
            elif ID == '\n':
                self._tiles.append(processed)
                processed = []
            else:
                processed.append(Empty())

    def get_row_info(self) -> str:
        """ returns the row info which have been added to this maze"""
        return self._row_info

    def get_tiles(self) -> list[list[Tile]]:
        """ Returns the Tile instances in this maze"""
        return self._tiles

    def unlock_door(self) -> None:
        """ Unlocks any doors that exist in the maze."""
        self._door.unlock()

    def get_tile(self, position: tuple[int, int]) -> Tile:
        """ Returns the Tile instance at the given position.

        Args:
            position (tuple[int, int]): the position of tile in the maze.
        """
        row, column = position
        return self._tiles[row][column]

    def __str__(self):
        """ Returns the string representation of this maze."""
        return self._row_info.strip('\n')

    def __repr__(self):
        """ Returns a string that could be copied and pasted to construct a
            new Maze instance with the same dimensions as this Maze instance"""
        return f"{type(self).__name__}({self._dimension})"


class Level(object):
    """ A Level instance keeps track of both the maze and the non-player
        entities placed on the maze for a single level.

    Attributes:
        This class has no public attributes
    """
    def __init__(self, dimensions: tuple[int, int]) -> None:
        """ Sets up a new level with empty maze using the given dimensions.
            The level is set up initially with no items or player.

        Args:
            dimensions (tuple[int, int]): The tuple indicates (#rows, #columns)
                                            of this level of maze.
        """
        self._player = None
        self._dimension = dimensions
        self._level = Maze(self._dimension)
        self._items = {}
        self._call_time = 0

    def get_maze(self) -> Maze:
        """ Returns the Maze instance for this level."""
        return self._level

    def attempt_unlock_door(self) -> None:
        """ Unlocks the doors in the maze if there are no coins remaining."""
        if COIN not in self._level.get_row_info():
            self._level.unlock_door()

    def add_row(self, row: str) -> None:
        """ Adds the tiles and entities from the row to this level. row is a
            string containing the Tile IDs and Entity IDs to place in this row.

        Args:
            row (str): The collection string of tile IDs in a row.
        """
        self.get_maze().add_row(row)
        for idx, ID in enumerate(row):
            if ID == COIN:
                self._items[(self._call_time, idx)] = \
                    Coin((self._call_time, idx))
            elif ID == POTION:
                self._items[(self._call_time, idx)] = \
                    Potion((self._call_time, idx))
            elif ID == HONEY:
                self._items[(self._call_time, idx)] = \
                    Honey((self._call_time, idx))
            elif ID == APPLE:
                self._items[(self._call_time, idx)] = \
                    Apple((self._call_time, idx))
            elif ID == WATER:
                self._items[(self._call_time, idx)] = \
                    Water((self._call_time, idx))
            elif ID == PLAYER:
                self._player = Player((self._call_time, idx))

        self._call_time += 1

    def add_entity(self, position: tuple[int, int], entity_id: str) -> None:
        """ Adds a new entity to this level in the given position. If an item
            existed at that position previously, this new item will replace it.

        Args:
              position (tuple[int, int]): the position of tile in this maze.
              entity_id (str): The ID of specific entity.
        """
        if not self._level.get_tiles():
            temp_row = ''
            _, column = position
            height, width = self._dimension
            for i in range(width):
                if i == column:
                    temp_row += entity_id
                else:
                    temp_row += ' '
            self.add_row(temp_row)

        if self._level.get_tile(position).get_id() in ITEM_ENTITY:
            row, column = position
            if entity_id == COIN:
                self._level.get_tiles()[row][column] = Coin(position)
                self._items[position] = Coin(position)
            elif entity_id == POTION:
                self._level.get_tiles()[row][column] = Potion(position)
                self._items[position] = Potion(position)
            elif entity_id == HONEY:
                self._level.get_tiles()[row][column] = Honey(position)
                self._items[position] = Honey(position)
            elif entity_id == APPLE:
                self._level.get_tiles()[row][column] = Apple(position)
                self._items[position] = Apple(position)
            elif entity_id == WATER:
                self._level.get_tiles()[row][column] = Water(position)
                self._items[position] = Water(position)

    def get_dimensions(self) -> tuple[int, int]:
        """ Returns the (#rows, #columns) in the level maze."""
        return self._dimension
    
    def get_items(self) -> dict[tuple[int, int], Item]:
        """ Returns a mapping from position to the Item at that position for
            all items currently in this level."""
        return self._items

    def remove_item(self, position: tuple[int, int]) -> None:
        """ Deletes the item from the given position. A precondition of this
            method is that there is an Item instance at the position."""
        if self._level.get_tile(position).get_id() in ITEM_ENTITY:
            self._items.pop(position)

    def add_player_start(self, position: tuple[int, int]) -> None:
        """ Adds the start position for the player in this level.

        Args:
            position (tuple[int, int]): the position of player in this maze.
        """
        if not self._level.get_tiles():
            temp_row = ''
            _, column = position
            height, width = self._dimension
            for i in range(width):
                if i == column:
                    temp_row += PLAYER
                else:
                    temp_row += ' '
            self.add_row(temp_row)

        self._player = Player(position)

    def get_player_start(self) -> Optional[tuple[int, int]]:
        """ Returns the starting position of the player for this level. If no
            player start has been defined yet, this method returns None."""
        if self._player:
            return self._player.get_position()
        else:
            return None

    def get_player(self) -> Player:
        """ Returns the player instance of this level"""
        return self._player

    def __str__(self):
        """ Returns a string representation of this level."""
        return f"Maze: {self._level}\nItems: {self._items}\nPlayer start: " \
               f"{self.get_player_start()}"

    def __repr__(self):
        """ Returns a string that could be copied and pasted to construct a
            new Level instance with the same dimensions as this Level instance."""
        return f"{type(self).__name__}({self._dimension})"


class Model(object):
    """ The controller uses to understand and mutate the game state.

    The model keeps track of a Player, and multiple Level instances. The Model
    class must provide the interface through which the controller can request
    information about the game state, and request changes to the game state.

    Attributes:
        This class has no public attributes
    """
    def __init__(self, game_file: str) -> None:
        """ Sets up the model from the given game_file, which is a path to a
            file containing game information (e.g. games/game1.txt).

        Args:
              game_file (str): A path to a file containing game information.
        """
        self._file = game_file
        self._levels = load_game(self._file)
        self._level_num = 0
        self._won_state = False
        self._lost_state = False
        self._level_up = False
        self._move_time = 0

    def has_won(self) -> bool:
        """ Returns True if the game has been won, otherwise returns False.
            A game has been won if all the levels have been successfully
            completed."""
        return self._won_state

    def has_lost(self) -> bool:
        """ Returns True if the game has been lost, otherwise returns False
            (HP too low or hunger or thirst too high)."""
        if self.get_player_stats()[0] <= MIN_HEALTH or \
                self.get_player_stats()[1] >= MAX_HUNGER or \
                self.get_player_stats()[2] >= MAX_THIRST:
            self._lost_state = True
        return self._lost_state

    def get_level(self) -> Level:
        """ Returns the current level."""
        return self._levels[self._level_num]

    def level_up(self) -> None:
        """ Changes the level to the next level in the game. If no more
            levels remain, the player has won the game."""
        self._level_num += 1
        if self._level_num == len(self._levels):
            self._won_state = True
        else:
            self._level_up = True

    def did_level_up(self) -> bool:
        """ Returns True if the player just moved to the next level on the
            previous turn, otherwise returns False."""
        return self._level_up

    def move_player(self, delta: tuple[int, int]) -> None:
        """ Tries to move the player by the requested (row, column) change
            (delta). This method should also level up if the player finished
            the maze by making the move.

        If the player did not level up and the tile that the player is moving
        into is non-blocking, this method should:
            • Update the players hunger, thirst based on the number of moves
                made.
            • Update players health based on the successful movement and the
                damage caused by the tile the player has moved onto.
            • Update the players position.
            • Attempt to collect any item that is on the players new position.
            • Levels up if the player finishes the maze by making the move.

        Args:
            delta (tuple[int, int]): The unit of distance the user moves in
                                        four directions
        """
        new_position = (self.get_player().get_position()[0] + delta[0],
                        self.get_player().get_position()[1] + delta[1])
        if self.get_current_maze().get_tile(new_position).get_id() == WALL:
            return None

        self._move_time += 1
        self.get_player().set_position(new_position)
        self.get_player().change_health(-MOVE_DAMAGE)

        if self._move_time % 5 == 0:
            self.get_player().change_hunger(HUNGER_CUMULATE)
            self.get_player().change_thirst(THIRST_CUMULATE)

        if self.get_current_maze().get_tile(new_position).get_id() == LAVA:
            self.get_player().change_health(-LAVA_DAMAGE)

        if new_position in self.get_level().get_items():
            self.attempt_collect_item(new_position)

        if self.get_level().attempt_unlock_door():
            self._level_num += 1

    def attempt_collect_item(self, position: tuple[int, int]) -> None:
        """ Collects the item at the given position if one exists. Unlocks
            the door if all coins have been collected.

        Args:
            position (tuple[int, int]): the position of item in this maze.
        """
        if position in self.get_level().get_items():
            self.get_player_inventory().add_item(
                self.get_level().get_items()[position])
            if self.get_level().get_items()[position].get_id() == COIN:
                coin_index = (position[0] + 1) * \
                             self.get_level().get_dimensions()[1] \
                             + position[1] - 1
                self.get_current_maze()._row_info = \
                    self.get_current_maze().get_row_info()[:coin_index] \
                    + ' ' + self.get_current_maze().get_row_info()[coin_index
                                                                   + 1:]
            self.get_level().remove_item(position)

    def get_player(self) -> Player:
        """ Returns the player in the game."""
        return self.get_level().get_player()

    def get_player_stats(self) -> tuple[int, int, int]:
        """ Returns the player’s current stats as (HP, hunger, thirst)."""
        return (self.get_player().get_health(),
                self.get_player().get_hunger(),
                self.get_player().get_thirst())

    def get_player_inventory(self) -> Inventory:
        """ Returns the players inventory."""
        return self.get_player().get_inventory()

    def get_current_maze(self) -> Maze:
        """ Returns the Maze for the current level."""
        return self.get_level().get_maze()

    def get_current_items(self) -> dict[tuple[int, int], Item]:
        """ Returns a dictionary mapping tuple positions to the item that
            currently exists at that position on the maze. Only positions
            at which an item exists should be included in the result."""
        return self.get_player_inventory().get_items()

    def __str__(self):
        """ Returns the text required to construct a new instance of Model
            with the same game file used to construct self."""
        return f"{type(self).__name__}('{self._file}')"

    def __repr__(self):
        """ Does the same thing as __str__."""
        return self.__str__()


class MazeRunner(object):
    """ MazeRunner is the controller class, which should maintain instances
        of the model and view, collect user input and facilitate communication
        between the model and view.

    Attributes:
        This class has no public attributes
    """
    def __init__(self, game_file: str, view: UserInterface) -> None:
        """ Creates a new MazeRunner game with the given view and a new Model
            instantiated using the given game_file.

        Args:
            game_file (str): A path to a file containing game information.
            view (UserInterface): Abstract class providing an interface for
                                    any MazeRunner View class.
        """
        self._file = game_file
        self._view = view

    def play(self) -> None:
        """ Executes the entire game until a win or loss occurs."""
        str(Model(self._file).get_current_maze())


def main():
    """Entry-point to gameplay."""
    game = input(FILE_PROMPT)
    maze_runner = MazeRunner(game, UserInterface)
    maze_runner.play()


if __name__ == '__main__':
    main()

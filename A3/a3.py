import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Union, Callable
from PIL import ImageTk, Image

from a3_support import AbstractGrid
from constants import GAME_FILE, TASK
from a2_solution import *

QUIT_MESSAGE = "Do you really want to quit the game?"
CANDY_HUNGER_AMOUNT = -10
CANDY_HEALTH_AMOUNT = -2
SHOP_IMAGE_WIDTH = 200
SHOP_IMAGE_HEIGHT = 200
SHOP_LIST = {"apple": (1, Apple((0, 0))), "water": (1, Water((0, 0))),
             "honey": (2, Honey((0, 0))), "potion": (2, Potion((0, 0)))}
ENTITY_PRICE = {"apple": "$1", "water": "$1", "honey": "$2",
                "potion": "$2", "candy": "$3"}

__author__ = "Shuo Yuan, 46920348"
__email__ = "s4692034@student.uq.edu.au"


# Write your classes here
class LevelView(AbstractGrid):
    """ Displays the maze(tiles) along with the entities.

    Note: Tiles are drawn on the map using coloured rectangles at their
        (row, column) positions, and entities are drawn over the tiles
        using coloured, annotated ovals at their (row, column) positions.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame],
                 dimension: tuple[int, int], size: tuple[int, int],
                 **kwargs) -> None:
        """ Constructor for LevelView.

        Parameters:
            master: the master frame for this Canvas.
            dimensions: (#rows, #columns).
            size: (width in pixels, height in pixels).
        """
        super().__init__(master, dimension, size, **kwargs)

    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], Item],
             player_pos: tuple[int, int]) -> None:
        """ Clears and redraws the entire level (maze and entities).

        Parameters:
            tiles: a list contains Tile instances in this level.
            items: a dictionary maps locations to the items currently at
                    those locations.
            player_pos: current position of player.
        """
        rows, columns = self._dimensions
        for row in range(rows):
            for col in range(columns):
                tile_color = TILE_COLOURS[tiles[row][col].get_id()]
                self.create_rectangle(self.get_bbox((row, col)),
                                      fill=tile_color)

        for item_pos, item in items.items():
            entity_color = ENTITY_COLOURS[item.get_id()]
            self.create_oval(self.get_bbox(item_pos), fill=entity_color)
            self.annotate_position(item_pos, item.get_id())

        self.create_oval(self.get_bbox(player_pos),
                         fill=ENTITY_COLOURS[PLAYER])
        self.annotate_position(player_pos, PLAYER)


class StatsView(AbstractGrid):
    """ Displays the player's stats (HP, health, thirst), along with the
        number of coins collected.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame], width: int,
                 **kwargs) -> None:
        """ Sets up a new StatsView in the master frame with the given width.

        Parameters:
            master: the master window of StatsView.
            width: the width of StatsView canvas.
        """
        super().__init__(master, (2, 4), (width, STATS_HEIGHT), **kwargs)
        self.config(bg=THEME_COLOUR)

    def draw_stats(self, player_stats: tuple[int, int, int]) -> None:
        """ Draws the player's stats (hp, hunger, thirst).

        Parameters:
            player_stats: the player's current (HP, hunger, thirst).
        """
        self.annotate_position((0, 0), "HP")
        self.annotate_position((1, 0), str(player_stats[0]))

        self.annotate_position((0, 1), "Hunger")
        self.annotate_position((1, 1), str(player_stats[1]))

        self.annotate_position((0, 2), "Thirst")
        self.annotate_position((1, 2), str(player_stats[2]))

    def draw_coins(self, num_coins: int) -> None:
        """ Draws the number of coins."""
        self.annotate_position((0, 3), "Coins")
        self.annotate_position((1, 3), str(num_coins))


class InventoryView(tk.Frame):
    """ Displays the items the player has in their inventory via tk.Labels,
        under a title label.

    Note: InventoryView also provides a mechanism through which the user
        can apply items.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
        """ Creates a new InventoryView within master.

        Parameters:
            master: the master window of InventoryView.
        """
        super().__init__(master, **kwargs)
        self._callback = None

    def set_click_callback(self, callback: Callable[[str], None]) -> None:
        """ Sets the function to be called when an item is clicked.

        Parameters:
            callback: the function to be called when an item is clicked,
                it should take one argument: the string name of the item.
        """
        self._callback = callback

    def clear(self) -> None:
        """ Clears all child widgets from this InventoryView."""
        for widget in self.winfo_children():
            widget.destroy()

    def _draw_item(self, name: str, num: int, colour: str) -> None:
        """ Creates and binds (if a callback exists) a single tk.Label in the
            InventoryView frame.

        Parameters:
            name: name of the item.
            num: quantity currently in the users inventory.
            colour: background colour for this item label.
        """
        inventory_item = tk.Label(self, text=f"{name}: {num}", bg=colour,
                                  font=TEXT_FONT)
        inventory_item.pack(side=tk.TOP, fill=tk.X)
        if self._callback:
            inventory_item.bind('<Button-1>', lambda x: self._callback(name))

    def draw_inventory(self, inventory: Inventory) -> None:
        """ Draws any non-coin inventory items with their quantities and binds
            the callback for each, if a click callback has been set.

        Parameters:
            inventory: the player's current inventory.
        """
        inventory_heading = tk.Label(self, text="Inventory", font=HEADING_FONT)
        inventory_heading.pack(side=tk.TOP, fill=tk.BOTH)
        for item_name, items in inventory.get_items().items():
            if item_name != Coin.__name__:
                self._draw_item(item_name, len(items),
                                ENTITY_COLOURS[items[0].get_id()])


class GraphicalInterface(UserInterface):
    """ Manages the overall view (i.e. the title banner and the three major
        widgets), and enables event handling.
    """

    def __init__(self, master: tk.Tk) -> None:
        """ Creates a new GraphicalInterface with master frame master.

        Parameters:
            master: master frame of GraphicalInterface.

        Note: this method is not responsible for instantiating the three
            major components, as you may not know the dimensions of the
            maze when the GraphicalInterface is instantiated.
        """
        self._master = master
        self._master.title("MazeRunner")

        self._level_view = None
        self._image_level_view = None
        self._inventory_view = None
        self._stats_view = None
        self._control_frame = None
        self._menu = None
        self._shop_btn = None
        self._time_played = 0

        game_banner = tk.Label(self._master, text='MazeRunner',
                               font=BANNER_FONT, bg=THEME_COLOUR)
        game_banner.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

    def create_interface(self, dimensions: tuple[int, int]) -> None:
        """ Creates the components (level view, inventory view, and stats view)
            in the master frame for this interface.

        Parameters:
            dimensions: the (row, column) dimensions of the maze in the current
                        level.
        """
        ui_frame = tk.Frame(self._master)
        ui_frame.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

        if TASK == 1:
            self._level_view = LevelView(ui_frame, dimensions,
                                         (MAZE_WIDTH, MAZE_HEIGHT))
            self._level_view.pack(side=tk.LEFT)
        else:
            self._image_level_view = ImageLevelView(ui_frame, dimensions,
                                                    (MAZE_WIDTH, MAZE_HEIGHT))
            self._image_level_view.pack(side=tk.LEFT)

        self._inventory_view = InventoryView(ui_frame)
        self._inventory_view.pack(side=tk.LEFT, fill=tk.BOTH)

        self._stats_view = StatsView(self._master,
                                     MAZE_WIDTH + INVENTORY_WIDTH)
        self._stats_view.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

    def create_game_control_interface(self,
                                      restart: Callable,
                                      new_game: Callable,
                                      save_game: Callable,
                                      load_game: Callable,
                                      quit_game: Callable,
                                      open_shop: Callable) -> None:
        """ Creates the components (controls frame, file menu, and shop view)
            in the master frame for this interface.

        Parameters:
            restart: the callback function implements restart the game.
            new_game: the callback function implements open new game.
            save_game: the callback function implements save game.
            load_game: the callback function implements load game.
            quit_game: the callback function implements quit game.
            open_shop: the callback function implements open shop.
        """
        self._control_frame = ControlsFrame(self._master, restart,
                                            new_game, open_shop)
        self._control_frame.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)
        self._draw_control_frame()
        self._calculagraph()

        self._menu = FileMenu(self._master, restart, save_game,
                              load_game, quit_game)
        self._master.config(menu=self._menu)

        if TASK == 3:
            self._shop_btn = tk.Button(self._control_frame, text='Shop')
            self._shop_btn.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.BOTH)

    def clear_all(self) -> None:
        """ Clears each of the three major components."""
        if TASK == 1:
            self._level_view.clear()
        else:
            self._image_level_view.clear()
        self._inventory_view.clear()
        self._stats_view.clear()
        self._control_frame.clear()

    def set_maze_dimensions(self, dimensions: tuple[int, int]) -> None:
        """ Updates the dimensions of the maze in the level to dimensions.

        Parameters:
            dimensions: the (row, column) dimensions of the maze.
        """
        if TASK == 1:
            self._level_view.set_dimensions(dimensions)
        else:
            self._image_level_view.set_dimensions(dimensions)

    def bind_keypress(self, command: Callable[[tk.Event], None]) -> None:
        """ Binds the given command to the general keypress event.

        Parameters:
            command: a function which takes in the keypress event, and performs
                    different actions depending on what character was pressed.
        """
        self._master.bind('<Key>', command)

    def set_inventory_callback(self, callback: Callable[[str], None]) -> None:
        """ Sets the function to be called when an item is clicked in the
            inventory view to be callback.

        Parameters:
            callback: a function apply the first instance of that item in the
                    inventory to the player.
        """
        self._inventory_view.set_click_callback(callback)

    def draw_inventory(self, inventory: Inventory) -> None:
        """ Draws any non-coin inventory items with their quantities and binds
            the callback for each, if a click callback has been set.

        Parameters:
            inventory: the player's current inventory.
        """
        self._inventory_view.draw_inventory(inventory)

    def draw(self, maze: Maze, items: dict[tuple[int, int], Item],
             player_position: tuple[int, int], inventory: Inventory,
             player_stats: tuple[int, int, int]) -> None:
        """ Clearing the three major components and redrawing them with the new
            state.

        Parameters:
              maze: the current Maze instance.
              items: a dictionary maps locations to the items currently at
                    those locations.
              player_position: the position of the player.
              inventory: the player's current inventory.
              player_stats: the player's current (HP, hunger, thirst).
        """
        self.clear_all()
        self._draw_level(maze, items, player_position)
        self._draw_inventory(inventory)
        self._draw_player_stats(player_stats)
        self._draw_control_frame()

    def _draw_inventory(self, inventory: Inventory) -> None:
        """ Draw both the non-coin items on the inventory view (see public draw
            inventory method), and also draw the coins on the stats view.

        Parameters:
            inventory: the player's current inventory.
        """
        self.draw_inventory(inventory)
        self._stats_view.draw_coins(self.get_num_coin(inventory))

    def _draw_level(self, maze: Maze, items: dict[tuple[int, int], Item],
                    player_position: tuple[int, int]) -> None:
        """ Draws the maze and all its items.

        Parameters:
            maze: the current maze for the level.
            items: a dictionary maps locations to the items currently at
                    those locations.
            player_position: the current position of the player.
        """
        if TASK == 1:
            self._level_view.draw(maze.get_tiles(), items, player_position)
        else:
            self._image_level_view.draw(maze.get_tiles(), items,
                                        player_position)

    def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
        """ Draws the players stats.

        Parameters:
            player_stats: the player's current (HP, hunger, thirst).
        """
        self._stats_view.draw_stats(player_stats)

    def _draw_control_frame(self) -> None:
        """ Draws the controls frame."""
        self._control_frame.draw_controls_frame()

    def _calculagraph(self) -> None:
        """ Counts how long the user plays."""
        self._time_played += 1

        # Call this function and update the timer label
        # in control frame every 1000ms
        self._master.after(1000, self._calculagraph)
        self._control_frame.set_timer_label(self._time_played)

    def get_num_coin(self, inventory: Inventory) -> int:
        """ Check how many coins user has.

        Parameters:
            inventory: the player's current inventory.

        Returns:
            The number of coins in the player's inventory.
        """
        return len(inventory.get_items().get(Coin.__name__, []))

    def get_time_played(self) -> int:
        """ Get the game played time.

        Returns:
            The number of minutes and seconds that have elapsed since the
            current game egan.
        """
        return self._time_played


class GraphicalMazeRunner(MazeRunner):
    """ A MazeRunner interface that uses graph to present information."""

    def __init__(self, game_file: str, root: tk.Tk) -> None:
        """ Creates a new GraphicalMazeRunner game, with the view inside the
            given root widget.

        Parameters:
            game_file: the path to the game file.
            root: the root window of the game.
        """
        self._root = root
        self._game_file = game_file
        self._model = Model(game_file)
        self._gui = GraphicalInterface(self._root)

        # record every player movement for loading game
        self._move_history = []

    def _handle_keypress(self, e: tk.Event) -> None:
        """ Handles a keypress.

        Parameters:
            e: a tkinter event object detects key press.
        """
        if e.char in (UP, DOWN, LEFT, RIGHT):
            self._model.move_player(MOVE_DELTAS.get(e.char))
            self._move_history.append(e.char)

        if self._model.did_level_up():
            self._gui.set_maze_dimensions(
                self._model.get_level().get_dimensions())
        elif self._model.has_won():
            messagebox.showinfo(title='Test', message=WIN_MESSAGE)
            self._root.destroy()
            return None
        elif self._model.has_lost():
            messagebox.showinfo(title='Test', message=LOSS_MESSAGE)

        self._draw()

    def _apply_item(self, item_name: str) -> None:
        """ Attempts to apply an item with the given name to the player.

        Parameters:
            item_name: the name of the item.
        """
        item = self._model.get_player().get_inventory().remove_item(item_name)
        if item is not None:
            item.apply(self._model.get_player())
        self._draw()

    def play(self) -> None:
        """ Called to cause gameplay to occur."""
        self._gui.create_interface(self._model.get_level().get_dimensions())
        self._gui.create_game_control_interface(self._restart,
                                                self._new_game,
                                                self._save_game,
                                                self._load_game,
                                                self._quit_game,
                                                self._draw_shop)

        self._gui.bind_keypress(self._handle_keypress)
        self._gui.set_inventory_callback(self._apply_item)
        self._draw()

    def _draw(self) -> None:
        """ Clearing the three major components and redrawing them with the new
            state."""
        self._gui.draw(self._model.get_level().get_maze(),
                       self._model.get_level().get_items(),
                       self._model.get_player().get_position(),
                       self._model.get_player().get_inventory(),
                       self._model.get_player_stats())

    def _restart(self) -> None:
        """ Restart the game.

        Note: the user should return to the start of the first level, their move
        count and stats should reset, and the game timer should return to 0.
        """
        self._model = Model(self._game_file)
        self._gui.set_maze_dimensions(
            self._model.get_current_maze().get_dimensions())
        self._gui._time_played = 0
        self._draw()

    def _check_valid_path(self) -> None:
        """ Check whether the relative path to the new game file is valid."""
        filename = self._entry.get()
        try:
            self._model = Model(filename)
            self._gui.set_maze_dimensions(
                self._model.get_current_maze().get_dimensions())
            self._window.destroy()
            self._draw()
        except FileNotFoundError:
            messagebox.showinfo(title='Error', message="File not found")
            self._window.destroy()

    def _new_game(self) -> None:
        """ Prompting the user to enter new game path via a tk.TopLevel
            window.

        Note: Once the user has acknowledged the messagebox, the toplevel
            window should close and the user should not be automatically
            reprompted.
        """
        self._window = tk.Toplevel(self._root)
        self._entry = tk.Entry(self._window)
        self._entry.pack(side=tk.LEFT)
        submit_btn = tk.Button(self._window, text="Play",
                               command=self._check_valid_path)
        submit_btn.pack(side=tk.LEFT)

    def _save_game(self) -> None:
        """ Prompt the user for the location to save their file and save all
            necessary information to replicate the current state of the game.
        """
        with filedialog.asksaveasfile('w') as file:
            self._saved_filepath = file.name
            file.write(f"game file: {self._game_file}\n")
            file.write(f"move history: {self._move_history}\n")
            file.write(f"timer: {self._gui.get_time_played()}\n")
            file.write(f"file path: {self._saved_filepath}\n")

    def _load_game(self) -> None:
        """ Prompt the user for the location of the file to load a game from
            and load the game described in that file.
        """
        pass

    def _quit_game(self) -> None:
        """ Prompt the player via messagebox to ask whether they are sure
            they would like to quit.
        """
        answer = messagebox.askyesno(title="Quit", message=QUIT_MESSAGE)
        if answer:
            self._root.destroy()

    def _draw_shop(self) -> None:
        """ Create a shop tk.TopLevel window where the user can spend their
            collected coins to buy items.
        """
        self._shop_window = tk.Toplevel(self._root)
        self._shop_window.minsize(MAZE_WIDTH, MAZE_HEIGHT)

        self._shop_view = ShopView(self._shop_window)
        self._shop_view.draw_shop()
        self._shop_view.set_shop_callback(self._shopping)
        self._shop_view.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

    def _try_buy_item(self, item_name: str, coin_num: int, inventory: Inventory):
        """ Check whether the coin player have could afford specific item.

        Parameters:
            item_name: the name of the item.
            coin_num: the number of the coin player have.
            inventory: the player's current inventory.
        """
        price, instance = SHOP_LIST[item_name]
        if coin_num >= price:
            for times in range(price):
                inventory.remove_item(Coin.__name__)
            inventory.add_item(instance)
            self._draw()

    def _shopping(self, item_name: str) -> None:
        """ When the image of an item is left-clicked, if the player can afford
            the item (has enough coins), then the price should be subtracted
            from the player's coins, and an instance of the item should be
            added to the player's inventory.

        Parameters:
            item_name: the name of the item.
        """
        coin_num = self._gui.get_num_coin(self._model.get_player_inventory())
        inventory = self._model.get_player_inventory()
        self._try_buy_item(item_name, coin_num, inventory)


class ImageLevelView(LevelView):
    """ Displays the maze(tiles) along with the images."""

    def __init__(self, master: Union[tk.Tk, tk.Frame],
                 dimensions: tuple[int, int], size, **kwargs) -> None:
        """ Constructor for ImageLevelView.

        Parameters:
            master: the master frame for this Canvas.
            dimensions: (#rows, #columns).
            size: (width in pixels, height in pixels).
        """
        super().__init__(master, dimensions, size, **kwargs)
        self._images = {}

    def draw(self, tiles: list[list[Tile]],
             items: dict[tuple[int, int], Item],
             player_pos: tuple[int, int]) -> None:
        """ Clears and redraws the entire level (maze and entities).

        Parameters:
            tiles: a list contains Tile instances in this level.
            items: a dictionary maps locations to the items currently at
                    those locations.
            player_pos: current position of player.
        """
        # Match the size of the image to the size of the individual cell
        cell_width = self._size[0] / self._dimensions[1]
        cell_height = self._size[1] / self._dimensions[0]

        # Create tile images
        rows, columns = self._dimensions
        for row in range(rows):
            for col in range(columns):
                tile = tiles[row][col]
                self._create_tk_image(TILE_IMAGES[tile.get_id()],
                                      int(cell_width), int(cell_height),
                                      (row, col), self._images)

        # Create item images
        for item_position, item in items.items():
            self._create_tk_image(ENTITY_IMAGES[item.get_id()],
                                  int(cell_width), int(cell_height),
                                  item_position, self._images)

        # Create player images
        self._create_tk_image(ENTITY_IMAGES[PLAYER], int(cell_width),
                              int(cell_height), player_pos, self._images)

    def _create_tk_image(self, image_name: str, width: int, height: int,
                         position: tuple[int, int], images_dict: dict) -> None:
        """ Translate image file into PhotoImage and create them in the
            specific position.

        Parameters:
            image_name: the name of the image we wanted to create.
            width: the width of the image after resize.
            height: the height of the image after resize.
            position: the (row, col) cell position.
            images_dict: a dictionary maps locations and image name to the
                        images currently at those locations.
        """
        image = Image.open("images/" + image_name)
        image = image.resize((width, height))
        image = ImageTk.PhotoImage(image)

        # If the PhotoImage doesn't been stored, it won't be drawn
        # because Python has a garbage collector mechanism
        images_dict[position + (image_name,)] = image
        self.create_image(self.get_midpoint(position), image=image)

    def clear(self) -> None:
        """ Clears all child widgets off the canvas."""
        super().clear()
        self._images = {}


class ControlsFrame(tk.Frame):
    """ Displays two buttons (restart and new game), as well as a timer
        of how long the current game has been going for.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame], restart: Callable,
                 new_game: Callable, open_shop: Callable, **kwargs) -> None:
        """ Creates a new ControlsFrame within master.

        Parameters:
            master: the master window of ControlsFrame.
            restart: the callback function implements restart the game.
            new_game: the callback function implements open new game.
            open_shop: the callback function implements open shop.
        """
        super().__init__(master, **kwargs)
        self._master = master
        self._restart = restart
        self._newgame = new_game
        self._shop = open_shop
        self._timer_label = None

    def clear(self) -> None:
        """ Clears all child widgets from this ControlsFrame."""
        for widget in self.winfo_children():
            widget.destroy()

    def draw_controls_frame(self) -> None:
        """ Draws any widgets within the ControlsFrame."""
        if TASK == 3:
            shop_btn = tk.Button(self, text="Shop", command=self._shop)
            shop_btn.pack(side=tk.LEFT, expand=tk.TRUE)

        restart_btn = tk.Button(self, text="Restart game",
                                command=self._restart)
        restart_btn.pack(side=tk.LEFT, expand=tk.TRUE)

        newgame_btn = tk.Button(self, text="New game", command=self._newgame)
        newgame_btn.pack(side=tk.LEFT, expand=tk.TRUE)

        self._timer_label = tk.Label(self, text="0m 0s", font=TEXT_FONT)
        self._timer_label.pack(side=tk.LEFT, expand=tk.TRUE)

    def set_timer_label(self, time_played: int) -> None:
        """ Modify the text of the timer label.

        Parameters:
            time_played: The seconds that have elapsed since the
                        current game egan.
        """
        self._timer_label.config(
            text=f"{time_played // 60}m {time_played % 60 - 1}s")


class FileMenu(tk.Menu):
    """ A file menu with options including: save game, load game,
        restart game ,quit.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame], restart: Callable,
                 save_game: Callable, load_game: Callable,
                 quit_game: Callable) -> None:
        """ Creates a new FileMenu within master.

        Parameters:
            master: the master window of FileMenu.
            restart: the callback function implements restart the game.
            save_game: the callback function implements save game.
            load_game: the callback function implements load game.
            quit_game: the callback function implements quit game.
        """
        tk.Menu.__init__(self, master)

        program_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label='File', menu=program_menu)
        program_menu.add_command(label='Save game', command=save_game)
        program_menu.add_command(label='Load game', command=load_game)
        program_menu.add_command(label='Restart game', command=restart)
        program_menu.add_command(label='Quit', command=quit_game)


class Candy(Food):
    """ Candy restores the player's hunger to 0 when applied, but also
        reduce their health by 2.
    """
    _id = CANDY

    def apply(self, player: Player) -> None:
        """ Changes player's hunger and health."""
        player.change_hunger(CANDY_HUNGER_AMOUNT)
        player.change_health(CANDY_HEALTH_AMOUNT)


class ShopView(tk.Frame):
    """ User can spend their collected coins to buy items."""

    def __init__(self, master: tk.Toplevel, **kwargs):
        """ Creates a new ShopFrame within master window.

        Parameters:
            master: the master window of ShopFrame.
        """
        super().__init__(master, **kwargs)
        self._master = master
        self._callback = None
        self._frame1 = None
        self._frame2 = None

    def set_shop_callback(self, callback: Callable):
        """ Sets the function to be called when an item is clicked in the
            shop view to be callback.

        Parameters:
            callback: a function apply the trying to buy specific item.
        """
        self._callback = callback

    def _draw_goods(self):
        """ Draw the image of each item accompany by their price."""
        apple_image = Image.open('images/apple.png')
        apple_image = apple_image.resize((SHOP_IMAGE_WIDTH, SHOP_IMAGE_HEIGHT))
        apple_image = ImageTk.PhotoImage(apple_image)
        self._apple = apple_image
        apple_label = tk.Label(self._frame1, text=ENTITY_PRICE["apple"],
                               font=TEXT_FONT, image=self._apple,
                               compound=tk.TOP)

        water_image = Image.open('images/water.png')
        water_image = water_image.resize((SHOP_IMAGE_WIDTH, SHOP_IMAGE_HEIGHT))
        water_image = ImageTk.PhotoImage(water_image)
        self._water = water_image
        water_label = tk.Label(self._frame1, text=ENTITY_PRICE["water"],
                               font=TEXT_FONT, image=self._water,
                               compound=tk.TOP)

        honey_image = Image.open('images/honey.png')
        honey_image = honey_image.resize((SHOP_IMAGE_WIDTH, SHOP_IMAGE_HEIGHT))
        honey_image = ImageTk.PhotoImage(honey_image)
        self._honey = honey_image
        honey_label = tk.Label(self._frame1, text=ENTITY_PRICE["honey"],
                               font=TEXT_FONT, image=self._honey,
                               compound=tk.TOP)

        potion_image = Image.open('images/potion.png')
        potion_image = potion_image.resize((SHOP_IMAGE_WIDTH,
                                            SHOP_IMAGE_HEIGHT))
        potion_image = ImageTk.PhotoImage(potion_image)
        self._potion = potion_image
        potion_label = tk.Label(self._frame2, text=ENTITY_PRICE["potion"],
                                font=TEXT_FONT, image=self._potion,
                                compound=tk.TOP)

        candy_image = Image.open('images/candy.png')
        candy_image = candy_image.resize((SHOP_IMAGE_WIDTH, SHOP_IMAGE_HEIGHT))
        candy_image = ImageTk.PhotoImage(candy_image)
        self._candy = candy_image
        candy_label = tk.Label(self._frame2, text=ENTITY_PRICE["candy"],
                               font=TEXT_FONT, image=self._candy,
                               compound=tk.TOP)

        apple_label.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.BOTH)
        apple_label.bind("<Button-1>", lambda x: self._callback("apple"))

        water_label.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.BOTH)
        water_label.bind("<Button-1>", lambda x: self._callback("water"))

        honey_label.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.BOTH)
        honey_label.bind("<Button-1>", lambda x: self._callback("honey"))

        potion_label.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.BOTH)
        potion_label.bind("<Button-1>", lambda x: self._callback("potion"))

        candy_label.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.BOTH)
        candy_label.bind("<Button-1>", lambda x: self._callback("candy"))

    def draw_shop(self):
        """ Draws any widgets within the ShopFrame."""
        shop_banner = tk.Label(self, text='Shop', font=BANNER_FONT,
                               bg=THEME_COLOUR)
        shop_banner.pack(side=tk.TOP, fill=tk.X)
        self._frame1 = tk.Frame(self)
        self._frame1.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)
        self._frame2 = tk.Frame(self)
        self._frame2.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

        SHOP_LIST["candy"] = (3, Candy((0, 0)))
        self._draw_goods()

        done_btn = tk.Button(self, text='Done', command=self._terminate)
        done_btn.pack(side=tk.TOP)

    def _terminate(self):
        """ Close the shop when "Done" button clicked."""
        self._master.destroy()


def play_game(root: tk.Tk):
    """ Executes the entire game until a win or loss occurs.

    Parameters:
        root: the root window of game.
    """
    controller = GraphicalMazeRunner(GAME_FILE, root)
    controller.play()


def main():
    """ Entry-point to gameplay."""
    root = tk.Tk()
    play_game(root)
    root.mainloop()


if __name__ == '__main__':
    main()
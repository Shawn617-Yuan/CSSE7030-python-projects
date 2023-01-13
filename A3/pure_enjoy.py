import sys
import tkinter as tk
from tkinter import messagebox
from typing import Union, Callable
from PIL import ImageTk, Image

from a3_support import AbstractGrid
from constants import GAME_FILE, TASK
from a2_solution import *


# Write your classes here
class LevelView(AbstractGrid):
    def __init__(self, master: Union[tk.Tk, tk.Frame], dimension: tuple[int, int], size: tuple[int, int], **kwargs):
        super().__init__(master, dimension, size, **kwargs)

    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], Item], player_pos: tuple[int, int]) -> None:
        """" Clears and redraws the entire level (maze and entities)"""
        rows, columns = self._dimensions  # 可能可以改一下
        for row in range(rows):
            for col in range(columns):
                tile_color = TILE_COLOURS[tiles[row][col].get_id()]
                self.create_rectangle(self.get_bbox((row, col)), fill=tile_color)

        for position, item in items.items():
            entity_color = ENTITY_COLOURS[item.get_id()]
            self.create_oval(self.get_bbox(position), fill=entity_color)
            self.annotate_position(position, item.get_id())

        self.create_oval(self.get_bbox(player_pos), fill=ENTITY_COLOURS[PLAYER])
        self.annotate_position(player_pos, PLAYER)


class StatsView(AbstractGrid):
    def __init__(self, master: Union[tk.Tk, tk.Frame], width: int, **kwargs) -> None:
        super().__init__(master, (2, 4), (width, STATS_HEIGHT), **kwargs)
        self.config(bg=THEME_COLOUR)

    def draw_stats(self, player_stats: tuple[int, int, int]) -> None:
        self.annotate_position((0, 0), "HP")
        self.annotate_position((0, 1), "Hunger")
        self.annotate_position((0, 2), "Thirst")

        self.annotate_position((1, 0), str(player_stats[0]))
        self.annotate_position((1, 1), str(player_stats[1]))
        self.annotate_position((1, 2), str(player_stats[2]))

    def draw_coins(self, num_coins: int) -> None:
        self.annotate_position((0, 3), "Coins")
        self.annotate_position((1, 3), str(num_coins))


class InventoryView(tk.Frame):
    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs):
        super().__init__(master, **kwargs)
        # self.config(width=INVENTORY_WIDTH, height=MAZE_HEIGHT)
        # self.pack_propagate(0)
        self._label_set = []
        # 这只是一个view结构，不会实现函数功能
        self._callback = None

    def set_click_callback(self, callback: Callable[[str], None]) -> None:  # 有问题，不知道callback是什么东西
        # 先传到UI再传到controller，这里是把callback存起来
        self._callback = callback

    def clear(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def _draw_item(self, name: str, num: int, colour: str) -> None:
        inventory_item = tk.Label(self, text=f"{name}: {num}", bg=colour, font=TEXT_FONT)
        inventory_item.pack(fill=tk.X)
        if self._callback:
            inventory_item.bind('<Button-1>', lambda e: self._callback(name))

    def draw_inventory(self, inventory: Inventory) -> None:
        heading = tk.Label(self, text="Inventory", font=HEADING_FONT)
        heading.pack(fill=tk.BOTH)
        for item_name, items in inventory.get_items().items():
            if item_name != Coin.__name__:
                self._draw_item(item_name, len(items), ENTITY_COLOURS[items[0].get_id()])


class GraphicalInterface(UserInterface):
    def __init__(self, master: tk.Tk) -> None:
        self._master = master
        self._master.title("MazeRunner")
        self._time_played = 0

        banner = tk.Label(self._master, text='MazeRunner', font=BANNER_FONT, bg=THEME_COLOUR)
        banner.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

    def _calculagraph(self):
        self._time_played += 1
        self._control_frame._timer_label.config(text=f"{self._time_played // 60}m {self._time_played % 60}s")
        return self._master.after(1000, self._calculagraph)

    def create_interface(self, dimensions: tuple[int, int], restart, new_game, save_game, load_game) -> None:
        ui_frame = tk.Frame(self._master)
        ui_frame.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

        # todo:只有在TASK等于1时才是levelview，否则时imagelevelview
        if TASK == 1:
            self._level_view = LevelView(ui_frame, dimensions, (MAZE_WIDTH, MAZE_HEIGHT))
            self._level_view.pack(side=tk.LEFT)
        elif TASK == 2:
            self._image_level_view = ImageLevelView(ui_frame, dimensions, (MAZE_WIDTH, MAZE_HEIGHT))
            self._image_level_view.pack(side=tk.LEFT)
        else:
            return None

        self._inventory_view = InventoryView(ui_frame)
        self._inventory_view.pack(side=tk.LEFT, fill=tk.BOTH)

        self._stats_view = StatsView(self._master, MAZE_WIDTH + INVENTORY_WIDTH)
        self._stats_view.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

        self._menu = MenuBar(self._master, restart, new_game, save_game, load_game)
        self._master.config(menu=self._menu)

        # todo:这里还要有最下面的界面，应该可以通过直接实例化一个类对象实现
        self._control_frame = ControlsFrame(self._master)
        self._control_frame.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)
        self._calculagraph()  # 这里还没有创建interface

        # todo:举个例子，这应该是shop_view
        # self._level_view.bind("<Button-1>", lambda e: self.button_clicked(e))

    def button_clicked(self, e):  # todo:先不管，如果要hardcore位置的话的shop
        x = e.x
        y = e.y
        row, column = x // (MAZE_WIDTH / self._level_view._dimensions[1]), y // (MAZE_HEIGHT / self._level_view._dimensions[0])
        # tiles[row][column]这就知道是点了哪个物品，依次对他们进行判断就好。tiles是shop里物品的集合，可以用create_image
        if row < 30 and column < 30:
            print('这是第一张图片')

    def clear_all(self) -> None:
        if TASK == 1:
            self._level_view.clear()
        elif TASK == 2:
            self._image_level_view.clear()
        self._inventory_view.clear()
        self._stats_view.clear()

    def set_maze_dimensions(self, dimensions: tuple[int, int]) -> None:
        if TASK == 1:
            self._level_view.set_dimensions(dimensions)
        elif TASK == 2:
            self._image_level_view.set_dimensions(dimensions)

    def bind_keypress(self, command: Callable[[tk.Event], None]) -> None:
        self._master.bind('<Key>', command)

    def set_inventory_callback(self, callback: Callable[[str], None]) -> None:
        self._inventory_view.set_click_callback(callback)

    def draw_inventory(self, inventory: Inventory) -> None:
        # todo: 可能要修改，因为所有的都在下面的draw里了（也不一定）
        self._inventory_view.draw_inventory(inventory)

    def draw(self, maze: Maze, items: dict[tuple[int, int], Item], player_position: tuple[int, int], inventory: Inventory, player_stats: tuple[int, int, int]) -> None:
        self.clear_all()
        self._draw_level(maze, items, player_position)
        self._draw_inventory(inventory)
        self._draw_player_stats(player_stats)
        self._draw_function_frame()  # todo:最下面的frame还没画

    def _draw_inventory(self, inventory: 'Inventory') -> None:
        # 在之前的基础上还要draw coins
        self.draw_inventory(inventory)
        self._stats_view.draw_coins(len(inventory.get_items().get(Coin.__name__, [])))

    def _draw_level(self, maze: 'Maze', items: dict[tuple[int, int], 'Item'], player_position: tuple[int, int]) -> None:
        if TASK == 1:
            self._level_view.draw(maze.get_tiles(), items, player_position)
        elif TASK == 2:
            self._image_level_view.draw(maze.get_tiles(), items, player_position)

    def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
        self._stats_view.draw_stats(player_stats)

    def _draw_function_frame(self):  # 这里放重新画timer的东西
        pass


# 这是controller，是model和view之间的桥梁，用来发出指令给model，然后更改view
class GraphicalMazeRunner(MazeRunner):
    def __init__(self, game_file: str, root: tk.Tk) -> None:
        self._root = root
        self._game_file = game_file
        # game model class，所有的数据都从这里来
        self._model = Model(game_file)
        # game view class
        self._gui = GraphicalInterface(self._root)

    def _draw(self):
        # 每次都会调用这个draw，根据当前游戏状态
        level = self._model.get_level()  # 拿level的数据
        player = self._model.get_player()

        # 根据数据来画UI
        self._gui.draw(level.get_maze(), level.get_items(), player.get_position(), player.get_inventory(), self._model.get_player_stats())

    def _handle_keypress(self, e: tk.Event) -> None:
        if e.char in (UP, DOWN, LEFT, RIGHT):
            print(e.char, "pressed")
            self._model.move_player(MOVE_DELTAS.get(e.char))
        # 这里加上如果赢了/输了怎么办
        if self._model.has_won():
            messagebox.showinfo(title='Test', message=WIN_MESSAGE)  # 用message box?
            self._root.destroy()
            return None
        if self._model.has_lost():
            messagebox.showinfo(title='Test', message=LOSS_MESSAGE)

        if self._model.did_level_up():
            self._gui.set_maze_dimensions(self._model.get_level().get_dimensions())

        self._draw()

    def _apply_item(self, item_name: str) -> None:
        item = self._model.get_player().get_inventory().remove_item(item_name)
        if item is not None:
            item.apply(self._model.get_player())

        self._draw()

    def play(self) -> None:  # set up the game
        # 创建interface
        self._gui.create_interface(self._model.get_level().get_dimensions(), self._restart, self._new_game, self._save_game, self._load_game)

        # w, a, s, d
        self._gui.bind_keypress(self._handle_keypress)
        self._gui.set_inventory_callback(self._apply_item)

        # todo:要么在这里加上一个self._buy_item
        # self._gui.set_shop_callback(self._but_item)
        self._draw()

    def _restart(self):  # 真正的对当前游戏进行restart
        self._model = Model(self._game_file)
        self._gui.set_maze_dimensions(self._model.get_current_maze().get_dimensions())
        self._draw()  # 没有反应就重新draw一遍，因为可能是还没有刷新的问题

    def _check_valid_path(self):
        filename = self._entry.get()
        try:  # todo:这里可以自己写一个函数，然后直接用
            self._model = Model(filename)  # 找到model并设置dimension
            self._gui.set_maze_dimensions(self._model.get_current_maze().get_dimensions())
            self._window.destroy()
            self._draw()
        except FileNotFoundError:
            print('file not found')  # todo:应该使用message box

    def _new_game(self):
        self._window = tk.Toplevel(self._root)
        # 先message box然后再叫用户输入路径
        self._entry = tk.Entry(self._window)
        self._entry.pack()
        tk.Button(self._window, text="Submit", command=self._check_valid_path).pack()
        self._window.mainloop()

    def _save_game(self):
        # 所有的信息都在model里，我们要保存所有需要的信息
        level = self._model.get_level()
        hp, hunger, thirst = self._model.get_player_stats()

        # todo:用entry去问玩家要保存在哪个位置，还需要存时间，coins，文件名，dimension(?)
        with open('game_archive.txt', 'w') as file:
            file.write(str(level)[7:])
            file.write(f"\nhp: {hp}\n")
            file.write(f"hunger: {hunger}\n")
            file.write(f"thirst: {thirst}\n")
            file.write("这里要存用户输入的路径")

    def _load_game(self):
        with open('game_archive.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('Items'):
                    pass  # todo:要自己一个一个去试


class ImageLevelView(LevelView):
    def __init__(self, master: Union[tk.Tk, tk.Frame], dimensions: tuple[int, int], size, **kwargs):
        super().__init__(master, dimensions, size, **kwargs)

        self._images = {}  # 存的永远是当前位置的图片，如果使list那么只会越来越多
        # self._size = size

    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], Item], player_pos: tuple[int, int]) -> None:
        rows, columns = self._dimensions

        # 使图片的大小和cell大小匹配，width/num_col
        cell_width = self._size[0] / self._dimensions[1]
        cell_height = self._size[1] / self._dimensions[0]

        for row in range(rows):
            for col in range(columns):
                tile = tiles[row][col]

                # todo:这里可以自己写一个函数简化这个步骤，一定要是private的
                tile_image = Image.open("images/" + TILE_IMAGES[tile.get_id()])
                tile_image = tile_image.resize((int(cell_width), int(cell_height)))  # Image.ANTIALIAS这个已经被弃用了
                tile_image = ImageTk.PhotoImage(tile_image)  # 转换为tk能接受的类型，放到photo image里
                self._images[(row, col)] = tile_image  # 如果不把tk image存起来，那么不会画出来，因为python有垃圾回收功能
                self.create_image(self.get_midpoint((row, col)), image=tile_image)

        for position, item in items.items():
            item_image = Image.open("images/" + ENTITY_IMAGES[item.get_id()])
            item_image = item_image.resize((int(cell_width), int(cell_height)))
            item_image = ImageTk.PhotoImage(item_image)  # used everywhere Tkinter expects an image object
            self._images[position + (item,)] = item_image
            self.create_image(self.get_midpoint(position), image=item_image)

        player_image = Image.open("images/" + ENTITY_IMAGES[PLAYER])
        player_image = player_image.resize((int(cell_width), int(cell_height)))
        player_image = ImageTk.PhotoImage(player_image)
        self._images[player_pos + (PLAYER,)] = player_image
        self.create_image(self.get_midpoint(player_pos), image=player_image)

        print(sys.getsizeof(self._images))  # 这里不能用sys，得换成其他的

    def clear(self):
        super().clear()
        self._images = {}


class ControlsFrame(tk.Frame):
    def __init__(self, master: Union[tk.Tk, tk.Frame], restart, new_game, **kwargs):
        super().__init__(master, **kwargs)
        self._master = master
        self._restart = restart
        self._newgame = new_game

    def clear(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def draw_controls_frame(self):
        restart_btn = tk.Button(self, text="Restart game", command=self._restart)
        restart_btn.pack(side=tk.LEFT, expand=tk.TRUE)
        newgame_btn = tk.Button(self, text="New game", command=self._newgame)
        newgame_btn.pack(side=tk.LEFT, expand=tk.TRUE)
        self._timer_label = tk.Label(self, text="0m 0s")  # 这里好像有重复的代码，不清楚
        self._timer_label.pack(side=tk.LEFT, expand=tk.TRUE)


class MenuBar(tk.Menu):
    def __init__(self, master, restart, new_game, save_game, load_game):
        tk.Menu.__init__(self, master)

        program_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label='File', underline=0, menu=program_menu)
        program_menu.add_command(label='New game', underline=1, command=new_game)  # 这个可以之后用，放在controller里
        program_menu.add_command(label='Save game', underline=1, command=save_game)
        program_menu.add_command(label='Load game', underline=1, command=load_game)
        program_menu.add_command(label='Restart game', underline=1, command=restart)
        program_menu.add_command(label='Quit', underline=1, command=self._quit)


def play_game(root: tk.Tk):
    controller = GraphicalMazeRunner(GAME_FILE, root)
    controller.play()
    root.mainloop()


def main():
    # Write your main function code here
    root = tk.Tk()
    play_game(root)


if __name__ == '__main__':
    main()

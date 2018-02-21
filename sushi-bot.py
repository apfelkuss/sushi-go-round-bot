import time
import numpy as np
from PIL import ImageOps
from pymouse import PyMouse
import pyscreenshot as ImageGrab


class GameControls:

    # top left corner of the game
    SCREEN_PADDING = (466, 307)
    GAME_WIDTH = 640
    GAME_HIGHT = 480

    def take_screenshot(self, x_pos, y_pos, width, height):
        area = (self.SCREEN_PADDING[0]+x_pos,
                self.SCREEN_PADDING[1]+y_pos,
                self.SCREEN_PADDING[0]+x_pos+width,
                self.SCREEN_PADDING[1]+y_pos+height)
        scr = ImageGrab.grab(area)
        return scr

    def click(self, xy_pos, n=1, interval=0.1):
        m = PyMouse()
        for i in range(n):
            m.click(self.SCREEN_PADDING[0]+xy_pos[0],
                    self.SCREEN_PADDING[1]+xy_pos[1])
            time.sleep(interval)


class Game(GameControls):

    lvl = 1
    game_over = False
    # buttons location
    PLAY_BTN = (320, 205)
    CONTINUE_BTN = (320, 390)
    SKIP_BTN = (580, 460)
    # level results pop-up window
    LVL_RESULTS_POS = (135, 200)
    LVL_RESULTS_RGB = {"win": (171, 245, 76), "failed": (255, 203, 45)}

    def start_game(self):
        self.click(self.PLAY_BTN)
        self.click(self.CONTINUE_BTN)
        self.click(self.SKIP_BTN)

    def start_lvl(self):
        k = Kitchen()
        k.reset()
        self.click(self.CONTINUE_BTN)

    def check_lvl_status(self):
        scr = self.take_screenshot(0, 0, self.GAME_WIDTH, self.GAME_HIGHT)
        rgb = scr.getpixel(self.LVL_RESULTS_POS)
        if rgb == self.LVL_RESULTS_RGB["win"]:
            self.click(self.CONTINUE_BTN)
            self.start_lvl()
            self.lvl += 1
        elif rgb == self.LVL_RESULTS_RGB["failed"]:
            self.game_over = True

    def play(self):
        seats = {1: Customer(26, 61, 6.5), 2: Customer(127, 61, 9),
                 3: Customer(228, 61, 11.5), 4: Customer(329, 61, 14),
                 5: Customer(430, 61, 16.5), 6: Customer(531, 61, 19)}
        self.start_game()
        self.start_lvl()
        while not self.game_over and self.lvl <= 7:
            for s in seats.values():
                s.clean()
                s.take_order()
            self.check_lvl_status()


class Kitchen(GameControls):

    # ingredients
    ingr_amount = {"fish egg": 10, "nori": 10, "rice": 10, "salmon": 5,
                   "shrimp": 5, "unagi": 5}
    INGR_POS = {"fish egg": (91, 388), "nori": (36, 388), "rice": (91, 333),
                "salmon": (36, 443), "shrimp": (36, 333), "unagi": (91, 443)}

    # bamboo mat
    BAMBOO_MAT_POS = (131, 310)
    BAMBOO_MAT_WIDTH = 143
    BAMBOO_MAT_HEIGHT = 152
    BAMBOO_MAT_CENTER = (BAMBOO_MAT_POS[0] + BAMBOO_MAT_WIDTH//2,
                         BAMBOO_MAT_POS[1] + BAMBOO_MAT_HEIGHT//2)
    BAMBOO_MAT_EMPTY_CODE = 23096

    # sushi
    RECIPE = {"california roll": {"rice": 1, "nori": 1, "fish egg": 1},
              "combo": {"rice": 2, "nori": 1, "fish egg": 1, "salmon": 1,
                        "shrimp": 1, "unagi": 1},
              "dragon roll": {"rice": 2, "nori": 1, "fish egg": 1, "unagi": 2},
              "gunkan maki": {"rice": 1, "nori": 1, "fish egg": 2},
              "onigiri": {"rice": 2, "nori": 1},
              "salmon roll": {"rice": 1, "nori": 1, "salmon": 2},
              "shrimp sushi": {"rice": 1, "nori": 1, "shrimp": 2},
              "unagi roll": {"rice": 1, "nori": 1, "unagi": 2}}

    def make_sushi(self, sushi):
        if self.enough_ingredients(sushi):
            # waits if there's sushi still on the mat
            while not self.bamboo_mat_is_empty():
                time.sleep(0.5)
            for ingredient, amount in self.RECIPE[sushi].items():
                self.click(self.INGR_POS[ingredient], n=amount)
                self.ingr_amount[ingredient] -= amount
            self.click(self.BAMBOO_MAT_CENTER)
            self.check_supply()
            return "Done"
        else:
            self.check_supply()

    def check_supply(self):
        for ingredient, amount in self.ingr_amount.items():
            if amount < 2:
                shop = Shop()
                shop.buy(ingredient)

    def enough_ingredients(self, sushi):
        for ingredient, amount in self.RECIPE[sushi].items():
            if amount > self.ingr_amount[ingredient]:
                return False
        return True

    def bamboo_mat_is_empty(self):
        scr = self.take_screenshot(self.BAMBOO_MAT_POS[0], self.BAMBOO_MAT_POS[1],
                                   self.BAMBOO_MAT_WIDTH, self.BAMBOO_MAT_HEIGHT)
        scr = ImageOps.grayscale(scr)
        scr = np.array(scr.getcolors())
        scr = scr.sum()
        if scr == self.BAMBOO_MAT_EMPTY_CODE:
            return True
        else:
            return False

    def reset(self):
        self.ingr_amount["fish egg"] = 10
        self.ingr_amount["nori"] = 10
        self.ingr_amount["rice"] = 10
        self.ingr_amount["salmon"] = 5
        self.ingr_amount["shrimp"] = 5
        self.ingr_amount["unagi"] = 5


class Shop(GameControls):

    last_time_bought = {"fish egg": 0, "nori": 0, "rice": 0, "salmon": 0,
                        "shrimp": 0, "unagi": 0}
    delivery_pending = {"fish egg": False, "nori": False, "rice": False,
                        "salmon": False, "shrimp": False, "unagi": False}

    # shop menu buttons location
    PHONE = (580, 365)
    TOPPING_MENU = (543, 272)
    RICE_MENU = (543, 293)
    DELIVERY_MENU = (492, 295)
    DELIVERY_TIME = 6
    EXIT_MENU = (590, 335)
    INGR = {"fish egg": (550, 275), "nori": (465, 270), "rice": (520, 270),
            "salmon": (465, 325), "shrimp": (465, 210), "unagi": (550, 215)}
    BUYABILITY_RGB = [(218, 246, 255), (237, 166, 171)]
    INGR_IS_RARE = {"fish egg": False, "nori": False, "rice": False,
                    "salmon": True, "shrimp": True, "unagi": True}
    INGR_MAX_AMOUNT = {"rare": 8, "common": 15}

    def buy(self, ingredient):
        # Checks if there was a recent purchase and adds the ingredients
        # if a certain amount of time has passed.
        if self.delivery_pending[ingredient] is True:
            if time.time() - self.last_time_bought[ingredient] > self.DELIVERY_TIME:
                self.add_pending(ingredient)
        # If there was no recent purchase, buys the ingredient
        else:
            self.click(self.PHONE)
            if ingredient == "rice":
                self.click(self.RICE_MENU)
            else:
                self.click(self.TOPPING_MENU)
            if not self.is_buyable(ingredient):
                self.click(self.EXIT_MENU)
                return
            self.click(self.INGR[ingredient])
            self.click(self.DELIVERY_MENU)
            self.last_time_bought[ingredient] = time.time()
            self.delivery_pending[ingredient] = True

    def is_buyable(self, ingredient):
        scr = self.take_screenshot(0, 0, self.GAME_WIDTH, self.GAME_HIGHT)
        if scr.getpixel(self.INGR[ingredient]) in self.BUYABILITY_RGB:
            return True
        return False

    def add_pending(self, ingredient):
        self.delivery_pending[ingredient] = False
        if self.INGR_IS_RARE[ingredient]:
            Kitchen.ingr_amount[ingredient] += 5
            # ensures ingredient amount doesn't exceed in-game maximum
            if Kitchen.ingr_amount[ingredient] > self.INGR_MAX_AMOUNT["rare"]:
                Kitchen.ingr_amount[ingredient] = self.INGR_MAX_AMOUNT["rare"]
        else:
            Kitchen.ingr_amount[ingredient] += 10
            # ensures ingredient amount doesn't exceed in-game maximum
            if Kitchen.ingr_amount[ingredient] > self.INGR_MAX_AMOUNT["common"]:
                Kitchen.ingr_amount[ingredient] = self.INGR_MAX_AMOUNT["common"]


class Customer(GameControls):

    WIDTH = 61
    HEIGHT = 14
    SUSHI_ID = {1792: "salmon roll", 1817: "onigiri", 1824: "gunkan maki",
                2040: "unagi roll", 2239: "shrimp sushi",
                2454: "dragon roll", 2461: "california roll", 3730: "combo"}

    def __init__(self, x_pos, y_pos, time_to_serve):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.plate = (x_pos+55, y_pos+145)
        self.timer = 0
        self.time_to_serve = time_to_serve

    def take_order(self):
        if self.is_new():
            order = self.take_screenshot(self.x_pos, self.y_pos, self.WIDTH,
                                         self.HEIGHT)
            order = ImageOps.grayscale(order)
            order = np.array(order.getcolors())
            order = order.sum()
            sushi = self.get_sushi_name(order)
            if sushi:
                kitchen = Kitchen()
                order = kitchen.make_sushi(sushi)
                if order == "Done":
                    self.timer = time.time()
            self.last_order = sushi

    def is_new(self):
        if time.time() - self.timer > self.time_to_serve:
            return True
        return False

    def get_sushi_name(self, order):
        if order in self.SUSHI_ID:
            return self.SUSHI_ID[order]

    def clean(self):
        self.click(self.plate)


if __name__ == "__main__":
    game = Game()
    game.play()

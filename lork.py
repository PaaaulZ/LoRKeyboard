import pywinauto
import requests
import json
import logging
import os
import numpy as np
import win32gui
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from time import sleep
from keycap import CaptureKeys
from PIL import Image, ImageGrab

API_HOST = 'http://localhost:21337'
CARD_POSITION_API_URL = 'http://localhost:21337/positional-rectangles'

toplist,winlist = [], []
SCREEN_WIDTH, SCREEN_HEIGHT = 0, 0
ALLIED_NEXUS_POSITION = (0, 0)
ENEMY_NEXUS_POSITION = (0, 0)
NEXUS_SIZE = (0, 0)

class Card:
    real_x = -1
    real_y = -1
    lor_code = 'XXXXXXX'
    click_x = -1
    click_y = -1
    in_hand = True
    width = -1
    height = -1
    original_x = -1
    original_y = -1
    is_vertical = False
    is_allied = False

    def __init__(self, real_x, real_y, card_width, card_height, lor_code, original_x, original_y, is_allied):
        self.real_x = real_x
        self.real_y = real_y
        self.lor_code = lor_code
        self.click_x = round(real_x + (card_width / 2))
        self.click_y = real_y + 50 # TODO: Change this fixed number with some sort of calculation to click the card center
        self.width = card_width
        self.height = card_height
        self.original_x = original_x
        self.original_y = original_y
        self.is_vertical = is_card_vertical(self)
        self.is_allied = is_allied

        
# Setup logging
fh = logging.FileHandler('lork.log')
log = logging.getLogger('LoRKeyboard')
logging.basicConfig(format='%(asctime)s - [%(levelname)s]: %(message)s')
log.setLevel(logging.DEBUG)
log.addHandler(fh)


def main():
    rectangles = get_rectangles_json()
    all_cards = get_card_positions(rectangles)
    draw_rectangles(all_cards)
    return

def get_rectangles_json():

    log.info("Getting data from game client API")

    try:
        r = requests.get(CARD_POSITION_API_URL)
    except:
        # Game closed / API disabled?
        log.critical(f"Unable to connect to {CARD_POSITION_API_URL}. Game needs to be open and API enabled in the settings")
        exit()

    if r.status_code != 200:
        log.error(f"{r.status_code} while getting cards position")

    result = json.loads(r.text) 
    # Fetch screen size from API 

    global SCREEN_WIDTH
    global SCREEN_HEIGHT

    SCREEN_WIDTH = result['Screen']['ScreenWidth']
    SCREEN_HEIGHT = result['Screen']['ScreenHeight']

    rectangles = result['Rectangles']

    return rectangles

def get_card_positions(rectangles):

    positions_hand = []
    positions_table = []
    positions_attacking_blocking = []

    positions_hand_enemy = []
    positions_table_enemy = []
    positions_attacking_blocking_enemy = []

    allied_cards, enemy_cards = [], []

    global ALLIED_NEXUS_POSITION
    global ENEMY_NEXUS_POSITION
    global NEXUS_SIZE
    global SCREEN_HEIGHT
    global SCREEN_WIDTH

    local_player = True

    for i in range(2):
        # Run this 2 times. 0 for ally and 1 for enemy
        for rectangle in rectangles:
            real_y_TMP = SCREEN_HEIGHT - rectangle['TopLeftY']
            real_x_TMP = rectangle['TopLeftX']

            if rectangle['CardCode'] == 'face' and i == 0:
                if rectangle['LocalPlayer'] == True:
                    # Allied nexus
                    ALLIED_NEXUS_POSITION = (rectangle['TopLeftX'], SCREEN_HEIGHT - rectangle['TopLeftY'])
                    NEXUS_SIZE = (rectangle['Width'], rectangle['Height'])
                    # 1 nexus size is enough
                    log.info("Got ALLIED nexus size and position")
                else:
                    # enemy nexus
                    ENEMY_NEXUS_POSITION = (rectangle['TopLeftX'], SCREEN_HEIGHT - rectangle['TopLeftY'])         
                    log.info("Got ENEMY nexus size and position")

            if rectangle['CardCode'] != 'face':
                cardTMP = Card(real_x_TMP, real_y_TMP, rectangle['Width'], rectangle['Height'], rectangle['CardCode'], rectangle['TopLeftX'], rectangle['TopLeftY'], rectangle['LocalPlayer'])
                if rectangle['LocalPlayer'] and i == 0:
                    if cardTMP.is_vertical:
                        if is_card_in_hand(cardTMP):
                            positions_hand.append(cardTMP)
                        else:
                            positions_table.append(cardTMP)
                    else:
                        # If card is horizontal means that is attacking or blocking
                        positions_attacking_blocking.append(cardTMP)
                    log.info("Got ALLIED cards")
                elif not rectangle['LocalPlayer'] and i == 1:
                    if cardTMP.is_vertical:
                        if is_card_in_hand(cardTMP):
                            positions_hand_enemy.append(cardTMP)
                        else:
                            positions_table_enemy.append(cardTMP)
                    else:
                        # If card is horizontal means that is attacking or blocking
                        positions_attacking_blocking_enemy.append(cardTMP)
                    log.info("Got ENEMY cards")

        # Sort cards from left to right (to generate the indexes that make sense)
        positions_hand.sort(key=lambda x: x.real_x, reverse=False)
        positions_table.sort(key=lambda x: x.real_x, reverse=False)
        positions_attacking_blocking.sort(key=lambda x: x.real_x, reverse=False)

        positions_hand_enemy.sort(key=lambda x: x.real_x, reverse=False)
        positions_table_enemy.sort(key=lambda x: x.real_x, reverse=False)
        positions_attacking_blocking_enemy.sort(key=lambda x: x.real_x, reverse=False)

        if local_player:
            # Store ally cards
            allied_cards.append(positions_hand)
            allied_cards.append(positions_table)
            allied_cards.append(positions_attacking_blocking)
        else:
            # Store enemy cards
            enemy_cards.append(positions_hand_enemy)
            enemy_cards.append(positions_table_enemy)
            enemy_cards.append(positions_attacking_blocking_enemy)

        local_player = False

    return [allied_cards, enemy_cards]
    
    # print("HAND: ")
    # print_positions(positions_hand)
    # print("TABLE: ")
    # print_positions(positions_table)
    # print("ATTACKING/BLOCKING: ")
    # print_positions(positions_attacking_blocking)
    # print("----------------------------------------------------")
    
    # ck = CaptureKeys()
    # ck.start_listener()
    
    # if ck.last_pressed_key == '':
    #     return

    # requested_card = int(ck.last_pressed_key) - 1

    # if ck.hand_or_table:
    #     positions = positions_table
    # else:
    #     positions = positions_hand

    # if requested_card > len(positions):
    #     log.error(f"Card number {int(requested_card)} is not valid in this state.")
    # else:
    #     if ck.move_or_click:
    #         click_card(positions, positions[requested_card].lor_code)
    #     else:
    #         move_card(positions, positions[requested_card].lor_code)


    # TODO: Fix blocking with more than one card
    # return


def print_positions(positions):

    for position in positions:
        print(f"{position.click_x} - {position.click_y} => {position.lor_code} [{position.in_hand}]")

    return

def move_card(positions, lor_code):

    for position in positions:
        if position.lor_code == lor_code:
            pywinauto.mouse.press(button='left', coords=(position.click_x, position.click_y))
            pywinauto.mouse.release(button='left', coords=(int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2)))
            # HACK: Move mouse "out of the screen" so it doesn't hover on cards
            pywinauto.mouse.move(coords=(1,1))

    return

def click_card(positions, lor_code):

    for position in positions:
        if position.lor_code == lor_code:
            pywinauto.mouse.click(button='left', coords=(position.click_x, position.click_y))
    # HACK: Move mouse "out of the screen" so it doesn't hover on cards
    pywinauto.mouse.move(coords=(1,1))

    return

def is_card_in_hand(card):
    # TODO: Calculate this
    return card.real_y >= (SCREEN_HEIGHT - 100)

def is_card_vertical(card):
    #print(f"CARD {card.lor_code} is vertical: {card.height > card.width}")
    return card.height > card.width

def get_screenshot():

    win32gui.EnumWindows(enum_cb, toplist)
    lor = [(hwnd, title) for hwnd, title in winlist if 'legends of runeterra' in title.lower()]
    lor = lor[0]
    hwnd = lor[0]

    win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    # Sleep 1 second to allow LoR to get in focus
    sleep(1)
    img = ImageGrab.grab(bbox)
    try:
        os.remove('screen.png')
    except Exception:
        pass
    img.save("screen.png")

def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

def draw_rectangles(all_cards):

    global ALLIED_NEXUS_POSITION
    global ENEMY_NEXUS_POSITION
    global NEXUS_SIZE

    index = 1

    get_screenshot()
    im = np.array(Image.open('screen.png'), dtype=np.uint8)

    ax = plt.subplots(1)[1]
    ax.imshow(im)

    keys = ['', 'CTRL + ', 'ALT + ']

    log.info("Drawing rectangles around the cards")

    for i in range(2):
        # Ally / enemy loop
        current_cards = all_cards[i]
        for i in range(3):
            # Hand, board, attacking/blocking loop
            cards = current_cards[i]
            for card in cards:
                # Single card loop
                rect_point = (card.original_x , SCREEN_HEIGHT - card.original_y) 

                text = keys[i] + str(index)

                if not card.is_allied:
                    text = 'SHIFT + ' + str(index)
                    color = 'r'
                else:
                    color = 'b'
                    
                log.debug(f"Drawing {card.lor_code} with index {text}")

                # Draw rectangle
                rect = patches.Rectangle(rect_point, card.width , card.height , linewidth=1, edgecolor=color, facecolor='none', label=text)
                # Write index near the rectangle
                plt.annotate(text, rect_point)
                index += 1

                ax.add_patch(rect)

            # Reset for next state
            index = 1

    # Draw allied nexus
    log.debug("Drawing allied nexus")
    rect = patches.Rectangle(ALLIED_NEXUS_POSITION, NEXUS_SIZE[0] , NEXUS_SIZE[1] , linewidth=1, edgecolor='b', facecolor='none', label="0")
    plt.annotate("0", ALLIED_NEXUS_POSITION)
    ax.add_patch(rect)

    # Draw enemy nexus
    log.debug("Drawing enemy nexus")
    rect = patches.Rectangle(ENEMY_NEXUS_POSITION, NEXUS_SIZE[0] , NEXUS_SIZE[1] , linewidth=1, edgecolor='r', facecolor='none', label="9")
    plt.annotate("9", ENEMY_NEXUS_POSITION)
    ax.add_patch(rect)

    plt.show()
    
    return

if __name__ == '__main__':
    main()

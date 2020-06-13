import pywinauto
import requests
import json
import logging
from keycap import CaptureKeys


class Card:
    real_x = -1
    real_y = -1
    lor_code = 'XXXXXXX'
    click_x = -1
    click_y = -1
    in_hand = True
    width = -1
    height = -1

    def __init__(self, real_x, real_y, card_width, card_height, lor_code):
        self.real_x = real_x
        self.real_y = real_y
        self.lor_code = lor_code
        self.click_x = round(real_x + (card_width / 2))
        self.click_y = real_y + 50 # TODO: Change this fixed number with some sort of calculation
        self.width = card_width
        self.height = card_height

API_HOST = 'http://localhost:21337'
CARD_POSITION_API_URL = 'http://localhost:21337/positional-rectangles'

# Setup logging
fh = logging.FileHandler('lork.log')
log = logging.getLogger('LoRKeyboard')
logging.basicConfig(format='%(asctime)s - [%(levelname)s]: %(message)s')
log.setLevel(logging.DEBUG)
log.addHandler(fh)

def main():
    while 1:
        get_card_positions()
    return

def get_card_positions():

    positions_hand = []
    positions_table = []
    positions_attacking_blocking = []

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
    # TODO: Cache it

    screen = result['Screen']
    SCREEN_WIDTH = screen['ScreenWidth']
    SCREEN_HEIGHT = screen['ScreenHeight']

    rectangles = result['Rectangles']

    # ONLY LOCAL PLAYER FOR NOW 

    for rectangle in rectangles:
        real_y_TMP = SCREEN_HEIGHT - rectangle['TopLeftY']
        real_x_TMP = rectangle['TopLeftX']
        if rectangle['CardCode'] != 'face' and rectangle['LocalPlayer'] == True:
            cardTMP = Card(real_x_TMP, real_y_TMP, rectangle['Width'], rectangle['Height'], rectangle['CardCode'])
            if is_card_vertical(cardTMP):
                if is_card_in_hand(cardTMP, SCREEN_HEIGHT):
                    positions_hand.append(cardTMP)
                else:
                    positions_table.append(cardTMP)
            else:
                positions_attacking_blocking.append(cardTMP)

    if not positions_hand and not positions_table:
        print("returning")
        return

    # Sort cards left to right
    positions_hand.sort(key=lambda x: x.real_x, reverse=False)
    positions_table.sort(key=lambda x: x.real_x, reverse=False)
    
    print("HAND: ")
    print_positions(positions_hand)
    print("TABLE: ")
    print_positions(positions_table)
    print("ATTACKING/BLOCKING: ")
    print_positions(positions_attacking_blocking)
    print("----------------------------------------------------")
    
    ck = CaptureKeys()
    ck.start_listener()
    
    if ck.last_pressed_key == '':
        return

    requested_card = int(ck.last_pressed_key) - 1

    if ck.hand_or_table:
        positions = positions_table
    else:
        positions = positions_hand

    if requested_card > len(positions):
        log.error(f"Card number {int(requested_card)} is not valid in this state.")
    else:
        if ck.move_or_click:
            click_card(positions, positions[requested_card].lor_code, SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
            move_card(positions, positions[requested_card].lor_code, SCREEN_WIDTH, SCREEN_HEIGHT)


    # TODO: Fix blocking with more than one card
    return


def print_positions(positions):

    for position in positions:
        print(f"{position.click_x} - {position.click_y} => {position.lor_code} [{position.in_hand}]")

    return

def move_card(positions, lor_code, screen_width, screen_height):

    for position in positions:
        if position.lor_code == lor_code:
            pywinauto.mouse.press(button='left', coords=(position.click_x, position.click_y))
            pywinauto.mouse.release(button='left', coords=(int(screen_width / 2), int(screen_height / 2)))
            # HACK: Move mouse "out of the screen" so it doesn't hover on cards
            pywinauto.mouse.move(coords=(1,1))

    return

def click_card(positions, lor_code, screen_width, screen_height):

    for position in positions:
        if position.lor_code == lor_code:
            pywinauto.mouse.click(button='left', coords=(position.click_x, position.click_y))
    # HACK: Move mouse "out of the screen" so it doesn't hover on cards
    pywinauto.mouse.move(coords=(1,1))

    return

def is_card_in_hand(card, screen_height):
    # TODO: Calculate this
    return card.real_y >= (screen_height - 100)

def is_card_vertical(card):
    #print(f"CARD {card.lor_code} is vertical: {card.height > card.width}")
    return card.height > card.width

if __name__ == '__main__':
    main()


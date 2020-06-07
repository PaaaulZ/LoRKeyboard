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

    def __init__(self, real_x, real_y, card_width, card_height, lor_code, in_hand):
        self.real_x = real_x
        self.real_y = real_y
        self.lor_code = lor_code
        self.click_x = round(real_x + (card_width / 2))
        self.click_y = real_y + 50 # Fixed number, i don't like it
        self.in_hand = in_hand

API_HOST = 'http://localhost:21337'
CARD_POSITION_API_URL = 'http://localhost:21337/positional-rectangles'

# Setup logging
fh = logging.FileHandler('lork.log')
log = logging.getLogger('LoRKeyboard')
logging.basicConfig(format='%(asctime)s - [%(levelname)s]: %(message)s')
log.setLevel(logging.DEBUG)
log.addHandler(fh)

def main():
    get_card_positions()
    return

def get_card_positions():

    positions = []

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
            # Only if it's really a card
            if is_card_in_hand(real_y_TMP):
                positions.append(Card(real_x_TMP, real_y_TMP, rectangle['Width'], rectangle['Height'], rectangle['CardCode']))
            else:
                positions.append(Card(real_x_TMP, real_y_TMP, rectangle['Width'], rectangle['Height'], rectangle['CardCode']))

    # Sort cards left to right
    positions.sort(key=lambda x: x.real_x, reverse=False)
    print_positions(positions)
    #move_card(positions,'01NX012')
    
    ck = CaptureKeys()
    ck.start_listener()
    
    requested_card = int(ck.last_pressed_key) - 1

    #print(f"Pressed: {ck.last_pressed_key}")

    if requested_card > len(positions):
        log.error(f"Card number {int(requested_card)} is not valid in this state.")
    else:
        move_card(positions,positions[requested_card].lor_code, SCREEN_WIDTH, SCREEN_HEIGHT)

    return


def print_positions(positions):

    for position in positions:
        print(f"{position.click_x} - {position.click_y} => {position.lor_code} [{position.in_hand}]")

    return

def move_card(positions, lor_code, screen_width, screen_height):

    for position in positions:
        # test
        if position.lor_code == lor_code:
            pywinauto.mouse.press(button='left', coords=(position.click_x, position.click_y))
            pywinauto.mouse.release(button='left', coords=(screen_width / 2, screen_height / 2))

    return

def is_card_in_hand(real_y, screen_height):
    # TODO: Calculate this
    return real_y >= (screen_height - 200)

if __name__ == '__main__':
    main()

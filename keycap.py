# Credits: Larz60+ @ https://python-forum.io/Thread-Keypress-when-running-a-python-app-in-a-console-on-windows
from pynput import keyboard
 
class CaptureKeys:
    last_pressed_key = ''
    hand_or_table = False
    move_or_click = False

    def __init__(self):
        pass
 
    def on_press(self, key):
        try:
        #print('alphanumeric key {0} pressed'.format(key.char))
            if key.char in ['1','2','3','4','5','6','7','8','9']:
                self.last_pressed_key = key.char
                return False
            elif key.char == 'u':
                print("[DEBUG] Updating")
                self.last_pressed_key = ''
                return False
        except AttributeError:
            #print('special key {0} pressed'.format(key))
            pass
        if key == keyboard.Key.esc:
            # Stop listener
            return False
        elif key == keyboard.Key.shift:
            self.hand_or_table = not self.hand_or_table
            if self.hand_or_table:
                print("[DEBUG] Selecting TABLE cards")
                #return True
            else:
                print("[DEBUG] Selecting HAND cards")
                #return True
        elif key == keyboard.Key.ctrl_l:
            self.move_or_click = not self.move_or_click
            if self.move_or_click:
                print("[DEBUG] Clicking")
                #return True
            else:
                print("[DEBUG] Moving")
                #return True
        # elif key == keyboard.Key.space:
        #     print("[DEBUG] Passing, reloading list")
        #     self.last_pressed_key = ''
        #     return True

 
    def on_release(self, key):
        pass
        #print('{0} released'.format(key))
        
 
    # Collect events until released
    def main(self):
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            listener.join()
 
    def start_listener(self):
        keyboard.Listener.start
        self.main()

# if __name__ == 'keycap':
#     ck = CaptureKeys()
#     ck.start_listener()
# LoRKeyboard

## WARNING: This is a working progress. Even if you can play a very simple match the code is very far from being done and a lot of important features are missing.

### What is this?

As the title says LoRKeyboard (LoRK for friends) allows you to play Legends of Runeterra without using your mouse.

### Why would I want to play with my keyboard?

Nobody is forcing you but I can give you some reasons, more or less valid:

- **Maybe you can't use your hands very well.** Not everyone can comfortably use a mouse, some have problems with grabbing stuff, some do not have hands at all and some just feel more comfortable using the keyboard.
- **Maybe all you have is a touchpad.** Let's be honest, touchpads are made in hell. Who likes doing things with a touchpad? Nobody. With LoRK you can ditch your touchpad and play with the keyboard instead.
- **Maybe you are too good with a mouse and need a new challenge.**. Who am I to stop you?
- **Maybe you want some keybindings to speed up your gameplay.** Nobody here said you **have** to play with only the keyboard, you could play normally but keep LoRK open and it will provide you some keyboard shortcuts.

### How does this work?

LoRK uses Legends of Runeterra's Game Client API to get object positions and with the help of some not so smart "calculations" and conditions is able to detect many things (if cards are on hand, on table, attacking/blocking, if you want to move the card and play it or just click it, and much more). For now it's a bit rusty and sometimes movements are too fast and fail but I promise that LoRK is doing his very best.

### Can I get banned for this?

I don't think so. Object positions come from the official Game Client API and the rest is just mouse movement emulation. Even if the mouse movements are very fast and not human made it's still you playing the game and making decisions, why would this be a problem?

### Any other bright ideas?

I have plans for LoRK. When finished I think I'll make it a module instead of a standalone script so that other scripts can interact with it and play the game. 

One of my future project will 100% be "Twitch plays Legends of Runeterra" a LoR version of "Twitch plays Pokèmon" where Twitch chat controls the game (I just need to finish writing the code, refactor it into a module and get at least 1 active viewer in my Twitch chat...).

### How do I play / What keybindings are available?

**Before we start remember this: for now every time cards change position you'll have to update by pressing the update key!**

- **[1-8]**: Do something on a card. With the default mode it just plays that card.
- **[9 and 0]**: 9 clicks the enemy nexus, 0 clicks the ally nexus.
- **u**: Updates the card position in memory, you will need to use this every time cards change position.
- **r**: Takes a screenshot of the game and shows you what the program can see (where cards are and which keys are bound to every object).
- **s**: Switches to HAND mode. Pressing **[1-8]** plays that card from your hand to the TABLE.
- **Left CTRL**: Switches to TABLE mode. Pressing **[1-8]** attacks with the selected card number (moves it from the TABLE to the ATTACKING/BLOCKING side of the board).
- **Left ALT**: Switches to ATTACKING/BLOCKING mode. Pressing **[1-8]** will click on the ATTACKING/BLOCKING card number.
- **Left SHIFT**: Switches to ENEMY mode. Pressing **[1-8]** clicks on the enemy card with that number.
- **Caps Lock**: Switches to BLOCKING mode. Pressing **[1-8]** will block with that card. **Cards are placed from left to right. If an enemy card cannot be blocked you will need to press it anyway and let it fail to skip to the next. After blocking you will need to press Caps Lock again and update**
- **ESC**: Quits LoRK. For now in a very cursed way...
- **SPACE**: End turn. **This is a LoR native keybinding**.


## What features are missing?

- Nexus clicking does not currently work. Maybe movements are too fast, I don't know.
- Card replace (the game start screen).
- Card targeting (for example when you use a card that lets you discard something from your hand).
- Hover card to see details. For now you can only play or target cards but not position your mouse on them to check them.
- Cancel current action. Stop a spell from casting by taking it back into the hand, take an attacking/blocking card back on the table, etc...
- Spell targeting. Cannot target spells on the board (the circles on the center of the board. For example you have no way currently to use the "Deny" card).
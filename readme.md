# Karmic Dice Roller - _A Discord Dice Bot_

## Commands

- **!r**<br>

&emsp; rolls various dice with or without modifiers. Only accepts `-` and `+` as operators.
&emsp; Examples:
&emsp; `!r d20+2d4-d6 +5-10+5`
&emsp; `!r d20 + 2d4 - d6 +5 - 10 +5`
&emsp; `!r d20+2d4 - d6 + 5- 10+5`
&emsp; `!r 4d20 -1d20+ 2d6-1+5 - 0`
- **!ra**<br>

&emsp; rolls the first die type with advantage, for example `!ra d20+d4` rolls only the d20 with advantage.
&emsp; It will roll all dice of that type, example `!ra 2d20+2d4` rolls both d20 dice on advantage.
- **!rd**<br>

&emsp; rolls the first die type with disadvantage, works the same as the above one.
- **!re**<br>

&emsp; rolls 2 d20's and selects the one furthest from 10 taking into account the karmic setting. `!re` do not add anything else to the command.
- **!rea**<br>

&emsp; rolls 2 d20's and selects the one furthest from 10 with no regard to karmic settings. `!rea` do not add anything else to the command.
- **!sn**<br>

&emsp; Allows the user to change their name the bot uses on the said server. `!sn Bob Howell`
&emsp; Whatever is typed after the command and first space `!sn ` will be their new name.
- **!sk**<br>

&emsp; Allows the user to change whether the dice's Karmic setting is enabled or disabled. (Currently a Global Setting)
    - Planned to be server specific at a later date.
- **!disDat**<br>

&emsp; Displays data such as the server's hashed identifier, the server's name, the current karmic setting,
&emsp; and the amount of users that have stored data that is server specific.
    - Planned to be server specific at a later date.

## Simple Dice Commands
- !d4 rolls a d4 `!d4 +5` `!d4 +d8+10`
- !d6 rolls a d6 `!d6 +5` `!d6 +d12-6`
- !d8 rolls a d8 `!d8 +5` `!d8 +d4+2-4`
- !d10 rolls a d10 `!d10 +5` `!d10 +5-10`
- !d12 rolls a d12 `!d12 +5` `!d12 +5-d4`
- !d20 rolls a d20 `!d20 +5` `!d20 +8+d10`
- !d100 rolls a d100 `!d100 +5` `!d100 +d4+10`


## Features

- Roll multiple dice at once.
- Roll multiple dice with the first having advantage or disadvantage
- Add multiple modifiers
- Perform an emphasized roll, 2d20's taking the one furthest from 10
- Set Karmic Dice off or on.
- Allows users to have a special name they can set to be used in place of their user/server nickname. (server specific)
- Displays data specific to the server the command is performed on.



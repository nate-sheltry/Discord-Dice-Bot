# Karmic Dice Roller - _A Discord Dice Bot_

## Commands

- **!r**
rolls various dice with or without modifiers. Only accepts `-` and `+` as operators.
Examples:
`!r d20+2d4-d6 +5-10+5`
`!r d20 + 2d4 - d6 +5 - 10 +5`
`!r d20+2d4 - d6 + 5- 10+5`
`!r 4d20 -1d20+ 2d6-1+5 - 0`
- **!ra**
rolls the first die type with advantage, for example `!ra d20+d4` rolls only the d20 with advantage.
It will roll all dice of that type, example `!ra 2d20+2d4` rolls both d20 dice on advantage.
- **!rd**
rolls the first die type with disadvantage, works the same as the above one.
- **!re**
rolls 2 d20's and selects the one furthest from 10. `!re` do not add anything else to the command.
- **!sn**
Allows the user to change their name the bot uses on the said server. `!sn Bob Howell`
Whatever is typed after the command and first space `!sn ` will be their new name.
- **!sk**
Allows the user to change whether the dice's Karmic setting is enabled or disabled. (Currently a Global Setting)
    - Planned to be server specific at a later date.
- **!disDat**
Displays data such as the server's hashed identifier, the server's name, the current karmic setting,
and the amount of users that have stored data that is server specific.
    - Planned to be server specific at a later date.


## Features

- Roll multiple dice at once.
- Roll multiple dice with the first having advantage or disadvantage
- Add multiple modifiers
- Perform an emphasized roll, 2d20's taking the one furthest from 10
- Set Karmic Dice off or on.
- Allows users to have a special name they can set to be used in place of their user/server nickname. (server specific)
- Displays data specific to the server the command is performed on.



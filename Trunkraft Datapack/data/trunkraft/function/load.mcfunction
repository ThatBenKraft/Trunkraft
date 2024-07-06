## Runs when datapack is reloaded

# Scoreboards
scoreboard objectives add height_in dummy {"text":"Height (in)","bold":true}

# Runs player sizing
function trunkraft:player_size
# Sends out pending server messages
function trunkraft:pending_messages

# Reloads pack every 10 seconds
schedule function trunkraft:reload 10s
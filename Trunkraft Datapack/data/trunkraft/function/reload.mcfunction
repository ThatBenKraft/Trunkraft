scoreboard objectives remove height_in
scoreboard objectives add height_in dummy {"text":"Height (in)","bold":true}

function trunkraft:player_size

schedule function trunkraft:texting/new_messages 10s
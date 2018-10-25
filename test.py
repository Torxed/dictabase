from dictabase import dictabase as dict, autodict

players = dict("players") 
players["New Player"]["url"] = "http://homepage/avatar.png"

print(players)
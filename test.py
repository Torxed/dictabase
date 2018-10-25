from dictabase import dictabase as dict

core = dict("core") # Loads the "core" branch from stash
core["players"]["new"] = 2

print(core)
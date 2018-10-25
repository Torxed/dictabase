# dictabase
A dictionary, but also a "database".

## Usage

### Starting the server

	python dictabase.py

### Using the dict that isn't a dict *(and also not recommended to any sane person)*:

Here's a short example of how you would load the top level item called `core` from the *"databas"*.
Everything stored in the *database* is virtually a dictionary, and choosing a top level item from it is required.

	from dictabase import dictabase as dict

	# Loads the "core" first level from the stash
	core = dict("core") 
	core["players"]["new"] = 2

	print(core)

If it isn't obvious, overriding `dict` is a pretty stupid idea.
You should also consider something like [MongoDB](https://github.com/mongodb/mongo) which is pretty stable and reliable. It also returns dict-ish types of results.

## Final note

	Duck typing
	   "If it walks like a duck,
	    and it quacks like a duck,
	    then it must be a duck"

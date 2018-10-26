# dictabase
A dictionary, but also a "database".

## Usage

### Starting the server

	[user@host]$ python dictabase.py

### Using the dict

Here's a short example of how you would load the top level item called `players` from the *databas*.<br>
Everything stored in the *database* is virtually a dictionary, and choosing a top level item from it is required.

```python
from dictabase import dictabase as dict

# Loads the "players" first level from the stash
players = dict("players") 
players["New Player"]["url"] = "http://homepage/avatar.png"

print(players)
```

If it isn't obvious, overriding `dict` is a pretty stupid idea.
You should also consider something like [MongoDB](https://github.com/mongodb/mongo) which is pretty stable and reliable. It also returns dict-ish types of results.

## What is this?

It's a network-based dictionary.<br>
A way to access a dictionary as if it's a dictionary, but all new data is fetched over the network.

The only reason behind this is to demonstrate in a extremely simplfied and minimal way how to access memory resources aacross a network.

## Final note

```python
    ## Duck typing
    #    "If it walks like a duck,
    #     and it quacks like a duck,
    #     then it must be a duck"
```

# ajo-bot
Count your ajo stats!

You can blame Mot for this exising :)

## Invite the bot
[Invite](https://discord.com/api/oauth2/authorize?client_id=967138080375046214&permissions=265280&scope=bot%20applications.commands)
[Without permissions](https://discord.com/api/oauth2/authorize?client_id=967138080375046214&permissions=265280&scope=bot%20applications.commands)

## Running the bot
To run the bot you will need Poetry and Redis.

```sh
poetry install
poetry run task start
```

## Redis data structure
User model is stored in keys, leaderboard in sorted set.
We use keys instead of a hash to benefit from redis' ttl system.

```
# [
#   {id: 111, name: "Zymna", count: 7}
#   {id: 222, name: "Axl", count: 4}
# ]
> incrby 111:count 7
> incrby 222:count 4

# leaderboard implemented as a sorted set
> zincrby leaderboard 7 "Zymna"
> zincrby leaderboard 4 "Axl"

# expiring award operations are stored in :{type}
> set 111:daily 1 ex 86400 # daily ttl
> set 111:weekly 1 ex 604800 # weekly ttl
```

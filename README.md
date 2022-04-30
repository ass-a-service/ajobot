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
There is no user model, a user is linked to a score via a redis sorted set.

```
# [
#   {name: "Zymna#0001", count: 7}
#   {name: "Axl#0001", count: 4}
# ]
# leaderboard implemented as a sorted set
> zincrby lb 7 "Zymna#0001"
> zincrby lb 4 "Axl#0001"

# expiring award operations are stored in :{type}
> set 111:daily 1 ex 86400 # daily ttl
> set 111:weekly 1 ex 604800 # weekly ttl
```

## Operations
Most operations run through a LUA script to avoid concurrency.

The following operation would be bulked into `pay.lua`:
```
# Axl#0001 pay 4 to Zymna#0001, with count check
> zscore lb Axl#0001
> zincrby lb -4 Axl#0001
> zincrby lb 7 Zymna#0001
```

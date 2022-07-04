# ARCHITECTURE

## Redis data structure
### Identifier
The ajo-bot uses discord's user ID, a redis key holds its discord username.
This key is checked and changed if necessary on each operation.

```
# file: setne.lua
> set 111 "Zymna#0001"
> get 111
"Zymna#0001"
> set 222 "Axl#0001"
```

### Leaderboard
The leaderboard is a redis sorted set connecting a user ID to his score.

```
# [
#   {name: "111", count: 7}
#   {name: "222", count: 4}
# ]
# leaderboard implemented as a sorted set
> zincrby lb 7 "111"
> zincrby lb 4 "222"
```

### User keys
All user related keys must follow the following schema: `{id}:{key}`. If the key
is composed of multiple words, a hyphen `-` should be used for separation.

#### Expiring rewards
Time based rewards are stored in an expiring redis key. The key is checked when
rewarding, and set to a value of 1 with the related TTL when the reward applies.

```
> set 111:daily 1 ex 86400 # daily ttl
> set 111:weekly 1 ex 604800 # weekly ttl
```

#### Vampire
The vampire key has a value equal to the next level of vampire that will appear.
The key is changed to expire according to the vampire level.

```
# a vampire level 1 will appear, and expires in 10 minutes
> set 111:vampire 1 EX 600
```

#### Inventory
The user's inventory is stored into a hash.
```
> hincrby 111:inventory ":cross:" 1
> hgetall 111:inventory
```

## Event streaming
All write operations are recorded into two different redis streams:
* the stream of ajo changes: `ajobus`
* the stream of inventory changes: `ajobus-inventory`

All events include a type describing where the change comes from:
```
# earned an item
> xadd "ajobus-inventory" "*" "user_id" 111 "item" ":cross:" "quantity" 1 "type" "item_earned"

# traded an item
> xadd "ajobus-inventory" "*" "user_id" 111 "item" ":cross:" "quantity" -1 "type" "trader"
> xadd "ajobus-inventory" "*" "user_id" 222 "item" ":cross:" "quantity" 1 "type" "tradee"

# earned ajos
> xadd "ajobus" "*" "user_id" 111 "amount" 1 "type" "farm"

# gamble
> xadd "ajobus" "*" "user_id" 111 "amount" 20 "type" "gamble"

# discombobulate
> xadd "ajobus" "*" "user_id" 111 "amount" -20 "type" "discombobulator"
> xadd "ajobus" "*" "user_id" 111 "amount" -25 "type" "discombobulatee"
```

## Operation examples
Most operations run through a LUA script to avoid concurrency.

### `pay.lua`
```
# 222 pays 4 to 111, with count check:
# ensure the user can pay
> zscore lb 222
# update leaderboard
> zincrby lb -4 222
> zincrby lb 4 111
```

### `timely-reward`
```
# Axl#0001 daily award
# ensure the user can be rewarded
> ttl 222:daily
# reward and block until next
> zincrby lb 32 222
> set 222 1 EX 86400
```

### Event guidelines
Events MUST include the following attributes at least:
* `version` the version of the event
* `type` the type of the event
* `user_id` the user identifier to which the event applied
* `guild_id` the guild identifier where the event applied (0 if none)

### LUA guidelines
The priority of keys for LUA scripts is the following:
* first the stream keys
* next any other key which is required

The priority for arguments of LUA scripts is the following:
* first the arguments required for the operation
* next the arguments required for events
* last the seed used for random if any

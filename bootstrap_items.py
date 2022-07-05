# this file is used to generate redis protocol in order to bulk load the
# item data (max stack, currency, prices, chance to appear)
def proto(hash_name, hash_data) -> None:
    # stringify the hash
    strings = ["HSET", hash_name]
    for key, value in hash_data.items():
        strings.extend([key, value])

    # transform to redis proto
    arg_count = len(strings)
    parts = [f"*{arg_count}"]
    for s in strings:
        parts.extend([f"${len(s)}", s])

    print("\r\n".join(parts), end="\r\n")

def main() -> None:
    data = {
        ":sauropod:": {
            "drop_rate": 1,
            "max_stack": 1
        },
        ":chopsticks:": {
            "drop_rate": 6,
            "max_stack": 5
        },
        ":cross:": {
            "drop_rate": 500,
            "max_stack": 10,
            "currency": ":garlic:",
            "price": 50
        },
        ":bomb:": {
            "drop_rate": 200,
            "max_stack": 1
        },
        ":herb:": {
            "drop_rate": 1000,
            "max_stack": 20
        },
        ":reminder_ribbon:": {
            "max_stack": 1,
            "currency": ":herb:",
            "price": 4
        }
    }

    protos = []
    hdrop_rate = {}
    for item, item_data in data.items():
        # prepare drop rate hash
        if "drop_rate" in item_data:
            hdrop_rate[item] = str(item_data["drop_rate"])

        # prototype the item hash
        hitem = {}
        for key, value in item_data.items():
            hitem[key] = str(value)
        proto("items:{}".format(item), hitem)

    # prototype drop rate
    proto("drop-rate", hdrop_rate)


main()

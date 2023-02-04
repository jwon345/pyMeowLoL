

def dontDraw(spellId):

    return False


abilities = {
    "draven": {
        -29353: {
            "name": "draven Q",
            "draw": False
        },
    },
    "lux": {
        "Q": [10972, True]
    },
    "blitzcrank": {
        
    }
}

for i in abilities:
    if (-29353 in abilities[i]):
        print("found")
    print(abilities[i])

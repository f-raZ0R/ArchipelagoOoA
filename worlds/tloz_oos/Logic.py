from BaseClasses import MultiWorld
from worlds.tloz_oos import LOCATIONS_DATA
from worlds.tloz_oos.data.logic.DungeonsLogic import *
from worlds.tloz_oos.data.logic.OverworldLogic import make_overworld_logic
from worlds.tloz_oos.data.Regions import REGIONS

def create_connections(multiworld: MultiWorld, player: int):
    dungeon_entrances = []
    for reg1, reg2 in multiworld.worlds[player].dungeon_entrances.items():
        dungeon_entrances.append([reg1, reg2, True, None])

    all_logic = [
        make_overworld_logic(player),
        make_d0_logic(player),
        make_d1_logic(player),
        make_d2_logic(player),
        make_d3_logic(player),
        make_d4_logic(player),
        make_d5_logic(player),
        make_d6past_logic(player),
        make_d6present_logic(player),
        make_d7_logic(player),
        make_d8_logic(player),
        dungeon_entrances,
    ]

    # Check unreachable regions
    unused_region = REGIONS
    unused_region.remove("Menu")
    for logic_array in all_logic:
        for entrance_desc in logic_array:
            if entrance_desc[1] in unused_region:
                unused_region.remove(entrance_desc[1])

    if unused_region.count != 0:
        print("Unused region :")
        for region in unused_region:
            print(region)
        print("------------")


    # Create connections
    for logic_array in all_logic:
        for entrance_desc in logic_array:
            region_1 = multiworld.get_region(entrance_desc[0], player)
            region_2 = multiworld.get_region(entrance_desc[1], player)
            is_two_way = entrance_desc[2]
            rule = entrance_desc[3]

            region_1.connect(region_2, None, rule)
            if is_two_way:
                region_2.connect(region_1, None, rule)


def apply_self_locking_rules(multiworld: MultiWorld, player: int):
    if multiworld.worlds[player].options.accessibility == Accessibility.option_locations:
        return

    # Process self-locking keys first
    MINIMAL_REQUIRED_KEYS_TO_REACH_KEYDOOR = {
        # TODO : Adapt it to OOA
        #"Hero's Cave: Final Chest": 0,
        #"Gnarled Root Dungeon: Item in Basement": 1,
        #"Snake's Remains: Chest on Terrace": 2,
        #"Poison Moth's Lair (1F): Chest in Mimics Room": 1,
        #"Dancing Dragon Dungeon (1F): Crumbling Room Chest": 2,
        #"Dancing Dragon Dungeon (1F): Eye Diving Spot Item": 2,
        #"Unicorn's Cave: Magnet Gloves Chest": 1,
        #"Unicorn's Cave: Treadmills Basement Item": 3,
        #"Explorer's Crypt (B1F): Chest in Jumping Stalfos Room": 4,  # Not counting poe skip
        #"Explorer's Crypt (1F): Chest Right of Entrance": 1
    }

    for location_name, key_count in MINIMAL_REQUIRED_KEYS_TO_REACH_KEYDOOR.items():
        location_data = LOCATIONS_DATA[location_name]
        dungeon = location_data["dungeon"]
        small_key_item_name = f"Small Key ({DUNGEON_NAMES[dungeon]})"
        location = multiworld.get_location(location_name, player)
        location.always_allow = make_self_locking_item_lambda(player, small_key_item_name, key_count)

    # Process other self-locking items
    OTHER_SELF_LOCKING_ITEMS = {
        # TODO Trade Sequence OOA
        'Yoll Graveyard: Graveyard Poe':"Poe Clock",
        'Lynna Village: Postman':"Stationery",
        'Lynna Village: Toilet Hand':"Stink Bag",
        'Crescent Island: Tokay Chef':"Tasty Meat",
        'Nuun: Happy Mask Salesman':"Doggie Mask",
        'Lynna Village: Mamamu Yan':"Dumbbell",
        'Symmetry City: Middle man':"Cheesy Mustache",
        'Lynna City: Comedian':"Funny Joke",
        'Lynna Village: Sad boi':"Touching Book",
        'Maple Trade':"Magic Oar",
        'Lynna Village Coast: Rafton':"Sea Ukulele",
        'Shore of No Return: Old Zora':"Broken Sword",
    }

    for loc_name, item_name in OTHER_SELF_LOCKING_ITEMS.items():
        location = multiworld.get_location(loc_name, player)
        location.always_allow = make_self_locking_item_lambda(player, item_name)

def make_self_locking_item_lambda(player: int, item_name: str, required_count: int = 0):
    if required_count == 0:
        return lambda state, item: (item.player == player and item.name == item_name)

    return lambda state, item: (item.player == player
                                and item.name == item_name
                                and state.has(item_name, player, required_count))

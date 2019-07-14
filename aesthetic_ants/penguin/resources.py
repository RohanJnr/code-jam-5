import pyglet

loader = pyglet.resource.Loader(path="../resources")


def load_image(filename: str, centered: bool = False):
    image = loader.image(filename)

    if centered:
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2

    return image


def load_level(filename: str):
    return loader.text(filename)


# Sprite images
ENEMY_BIG_IMAGE = load_image("evil_business_man_big.png", centered=True)
ENEMY_FAST_IMAGE = load_image("evil_business_man_fast.png", centered=True)
ENEMY_TRUCK_IMAGE = load_image("truck.png", centered=True)
PLAYER_IMAGE = load_image("penguin.png", centered=True)

# Projectile images
SNOWBALL_IMAGE = load_image("snowball.png")
ROCKET_IMAGE = load_image("snowball_rocket.png")
SNOWSPLOSION_IMAGE = load_image("snowsplosion.png")

# Projectile icons
SNOWBALL_ICON = load_image("snowball_icon.png")
SHOTGUN_ICON = load_image("shotgun_icon.png")
RPG_ICON = load_image("rpg_icon.png")

# Tile images
WATER_TILE = load_image("tiles/water.png")
ICE_TILE = load_image("tiles/ice.png")
WEAK_ICE_TILE = load_image("tiles/weak_ice.png")
WALL_TILE = load_image("tiles/wall.png")

# Levels
LEVEL_1 = load_level("levels/1.level")

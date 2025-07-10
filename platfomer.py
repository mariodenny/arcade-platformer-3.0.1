from time import sleep

import arcade


SCREEN_TITLE = "Lesson 7&8 - Integrating tile maps"
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

TILE_SPRITE_SCALING = 1.0
PLAYER_SCALING = 0.5
SPRITE_PIXEL_SIZE = 32
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SPRITE_SCALING
CAMERA_PAN_SPEED = 1.0 # KECEPATAN MOVEMENT KAMERA

# PHYSICS
MOVEMENT_SPEED = 5
JUMP_SPEED = 15
GRAVITY = 1


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        # Prepare object for loading map
        self.tile_map = None
        # Prepare object for player
        self.player_list = None
        self.player_sprite = None
        self.score = 0

        # Prepare object for physic and camera
        self.physic_engine = None
        self.end_of_map = 0
        self.game_over = False
        self.game_camera = None
        self.gui_camera = None
        self.camera_bounds = None
        # self.teleport_sprites = None
        # self.teleport_targets = None

        # Optional : Count the fps of the games
        self.fps_text = arcade.Text("Fps :", 10,20, arcade.csscolor.DARK_GREEN, 15)
        self.game_over_text = None

        # start level
        self.level = 0
        self.max_level = 3

    def setup(self):
        # Prepare for character
        self.player_list = arcade.SpriteList()
        # Load from file here
        self.player_sprite = arcade.Sprite(
            ":resources:/images/animated_characters/female_person/femalePerson_idle.png",
            scale=PLAYER_SCALING
        )
        self.player_list.append(self.player_sprite)
        print(f"Characters : {self.player_sprite}")

        self.game_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        # show fps
        self.fps_text = arcade.Text('Fps: ',10,20,arcade.csscolor.DARK_GREEN,15)
        self.game_over_text = arcade.Text(
            'GAME OVER!',
            self.window.center_x,
            self.window.center_y,
            arcade.csscolor.BLACK,
            30,
            anchor_x='center',
            anchor_y='center'
        )

    def load_level(self,level):
        # Lets load from tiled file(tmj)
        print(level)
        self.tile_map = arcade.load_tilemap(
            f"level_{level}.tmj", scaling=TILE_SPRITE_SCALING
        )
        print(f"Load map : {self.tile_map}")
        # Teleport
        self.teleport_sprites = self.tile_map.sprite_lists.get("teleport_up", arcade.SpriteList())
        self.teleport_targets = {obj.name: obj for obj in self.tile_map.object_lists.get("target_tp_up", [])}
        print(f"Teleport door : {self.teleport_sprites}")
        print(f"Teleport target : {self.teleport_targets}")

        self.map_height = self.tile_map.height * self.tile_map.tile_height
        self.coin_list = self.tile_map.sprite_lists.get("coins", arcade.SpriteList())

        spawn_points = self.tile_map.object_lists.get("player_spawn")
        print(f"Spawn point {spawn_points}")
        if spawn_points:
            for obj in spawn_points:
                print(f"Object in spawn point : {obj}")
                if obj.name == "player_spawn":
                    x = obj.shape[0]
                    y = obj.shape[1]

                    y = self.map_height - y
                    self.player_sprite.center_x = x
                    self.player_sprite.center_y = y
                    print(f"Player spawn at x:{x} , y:{y}")
                    break

        # Load the platforms
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE
        self.physic_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            self.tile_map.sprite_lists["platforms"],
            gravity_constant=GRAVITY
        )

        if self.tile_map.background_color:
            self.window.background_color = self.tile_map.background_color # Guna nya untuk bg color

        #set up the map limit

        max_x = GRID_PIXEL_SIZE * self.tile_map.width
        max_y = GRID_PIXEL_SIZE * self.tile_map.height

        limit_y = max_y > self.window.height
        # Set up the camera limit
        self.camera_bounds = arcade.LRBT(
            self.window.width / 2.0,
            max_x - self.window.width / 2.0,
            self.window.height / 2.0,
            max_y - (self.window.height / 2.0 if limit_y else 0)
        )
        # set posisi default kamera game
        self.game_camera.position = self.window.center

    def on_draw(self):
        self.clear()
        self.tile_map.sprite_lists["background"].draw()

        with self.game_camera.activate():
            self.tile_map.sprite_lists['platforms'].draw()
            self.tile_map.sprite_lists['coins'].draw()
            self.tile_map.sprite_lists['stones'].draw()
            self.tile_map.sprite_lists['benches'].draw()
            self.tile_map.sprite_lists['fences'].draw()
            self.tile_map.sprite_lists['trees'].draw()
            self.tile_map.sprite_lists['teleport_up'].draw()
            # self.tile_map.sprite_lists['target_tp_up'].draw()

            #

            self.player_list.draw()

        with self.gui_camera.activate():
            self.fps_text.text = f"Fps : {1 / self.window.delta_time: .0f}"
            self.fps_text.draw()

            # Game over text
            if self.game_over:
                self.game_over_text.position = self.window.center
                self.game_over_text.draw()

    def on_update(self, delta_time):
        if self.player_sprite.right >= self.end_of_map:
            if self.level < self.max_level:
                self.level += 1  # kalau mau naik level
                self.load_level(self.level)
                self.player_sprite.center_x = 128
                self.player_sprite.center_y = 64
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
            else:
                self.game_over = True

        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.teleport_sprites)
        for teleport in hit_list:
            target_name = teleport.properties.get("target")
            if target_name and target_name in self.teleport_targets:
                target_obj = self.teleport_targets[target_name]
                x, y = target_obj.shape[0], target_obj.shape[1]
                y = self.map_height - y
                self.player_sprite.center_x = x
                self.player_sprite.center_y = y
                print(f"Player teleported to {target_name} at x:{x} and y:{y}")
                break

        if not self.game_over:
            if self.player_sprite.center_y < -50:
                self.game_over = True
                print("Game over : Player fall from the map!")

            self.physic_engine.update()

            self.game_camera.position = arcade.math.smerp_2d(
                self.game_camera.position,
                self.player_sprite.position,
                delta_time,
                CAMERA_PAN_SPEED
            )
        coin_hit = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
        for coin in coin_hit:
            coin.remove_from_sprite_lists()
            self.score += 1
            print(f"Coin collected Score : {self.score}")

    def on_key_press(self,key,modifiers):
        if key == arcade.key.UP:
            if self.physic_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        if key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        if key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

        if key == arcade.key.ESCAPE:
            self.level = 1
            self.load_level(self.level)
            self.player_sprite.center_x = 128
            self.player_sprite.center_y = 64
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.game_over = False

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

def main():
    window = arcade.Window(SCREEN_WIDTH,SCREEN_HEIGHT,SCREEN_TITLE)
    game = GameView()
    game.setup()

    window.show_view(game)
    window.run()

main()
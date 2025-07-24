from time import sleep

import arcade
import random


SCREEN_TITLE = "SUPER EPIC MMORPG GAME"
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

TILE_SPRITE_SCALING = 1.0
PLAYER_SCALING = 0.5
SPRITE_PIXEL_SIZE = 32
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SPRITE_SCALING
CAMERA_PAN_SPEED = 1.0 # KECEPATAN MOVEMENT KAMERA

# PHYSICS
MOVEMENT_SPEED = 3
JUMP_SPEED = 10
GRAVITY = 1
UPDATES_PER_FRAME = 5

RIGHT_FACING = 0
LEFT_FACING = 1

class PlayerCharacter(arcade.Sprite):
    def __init__(self, idle_texture_pair,walk_texture_pair):
        self.character_face_direction = RIGHT_FACING

        self.cur_texture = 0
        self.idle_texture_pair = idle_texture_pair
        self.walk_textures = walk_texture_pair

        self.points = [
            [-22.-64],
            [22,-6],
            [22,28],
            [-22,28]
        ]

        super().__init__(self.idle_texture_pair[0], scale=PLAYER_SCALING)

    def update_animation(self, delta_time: float = 1/60):
        if self.change_x < 0 and self.character_face_direction ==RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction ==LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]

class InstructionView(arcade.View):
    def __init__(self):
        super().__init__()
        self.title_text = None
        self.instruction_text = None

    def on_show_view(self):
        arcade.set_background_color(arcade.csscolor.GREEN)

        self.title_text = arcade.Text(
            "HOW TO PLAY",
            self.window.center_x,
            self.window.height - 100,
            arcade.csscolor.GOLD,
            font_size = 32,
            anchor_x='center'
        )

        self.instruction_text = arcade.Text(
            "Good Luck! Arrow Keys (left, right), Up keys to jump \n"
            "ESC for escape, I for manual, and R for restart",
            self.window.center_x,
            self.window.height - 250,
            arcade.csscolor.BLACK,
            font_size=10,
            anchor_x='center'
        )
    def on_draw(self):
        self.clear()
        self.title_text.draw()
        self.instruction_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            character_view =SelectCharacterView()
            self.window.show_view(character_view)
        elif key == arcade.key.ESCAPE:
            self.window.close()

class SelectCharacterView(arcade.View):
    def __init__(self):
        super().__init__()
        self.character_types = [
            ':resources:/images/animated_characters/female_adventurer/femaleAdventurer',
            ':resources:/images/animated_characters/male_adventurer/maleAdventurer',
            ':resources:/images/animated_characters/robot/robot'
        ]

        self.character_names = [
            "",
            "",
            ""
        ]

        self.selected_character = 0
        self.character_sprites = []
        self.title_text = None
        self.instruction_text = None
        self.character_name_text = None

        self.character_scale = PLAYER_SCALING
        self.selection_border_padding = 30
        self.selection_border_thickness = 5
        self.character_spacing = 100

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GREEN)

        self.character_sprite_list = arcade.SpriteList()
        self.character_sprites = []

        for character_path in self.character_types:
            try:
                texture = arcade.load_texture(f"{character_path}_idle.png")
                sprite = arcade.Sprite(texture, scale=self.character_scale)
                self.character_sprites.append(sprite)
                self.character_sprite_list.append(sprite)
            except:
                sprite =arcade.Sprite(scale=self.character_scale)
                self.character_sprites.append(sprite)
                self.character_sprite_list.append(sprite)

        center_x = self.window.center_x
        center_y = self.window.center_y
        start_x = center_x - (len(self.character_sprites) - 1)* self.character_sprites//2

        for i, sprite in enumerate(self.character_sprites):
            sprite.center_x = start_x + i * self.character_spacing
            sprite.center_y = center_y

        self.title_text = arcade.Text(
            "CHOOSE YOUR CHARACTERS!",
            self.window.height - 100,
            arcade.color.WHITE,
            font_size = 30,
            anchor_x = "center"
        )

        self.instruction_text = arcade.Text(
            "Use LEFT/RIGHT arrows to select, ENTER to start game",
            self.window.center_x,
            100,
            arcade.color.WHITE,
            font_size=16,
            anchor_x="center"
        )

        self.character_name_text = arcade.Text(
            self.character_names[self.selected_character],
            self.window.center_x,
            center_y - 80,
            arcade.color.YELLOW,
            font_size = 20,
            anchor_x = "center"
        )

    def on_draw(self):
        self.clear()
        if hasattr(self,'character_sprites') and self.character_sprites:
            selected_sprite = self.character_sprites[self.selected_character]
            if selected_sprite.texture:
                arcade.draw_rect_outline(
                    arcade.LRBT(
                        selected_sprite.center_x - (selected_sprite.width + self.selection_border_padding) // 2,
                        selected_sprite.center_x + (selected_sprite.width + self.selection_border_padding) // 2,
                        selected_sprite.center_y - (selected_sprite.height + self.selection_border_padding) // 2,
                        selected_sprite.center_y + (selected_sprite.height + self.selection_border_padding) // 2
                    ),
                    arcade.color.YELLOW, self.selection_border_padding
                )
            if hasattr(self, 'character_sprite_list'):
                self.character_sprite_list.draw()

                self.title_text.draw()
                self.instruction_text.draw()
                self.character_name_text.draw()

    def on_key_press(self,key,modifiers):
        if key == arcade.key.LEFT:
            self.selected_character = (self.selected_character - 1) % len(self.character_types)
            self.character_name_text.text = self.character_names[self.selected_character]
        elif key == arcade.key.RIGHT:
            self.selected_character = (self.selected_character + 1) % len(self.character_types)
            self.character_name_text.text = self.character_names[self.selected_character]
        elif key == arcade.key.ENTER:
            game_view = GameView(selected_character = self.selected_character)
            game_view.setup()
            game_view.level = 1
            game_view.load_level(game_view.level)
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            instruction_view = InstructionView()
            self.window.show_view(instruction_view)

class GameOverView(arcade.View):
    pass

class GameView(arcade.View):
    def __init__(self, selected_character= None):
        super().__init__()
        # Prepare object for loading map
        self.tile_map = None
        # Prepare object for player
        self.player_list = None
        self.player = None
        self.player_sprite = None
        self.score = 0

        self.selected_character = selected_character
        self.character_types = [
            ':resources:/images/animated_characters/female_adventurer/femaleAdventurer',
            ':resources:/images/animated_characters/male_adventurer/maleAdventurer',
            ':resources:/images/animated_characters/robot/robot'
        ]

        if selected_character is not None:
            chosen_characters = self.character_types[selected_character]
        else:
            chosen_characters = random.choice(self.character_types)
            self.selected_character = self.character_types.index(chosen_characters)

        try:
            idle_texture = arcade.load_texture(f"{chosen_characters}_idle.png")
            self.idle_texture_pairs = idle_texture,idle_texture.flip_left_right()
        except Exception as e:
            print(f"Error load idle texture {e}")
            self.idle_texture_pairs = None, None

        self.walk_texture_pairs = []
        try:
            for i in range(8):
                texture = arcade.load_texture(f"{chosen_characters}_walk{i}.png")
                self.walk_texture_pairs.append((texture, texture.flip_left_right()))
        except Exception as e:
            print(f"Error loading walk animation {e}")
            self.walk_texture_pairs = []


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
        self.score_text = arcade.Text("Coins: ",20, 20,arcade.csscolor.GOLD,30)

        # start level
        self.level = 0
        self.max_level = 3

    def setup(self):
        # Prepare for character
        self.player_list = arcade.SpriteList()
        self.player = PlayerCharacter(self.idle_texture_pairs,self.walk_texture_pairs)
        self.player.scale = PLAYER_SCALING
        self.player_list.append(self.player)
        # Load from file here
        # self.player_sprite = arcade.Sprite(
        #     ":resources:/images/animated_characters/female_person/femalePerson_idle.png",
        #     scale=PLAYER_SCALING
        # )
        # self.player_list.append(self.player)
        # print(f"Characters : {self.player}")

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
                    self.player.center_x = x
                    self.player.center_y = y
                    print(f"Player spawn at x:{x} , y:{y}")
                    break

        # Load the platforms
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE
        self.physic_engine = arcade.PhysicsEnginePlatformer(
            self.player,
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
            (self.tile_map.sprite_lists.get('benches') or arcade.SpriteList()).draw()
            (self.tile_map.sprite_lists.get('coins') or arcade.SpriteList()).draw()
            (self.tile_map.sprite_lists.get('platforms') or arcade.SpriteList()).draw()
            (self.tile_map.sprite_lists.get('stones') or arcade.SpriteList()).draw()
            (self.tile_map.sprite_lists.get('fences') or arcade.SpriteList()).draw()
            (self.tile_map.sprite_lists.get('trees') or arcade.SpriteList()).draw()
            (self.tile_map.sprite_lists.get('teleport_up') or arcade.SpriteList()).draw()

            # self.tile_map.sprite_lists['platforms'].draw()
            # self.tile_map.sprite_lists['coins'].draw()
            # self.tile_map.sprite_lists['stones'].draw()
            # self.tile_map.sprite_lists['benches'].draw()
            # self.tile_map.sprite_lists['fences'].draw()
            # self.tile_map.sprite_lists['trees'].draw()
            # self.tile_map.sprite_lists['teleport_up'].draw()
            # self.tile_map.sprite_lists['target_tp_up'].draw()
            self.player_list.draw()

        with self.gui_camera.activate():
            self.fps_text.text = f"Fps : {1 / self.window.delta_time: .0f}"
            self.fps_text.draw()
            self.score_text.text = f'Score : {self.score}'
            self.score_text.draw()
            # Game over text
            if self.game_over:
                self.game_over_text.position = self.window.center
                self.game_over_text.draw()

    def on_update(self, delta_time):
        self.player_list.update()
        self.player_list.update_animation()
        if self.player.right >= self.end_of_map:
            if self.level < self.max_level:
                self.level += 1  # kalau mau naik level
                self.load_level(self.level)
                self.player.center_x = 128
                self.player.center_y = 64
                self.player.change_x = 0
                self.player.change_y = 0
            else:
                self.game_over = True

        hit_list = arcade.check_for_collision_with_list(self.player, self.teleport_sprites)
        for teleport in hit_list:
            target_name = teleport.properties.get("target")
            if target_name and target_name in self.teleport_targets:
                target_obj = self.teleport_targets[target_name]
                x, y = target_obj.shape[0], target_obj.shape[1]
                y = self.map_height - y
                self.player.center_x = x
                self.player.center_y = y
                print(f"Player teleported to {target_name} at x:{x} and y:{y}")
                break

        if not self.game_over:
            if self.player.center_y < -50:
                self.game_over = True
                print("Game over : Player fall from the map!")

            self.physic_engine.update()

            self.game_camera.position = arcade.math.smerp_2d(
                self.game_camera.position,
                self.player.position,
                delta_time,
                CAMERA_PAN_SPEED
            )
        coin_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coin_hit:
            coin.remove_from_sprite_lists()
            self.score += 1
            print(f"Coin collected Score : {self.score}")

    def on_key_press(self,key,modifiers):
        if key == arcade.key.UP:
            if self.physic_engine.can_jump():
                self.player.change_y = JUMP_SPEED
        if key == arcade.key.LEFT:
            self.player.change_x = -MOVEMENT_SPEED
        if key == arcade.key.RIGHT:
            self.player.change_x = MOVEMENT_SPEED

        if key == arcade.key.ESCAPE:
            self.level = 1
            self.load_level(self.level)
            self.player.center_x = 128
            self.player.center_y = 64
            self.player.change_x = 0
            self.player.change_y = 0
            self.game_over = False

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0

def main():
    window = arcade.Window(SCREEN_WIDTH,SCREEN_HEIGHT,SCREEN_TITLE)

    instruction_view = InstructionView()
    window.show_view(instruction_view)
    window.run()

main()
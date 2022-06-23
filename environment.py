from tetris_game import Tetris
from tetris_model import BOARD_DATA, Shape
import gym
from gym import spaces, Env
from pynput.keyboard import Key, Controller
from PyQt5.QtWidgets import QApplication
import sys

class TetrisEnv(Env):
    def __init__(self):
        # Create an actionspace with 5 actions (nothing, rotate, left, right, hard drop)
        self.action_space = spaces.Discrete(5)

        # Create a observation space with the board data, 0 for empty, 1 untill 7 for filled, depending on blocktype
        self.observation_space = spaces.Box(low=0, high=7, shape=(BOARD_DATA.width, BOARD_DATA.height))

        # Initialize pynput controller used for simulating keypresses
        self.keyboard = Controller()
    
        app = QApplication([])
        self.game = Tetris()
        sys.exit(app.exec_())
        #self.game.start()

    def step(self, action: int):
        self._give_input(action)

        gamestate = self.game.receive_gamestate()

        # Get observation
        observation = gamestate['board']

        # Get reward
        reward = self.game._get_reward(gamestate, action)

        # Check if the game is over
        if self.game_over():
            # Print total reward
            print("Reward is", self.total_reward)

            # Log total reward
            with open('rewards.txt', 'a', encoding='utf-8') as file:
                file.write(str(self.total_reward["total"]) + " " + str(self.score) + "\n")
            done = True
        else:
            done = False

        info = {}

        return observation, reward, done, info

    # Input function
    def _give_input(self, action: int):
        # Reset last input
        self.keyboard.release(Key.up)
        self.keyboard.release(Key.right)
        self.keyboard.release(Key.left)
        self.keyboard.release(Key.space)

        # Do nothing
        if action == 0:
            pass
        # Rotate
        elif action == 1:
            self.keyboard.press(Key.up)
        # Move left
        elif action == 2:
            self.keyboard.press(Key.left)
        # Move right
        elif action == 3:
            self.keyboard.press(Key.right)
        # Hard drop
        elif action == 4:
            self.keyboard.press(Key.space)

    # Possible rewards and penalties
    def _get_reward(self, gamestate: dict, action:int):
        reward = 0

        # Calculating the reward for the action
        reward += (gamestate['score'] * 100 - self.score)

        # Saving this score also in total_reward
        self.total_reward["score"] += (gamestate["score"] * 100 - self.score)

        # Saving the current score in self.score, to use it as the old score in the next iteration.
        self.score = gamestate["score"]

        # Passing of time gives a reward (surive longer)
        reward += 5
        self.total_reward["time_alive"] += 5

        # Pressing buttons is not free
        if action != 0 or action != 4:
            reward -= 5
            self.total_reward["button_presses"] -= 5

       # Dying gives a penalty
        if gamestate["is_alive"] == False:
            reward -= 500
            self.total_reward["dying"] -= 500

        # Saving the total reward in self.total_reward for this step
        self.total_reward["total"] += reward 

        return reward 

    def render(self):
        pass
    def reset(self):
         # Reset total_reward variable (used for logging) to 0
        self.total_reward = {
            "score": 0,
            "time_alive": 0,
            "button_presses": 0,
            "dying": 0,
            "total": 0
        }

        # Reset score variable
        self.score = 0

        # Reset step counter
        self.step_counter = 0

        # Reset the game
        self.game.restartGame()

        # Set input to none
        self._input(0)

        # Read an observation
        gamestate = self.game.receive_gamestate()
        observation = gamestate["board"]

        # Return the observation
        return observation

    def game_over(self):
        gamestate = self.game.receive_gamestate()
        for block in range(0, BOARD_DATA.width - 1):
            return gamestate["board"][block] != 0
                
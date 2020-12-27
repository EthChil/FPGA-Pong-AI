import gym
from gym import error, spaces, utils
from gym.utils import seeding

class PongEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    # Dimensions of LED array
    # TODO: Ethan - update values
    L, W = (20, 8)
    PADDLE_WIDTH = 3

    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.MultiDiscrete([
            self.L,
            self.W,
            self.W - 2*(self.PADDLE_WIDTH//2),
        ])
        self.reward_range = (0, 1)

        # Generate randomly
        self.paddle_pos = 0
        self.ball_pos = (0, 0)


    def step(self, action):
        observation = self._take_action(action)
        reward = None
        done = None
        info = None
        return observation, reward, done, info

    def reset(self):
        pass

    def render(self, mode='human'):
        pass

    def close(self):
        super().close()

    def _take_action(self, action):
        '''
        :param action: One of (0, 1, 2), 0 is no action, 1 is left, 2 is right
        :return:
        '''
        paddle_move = 0

        if action == 1:
            paddle_move = -1
        elif action == 2:
            paddle_move = 1

        if self.observation_space.contains([self.ball_pos[0], self.ball_pos[1], self.paddle_pos + paddle_move]):
            self.paddle_pos += paddle_move

        self._update_ball_pos()

        return [self.ball_pos[0], self.ball_pos[1], self.paddle_pos]

    def _update_ball_pos(self):
        # TODO: Implement Ethan's game logic
        pass





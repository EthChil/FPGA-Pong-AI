import gym
from gym import spaces
from gym.utils import seeding

class PongEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    # Dimensions of LED array
    # TODO: Ethan - update values
    L, W = (20, 8)
    PADDLE_WIDTH = 3
    PADDLE_RANGE = W - 2 * (PADDLE_WIDTH//2)
    BALL_DIRECTION_NUM = 6
    MISS_REWARD = -5
    HIT_REWARD = 1
    NOT_LOST_REWARD = 0.1

    def __init__(self):
        self.seed()
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.MultiDiscrete([
            self.L,
            self.W,
            self.PADDLE_RANGE,
            self.BALL_DIRECTION_NUM
        ])
        self.reward_range = (self.MISS_REWARD, self.HIT_REWARD)
        self.reset()

    def step(self, action):
        observation = self._take_action(action)
        reward = self._get_reward()
        done = reward < 0
        info = None
        return observation, reward, done, info

    def reset(self):
        self.paddle_pos = self.np_random.randint(0, self.PADDLE_RANGE)
        ball_x = self.np_random.randint(0, self.W)
        ball_y = self.np_random.randint(0, self.L)
        self.ball_pos = (ball_x, ball_y)

        return [ball_x, ball_y, self.paddle_pos]

    def render(self, mode='human'):
        pass

    def close(self):
        pass

    def seed(self, seed=None):
        self.np_random , seed = seeding.np_random(seed)
        return [seed]

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
        # If hits other side of the board, go in random direction
        pass

    def _get_reward(self):
        if self.ball_pos[1] == 0:
            return self.MISS_REWARD
        elif self._successful_hit():
            return self.HIT_REWARD
        return self.NOT_LOST_REWARD

    def _successful_hit(self):
        # Check if ball is 1 away from paddle and is goign away from it
        pass

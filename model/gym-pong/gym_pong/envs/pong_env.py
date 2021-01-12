import gym
import pyglet
from gym import spaces
from gym.utils import seeding
from gym.envs.classic_control import rendering


class PongBoard():

    def __init__(self, L, W, paddle_width, init_ball_pos=None, init_ball_direction=None, init_paddle_pos=None):
        # Board params
        self.L = L
        self.W = W
        self.paddle_width = paddle_width
        self.paddle_range = W - 2 * (paddle_width//2)
        # Optional init params
        self.reset(init_ball_pos, init_ball_direction, init_paddle_pos)

    def reset(self, init_ball_pos, init_ball_direction, init_paddle_pos):
        self.ball_pos = init_ball_pos
        self.ball_direction = init_ball_direction
        self.paddle_pos = init_paddle_pos

    def update(self, paddle_move=0):
        self.paddle_pos = max(0, self.paddle_pos + paddle_move)
        self.paddle_pos = min(self.paddle_pos, self.paddle_range-1)
        # update ball position
        # if ball hits other side of board, take random direction
        # TODO: Ethan - add board update logic

    def get_observation(self):
        return [self.ball_pos[0], self.ball_pos[1], self.ball_direction, self.paddle_pos]

    def missed_ball(self):
        # TODO: Ethan - add logic for when agent misses ball
        pass

    def hit_ball(self):
        # TODO: Ethan - add logic for when agent hits ball
        pass


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
            self.W,
            self.L,
            self.BALL_DIRECTION_NUM,
            self.PADDLE_RANGE
        ])
        self.reward_range = (self.MISS_REWARD, self.HIT_REWARD)
        self.board = PongBoard(self.L, self.W, self.PADDLE_WIDTH)
        self.reset()

    def step(self, action):
        self._take_action(action)
        observation = self.board.get_observation()
        reward = self._get_reward()
        done = reward == self.MISS_REWARD
        info = None
        return observation, reward, done, info

    def reset(self):
        paddle_pos = self.np_random.randint(0, self.PADDLE_RANGE)
        ball_x = self.np_random.randint(0, self.W)
        ball_y = self.np_random.randint(0, self.L)
        ball_pos = (ball_x, ball_y)
        ball_direction = self.np_random.randint(0, self.BALL_DIRECTION_NUM)

        self.board.reset(ball_pos, ball_direction, paddle_pos)

    def render(self, mode='human'):
        ball_radius = 10
        screen_width = 2 * ball_radius * self.W
        screen_height = 2 * ball_radius * self.L

        if self.viewer is None:
            self.viewer = rendering.Viewer(screen_width, screen_height)
            # Ball geom and transform
            ball = rendering.make_circle(radius=ball_radius, res=10, filled=True)
            self.ball_transform = rendering.Transform()
            ball.add_attr(self.ball_transform)
            ball.set_color(0, 0, 0)
            self.viewer.add_geom(ball)
            # Paddle geom and transform
            paddle = rendering.make_capsule(4 * ball_radius, 2 * ball_radius)
            self.paddle_transform = rendering.Transform()
            paddle.add_attr(self.paddle_transform)
            paddle.set_color(0, 0, 0)
            self.viewer.add_geom(paddle)

        ball_x, ball_y = self.board.ball_pos
        ball_x ,ball_y = 2 * ball_radius * ball_x, 2 * ball_radius * ball_y
        self.ball_transform.set_translation(ball_x + ball_radius, ball_y + ball_radius)

        paddle_x, paddle_y = ball_radius * (2 * self.board.paddle_pos + 1), ball_radius
        self.paddle_transform.set_translation(paddle_x, paddle_y)

        return self.viewer.render()


    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None

    def seed(self, seed=None):
        self.np_random , seed = seeding.np_random(seed)
        return [seed]

    def _take_action(self, action):
        if action == 1:
            # Move paddle left
            self.board.update(paddle_move=-1)
        elif action == 2:
            # Move paddle right
            self.board.update(paddle_move=1)
        else:
            # No movement, just update ball location
            self.board.update()

    def _get_reward(self):
        if self.board.missed_ball() == 0:
            return self.MISS_REWARD
        elif self.board.hit_ball():
            return self.HIT_REWARD

        return self.NOT_LOST_REWARD

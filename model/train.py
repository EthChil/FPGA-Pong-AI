import gym
import matplotlib.pyplot as plt

from .pong_agent import PongAgent

episodes = 1000

if __name__ == '__main__':
    env = gym.make('gym_pong:pong-v0')
    agent = PongAgent(env)

    rewards = []
    for i in range(episodes):
        episode_reward = agent.train_step()
        rewards.append(episode_reward)

    plt.plot(rewards)
    plt.show()

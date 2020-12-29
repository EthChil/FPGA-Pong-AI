import numpy as np
import tensorflow as tf

class PongAgent():

    def __init__(self, env, gamma=1, latent_dim=32, learning_rate=2e-10):
        self.env = env
        self.policy = tf.keras.models.Sequential([
            tf.keras.layers.Dense(latent_dim),
            tf.keras.layers.Dense(self.env.action_space.n)
        ])
        self.gamma = gamma
        self.optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate)


    def _env_step(self, action):
        state, reward, done, info = self.env.step(action)
        return (state.as_type(np.int32),
                np.array(reward, np.float32),
                np.array(done, np.bool))

    def _tf_env_step(self, action):
        return tf.numpy_function(self._env_step, [action], [tf.int32, tf.float32, tf.bool])

    def sample_episode(self, max_steps):
        states = tf.TensorArray(dtype=tf.int32, size=0, dynamic_size=True)
        # Cache action probabilities for taken actions to not have to evaluate policy during paramater update
        action_probs = tf.TensorArray(dtype=tf.float32, size=0, dynamic_size=True)
        rewards = tf.TensorArray(dtype=tf.float32, size=0, dynamic_size=True)

        initial_state = tf.constant(self.env.reset(), dtype=tf.float32)
        initial_state_shape = initial_state.shape
        state = initial_state

        for t in tf.range(max_steps):
            self.env.render()

            states = states.write(t, state)
            state = tf.expand_dims(state, 0)

            action_logits = self.policy(state)
            action_probs_t = tf.nn.softmax(action_logits)
            action = tf.random.categorical(action_logits, 1)[0, 0]
            action_probs = action_probs.write(t, action_probs_t[0, action])

            state, reward, done = self._tf_env_step(action)
            state.set_shape(initial_state_shape)

            rewards = rewards.write(t, reward)

            if done:
                break

        states = states.stack()
        action_probs = action_probs.stack()
        rewards = rewards.stack()

        # Return (S, A, R) tuple + cached action probs
        return states, action_probs, rewards

    def _get_returns(self, rewards):
        T = tf.shape(rewards)[0]
        returns = tf.TensorArray(dtype=tf.float32, size=T)

        rewards = tf.cast(rewards[::-1], dtype=tf.float32)
        discounted_sum = tf.constant(0.0)
        discounted_sum_shape = discounted_sum.shape

        # Iteratate backwards through rewards
        for t in tf.range(T):
            reward = rewards[t]
            discounted_sum = reward + self.gamma * discounted_sum
            discounted_sum.set_shape(t, discounted_sum_shape)
            returns = returns.write(t, discounted_sum)

        returns = returns.stack()[::-1]
        return returns


    @tf.function
    def train_step(self, max_steps=100):
        with tf.GradientTape() as tape:
            states, action_probs, rewards = self.sample_episode(max_steps)

            returns = self._get_returns(rewards)

            states, action_probs, rewards = [tf.expand_dims(x, 1) for x in [states, action_probs, rewards]]

        T = tf.shape(rewards)[0]
        for t in tf.range(T):
            # γ^t and G_t should be ignored in auto-differentiation of pi(a|s)
            # Negative sign to maximize eligibility with gradient ascent
            eligibility = -(self.gamma**t) * returns[t] * tf.math.log(action_probs[t])

            grads = tape.gradient(eligibility, self.policy.trainable_variables)

            self.optimizer.apply_gradients(zip(grads, self.policy.trainable_variables))

        episode_rewards = tf.reduce_sum(rewards)

        return episode_rewards

import numpy as np
import json

from Environment import agent
from Environment import server_env
from Qlearn import qlearn

# parameters
epsilon = .4 # exploration
num_actions = 8  # [ # 0 => -2 , 1 => -1 , 2 => 0, 3 => +1, 4 => +2, 5 => flash_change_temp]
epoch = 1000
max_memory = 500
hidden_size = 100
batch_size = 100
grid_size = 10

agent = agent.Agent(learning_rate=0.00001)
model = agent.model

# If you want to continue training from a previous model, just uncomment the line bellow
# model.load_weights("model.h5")

# Define environment/game
env = server_env.Server(optimum_temp=(21.0, 22.0), start_month=0, initial_n_users=20, initial_rdt=30, weight_power=0.8)

# Initialize experience replay object
exp_replay = qlearn.ExperienceReplay(max_memory=max_memory)

# Train
score = 0

for e in range(epoch):

    score = 0
    loss = 0.
    env.reset()
    game_over = False
    # get initial input
    input_t,x,y,z = env.observe()
    timestep = 0

    while (not game_over and timestep < 2000):

        print timestep
        input_tm1 = input_t
        # get next action

        if np.random.rand() <= epsilon:
            action = np.random.randint(0, num_actions, size=1)
            print "EPSILON ACTION:", action
        else:
            q = model.predict(input_tm1)
            print q
            action = np.argmax(q[0])
            print "ACTION:", action
        # apply action, get rewards and new state

        input_t, inp, reward, game_over = env.update_env(action,int(timestep/(200)))

        if reward > 0:
            score += reward

        # store experience
        exp_replay.remember([input_tm1, action, reward, input_t], game_over)

        # adapt model
        inputs, targets = exp_replay.get_batch(model, batch_size=batch_size)

        loss += model.train_on_batch(inputs, targets)

        timestep+=1

    print("Epoch {:03d}/999 | Loss {:.4f} | Win count {}".format(e, loss, score))

# Save trained model weights and architecture, this will be used by the visualization code
model.save_weights("model.h5", overwrite=True)
with open("model.json", "w") as outfile:
    json.dump(model.to_json(), outfile)

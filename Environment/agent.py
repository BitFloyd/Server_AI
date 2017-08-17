from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam


class Agent(object):

    def __init__(self,learning_rate=0.001):

        self.learning_rate = learning_rate
        self.model = Sequential()

        self.model.add(Dense(3, input_dim=3, activation='sigmoid'))
        self.model.add(Dense(2, activation='sigmoid'))
        self.model.add(Dense(8, activation='softmax'))

        # 0 => -2 , 1 => -1 , 2 => 0, 3 => +1, 4 => +2, 5 => flash_change_temp

        self.model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))


import numpy as np


class Server(object):
    # A class that models a server

    """
    Attributes of the server
    ---------------------------

       Constants
       -----------
       Optimum temperature range - core_temp_opt_range - Tuple (min,max) in degree C
       Absolute maximum temperature - core_temp_max
       Absolute minimum temperature - core_temp_min

       Month when simulation is started - start_month
       Number of users that can go up or down per minute - num_users_update
       Data transmission that can change per minute - rdt_update
       Lower threshold for number of users - num_users_lt
       Lower threshold for data transmission - rdt_lt
       Maximum number of users - max_users_ht
       Maximum rdt - max_rdt

       Effect of users on the temperature - effect_users
       Effect of data transmission on temperature - effect_data
       Effect on performance from the number of users if temperature is not optimum - perf_effect_users
       Effect on performance from the rdt if temperature is not optimum - perf_rdt
       Weight given to power saving - weight_power
       Weight given to performance - weight_perf

       Initial number of users - initial_n_users

       Variables
       ---------
       Atmospheric temperature - atm_temp
       Temperature of core - core_temp

       Number of users at time in the server - n_users
       Rate of data transmission - rdt

       Energy spent by AI - energy
       Total energy spent - energy_tot
       Total energy spent without the agent - energy_wo_agent_tot

       Performance score - perf_score

       Score per update - score
       Total score -  score_tot

       status = 1 -> If server is active
       status = 0 -> If server is dead (if temp goes out of extremes)

    """

    avg_temp_month = [11.0, 15.0, 16.0, 20.0, 21.0, 22.0, 23.0, 24.0, 22.0, 20.0, 18.0, 15.0]

    atm_temp = avg_temp_month[0]

    num_users_update = 50
    num_users_lt = 10
    num_users_ht = 300

    initial_n_users = num_users_lt
    n_users = initial_n_users

    rdt_update = 100
    rdt_lt = 20
    rdt_ht = 500

    initial_rdt = rdt_lt
    rdt = initial_rdt

    effect_users = 0.05
    effect_data = 0.05

    core_temp = atm_temp + n_users * effect_users + rdt * effect_data
    maintained_core_temp = core_temp
    core_temp_max = 80
    core_temp_min = -10
    max_change = core_temp_max - core_temp_min

    perf_effect_users = 0.3
    perf_effect_data = 0.1

    energy = 0.0
    energy_tot = 0.0
    energy_wo_agent_tot = 0.0

    perf_score = 0
    weight_perf = 0.5
    weight_power = 0.5

    score = 0.0
    score_tot = 0.0

    game_over = 0

    def __init__(self, optimum_temp=(20.0, 22.0), start_month=0, initial_n_users=10, initial_rdt=60, weight_power=0.5):

        # INITIALIZE THE SERVER

        assert (initial_n_users >= self.initial_n_users)
        self.initial_n_users = initial_n_users

        assert (initial_rdt >= self.initial_rdt)
        self.initial_rdt = initial_rdt

        self.core_temp_opt = optimum_temp
        self.start_month = start_month
        self.atm_temp = self.avg_temp_month[start_month]

        self.n_users = initial_n_users
        self.rdt = initial_rdt

        self.core_temp = self.atm_temp + self.n_users * self.effect_users + self.rdt * self.effect_data
        self.maintained_core_temp = self.core_temp

        self.weight_power = weight_power
        self.weight_perf = 1 - weight_power

    def update_env(self, action, month):


        # DO THE ACTION

        temp_change_from_action = 0
        # temp_change_from_action = action*self.max_change

        # 0 = -2
        # 1 = -1
        # 3 = 0
        # 4 = +1
        # 5 = +2
        # 6 = flash cool

        flash_required = 0
        if (self.maintained_core_temp < self.core_temp_opt[0]):
            flash_required = self.core_temp_opt[0] - self.maintained_core_temp
        elif (self.maintained_core_temp > self.core_temp_opt[1]):
            flash_required = self.core_temp_opt[1] - self.maintained_core_temp

        if (action == 0):
            temp_change_from_action = -3
        elif (action == 1):
            temp_change_from_action = -2
        elif (action == 2):
            temp_change_from_action = -1
        elif (action == 3):
            temp_change_from_action = 0
        elif (action == 4):
            temp_change_from_action = 1
        elif (action == 5):
            temp_change_from_action = 2
        elif (action == 6):
            temp_change_from_action = 3
        elif (action == 7):
            temp_change_from_action = flash_required


        print "---------------------------------------------------"
        print "BEFORE ACTION"
        print "-------------"
        print "MAINTAINED CORE TEMP:", self.maintained_core_temp, "FLASH REQD:", flash_required


        # UPDATE THE ENERGY STATS
        self.energy = temp_change_from_action
        self.energy_tot += temp_change_from_action
        self.energy_wo_agent_tot += flash_required

        # GET THE SCORE TO BE RETURNED. SCORE - Energy saved - Performance
        self.score = (self.weight_perf * np.abs(flash_required))**2 - self.weight_power * np.abs(temp_change_from_action)**2
        self.score = 10*self.score

        # self.score = self.weight_power * (flash_required - temp_change_from_action) - self.weight_perf * (flash_required)
        self.score_tot += self.score

        # UPDATE THE ENV
        new_n_users = self.n_users + np.random.randint(-self.num_users_update, self.num_users_update)

        if (new_n_users > self.num_users_ht):
            new_n_users = self.num_users_ht
        elif (new_n_users < self.num_users_lt):
            new_n_users = self.num_users_lt

        new_rdt = self.rdt
        if (new_rdt > self.rdt_ht):
            new_rdt = self.rdt_ht
        elif (new_rdt < self.rdt_lt):
            new_rdt = self.rdt_lt

        self.n_users = new_n_users
        self.rdt = new_rdt

        self.atm_temp = self.avg_temp_month[month]
        core_temp_past = self.core_temp
        self.core_temp = self.atm_temp + self.n_users * self.effect_users + self.rdt * self.effect_data
        core_temp_delta = self.core_temp - core_temp_past

        print "CTD:", core_temp_delta
        self.maintained_core_temp = self.maintained_core_temp + core_temp_delta + temp_change_from_action

        if (self.maintained_core_temp > self.core_temp_max or self.maintained_core_temp < self.core_temp_min):
            self.game_over = 1

        # Return the maintained_core_temp, the score, and the game status.


        scaled_core_temp = (self.maintained_core_temp - self.core_temp_min) / (self.core_temp_max - self.core_temp_min + 0.0)
        scaled_n_users = (self.n_users-self.num_users_lt)/(self.num_users_ht-self.num_users_lt)
        scaled_rdt = (self.rdt-self.rdt_lt)/(self.rdt_ht-self.rdt_lt)

        scaled_states = np.matrix([scaled_core_temp,scaled_n_users,scaled_rdt])

        print "AFTER ACTION"
        print "MAINTAINED CORE TEMP:", self.maintained_core_temp, "SCORE:", self.score

        return scaled_states, self.maintained_core_temp, self.score, self.game_over

    def reset(self):
        self.atm_temp = self.avg_temp_month[self.start_month]

        self.n_users = self.initial_n_users
        self.rdt = self.initial_rdt

        self.core_temp = self.atm_temp + self.n_users * self.effect_users + self.rdt * self.effect_data
        self.maintained_core_temp = self.core_temp
        self.game_over = 0
        self.energy = 0
        self.energy_tot = 0
        self.energy_wo_agent_tot = 0

    def observe(self):
        scaled_core_temp = (self.maintained_core_temp - self.core_temp_min) / (self.core_temp_max - self.core_temp_min + 0.0)
        scaled_n_users = (self.n_users-self.num_users_lt)/(self.num_users_ht-self.num_users_lt)
        scaled_rdt = (self.rdt-self.rdt_lt)/(self.rdt_ht-self.rdt_lt)

        scaled_states = np.matrix([scaled_core_temp,scaled_n_users,scaled_rdt])

        return scaled_states, self.maintained_core_temp, self.score, self.game_over

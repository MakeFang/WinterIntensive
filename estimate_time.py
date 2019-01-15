import numpy as np
import pandas as pd
import seaborn as sns
import scipy as sp
import copy
import scipy.integrate as integrate


class TimeEstimation(object):

    def __init__(self, num_table = 4, rv = sp.stats.gamma(36, loc = 0., scale = 50.)):
        self.num_table = num_table
        self.rv = rv
        self.cur_state = self.current_state()

    def current_state(self):
        return self.rv.rvs(size=self.num_table)

    def sf_after_t(self, t_0, t_1):
        return self.rv.sf(t_1)/self.rv.sf(t_0)

    def waiting_dist(self, cur_state):
        return lambda x: np.prod([self.sf_after_t(cur_state[i], cur_state[i]+x) for i in range(self.num_table)])

    def get_waiting_cdfs(self, num_in_queue):
        current_dining_state = copy.deepcopy(self.cur_state)
        result_cdf = []
        result_mean = []
        cur_cdf = 0
        for i in range(num_in_queue):
            cur_cdf = self.waiting_dist(current_dining_state)
            cur_mean, cur_error = integrate.quad(cur_cdf, 0, 3500)
            current_dining_state += cur_mean
            current_dining_state[np.argmax(current_dining_state)] = 0
            result_cdf.append(cur_cdf)
            result_mean.append(cur_mean)
            # print(cur_mean)
        return result_cdf, result_mean

    def get_total_time(self, num_in_queue):
        result_cdf, result_mean = self.get_waiting_cdfs(num_in_queue)
        return np.cumsum(result_mean)

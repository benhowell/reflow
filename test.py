import os
import sys

import config as conf

from reflow import subscribe, dispatch, state
from reflow.registry import state as app_state

def main():

    print("state: ", app_state)
    dispatch('state', ['count'], 78)
    dispatch('state', ['count_x_2'], 146)
    dispatch('state', ['devil', 'beast'], 421)
    print("state 1: ", app_state)

    print("state [count]: ", state('count'))
    print("state [count_x_2]: ", state(['count_x_2']))
    print("subscribe [jesus]", subscribe('jesus'))
    print("subscribe [jesus_saves_2]", subscribe('jesus_saves_2'))
    print("state [devil, beast]: ", state(['devil', 'beast']))



if __name__ == "__main__":
    main()

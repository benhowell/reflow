import os
import sys

import config as conf

from reflow import subscribe, dispatch, state
from reflow.registry import state as app_state

def main():

    print("state: ", app_state)
    dispatch('state', ['count'], 78)
    dispatch('state', ['count_x_2'], 146)
    dispatch('state', ['path_to', 'another_number'], 421)
    print("state 1: ", app_state)

    print("state [count]: ", state('count'))
    print("state [count_x_2]: ", state(['count_x_2']))
    print("subscribe [var1]", subscribe('var1'))
    print("subscribe [var2]", subscribe('var2'))
    print("subscribe [var3]", subscribe('var3'))
    print("state [path_to, another_number]: ", state(['path_to', 'another_number']))



if __name__ == "__main__":
    main()

import os
import sys
ROOT_PATH = os.path.abspath(os.getcwd())
if not ROOT_PATH in sys.path:
    sys.path.insert(0, ROOT_PATH)

from reflow import subscribe, dispatch, state
from reflow.registry import state as app_state
from reflow.registry import pg_notifier

def main():

    pg_notifier.subscribe(
        'abc', lambda k,x: print("[pg_listener] test callback: ", k, " -> ", x))


    print(app_state)
    dispatch('state', ['count'], 78)
    dispatch('state', ['count_x_2'], 146)
    dispatch('state', ['devil', 'beast'], 421)
    print(app_state)

    pg_notifier.subscribe(
        'xyz', lambda k,x: print("[pg_listener] test xyz callback: ", k, " -> ", x))


    print(state('count'))
    print(state(['count_x_2']))
    print(subscribe('jesus'))
    print(subscribe('jesus_saves_2'))
    print(state(['devil', 'beast']))

    pg_notifier.subscribe(
        '123', lambda k,x: print("[pg_listener] test again callback: ", k, " -> ", x))


if __name__ == "__main__":
    main()

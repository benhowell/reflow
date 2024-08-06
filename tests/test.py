from reflow import subscribe, dispatch, state
#from reflow.subs import subscribe, state
#from .router import dispatch
from reflow.registry import state as app_state

def run():
	print(app_state)
	dispatch('state', ['count'], 78)
	dispatch('state', ['count_x_2'], 146)
	dispatch('state', ['devil', 'beast'], 421)
	print(app_state)

	print(state('count'))
	print(state(['count_x_2']))
	print(subscribe('jesus'))
	print(subscribe('jesus_saves_2'))
	print(state(['devil', 'beast']))


def main():
    run()

if __name__ == "__main__":
    main()

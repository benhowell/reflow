from reflow.subs import subscribe, state
from .router import dispatch
from .registry import state as st

print(st)
dispatch('state', ['count'], 78)
dispatch('state', ['count_x_2'], 146)
dispatch('state', ['devil', 'beast'], 421)
print(st)

print(state('count'))
print(state(['count_x_2']))
print(subscribe('jesus'))
print(subscribe('jesus_saves_2'))
print(state(['devil', 'beast']))

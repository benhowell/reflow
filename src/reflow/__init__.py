"""Reactive-flow state management framework."""

__version__ = "0.0.1"

#----------------------------------------------#

# Imported public functions from various modules
#from .subs import sub
#from .events import event

from reflow.containers import box
from reflow.util import get_in, upssoc_in
from reflow.subs import subscribe, state, register_flow
from reflow.events import event
from reflow.router import dispatch

#from reflow.core import help



# __all__ = (
#     # public functions
#     #"reflow",
#     "sub",
#     "event",
#     "subscribe",
#     "dispatch",
#     "help",
# )

#
# registry.py
#
"""
Module that acts as a centralized global registry.
"""

import config
import pyrsistent as pyr

from reflow.containers import Box
from reflow.util import get_in, upssoc_in



"""
State

Application level access to state is via event and subscription handlers only.
"""
state = Box(pyr.pmap({'count': 43, 'letters': 'abc',
                      'devil': {'beast': 666, 'adjesus': 623}}))


def get_in_state(pv):
    return get_in(state.unbox(), pv)


"""
Flow register
"""
flows = Box(pyr.m())


def flow_path(id):
    return get_in(flows.unbox(), [id, 'path'])


def get_flow(id):
    return get_in(flows.unbox(),[id])


"""
 Handler fn register for processing all events in reflow.
 Handler map is keyed by handler kind (event, sub, error, etc.) and id.

 Everything that happens in reflow affects state.

 Pre-configured with generic state change, and state subscription
 handler references. See events.py for those specific handlers.
"""
handlers = Box(pyr.m(event={}, fx={}, cofx={}, error={}))


def register_handler(kind, id, interceptors):
    handlers.swap(upssoc_in, [kind, id], interceptors)


def handler(kind, id):
    return get_in(handlers.unbox(), [kind, id])


"""
 Router event dispatch queue
"""
dq = Box(pyr.dq()) # FIFO queue of incoming dispatch events.

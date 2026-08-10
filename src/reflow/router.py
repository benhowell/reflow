"""
Dispatch router finite state machine
"""

import pyrsistent as pyr
from reflow.registry import dq, handler


def _exec_callbacks(ev, dq):
    print("    _exec_callbacks : {x}, {y}".format(x=ev, y=dq))



def context(event, interceptors):
    return pyr.pmap({
        'coeffects': {
            'event': event,
            'o_event': event},
        'queue': pyr.pdeque(interceptors),
        'stack': pyr.pdeque()})



def exec_interceptors(ctx, direction):
    ds = 'queue'
    if direction == 'after':
        ds = 'stack'
    while len(ctx[ds]) > 0:
        fn = ctx[ds].left.get(direction, None)
        if fn:
            try:
                ctx = fn(ctx)
            except Exception as e:
                print(e)
        if direction == 'before':
            ctx = ctx.set('stack', ctx['stack'].appendleft(ctx['queue'].left))
        ctx = ctx.set(ds, ctx[ds].popleft())
    return ctx



def _run_queue(*args):
    """
    Processes what's currently in the queue. New events will continue to be
    queued and processed in a future run.
    """

    qlen = len(dq.unbox()) # only process what's in queue now...
    events = dq.unbox()[qlen:]
    for ev in events:

        #fn = handler('event', ev[0])
        #r = fn(state, ev[1], ev[2])

        if interceptors := handler('event', ev[0]):
            ctx = context(ev, interceptors)
            error_handler = handler('error', 'event_handler')
            direction = 'before'
            try:
                ctx = exec_interceptors(ctx, direction)
                direction = 'after'
                ctx = exec_interceptors(ctx, direction)
            except Exception as e:
                error_handler(e, ev, direction)
        dq.swap(lambda q: q.popleft())
        _exec_callbacks(ev, dq)

    # if more events entered the queue during processing, run_queue again
    if len(dq.unbox()) > 0:
        return 'run_queue'
    # else, end run
    return 'end_run'



def _exception(ex):
    print(ex)
    return 'idle'



def _end_run(*args):
    return None



def fsm(t):
    # State transition table
    # Key: (state_0, trigger)
    # Value (action_fn, state_1)
    stt = pyr.pmap({
    #    state_0  &  trigger  -->  action   &   state_1
        ('idle',    'run_queue'): (_run_queue, 'running'),
        ('running', 'run_queue'): (_run_queue, 'running'),
        ('running', 'exception'): (_exception, 'idle'),
        ('running', 'end_run'):   (_end_run,   'idle')})

    s = 'idle'
    def trigger_arg(t):
        nonlocal stt
        nonlocal s
        try:
            f,s = stt[(s,t)]   # fn and next state (fn, s1 <- s0, t0)
            t = f()            # next trigger <- fn (t1 <- fn)
            if t is None:      # if no trigger, end of run.
                return
            trigger_arg(t)     # else, trigger next run
        except Exception as ex:
            print("exception: ", ex)
            s = 'idle'
            return
    trigger_arg(t)



def dispatch(handler_id, qv, val):
    event = pyr.v(handler_id, qv, val)
    dq.swap(lambda q, v: q.append(v), event)
    fsm('run_queue')

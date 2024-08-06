import pyrsistent as pyr

from decorator import decorate
from .graph import run_graph

from .util import (
    dict_diff,
    update_in,
    upssoc_in,
    assoc,
    dissoc,
    update,
    mapkv)

from .registry import (
    register_handler,
    handler,
    flows,
    state)


def flow_fx_ids():
    return pyr.pvector(['register_flow', 'remove_flow'])


def interceptor(id=None, comment=None, before=None, after=None):
    return pyr.pmap(
        {'id': 'unnamed' if not id else id,
         'before': before,
         'after': after,
         'comment': comment})


def debug():
    def before(ctx):
        print("[DEBUG] Handling coeffects: ", ctx['coeffects'])
        print("        Handling event: ", ctx['coeffects']['event'])
        return ctx

    def after(ctx):
        print("\n[DEBUG] context: ", ctx)
        event = ctx['coeffects']['event']
        o_state = ctx['coeffects']['state']
        n_state = ctx['effects'].get('state', None)
        if not n_state:
            print("[DEBUG] state unchanged post event: ", event, "\n")
        else:
            only_before, only_after, common_d1, common_d2 = dict_diff(o_state, n_state)
            if only_before or only_after:
                print("[DEBUG] state change post event: ", event)
                print("        old state: ", o_state)
                print("        new state: ", n_state)
                print("[DEBUG] difference between old and new state")
                print("        only in old state: ", only_before)
                print("        only in new state: ", only_after)
                print("[DEBUG] common to old and new state (MUST MATCH!)")
                print("        common old -> new: ", common_d1)
                print("        common new -> old: ", common_d2)
                print("        difference: ", [
                    i for i in common_d1 if i not in common_d2], "\n")
            else:
                print("[DEBUG] state unchanged post event: ", event, "\n")
        return ctx
    return interceptor(id='debug', before=before, after=after)



def do_flow_fx():
    def after(ctx):
        effects = ctx.get('fx')
        if not effects:
            return ctx
        ctx = ctx['effects']
        flow_fx = pyr.pmap({k: effects[k] for k in flow_fx_ids()})
        mapkv(lambda k,v: handler('fx', k)(v), flow_fx)
        ctx = update_in(ctx, ['effects', 'fx'], lambda x: dissoc(x, flow_fx_ids))
        ctx = update(ctx, 'effects', lambda x: dissoc(x, flow_fx_ids))
        return ctx
    return interceptor(id='do_flow_fx', after=after)



def flow_interceptor():
    def after(ctx):
        nctx = upssoc_in(
            ctx, ['effects','pre_flow_state'],
            ctx['effects']['state'])
        return run_graph(nctx, flows)
    return interceptor(id='flow', after=after)



def do_fx():
    def after(ctx):
        effects = ctx['effects']
        effects_no_state = dissoc(effects, 'state')
        if n_state := effects.get('state'):
            handler('fx', 'state')(n_state)
        for k,v in effects_no_state.items():
            if effect_fn := handler('fx', k):
                effect_fn(v)
        return ctx
    return interceptor(id='do_fx', after=after)



def inject_cofx(id, val=None):
    def before(ctx):
        if handler_fn := handler('cofx', id):
            if val:
                ctx = update(ctx, 'coeffects', handler_fn, val)
            else:
                ctx = update(ctx, 'coeffects', handler_fn)
        return ctx
    return interceptor(id='coeffects', before=before)



### event handler interceptor factories ###
# - state: @event(id)
# - fx:    @fx(id)...  TODO: not implemented yet
# - ctx:   @ctx(id)... TODO: not implemented yet

def state_handler_interceptor(fn):
    def before(ctx):
        state = ctx['coeffects']['state']
        event = ctx['coeffects']['event']
        if r := fn(state, event[1], event[2]):
            ctx = upssoc_in(ctx, ['effects', 'state'], r)
        return ctx
    return interceptor(id='state_handler', before=before)

### END event handler interceptor factories ###



#FIXME: this should be custom exception class
def default_error_handler(error, event, direction):
    print("ERROR: ", error, " during event: ", event, " while processing: ", direction)



def state_effects_handler(newv):
    if not state.unbox() == newv:
        state.reset(newv)



def state_coeffects_handler(cofx):
    return assoc(cofx, 'state', state.unbox())



def dec(f, id, kind):                   # decorator
    f.__name__ = kind + '_' + id + '_fn'
    f.__qualname__ = f.__name__
    def fix_sig(f, *args, **kwargs):    # do nothing...
        return f(*args, **kwargs)       # fn is a hack to use decorate...
    return decorate(f, fix_sig)         # to clone fn and all attrs



def event(id):                     # decorator decorator, returning...
    def dp(f):                     # decorator partial, returning...
        dfn = dec(f, id, 'event')
        register_handler(
            'event', id,
            pyr.pvector([inject_cofx('state'), do_fx(), debug(),
             flow_interceptor(), do_flow_fx(),
             state_handler_interceptor(dfn)]))
        return dfn                 # decorator
    return dp



register_handler('fx', 'state', state_effects_handler)
register_handler('cofx', 'state', state_coeffects_handler)
register_handler('error', 'event_handler', default_error_handler)

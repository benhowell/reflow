import pyrsistent as pyr

from .registry import flow_path, flows
from .exceptions import GraphCycleError

from .util import (
    cache,
    get_in,
    update_in,
    upssoc_in,
    is_dict)



def resolve_inputs(inputs, _state):
    r = pyr.pmap()
    for k,v in inputs.items():
        r = r.set(k, pyr.pmap())
        if is_dict(v):
            ref = list(v)[0]
            if ref == 'path':
                r = r.set(k, get_in(_state, v[ref]))
            if ref == 'flow':
                r = r.set(k, get_in(_state, flow_path(v[ref])))
    return r



def run(ctx, graph):
    """
    active -> active:   run output (when inputs have changed)
    inactive -> active: run output
    new -> active:      run output
    active -> inactive: run remove
    active -> removed:  run remove
    """
    for k,v in graph.items():
        o_state  = get_in(ctx, ['coeffects', 'state'])
        o_inputs = resolve_inputs(v['inputs'], o_state)
        n_state  = ctx['effects'].get('state', o_state)
        n_inputs = resolve_inputs(v['inputs'], n_state)

        s0 = s1 = 'inactive'
        if v['__new__']:
            s0 = 'new'
        elif v['is_active'](resolve_inputs(v['active_inputs'], o_state)):
            s0 = 'active'

        if v['__removed__']:
            s1 = 'removed'
        elif v['is_active'](resolve_inputs(v['active_inputs'], n_state)):
            s1 = 'active'

        match [s0,s1]:
            case ['active', 'active']:
                if o_inputs != n_inputs:
                    n_state = upssoc_in(n_state, v['path'], v['output'](**n_inputs))
            case ['active', 'inactive']:
                n_state = v['remove'](n_state, v['path'])
            case ['inactive', 'active']:
                upssoc_in(n_state, v['path'], v['output'](**n_inputs))
            case ['new', 'active']:
                flows.swap(upssoc_in, [v['id'], '__new__'], False)
                n_state = upssoc_in(n_state, v['path'], v['output'](**n_inputs))
            case ['active', 'removed']:
                n_state = v['remove'](n_state, v['path'])
            case _:
                pass
        if n_state:
            ctx = upssoc_in(ctx, ['effects', 'state'], n_state)
    return ctx



def topsort_kahn(graph):
    top_order = pyr.pvector()
    q = pyr.dq()
    for k,v in graph.items():
        if get_in(v, ['edges', 'in', 'degree']) == 0:
            q = q.append(k)

    while len(q) > 0:
        top_order = top_order.append(q.left)
        for v in get_in(graph, [q.left, 'edges', 'out', 'vertices']):
            graph = update_in(graph, [v, 'edges', 'in', 'degree'], lambda x: x-1)
            if get_in(graph, [v, 'edges', 'in', 'degree']) == 0:
                q = q.append(v)
        q = q.popleft()

    if len(top_order) == len(graph):
        return top_order
    else:
        raise GraphCycleError()




def calc_graph(_flows):
    vdm = pyr.pmap({'vertices': pyr.pvector(), 'degree': 0})

    def _update_edges(x,y):
        if not x:
            return pyr.pmap({'vertices':pyr.pvector([y]), 'degree':1})
        return pyr.pmap({'vertices':x['vertices'].append(y), 'degree':x['degree']+1})

    def _map_args(x, f, id):
        if not id in x:
            x = x.set(id, f.set('edges', pyr.pmap({'in': vdm, 'out': vdm})))
        else:
            if not 'in' in get_in(x, [id, 'edges']):
                x = upssoc_in(x, [id, 'edges', 'in'], vdm)
            if not 'out' in get_in(x, [id, 'edges']):
                x = upssoc_in(x, [id, 'edges', 'out'], vdm)
        return x

    g = pyr.pmap()
    for id, f in _flows.items():
        inputs = f['inputs'].update(f['active_inputs'])
        g = _map_args(g, f, id)
        for k,v in inputs.items():
            ins = list(v.items())[0]
            if ins[0] == 'flow':
                g = update_in(g, [id, 'edges', 'in'], _update_edges, ins[1])
                g = _map_args(g, _flows[ins[1]], ins[1])
                g = update_in(g, [ins[1], 'edges', 'out'], _update_edges, id)
    return g



@cache
def topsort(_flows):
    graph = calc_graph(_flows)
    node_order = topsort_kahn(graph)
    return {k: graph[k] for k in node_order}


def run_graph(ctx, flows):
    _flows = topsort(flows.unbox())
    return run(ctx, _flows)

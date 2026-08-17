import pyrsistent as pyr
from reflow.exceptions import FlowArgumentError, SubscribeArgumentError
from .util import is_str, upssoc_in, is_list, is_dict, any_key, dissoc
from .registry import flows, get_in_state, flow_path, get_flow


def flow(id):
    return pyr.pmap({'flow': id})


def path(p):
    return pyr.pmap({'path': p})


def state(p):
    if is_list(p):
        return get_in_state(p)
    elif is_str(p):
        return get_in_state([p])
    else:
        print("ERROR")


def subscribe(id, *args):
    return get_in_state(flow_path(id))


def validate_flow(m):
    if id := m['id']:
        pass
    else:
        raise FlowArgumentError(m['id'], 'id')
    if inputs := m['inputs']:
        for k,v in inputs.items():
            if not is_list(v):
                if not is_dict(v):
                    raise FlowArgumentError(id, 'input_args')
                elif not any_key(['flow', 'path'], v):
                    raise FlowArgumentError(id, 'input_args')
    else:
        raise FlowArgumentError(id, 'inputs')
    if output := m['output']:
        pass
    else:
        raise FlowArgumentError(id, 'output')



def default_flow(id):
    return pyr.pmap({
        'id': id,
        '__new__': True if not get_flow(id) else False,
        '__removed__': False,
        'path': pyr.pvector([id]),
        'inputs': pyr.pmap(),
        'active_inputs': pyr.pmap(),
        'is_active': lambda m: True,
        # could dissoc, set to None, set to unknown, do nothing, etc.
        'remove': lambda x, y: upssoc_in(x, y, 'unknown')})


def register_flow(d):
    mid = d['id']
    m = default_flow(mid)
    m = m.update(d)

    def _input_paths(x,y,ik):
        if ik in y:
            for k,v in y.get(ik).items():
                x = upssoc_in(x, [ik,k], path(v) if is_list(v) else v)
        return x

    m = _input_paths(m, d, 'inputs')
    m = _input_paths(m, d, 'active_inputs')

    try:
        validate_flow(m)
    except FlowArgumentError as e:
        print(e.message)
        return

    flows.swap(upssoc_in, pyr.pvector([mid]), m)



#TODO:
#register_fx
#register_ctx


register_flow({
    'id': 'var1',
    'inputs': {'count': ['count'],
               'number': path(['path_to', 'another_number']),
               'factor': {'path': ['path_to', 'var1_adjusted']}},
    'output': lambda count, number, factor: (
        count + factor) if number != 666 else (number - factor)})


register_flow({
    'id': 'var2',
    'inputs': {'number': flow('var1_adjusted')},
    'output': lambda number: number*2})


register_flow({
    'id': 'var3',
    'inputs': {'number': {'flow': 'var1_adjusted'}},
    'output': lambda number: number*3})

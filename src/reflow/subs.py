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



#FIXME:
#register_fx
#register_ctx


# def jesus(count, number, adjust):
#     print("running jesus")
#     if number != 666:
#         return count + adjust
#     else:
#         return number - adjust


register_flow({
    'id': 'jesus',
    'inputs': {'count': ['count'],
               'number': path(['devil', 'beast']),
               'adjust': {'path': ['devil', 'adjesus']}},
    #'output': jesus
    'output': lambda count, number, adjust: (
        count + adjust) if number != 666 else (number - adjust)
              })


register_flow({
    'id': 'jesus_saves',
    'inputs': {'number': flow('jesus')},
    'output': lambda number: number*2})


register_flow({
    'id': 'jesus_saves_2',
    'inputs': {'number': {'flow': 'jesus'}},
    'output': lambda number: number*3})






# (reg-event-fx
#  :sync-study-callback
#  (fn [{db :db} [_ on-success-events data]]
#    {:db (assoc db :current-study data)
#     :dispatch-n (cset/union
#                  (list [:reset-tree-view]) on-success-events)}))


# (reg-event-fx
#  :sync-study
#  (fn [_ [_ id on-success-events]]
#    {:ws-send! {:event [:event/db {:ev-id :get-study :id id}]
#                :on-success on-success-events
#                :on-failure [:ws-fail]}}))




# def subscribe(*args):
#     if not args:
#         raise SubscribeArgumentError()
#     if is_dict(args[0]):
#         if len(args) != 1:
#             raise SubscribeArgumentError()
#         k,v = args[0].popitem()
#         if k == 'state':
#             return get_in_state(v['path'])
#         if k == 'flow':
#             return get_in_state(flow_path(v['id']))
#     else:
#         if len(args) != 2:
#             raise SubscribeArgumentError()
#         if args[0] == 'state':
#             return get_in_state(args[1])
#         if args[0] == 'flow':
#             return get_in_state(flow_path(args[1]))
#     return None


# def sub_state(path):
#     """Alias"""
#     return subscribe('state', path)


# def sub_flow(id):
#     """Alias"""
#     return subscribe('flow', id)








# def jesus_saves_2_signal(height, width):
#     if height != 0:
#         return height * width
#     else:
#         z = state(['devil', 'beast'])
#         return z * width

# register_flow({
#     'id': 'jesus_saves_2',
#     'inputs': {'number': {'flow': 'jesus'}},
#     'output': jesus_saves_2})


# register_flow({
#     'id': 'jesus_saves_2',
#     'inputs': {'number': {'flow': 'jesus'}},
#     'output': (fn(height, width):
#                if height != 0:
#                return height * width
#                else:
#                z = state(['devil', 'beast'])
#                return z * width)})





# # implicit extract/compute (layer 2)
# @sub('state')
# def _(qry_v):
#     def compute(state, qry_v):
#         return get_in(qry_v, state)

# # implicit extract/compute (layer 2)
# @sub('state_1')
# def _(state, qry_v):
#     return get_in(qry_v, state) # <-- syntactic sugar for explicit compute



# #FIXME: if qry_v not supplied, insert qry_v when creating fn
# # explicit extract/compute (layer 2)
# @sub('get_count')
# def _():
#     def compute(state): # <-- explicit compute
#         return get_in(['count'], state)


# # materialised view (layer 3)
# # NOTE: materialised views must always use an explicit compute fn
# @sub('greeting')
# def _():
#     def signal():                  # <-- fn returns args used in compute
#         return subscribe('get_count')
#     def compute(count):            # <-- count arg is value returned from signal fn
#         return "Hello " + str(count)



# @event('state')
# def _(state, qry_v, val):
#     print("event_state_fn")
#     state.swap(upssoc_in, qry_v, val)
#     return get_in(qry_v, state.deref())




# @event('set_count')
# def _(state, qry_v, val):
#     print("event_state_fn")
#     state.swap(upssoc_in, qry_v, val)
#     return get_in(qry_v, state.deref())







# {

#  'jesus': {
#     'is_active': True,
#     'id': 'jesus',
#     'when_inactive': 'inactive',
#     'path': ['jesus'],
#     'active_inputs': {},
#     'inputs': {'count': {'path': ['count']},
#                'adjust': {'path': ['adjesus']},
#                'number': {'path': ['devil', 'beast']}},
#     'output': <function <lambda> at 0x7f6c4aaabd00>},

#  'jesus_saves': {
#      'is_active': True,
#      'id': 'jesus_saves',
#      'when_inactive': 'inactive',
#      'path': ['jesus_saves'],
#      'active_inputs': {},
#      'inputs': {'number': {'flow': 'jesus'}},
#      'output': <function <lambda> at 0x7f6c4aaabd90>},

#  'jesus_saves_2': {
#      'is_active': True,
#      'id': 'jesus_saves_2',
#      'when_inactive': 'inactive',
#      'path': ['jesus_saves_2'],
#      'active_inputs': {},
#      'inputs': {'number': {'flow': 'jesus'}},
#      'output': <function <lambda> at 0x7f6c4aaabe20>}
#  }



# def sub(id):                       # decorator decorator, returning...
#     def dp(f):                     # decorator partial, returning...

#         print("sub: register handler_fn reaction")
#         # define new fn that takes signal qry_v and compute qry_v

#         signal_fn = make_signal_fn(f, id)
#         compute_fn = make_compute_fn(f, id)
#         cache_node(id, {'signal_fn': signal_fn, 'compute_fn': compute_fn})

#         #return graph


#         def fn(state=None, qry_v=None):
#             #subscriptions = exec_signal_fn(f, id, qry_v)

#             # def subscription():
#             #     if nargs == 1:
#             #         return compute_fn(deref_signals(subscriptions))
#             #     elif nargs == 2:
#             #         return compute_fn(deref_signals(subscriptions), qry_v)
#             #     else:
#             #         return None

#             # reaction = Reaction(subscription, id)
#             # return reaction
#             return None
#         # fn.__name__ = 'sub_' + id + '_fn'
#         # fn.__qualname__ = fn.__name__

#         #register_handler('sub', id, fn)

#         return fn                   # decorator
#     return dp

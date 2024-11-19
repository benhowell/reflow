import copy
import operator
import typing
import inspect
from decorator import decorator
import pyrsistent as pyr
from concurrent.futures import ThreadPoolExecutor
import asyncio
import functools
from .exceptions import DictTypeError


def as_async(fn, *args):
    loop = asyncio.new_event_loop()
    result = loop.run_in_executor(ThreadPoolExecutor(max_workers=1), fn, *args)
    return result


def cache(f):
    return functools.cache(f)


def partial(f,a):
    return functools.partial(f,a)


def get_in(m,pv,default=None):
    try:
        return functools.reduce(operator.getitem, pv, m)
    except (KeyError, TypeError):
        return default


def key_in(m,pv):
    if get_in(m,pv):
        return True
    return False


def mset(m,pv,v):
    """
    `mset`

    Map set. Set or update a value in nested map `m` by path `pv`.
    Path (or part thereof) will be created if it doesn't already exist.
    """
    _nm = nm = dict_copy(m)
    for i, k in enumerate(pv):
        if i == len(pv) - 1:
            _nm[k] = v
        else:
            if not k in _nm:
                _nm[k] = {}
            elif not dict_type(_nm[k]):
                _nm[k] = {}
            _nm = _nm[k]
    return pyr.freeze(nm, strict=True) if dict_type(m) == 'pmap' else nm



def upssoc_in(m,pv,v):
    """
    Nested map update.
    If pv path exists and current v == new v, return orig unmodified map.
    If pv path exists and current v != new v, set v, return new map.
    If pv path does not exist, create key(s), set v, return new map.
    """
    if get_in(m, pv) != v:
        m = mset(m, pv, v)
    return m



def assoc(m,k,v):
    return upssoc_in(m,[k],v)


def dissoc(m,k):
    nm = dict_copy(m)
    try:
        del nm[k]
    except (KeyError):
        pass
    return pyr.freeze(nm, strict=True) if dict_type(m) == 'pmap' else nm


def dissoc_in(m,pv):
    *_pv, k = pv
    nm = dict_copy(m)
    del functools.reduce(operator.getitem, _pv, nm)[k]
    return pyr.freeze(nm, strict=True) if dict_type(m) == 'pmap' else nm


def update(m,k,f,*args):
    if not args:
        return upssoc_in(m, [k], f(get_in(m,[k])))
    return upssoc_in(m, [k], f(get_in(m,[k]), args))


def update_in(m,pv,f,*args):
    if not args:
        return upssoc_in(m, pv, f(get_in(m,pv)))
    return upssoc_in(m, pv, f(get_in(m,pv), *args))


#TODO: allow return of dict or pmap
def list_to_dict(v):
    """
    Converts alternating key, value list to a dict
    """
    ks = v[::2]
    vs = v[1::2]
    return {ks[i]: vs[i] for i in range(len(ks))}



def var_name(v,a):
    """
    a: how many ancestors to look back... could prob use a max instead, then
       loop from max to current until found
    """
    f = inspect.currentframe()
    p = inspect.getouterframes(f)[a]
    for k, val in p.frame.f_locals.items():
        if val is v:
            return k
    return


def rename_fn(f,a=1):
    """
    Renames a function to be that of the var that holds that function.
    e.g.
    my_print_fn = print
    > my_print_fn.__name__
    > print

    my_print_fn = rename_fn(my_print_fn)
    > my_print_fn.__name__
    > my_print_fn
    """
    if not callable(f):
        print("Error [rename_fn]: variable is not a callable function")
        return
    n = var_name(f,a+1)
    if not n:
        print("Error [rename_fn]: variable not found")
        return
    f.__name__ = f.__qualname__ = n
    return f

FIXME: datastructure, fn, *args

def mapv(fn,v,*a):
    return {fn(v,*a) for v in v}


def mapkv(fn,m,*a):
    return {fn(k,v,*a) for (k,v) in m.items()}


def filterkv(fn,m,*a):
    return {k:v for (k,v) in m.items() if fn(k,v,*a)}


def is_str(x):
    if isinstance(x, str) \
        or type(x) == str:
        return True
    return False


def is_list(x):
    if isinstance(x, list) \
        or type(x) == list \
        or isinstance(x, pyr._pvector.PVector):
        return True
    return False


def is_dict(x):
    if isinstance(x, dict) \
        or type(x) == dict \
        or isinstance(x, typing.Dict) \
        or isinstance(x, pyr._pmap.PMap):
        return True
    return False


def list_eq(x,y):
    _len = lambda a: 0 if not a else len(a)
    x_len = _len(x)
    y_len = _len(y)
    if x_len == y_len:
        for i,v in enumerate(x):
            if x[i] != y[i]:
                return False
    return True


def dict_copy(m,thaw=True):
    dtype = dict_type(m)
    if dtype == 'pmap':
        if thaw:
            return pyr.thaw(m, strict=True)
        return m.copy()
    elif dtype == 'dict':
        return copy.deepcopy(m)
    else:
        raise DictTypeError("[ERROR] Unable to copy dictionary/map. Unrecognised type.")


def dict_type(m):
    if isinstance(m, pyr._pmap.PMap):
        return 'pmap'
    elif isinstance(m, typing.Dict):
        return 'dict'
    else:
        return False


def dict_diff(m1,m2):
    acc={'m1': [], 'm2': [], 'common_m1': [], 'common_m2': []}

    def _sort(m):
        return sorted(m, key=lambda x: x['path'])

    def _diff(x,y,m,acc,path):
        c = 'common_' + str(m)
        for k in x:
            if k in y:
                if is_dict(x[k]):
                    _diff(x[k],y[k], m, acc, path.__add__([k]))
                elif x[k] != y[k]:
                    acc[m] = acc[m] + [{'path': path.__add__([k]), 'val': y[k]}]
                elif x[k] == y[k]:
                    acc[c] = acc[c] + [{'path': path.__add__([k]), 'val': x[k]}]
            else:
                acc[m] = acc[m] + [{'path': path.__add__([k]), 'val': x[k]}]

    _diff(m1,m2,'m2',acc, [])
    _diff(m2,m1,'m1',acc, [])
    return _sort(acc['m1']),_sort(acc['m2']), _sort(acc['common_m1']), _sort(acc['common_m2'])


def any_key(kv,m):
    if not is_list(kv):
        kv = [kv]
    for k in m:
        if k in kv:
            return True
    return False


def curry(f):
    """
    As the name suggests. Easiest to use as a decorator.

    e.g.

    @curry
    def add(f, s, t):
        return f + s + t

    > x = add(1)
    > y = add(2)
    > z = add(3)
    > print(z)
    6

    > print(add(1)(2)(3))
    6

    """
    def cf(a):
        if len(inspect.signature(f).parameters) == 1:
            return f(a)
        return curry(partial(f, a))
    return cf




#TODO: move to debug file

def inspect_f(*args):
    print("\n\n-------",args[0].__name__,"-----------")

    for f in list(args):
        print("*** ",f.__name__," ***")
        print("doc: ", f.__doc__)
        print("name: ", f.__name__)
        #print("src_name: ", getclosurevars(f))
        #print("qualname: ",f.__qualname__)
        #print("defaults: ",f.__defaults__)
        #print("kwdefaults: ",f.__kwdefaults__)
        print("annotations: ", f.__annotations__)
        #print("inspect annotations: ", inspect.get_annotations(f))
        print("fullargspec: ", inspect.getfullargspec(f))
        print("fullargspec.args: ", inspect.getfullargspec(f).args)
        print("source: ",inspect.getsource(f))
        sig = inspect.signature(f)
        print("return anno: ", sig.return_annotation)
        try:
            type_hint = typing.get_type_hints(f)["arg"]
            arg_types, return_type = typing.get_args(type_hint)
            print(arg_types)
            print(return_type)
        except:
            pass
        #print("type hints: ",typing.get_type_hints(f))
        #print("code: ",f.__code__)
        # print("code co_consts: ",f.__code__.co_consts)
        # for x in f.__code__.co_consts:
        #     if inspect.iscode(x):
        #         print("  co_name: ", x.co_name)
        #         print("  co_argcount: ", x.co_argcount)
    print("----- END: ",args[0].__name__,"--------\n")


def nargs(f):
    return len(inspect.getfullargspec(f).args)

@decorator
def trace(f, *args, **kw):
    kwstr = ', '.join('%r: %r' % (k, kw[k]) for k in sorted(kw))
    print("calling %s with args %s, {%s}" % (f.__name__, args, kwstr))
    #inspect_f(f)
    return f(*args, **kw)

def args(f, *args, **kwargs):
    kwstr = ', '.join('%r: %r' % (k, kwargs[k]) for k in sorted(kwargs))
    print("calling %s with args %s, {%s}" % (f.__name__, args, kwstr))
    return inspect.getfullargspec(f).args



#def filterkv(fn,m,depth=1,ks=[],vs=[]):
# _dp = depth-1
#     if _dp == 0:
#         return {k:v for (k,v) in m.items() if fn(k,v)}
#     else:

#         filterkv(fn,v,_dp)


# def ny():
#     return True


# def filterkv(m,pv,f,*args):

#     FIXME: make vector of paths (if ny) then create map from each if match filter

#     ks = pyr.pvector(pv)
#     r = pyr.m()

#     for k in v:
#         if callable(k) and k.__name__ == ny.__name__:
#             print("yes", v[0].__name__)
#             print("yes", ny.__name__)





#return functools.reduce(operator.getitem, pv, m)


# def filterkv(fn,m,depth=1):
#     if depth == 1:

#     else:
#         for k0,v0 in m.items():
#             for k1,v1 in v0.items():
#                 if k1 == 'subs':
#                     #print("k1,v1: ", k1,v1)
#                     for k2,v2 in v1.items():
#                         print("k2,v2: ", v2.get('mute', None))


    # match depth:
    #     case 1:
    #         return {k:v for (k,v) in m.items() if fn(k,v)}
    #     case 2:
    #         return {k1: {k2: v2
    #                      for (k2,v2) in v1.items() if fn([k1,k2],[v1,v2])} #fn([k1,k2],[v1,v2])
    #                 for k1, v1 in m.items()}
    #     case 3:
    #         return {k1: {k2: {k3: v3
    #                           for (k3,v3) in v2.items() if fn([k1,k2,k3],[v1,v2,v3])}
    #                      for (k2,v2) in v1.items()}
    #                 for k1, v1 in m.items()}

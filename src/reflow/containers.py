import threading
import pyrsistent as pyr

"""
Lisp-like container classes
"""


class Box:
    """
    Box provides a thread-safe structure for managing shared state. All
    operations on a box are protected from race conditions.

    Box mixes design elements from both Clojure's Atom, and it's
    inspirational namesake, Racket's box.

    Designed to contain a single immutable data structure. Think of it as a
    reference to a value, or perhaps a... box, er... containing a value?!

    Changes made to a value inside a box are free of race conditions.
    """

    def __init__(self, x=None):
        self.x = x


    def __repr__(self):  # pragma: no cover
        return f"box({repr(self.x)})"


    def __contains__(self, x):
        return self.x == x


    def __iter__(self):
        return (x for x in (self.x,))


    def __len__(self):
        return 1


    def __eq__(self, other):
        return other == self.x


    def set(self, x):
        with threading.Lock():
            self.x = x
            return x


    def reset(self, v):
        """Alias for set"""
        return self.set(v)


    def get(self):
        with threading.Lock():
            return self.x


    def unbox(self):
        """Alias for get"""
        return self.get()


    def compare_reset(self, expectv, newv):
        with threading.Lock():
            if self.x == expectv:
                self.x = newv
                return True
            return False


    def swap(self, fn, *args, **kwargs):
        """
        Changes the value by applying a function atomically to the current value.
        - read the current value
        - apply the function (and optional args/kwargs) to that value
        - attempt to compare_and_set the value derived applying that function
        - if compare_reset is successful (True), return, else: recur

        Protection against race conditions where another thread alters the
        current value is achieved by looping over the change algorithm until
        compare_and_set of the current value and new value is valid. Thus, the
        function will only ever be applied to the most current value.

        NOTE: The function supplied to swap must be free from side-effects as it
        will be called multiple times where race conditions arise.
        """
        while True:
            oldv = self.get()
            newv = fn(oldv, *args, **kwargs)
            if self.compare_reset(oldv, newv):
                return newv



def is_box(b):
    if not isinstance(b, (box, Some)):
        return False
    return True


def unbox(b):
    """Functional alias for box.get()"""
    if not is_box(b):
        raise TypeError(f"Expected box, got {type(b)} with value {repr(b)}")
    return b.get()


def reset(b,v):
    """Functional alias for box.reset() and box.get()"""
    return b.set(v)


def compare_reset(b, oldv, newv):
    """Functional alias for box.compare_reset()"""
    return b.compare_reset(b, oldv, newv)


def swap(b, fn, *args, **kwargs):
    """
    Uses function passed in to transform the value in box.
    The (unboxed) value is the first parameter passed to fn.
    Equivalent to:
    compare_reset(b, unbox(b), fn(unbox(b), *args, **kwargs))
    """
    return b.swap(fn, *args, **kwargs)



# Alias helps when using box in a function style
#   e.g. when coding style treats box as a functional unit
#   rather than OO style of treating Box as an object with methods
#
#   functional style
#   b = box(5)
#   box_set(b,5)
#   unbox(b)
#   >> 5
#   box_set(b,8)
#   unbox(b)
#   >> 8
#
#   OO style
#   b = Box(5)
#   b.get()
#   >> 5
#   b.set(8)
#   b.get()
#   >> 8
box = Box



class Some:
    """
    Represents some value, even if that value is None.
    Used to juxtapose a value of None versus the absence of a value.

    The existence of Some is the opposite of None, even when Some contains None.

    Some(None) != None
    >> True
    """
    def __init__(self, x=None):
        self.x = x

    def __repr__(self):  # pragma: no cover
        return f"Some({repr(self.x)})"

    def __contains__(self, x):
        return self.x == x

    def __iter__(self):
        return (x for x in (self.x,))

    def __len__(self):
        return 1

    def __eq__(self, other):
        return other == self.x

    def get(self):
        return self.x

    def unbox(self):
        """Alias for get"""
        return self.get()

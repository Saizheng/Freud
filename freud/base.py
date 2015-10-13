__copyright__ = "Saizheng Zhang, 2015"
import theano
import numpy as np
from copy import copy as shallowcopy
from copy import deepcopy
import inspect
import pdb

def message_if(m, condition = True):
    if condition:
        print m

class Ego(object):
    def __init__(self, f = None, f_in = [], **kwargs):
        if f is None:
            if f_in != []:
                raise ValueError("When f is *None*, the list of son should be empty.")
            else:
                 self._son = []
                 self._f = f
                 message_if("Warning: the Ego object is intialized with f being *None*.")
        else:
            num_in = len(inspect.getargspec(f).args) if not hasattr(f, 'num_in') else f.num_in

            if f_in == []:
                self._son = [() for i in xrange(num_in)]
                self._f = f #TODO: shallowcopy(f) or deepcopy(f)?
                self._f.num_in = num_in
            else:
                if np.any([isinstance(i, Ego) for i in f_in]):
                    raise ValueError("When initializing Ego object, the *f_in* cannot include Ego objects.")
                    #TODO: fix this.
                if len(f_in) != num_in:
                    raise ValueError("When *f* and *f_in* are both specified, the number of f's input(s) should equal to len(f_in).")
                else:
                    def f_ (*args):
                        x = [t for (c,t) in enumerate(args)]
                        for i in xrange(len(f_in)):
                            if f_in[i] != ():
                                x.insert(i, f_in[i])
                        return f(*x)
                    f_.num_in = sum([1 if t==() else 0 for t in f_in])
                    self._son = [() for i in xrange(f_.num_in)] 
                    self._f = f_
        self._id = self
        self.__dict__.update(kwargs)

    def __call__(self, *args):
        x = [t for c,t in enumerate(args)]
        if not x:
            return Ego.copy(self)
        else:
            if len(x) != self._f.num_in:
                raise ValueError("The number of inputs does not equal to number of self._f.num_in.")

            self_ = Ego.copy(self)

            in_ = self_._in()
            for i in xrange(len(x)):
                if isinstance(x[i], Ego):
                   in_[i][0]._son[in_[i][1]] = Ego.copy(x[i])
                elif x[i] == ():
                   pass
                else:
                   in_[i][0]._son[in_[i][1]] = x[i] #TODO: shallowcopyof(x) or deepcopy(x)?
            self_._f = lambda *args:self_.f(*args)
            self_._f.num_in = len(self_._in())
            return self_
 
    def _in(self):
        in_ = []
        for i in xrange(len(self._son)):
            if self._son[i] == ():
                in_ += [(self, i)]
            elif isinstance(self._son[i], Ego):
                in_ += self._son[i]._in()
        return in_

    def params(self):
        params_ = self._id._params if hasattr(self._id, '_params') else []
        for s in self._son:
            if isinstance(s, Ego):
                params_ += s.params()
        return params_

    def f(self, *args):
        if self._id._f:
            x = [t for (c,t) in enumerate(args)]
            if len(x) != len(self._in()):
                raise ValueError("The len(x) should equal to the number of inputs.")

            if not np.any([isinstance(t, Ego) for t in self._son]):
                x_ = x
                for i in xrange(len(self._son)):
                    if self._son[i] != ():
                        x_.insert(i, self._son[i])
                return self._id._f(*x_)
            else:
                x_ = []
                for i in xrange(len(self._son)):
                    if isinstance(self._son[i], Ego):
                       x_.append(self._son[i]._id._f(*x[:len(self._son[i]._in())]))
                       x = x[len(self._son[i]._in()):]
                    elif self._son[i] == ():
                       x_.append(x[0])
                       x = x[1:]
                    else:
                       x_.append(self._son[i])
                return self._id._f(*x_)
        else:
            raise NotImplementedError("_f is not implemented for this Ego object.")

    @staticmethod
    def copy(x):
        if not x._son:
            return shallowcopy(x)
        else:
            x_ = shallowcopy(x)
            x_._son = [Ego.copy(t) if isinstance(t, Ego) else t for t in x._son]
            return x_



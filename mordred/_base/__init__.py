import os
from importlib import import_module

from .descriptor import Descriptor
from .calculator import Calculator, get_descriptors_from_module


__all__ = (
    'all_descriptors',
    'Descriptor',
    'Calculator',
    'get_descriptors_from_module',
)


def Descriptor__call__(self, mol, coord_id=-1):
    return Calculator(self)(mol, coord_id)[0]


def all_descriptors():
    r"""yield all descriptor modules.

    :returns: all modules
    :rtype: :py:class:`Iterator` (:py:class:`Descriptor`)
    """
    base_dir = os.path.dirname(__file__)

    for name in os.listdir(base_dir):
        name, ext = os.path.splitext(name)
        if name[:1] == '_' or ext != '.py':
            continue

        yield import_module('.' + name, __package__)


Descriptor.__call__ = Descriptor__call__

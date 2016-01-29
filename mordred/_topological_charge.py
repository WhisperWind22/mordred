from itertools import chain

import numpy as np

from six import integer_types

from ._base import Descriptor
from ._common import AdjacencyMatrix, DistanceMatrix


class ChargeTermMatrix(Descriptor):
    explicit_hydrogens = False

    def __reduce_ex__(self, version):
        return self.__class__, ()

    def dependencies(self):
        return dict(
            A=AdjacencyMatrix(self.explicit_hydrogens),
            D=DistanceMatrix(self.explicit_hydrogens),
        )

    def calculate(self, mol, A, D):
        D2 = D.copy()
        D2[D2 != 0] **= -2
        np.fill_diagonal(D2, 0)

        M = A.dot(D2)
        return M - M.T


class TopologicalCharge(Descriptor):
    r"""topological charge descriptor.

    :type type: str
    :param type:
        * 'sum': sum of order-distance atom pairs coefficient
        * 'mean': mean of order-distance atom pairs coefficient
        * 'global': sum of mean-topoCharge over 0 to order

    :type order: int
    :param order: int

    References
        * :cite:`10.1021/ci00019a008`
    """

    explicit_hydrogens = False

    tc_types = ('global', 'mean', 'raw')

    @classmethod
    def preset(cls):
        return chain(
            (cls(t, o) for t in ('raw', 'mean') for o in range(1, 11)),
            [cls('global', 10)]
        )

    def __str__(self):
        if self._type == 'global':
            return 'JGT{}'.format(self._order)
        elif self._type == 'mean':
            return 'JGI{}'.format(self._order)
        else:
            return 'GGI{}'.format(self._order)

    __slots__ = ('_type', '_order',)

    def __reduce_ex__(self, version):
        return self.__class__, (self._type, self._order)

    def __init__(self, type='global', order=10):
        assert type in self.tc_types
        assert type == 'global' or isinstance(order, integer_types)

        self._type = type
        self._order = order

    def dependencies(self):
        return dict(
            CT=ChargeTermMatrix(),
            D=DistanceMatrix(self.explicit_hydrogens)
        )

    def calculate(self, mol, CT, D):
        D = D * np.tri(*D.shape)
        D[D == 0] = np.inf

        f = D <= self._order if self._type == 'global' else D == self._order

        CT = CT[f]

        if self._type == 'raw':
            return np.abs(CT).sum()

        # create frequency vector
        Df = D[f]
        C = Df.copy()
        for i in np.unique(Df):
            C[Df == i] = len(Df[Df == i])

        return np.abs(CT / C).sum()

    rtype = float
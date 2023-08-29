from __future__ import annotations

import numpy as np
import random

class Tree:
    def __init__(self):
        self._l: Tree = None
        self._r: Tree = None
        self.value: Any = None

    def insert(self, value: int) -> Tree:
        if self.value is None:
            self.value = value
            return self
        if value <= self.value:
            if self._l is None:
                self._l = Tree().insert(value)
            else:
                self._l.insert(value)
        else:
            if self._r is None:
                self._r = Tree().insert(value)
            else:
                self._r.insert(value)
        return self

    def traverse(self):
        yield self 
        if self._l is not None:
            yield from self._l.traverse()
        if self._r is not None:
            yield from self._r.traverse()

    def __str__(self) -> str:
        l = "" if self._l is None else str(self._l)
        r = "" if self._r is None else str(self._r)
        return f"({l}{',' if l and r else ''}{r})"

    def tolambda_h(self, ldepth: int, nmax_free: int) -> str:
        match self._l, self._r:
            case (None, None):
                max_label = nmax_free if ldepth == 0 else ldepth
                self.value = f"x{random.randint(0, max_label)}"
            case (None, _):
                body = self._r.tolambda_h(ldepth + 1, nmax_free)
                self.value = f"\\x{ldepth + 1}.({body})"
            case (_, None):
                body = self._l.tolambda_h(ldepth + 1, nmax_free)
                self.value = f"\\x{ldepth + 1}.({body})"
            case (_, _):
                l_lambda = self._l.tolambda_h(ldepth, nmax_free)
                r_lambda = self._r.tolambda_h(ldepth, nmax_free)
                self.value = f"({l_lambda})({r_lambda})"
        return self.value

    def tolambda(self, nmax_free: int) -> str:
        return self.tolambda_h(0, nmax_free)


def random_btree(n: int) -> random_btree.Tree:
    permutation = np.random.permutation(n)
    tree = Tree()
    for i in permutation:
        tree.insert(i)
    return tree


def main():
    NODES = 20
    MAX_FREE_VARIABLES = 10
    EXPRESSIONS = 1000

    # If you need a single tree
    tree = random_btree(NODES)

    for i in range(EXPRESSIONS):
        print(random_btree(NODES).tolambda(MAX_FREE_VARIABLES))

if __name__ == '__main__':
    main()

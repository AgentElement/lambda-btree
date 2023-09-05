from __future__ import annotations

import numpy as np
import random


class Tree:
    def __init__(self):
        self.left: Tree = None
        self.right: Tree = None
        self.value: Any = None

    def insert(self, value: int) -> Tree:
        if self.value is None:
            self.value = value
            return self
        if value <= self.value:
            if self.left is None:
                self.left = Tree().insert(value)
            else:
                self.left.insert(value)
        else:
            if self.right is None:
                self.right = Tree().insert(value)
            else:
                self.right.insert(value)
        return self

    def traverse(self):
        yield self
        if self.left is not None:
            yield from self._l.traverse()
        if self.right is not None:
            yield from self._r.traverse()

    def __str__(self) -> str:
        l = "" if self.left is None else str(self.left)
        r = "" if self.right is None else str(self.right)
        return f"({l}{',' if l and r else ''}{r})"

    # display() and _display_aux() copied from
    # https://stackoverflow.com/a/54074933
    def display(self):
        lines, *_ = self._display_aux()
        for line in lines:
            print(line)

    def _display_aux(self):
        """Returns list of strings, width, height, and horizontal coordinate
        of the root."""
        # No child.
        if self.right is None and self.left is None:
            line = f"{self.value}"
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if self.right is None:
            lines, n, p, x = self.left._display_aux()
            s = f"{self.value}"
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child.
        if self.left is None:
            lines, n, p, x = self.right._display_aux()
            s = f"{self.value}"
            u = len(s)
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children.
        left, n, p, x = self.left._display_aux()
        right, m, q, y = self.right._display_aux()
        s = f"{self.value}"
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * \
            '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + \
            (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + \
            [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2

    def tolambda_h(self, ldepth: int, nmax_free: int) -> str:
        match self.left, self.right:
            case (None, None):
                max_label = nmax_free if ldepth == 0 else ldepth
                self.value = f"x{random.randint(0, max_label)}"
            case (None, _):
                body = self.right.tolambda_h(ldepth + 1, nmax_free)
                self.value = f"\\x{ldepth + 1}.({body})"
            case (_, None):
                body = self.left.tolambda_h(ldepth + 1, nmax_free)
                self.value = f"\\x{ldepth + 1}.({body})"
            case (_, _):
                l_lambda = self.left.tolambda_h(ldepth, nmax_free)
                r_lambda = self.right.tolambda_h(ldepth, nmax_free)
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
    #  tree = random_btree(NODES)

    for i in range(EXPRESSIONS):
        print(random_btree(NODES).tolambda(MAX_FREE_VARIABLES))


if __name__ == '__main__':
    main()

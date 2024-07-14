from __future__ import annotations
from typing import Any

import numpy as np
import random
import collections
# import ete3
import re

from enum import Enum

from lambda_ast import ASTNode

import utils

random.seed(314159)


class Standardization(Enum):
    POSTFIX = 0
    PREFIX = 1
    NONE = 2


class PermutationTree:
    def __init__(self):
        self.left: PermutationTree = None
        self.right: PermutationTree = None
        self.value: Any = None
        self.id: int = 0
        self.depth = 0

    def insert(self, value: int) -> PermutationTree:
        if self.value is None:
            self.value = value
            return self
        if value <= self.value:
            if self.left is None:
                self.left = PermutationTree().insert(value)
            else:
                self.left.insert(value)
        else:
            if self.right is None:
                self.right = PermutationTree().insert(value)
            else:
                self.right.insert(value)
        return self

    def traverse(self):
        yield self
        if self.left is not None:
            yield from self._l.traverse()
        if self.right is not None:
            yield from self._r.traverse()

    @classmethod
    def annotate_depths_h(cls, tree, depth):
        tree.depth = depth
        match (tree.left, tree.right):
            case (None, None):
                pass
            case (None, _):
                cls.annotate_depths_h(tree.right, depth + 1)
            case (_, None):
                cls.annotate_depths_h(tree.left, depth + 1)
            case (_, _):
                cls.annotate_depths_h(tree.left, depth)
                cls.annotate_depths_h(tree.right, depth)


    def annotate_depths(self):
        self.annotate_depths_h(self, 0)


    def __str__(self) -> str:
        left = "" if self.left is None else str(self.left)
        right = "" if self.right is None else str(self.right)
        return f"({left}{',' if left and right else ''}{right})"


class BtreeGen:
    def __init__(self, freevar_p=0.2, max_free_vars=6, n_nodes=20, std=Standardization.PREFIX):
        self.max_free_vars = max_free_vars
        self.freevar_p = freevar_p
        self.n_nodes = n_nodes
        self.std = std

    def set_max_free_vars(self, n: int) -> BtreeGen:
        self.max_free_vars = n
        return self

    def set_node_count(self, n: int) -> BtreeGen:
        self.n_nodes = n
        return self

    def postfix_standardize(self, tree: ASTNode) -> ASTNode:
        def one_step_lookahead(tree):
            match tree.left, tree.right:
                case (None, None):
                    return True
                case (None, _) | (_, None) | (_, _):
                    return False

        if tree.right is not None:
            if one_step_lookahead(tree.right) and tree.right.value.isalpha():
                tree.right = ASTNode(tree.right, None).set_value(tree.right.value)
            else:
                self.postfix_standardize(tree.right)
        
        if tree.left is not None:
            if one_step_lookahead(tree.left) and tree.left.value.isalpha():
                tree.left = ASTNode(tree.left, None).set_value(tree.left.value)
            else:
                self.postfix_standardize(tree.left)
        return tree

    def prefix_standardize(self, tree: ASTNode) -> ASTNode:
        node = tree
        if tree.must_have_free_variables():
            node = ASTNode(node, None).set_value(r"x0")
            pass
        for i in range(self.max_free_vars + 1):
            freevar_value = chr(97 + i)
            if tree.search_for_value(freevar_value):
                node = ASTNode(node, None).set_value(freevar_value)
        return node

    def standardize(self, tree: ASTNode) -> ASTNode:
        match self.std:
            case Standardization.PREFIX:
                return self.prefix_standardize(tree)
            case Standardization.POSTFIX:
                return self.postfix_standardize(tree)
            case Standardization.NONE:
                return None

    def random_lambda(self):
        random_tree = self.random_tree()
        return random_tree.tolambda()

    def annotate_tree(self, tree: PermutationTree) -> ASTNode:
        match (tree.left, tree.right):
            case (None, None):
                coin = random.random() < self.freevar_p
                if coin or tree.depth == 0:
                    random_freevar = chr(97 + random.randint(0, self.max_free_vars))
                    return ASTNode(None, None).set_value(random_freevar)
                else:
                    random_variable = f"x{random.randint(0, tree.depth - 1 if tree.depth != 0 else 0)}"
                    return ASTNode(None, None).set_value(random_variable)
            case (_, None):
                subtree = self.annotate_tree(tree.left)
                return ASTNode(subtree, None).set_value(f"x{tree.depth}")
            case (None, _):
                subtree = self.annotate_tree(tree.right)
                return ASTNode(subtree, None).set_value(f"x{tree.depth}")
            case (_, _):
                right = self.annotate_tree(tree.right)
                left = self.annotate_tree(tree.left)
                return ASTNode(left, right)

    def random_tree(self):
        permutation = np.random.permutation(self.n_nodes)
        tree = PermutationTree()
        for i in permutation:
            tree.insert(i)
        tree.annotate_depths()
        tree = self.annotate_tree(tree)
        tree = self.standardize(tree)
        return tree


def main():
    gen = BtreeGen(n_nodes=40, std=Standardization.PREFIX)
    utils.dump_gen(gen, 100000)


if __name__ == '__main__':
    main()

from btree_generator import BtreeGen
from fontana_generator import FontanaGen

from lambda_parse import LambdaLexer, LambdaParser
from lambda_ast import ASTNode


def average_degree(tree):
    # The average degree of a graph is related to its order and size by
    # d(G) = 2 * ||G|| / |G|
    # [Die17]

    size = len([e for e in tree.edges_breadth()])
    ord = len([v for (v, _) in tree.vertices_breadth()])

    return 2 * ord / size

def main():
    pass


if __name__ == "__main__":
    pass

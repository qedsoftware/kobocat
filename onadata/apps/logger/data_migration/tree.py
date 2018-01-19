from functools import partial


def rev_getattr(param):
    return lambda obj: getattr(obj, param)


class Tree(object):
    def __init__(self, label='root', parent=None, children=None):
        self.label = label
        self.parent = parent
        self.children = []
        list(map(self.add_child, (children or [])))

    def __repr__(self):
        return self.label

    def add_child(self, node):
        assert isinstance(node, Tree)
        self.children.append(node)

    def find_child_by_label(self, label):
        return next(
            [child for child in self.children if child.label == label], None
        )

    def get_child_attribs(self, attrib):
        return map(rev_getattr(attrib), self.children)

    @property
    def is_leaf(self):
        return self.children == []

    def search_node_by_label(self, label):
        return self._dfs_search_node(self, label)

    @classmethod
    def _dfs_search_node(cls, tree, label):
        for child in tree.children:
            if child.is_leaf and child.label == label:
                return child
            child_search = cls._dfs_search_node(child, label)
            if child_search:
                return child_search
        return None

    def extract_ancestors_labels(self):
        labels = []
        while self.parent is not None:
            labels.append(self.parent.label)
        return labels

    @classmethod
    def construct_tree(cls, iterable, root=None):
        """Construct tree from plain python data structures
        iterable format: [
            'leaf1_label', 'leaf2_label', {
                'node1_label': ['node1_leaf_label', {
                    nested_node_label: [...]
                }]
            }
        ]

        :param iterable:
        :param Tree root: root of the iterable, by default creates one
        :rtype: Tree
        """
        root = root or Tree()
        cls.construct_children(root, iterable)
        return root

    @classmethod
    def construct_children(cls, root, iterable):
        list(map(partial(cls._construct_child, root), iterable))

    @classmethod
    def _construct_child(cls, root, elem):
        node = (cls._construct_node_from_dict(root, elem)
                if type(elem) == dict
                else Tree(label=elem, parent=root))
        root.add_child(node)

    @classmethod
    def _construct_node_from_dict(cls, root, elem):
        """Construct tree from dictionary

        :param elem: format: {'tree_root_label': [child1, child2]}
        :return: Tree object
        """
        assert len(elem.keys()) == 1
        node = Tree(label=elem.keys()[0], parent=root)
        cls.construct_tree(elem.values[0], node)
        return node

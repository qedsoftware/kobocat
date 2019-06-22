from functools import partial
from itertools import ifilter
from lxml import etree

from .xmltree import XMLTree, MissingFieldException
from .xformtree import XFormTree
from .common import compose, concat_map


class SurveyTree(XMLTree):
    """
    Parse XForm Instance from xml string into tree.
    """
    def __init__(self, survey):
        # Handle both cases when instance or string is passed.
        try:
            self.root = etree.XML(survey.xml)
        except AttributeError:
            self.root = etree.XML(survey)

    def permanently_remove_field(self, field):
        """WARNING: It is not possible to revert this operation"""
        field.getparent().remove(field)

    def change_field_tag(self, field, new_tag):
        field.tag = new_tag

    def set_field_attrib(self, field, attrib, new_value):
        field.attrib[attrib] = new_value

    def get_or_create_field(self, field_tag, text='', groups=None):
        groups = groups if groups is not None else []
        try:
            field = self.get_field(field_tag)
        except MissingFieldException:
            field = self.create_element(field_tag, text)
            self.insert_field_into_group_chain(field, groups)
        return field

    def find_group(self, name):
        """Find group named :group_name: or throw exception"""
        return compose(
            self._get_first_element(name),
            partial(ifilter, lambda e: self.field_tag(e) == name),
        )(self.get_groups())

    def insert_field_into_group_chain(self, field, group_chain):
        """Insert field into a chain of groups. Function handles group field
        creation if one does not exist
        """
        assert etree.iselement(field)
        parent = self.root

        for group_tag in group_chain:
            try:
                group_field = self.get_child_field(parent, group_tag)
            except MissingFieldException:
                group_field = self.create_element(group_tag)
                parent.append(group_field)
            parent = group_field

        parent.append(field)

    def sort(self, xformtree):
        """Sort XML tree fields according to the order provided by XFormTree"""
        pattern = xformtree.get_el_by_path(xformtree.DATA_STRUCT_PATH)[0]
        self._sort(self.root, pattern)

    @staticmethod
    def get_order(tree, pattern):
        """Get order according to which fields in XML should be sorted"""
        LAST_FIELDS = ['imei', 'meta']
        order = XFormTree.children_tags(pattern)
        # Put other fields into order list
        order += [e.tag for e in tree if e.tag not in order]
        for field in LAST_FIELDS:  # Ensure LAST_FIELDS are in the end of XML
            order.remove(field) if field in order else None
        order += LAST_FIELDS
        return order

    @classmethod
    def _sort(cls, tree, pattern):
        order = cls.get_order(tree, pattern)

        for el in ifilter(lambda e: e.tag in cls.children_tags(pattern), tree):
            cls._sort(el, cls.get_child_field(pattern, el.tag))

        for el in sorted(tree, key=lambda e: order.index(e.tag)):
            tree.remove(el)
            tree.append(el)

    def remove_duplicates(self):
        """
        Remove duplicated fields from the xml tree. It assumes that
        fields in the tree are sorted
        """
        self._remove_duplicates(self.root)

    @classmethod
    def _remove_duplicates(cls, tree):
        if cls.is_leaf(tree):
            return
        prev_el, next_el = tree[0], tree[0]
        for next_el in tree[1:]:
            are_leaves = cls.is_leaf(prev_el) and cls.is_leaf(next_el)
            if are_leaves and cls.are_elements_equal(prev_el, next_el):
                tree.remove(prev_el)
            else:
                cls._remove_duplicates(prev_el)
            prev_el = next_el
        cls._remove_duplicates(next_el)

    def remove_version(self):
        try:
            version_element = self.get_child_field(self.root, '__version__')
            self.root.remove(version_element)
        except MissingFieldException:
            pass

import re
from operator import not_
from functools import partial
from itertools import ifilter
from lxml import etree

from .common import concat_map, compose, fst


class MissingFieldException(Exception):
    pass


class XMLTree(object):
    """
    Common class for handling XML trees
    """
    # XML elements that should not be considered as fields
    NOT_RELEVANT = ['formhub', 'meta', 'imei', '__version__']

    def __init__(self, xml):
        # xml is stored in database as unicode, thus, in order to
        # match with xml declaration, we need to encode it to utf-8
        self.root = etree.XML(xml.encode('utf-8'))

    def __repr__(self):
        return self.to_string()

    def to_string(self, pretty=True):
        return etree.tostring(self.root, pretty_print=pretty)

    def to_xml(self, pretty=True):
        return etree.tostring(self.root, pretty_print=pretty,
                              xml_declaration=True, encoding='utf-8')

    def set_tag(self, field, value):
        cleaned_tag = self.field_tag(field)
        field.tag = field.tag.replace(cleaned_tag, value)

    def get_fields(self):
        """Parse and return list of all fields in form."""
        return map(fst, self.retrieve_leaf_elems(self.root))

    def get_groups(self):
        return concat_map(self.retrieve_groups, self.root.getchildren())

    def get_fields_names(self):
        """Return fields as list of string with field names."""
        return map(lambda f: f.tag, self.get_fields())

    def get_groups_names(self):
        """Return fields as list of string with field names."""
        return map(lambda g: g.tag, self.get_groups())

    def _get_matching_elems(self, condition_func):
        """Return elems that match condition"""
        return ifilter(condition_func, self.retrieve_all_elems(self.root))

    @staticmethod
    def is_leaf(element):
        return len(element.getchildren()) == 0

    @staticmethod
    def _get_first_element(name):
        def get_next_from_iterator(iterator):
            try:
                return next(iterator)
            except StopIteration:
                raise MissingFieldException("Element '{}' does not exist in "
                                            "xml tree".format(name))
        return get_next_from_iterator

    def get_field_with_path(self, name):
        """Get field along with path in tree by name."""
        cond = lambda field: self.field_tag(field[0]) == name
        matching_elems = self._get_matching_elems(cond)
        return self._get_first_element(name)(matching_elems)

    def get_field(self, name):
        """Get field in tree by name."""
        return compose(fst, self.get_field_with_path)(name)

    @classmethod
    def get_child_field(cls, element, name):
        """Get child of element by name"""
        return compose(
            cls._get_first_element(name),
            partial(ifilter, lambda f: cls.field_tag(f) == name),
        )(element)

    @classmethod
    def children_tags(cls, element):
        return map(cls.field_tag, element)

    def get_el_by_path(self, path):
        return reduce(self.get_child_field, path, self.root)

    @classmethod
    def retrieve_elems(cls, path, base_cond, element):
        if not cls.is_relevant(element.tag):
            return []

        new_elem = [(element, path)] if base_cond(element) else []
        new_path = path+[cls.clean_tag(element.tag)]
        induction_step = partial(cls.retrieve_elems, new_path, base_cond)
        return new_elem + concat_map(induction_step, element)

    @classmethod
    def retrieve_leaf_elems(cls, element):
        return cls.retrieve_elems([], cls.is_leaf, element)

    @classmethod
    def retrieve_leaf_elems_tags(cls, element):
        return map(compose(cls.field_tag, fst), cls.retrieve_leaf_elems(element))

    @classmethod
    def retrieve_groups(cls, element):
        cond = compose(not_, cls.is_leaf)
        return map(fst, cls.retrieve_elems([], cond, element))

    @classmethod
    def retrieve_all_elems(cls, element):
        return cls.retrieve_elems([], lambda _: True, element)

    @classmethod
    def is_relevant(cls, tag):
        return cls.clean_tag(tag) not in cls.NOT_RELEVANT

    @classmethod
    def is_group(cls, element):
        return element.getchildren() and cls.is_relevant(element.tag)

    @staticmethod
    def create_element(field_name, text=''):
        return etree.XML('<{name}>{text}</{name}>'.format(name=field_name,
                                                          text=text))

    @staticmethod
    def clean_tag(tag):
        """
        Remove w3 header that tag may contain.
        Example: '{http://www.w3.org/1999/xhtml}head'
        """
        header_end = tag.find('}')
        return tag[header_end+1:] if header_end != -1 else tag

    @classmethod
    def field_tag(cls, field):
        return cls.clean_tag(field.tag)

    @classmethod
    def are_elements_equal(cls, e1, e2):
        to_str = lambda el: re.sub(r"\s+", "", etree.tostring(el))
        return to_str(e1) == to_str(e2)

    def _get_matching_leafs(self, condition_func):
        """Return elems that match condition"""
        return ifilter(condition_func, self.retrieve_leaf_elems(self.root))

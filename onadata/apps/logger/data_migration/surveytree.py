from functools import partial
from lxml import etree

from .common import compose


class MissingFieldException(Exception):
    pass


class SurveyTree(object):
    """
    Parse XForm Instance from xml string into tree.
    """
    # XML elements that should not be considered as fields
    NOT_RELEVANT = ['formhub', 'meta', 'imei']

    def __init__(self, survey):
        # Handle both cases when instance or string is passed.
        try:
            self.root = etree.XML(survey.xml)
        except AttributeError:
            self.root = etree.XML(survey)

    def __repr__(self):
        return self.to_string()

    def to_string(self, pretty=True):
        return etree.tostring(self.root, pretty_print=pretty)

    def get_fields(self):
        """Return fields as list with tree Elements."""
        return [
            field for field in self.root.getchildren()
            if field.tag not in self.NOT_RELEVANT
        ]

    def get_fields_names(self):
        """Return fields as list of string with field names."""
        return [
            field.tag for field in self.root.getchildren()
            if field.tag not in self.NOT_RELEVANT
        ]

    def _get_matching_fields(self, condition_func):
        """Return fields that match condition"""
        return iter(filter(condition_func, self.get_fields()))

    @staticmethod
    def _get_fst_el(name, iterator):
        try:
            return next(iterator)
        except StopIteration:
            raise MissingFieldException("Element '{}' does not exist in "
                                        "survey tree".format(name))

    def get_field(self, name):
        """Get field Element by name."""
        return compose(
            partial(self._get_fst_el, name),
            self._get_matching_fields,
        )(lambda f: f.tag == name)

    def create_element(self, field_name):
        return etree.XML('<{name}></{name}>'.format(name=field_name))

    def permanently_remove_field(self, field_name):
        """WARNING: It is not possible to revert this operation"""
        field = self.get_field(field_name)
        field.getparent().remove(field)
        return field

    def modify_field(self, field_name, new_tag):
        field = self.get_field(field_name)
        field.tag = new_tag

    def add_field(self, field_name, text='', parent=None):
        parent = parent or self.root
        try:
            field = self.get_field(field_name)
        except MissingFieldException:
            field = self.create_element(field_name)
            field.text = text
            parent.append(field)
        return field

    def find_group(self, group_name):
        """Find group named :group_name: or throw exception"""
        return compose(
            partial(self._get_fst_el, group_name),
            iter,
            partial(filter, lambda e: e.getchildren != []),
            self._get_matching_fields,
        )(lambda f: f.tag == group_name)

    def insert_field_into_group_chain(self, field, group_chain):
        """Insert field into a chain of groups. Function handle group field
        creation if one does not exist
        """
        assert etree.iselement(field)
        group_chain = iter(group_chain)

        def aux(parent):
            group = next(group_chain, None)
            if group is None:
                parent.append(field)
                return field
            group_field = self.add_field(group, parent=parent)
            return aux(group_field)

        return aux(self.root)

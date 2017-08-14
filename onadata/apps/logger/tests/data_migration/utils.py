from django.test import TestCase
from django.contrib.auth.models import User

from onadata.apps.logger.models import Instance, XForm
from onadata.apps.viewer.models import ParsedInstance
from onadata.apps.logger.data_migration.factories import data_migrator_factory

from . import fixtures


def remove_whitespaces(string):
    return string.replace('\n', '').replace(' ', '')


class MigrationTestCase(TestCase):
    def setUp(self):
        self.user = self.create_user('johnny_cash')
        self.xform = self.create_xform(fixtures.form_xml_case_1)
        self.xform_new = self.create_xform(fixtures.form_xml_case_1_after)
        self.survey = self.create_survey(self.xform_new)
        self.setup_data_migrator(self.xform, self.xform_new)

    def create_user(self, username):
        return User.objects.create_user(username=username,
                                        password='password')

    def create_xform(self, xml):
        return XForm.objects.create(
            xml=xml,
            user=self.user
        )

    def create_survey(self, xform, xml=fixtures.survey_xml):
        survey = Instance.objects.create(
            xml=xml,
            user=self.user,
            xform=xform)
        survey.parsed_instance = ParsedInstance.objects.create(
            instance=survey)
        return survey

    def setup_data_migrator(self, xform, xform_new):
        self.migration_decisions = self.get_migration_decisions()
        self.data_migrator = data_migrator_factory(xform, xform_new,
                                                   **self.migration_decisions)

    def get_migration_decisions(self):
        return {
            'prepopulate_last_name': ['Fowler'],
            'determine_first_name': ['name'],
            'determine_birthday': ['__new_field__'],
            'determine_last_name': ['__new_field__'],
        }

    def assertEqualIgnoringWhitespaces(self, result, expected):
        self.assertEqual(
            remove_whitespaces(result),
            remove_whitespaces(expected),
        )

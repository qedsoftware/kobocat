"""
Third example xml files to parse and compare with each other.
These fixtures asserts that in case of already corrupted data, migrator is
going to fix it.

Differences between form_xml_case_1 and form_xml_case_1_after:
- Rename 'name' to 'first_name' and insert into group
- Add 'last_name' field inside group
- Add date field
- Survey has age field in a wrong group
- Survey has photo field in a wrong group

XML of Surevey instance (answer to xform)
"""

FIELDS_3 = [
    'name', 'gender', 'photo', 'location',
    'age', 'thanks', 'start_time', 'end_time', 'today',
]

form_xml_case_3 = '''<?xml version="1.0" encoding="utf-8"?>
<h:html xmlns="http://www.w3.org/2002/xforms" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:jr="http://openrosa.org/javarosa" xmlns:orx="http://openrosa.org/xforms/" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <h:head>
    <h:title>SurveyGroups</h:title>
    <model>
      <instance>
        <SurveyGroups id="SurveyGroups">
          <formhub>
            <uuid/>
          </formhub>
          <name/>
          <gender/>
          <photo/>
          <age/>
          <location/>
          <meta>
            <instanceID/>
          </meta>
        </SurveyGroups>
      </instance>
      <bind nodeset="/SurveyGroups/name" required="true()" type="string"/>
      <bind nodeset="/SurveyGroups/age" required="true()" type="int"/>
      <bind nodeset="/SurveyGroups/gender" required="true()" type="select1"/>
      <bind nodeset="/SurveyGroups/photo" type="binary"/>
    </model>
  </h:head>
  <h:body>
    <input ref="/SurveyGroups/name">
      <label>What is your name?\u2019</label>
    </input>
    <input ref="/SurveyGroups/age">
      <label>How old are you?\u2018</label>
    </input>
    <select1 ref="/SurveyGroups/gender">
      <label>Gender</label>
      <item>
        <label>Male</label>
        <value>male</value>
      </item>
      <item>
        <label>Female</label>
        <value>female</value>
      </item>
    </select1>
    <upload mediatype="image/*" ref="/SurveyGroups/photo">
      <label>Portrait</label>
    </upload>
    <input ref="/SurveyGroups/location">
      <label>Where are you?</label>
      <hint>You need to be outside for your GPS to work.</hint>
    </input>
  </h:body>
</h:html>
'''

form_xml_case_3_after = '''<?xml version="1.0" encoding="utf-8"?>
<h:html xmlns="http://www.w3.org/2002/xforms" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:jr="http://openrosa.org/javarosa" xmlns:orx="http://openrosa.org/xforms/" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <h:head>
    <h:title>SurveyGroups2</h:title>
    <model>
      <instance>
        <SurveyGroups2 id="SurveyGroups2">
          <formhub>
            <uuid/>
          </formhub>
          <private>
            <first_name/>
            <last_name/>
          </private>
          <gender/>
          <photo/>
          <group_age>
            <age/>
          </group_age>
          <group_1>
            <group_2>
              <group_3>
                <date/>
              </group_3>
            </group_2>
          </group_1>
          <location/>
          <meta>
            <instanceID/>
          </meta>
        </SurveyGroups2>
      </instance>
      <bind nodeset="/SurveyGroups2/first_name" required="true()" type="string"/>
      <bind nodeset="/SurveyGroups2/last_name" required="true()" type="string"/>
      <bind nodeset="/SurveyGroups2/age" required="true()" type="int"/>
      <bind nodeset="/SurveyGroups2/gender" required="true()" type="select1"/>
      <bind nodeset="/SurveyGroups2/location" required="false()" type="geopoint"/>
      <bind nodeset="/SurveyGroups2/date" required="true()" type="date"/>
    </model>
  </h:head>
  <h:body>
    <input ref="/SurveyGroups2/name">
      <label>What is your name?\u2019</label>
    </input>
    <input ref="/SurveyGroups2/age">
      <label>How old are you?\u2018</label>
    </input>
    <select1 ref="/SurveyGroups2/gender">
      <label>Gender</label>
      <item>
        <label>Male</label>
        <value>male</value>
      </item>
      <item>
        <label>Female</label>
        <value>female</value>
      </item>
    </select1>
    <input ref="/SurveyGroups2/date">
      <label>Date</label>
    </input>
    <upload mediatype="image/*" ref="/SurveyGroups2/photo">
      <label>Portrait</label>
    </upload>
    <input ref="/SurveyGroups2/location">
      <label>Where are you?</label>
      <hint>You need to be outside for your GPS to work.</hint>
    </input>
  </h:body>
</h:html>
'''

survey_template_3 = '''<SurveyGroups xmlns:jr="http://openrosa.org/javarosa" xmlns:orx="http://openrosa.org/xforms/" id="SurveyGroups">
  <formhub>
    <uuid>{formhub_uuid}</uuid>
  </formhub>
  <name>{name}</name>
  <gender>male</gender>
  <new_record_already_in_template__wrong_group>
    <date/>
  </new_record_already_in_template__wrong_group>
  <photo/>
  <location>-1 1.1 1 2</location>
  <redundant_group>
    <age>{age}</age>
  </redundant_group>
  <thanks/>
  <start_time>2016-01-01T18:32:20.000+03:00</start_time>
  <end_time>2016-01-01T18:33:03.000+03:00</end_time>
  <today>2016-01-01</today>
  <imei>example.com:d123das</imei>
  <__version__>xyz</__version__>
  <meta>
    <instanceID>uuid:{instance_uuid}</instanceID>
  </meta>
</SurveyGroups>
'''

survey_after_migration_template_3 = '''<SurveyGroups2 xmlns:jr="http://openrosa.org/javarosa" xmlns:orx="http://openrosa.org/xforms/" id="SurveyGroups2">
  <formhub>
    <uuid>{formhub_uuid}</uuid>
  </formhub>
  <private>
    <first_name>{name}</first_name>
    <last_name/>
  </private>
  <gender>male</gender>
  <photo/>
  <group_age>
    <age>{age}</age>
  </group_age>
  <group_1>
    <group_2>
      <group_3>
        <date/>
      </group_3>
    </group_2>
  </group_1>
  <location>-1 1.1 1 2</location>
  <new_record_already_in_template__wrong_group>
  </new_record_already_in_template__wrong_group>
  <redundant_group>
  </redundant_group>
  <thanks/>
  <start_time>2016-01-01T18:32:20.000+03:00</start_time>
  <end_time>2016-01-01T18:33:03.000+03:00</end_time>
  <today>2016-01-01</today>
  <imei>example.com:d123das</imei>
  <meta>
    <instanceID>uuid:{instance_uuid}</instanceID>
  </meta>
</SurveyGroups2>
'''


_survey_data_3 = {
    'formhub_uuid': '123abc',
    'name': 'Kurt Godel',
    'age': '50',
    'instance_uuid': 'das-d123-dsa-dsa-dsa',
}

survey_xml_3 = survey_template_3.format(**_survey_data_3)
survey_3_after_migration = survey_after_migration_template_3.format(**_survey_data_3)

append_extra_data_3 = lambda survey, data: survey.replace('</SurveyGroups>', data + '</SurveyGroups>')

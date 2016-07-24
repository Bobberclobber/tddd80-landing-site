import unittest
import db
import landing_site as ls
from landing_site import app

TEST_MEMBERS = [("Josef", "Fagerstrom", "josef.fagerstrom@hotmail.com"),
                ("Gunnar", "Nilsson", "gunnar.nilsson@gmail.com"),
                ("Anne", "Johnson", "anne.johnson@hotmail.com"),
                ("Karin", "Peterson", "karin.peterson@bredband.net"),
                ("Nicklas", "Gren", "nicklas.gren@gmail.com")]
TEST_GROUPS = {"Facebook": [TEST_MEMBERS[0], TEST_MEMBERS[2], TEST_MEMBERS[3]],
               "Sweden": [TEST_MEMBERS[1], TEST_MEMBERS[4]],
               "Relatives": [TEST_MEMBERS[0], TEST_MEMBERS[1], TEST_MEMBERS[2], TEST_MEMBERS[3]]}
INVALID_MEMBER = ("Fredrik", "Karlsson", "fredrik.karlsson@gmail.se")
VALID_MEMBER = ("Gunnar", "Nilsson", "gunnar.nilsson@gmail.com")
INVALID_GROUP = "Invalid"
VALID_GROUP = "Sweden"


class StatusEmailSentTests(unittest.TestCase):
    def setUp(self):
        with app.test_request_context():
            # Sets up the test database
            db.init()
            for key in TEST_GROUPS:
                db.add_to_group(key, TEST_GROUPS[key])

    # Tests if a valid member in an invalid group can be updated
    def testValidMemberInvalidGroupUpdate(self):
        with app.test_request_context():
            valid_member_email = VALID_MEMBER[2]
            db.status_e_mail_sent(valid_member_email, INVALID_GROUP)
            groups = db.get_groups()

            # Checks if the member's status has been updated to 0
            def is_updated():
                for key in groups:
                    for member in groups[key]:
                        current_member_email = member[2]
                        current_member_accepted = member[3]
                        if current_member_email == valid_member_email and current_member_accepted == 0:
                            return True
                return False

            self.failIf(is_updated())

    # Tests if a member can get incorrectly updated by passing an invalid member as argument
    def testInvalidMemberValidGroupUpdate(self):
        with app.test_request_context():
            invalid_member_email = INVALID_MEMBER[2]
            db.status_e_mail_sent(invalid_member_email, VALID_GROUP)
            groups = db.get_groups()

            # Checks if any member's status has been updated to 0
            def is_updated():
                for key in groups:
                    for member in groups[key]:
                        current_member_accepted = member[3]
                        if current_member_accepted == 0:
                            return True
                return False

        self.failIf(is_updated())

    # Tests if a valid member can be updated in a valid group
    def testValidMemberUpdated(self):
        with app.test_request_context():
            valid_member_email = VALID_MEMBER[2]
            db.status_e_mail_sent(valid_member_email, VALID_GROUP)
            group = db.get_groups()[VALID_GROUP]

            # Checks if the member's status has been updated to 0
            def is_updated():
                for member in group:
                    current_member_email = member[2]
                    current_member_accepted = member[3]
                    if current_member_email == valid_member_email and current_member_accepted == 0:
                        return True
                return False

            self.failUnless(is_updated())

    # Tests if the accepted status can be updated from higher to lower
    def testValidMemberIncorrectUpdate(self):
        with app.test_request_context():
            valid_member_email = VALID_MEMBER[2]
            # Here we update from -1 to 0 to 1 and then try to downgrade
            db.status_e_mail_sent(valid_member_email, VALID_GROUP)
            db.status_invitation_accepted(valid_member_email, VALID_GROUP)
            db.status_e_mail_sent(valid_member_email, VALID_GROUP)
            group = db.get_groups()[VALID_GROUP]

            # Checks if the member's status has been updated to 0
            def is_updated():
                for member in group:
                    current_member_email = member[2]
                    current_member_accepted = member[3]
                    if current_member_email == valid_member_email and current_member_accepted == 0:
                        return True
                return False

            self.failIf(is_updated())

    def tearDown(self):
        with app.test_request_context():
            db.destroy()
            db.close()


class StatusInvitationAcceptedTests(unittest.TestCase):
    def setUp(self):
        with app.test_request_context():
            # Sets up the test database
            db.init()
            for key in TEST_GROUPS:
                db.add_to_group(key, TEST_GROUPS[key])

    # Tests if a valid member in an invalid group can be updated
    def testValidMemberInvalidGroupUpdate(self):
        with app.test_request_context():
            valid_member_email = VALID_MEMBER[2]
            db.status_invitation_accepted(valid_member_email, INVALID_GROUP)
            groups = db.get_groups()

            # Checks if the member's status has been updated to 1
            def is_updated():
                for key in groups:
                    for member in groups[key]:
                        current_member_email = member[2]
                        current_member_accepted = member[3]
                        if current_member_email == valid_member_email and current_member_accepted == 1:
                            return True
                return False

            self.failIf(is_updated())

    # Tests if a member can get incorrectly updated by passing an invalid member as argument
    def testInvalidMemberValidGroupUpdate(self):
        with app.test_request_context():
            invalid_member_email = INVALID_MEMBER[2]
            db.status_invitation_accepted(invalid_member_email, VALID_GROUP)
            groups = db.get_groups()

            # Checks if any member's status has been updated to 1
            def is_updated():
                for key in groups:
                    for member in groups[key]:
                        current_member_accepted = member[3]
                        if current_member_accepted == 1:
                            return True
                return False

        self.failIf(is_updated())

    # Tests if a valid member can be updated in a valid group
    def testValidMemberUpdated(self):
        with app.test_request_context():
            valid_member_email = VALID_MEMBER[2]
            db.status_e_mail_sent(valid_member_email, VALID_GROUP)
            db.status_invitation_accepted(valid_member_email, VALID_GROUP)
            group = db.get_groups()[VALID_GROUP]

            # Checks if the member's status has been updated to 1
            def is_updated():
                for member in group:
                    current_member_email = member[2]
                    current_member_accepted = member[3]
                    if current_member_email == valid_member_email and current_member_accepted == 1:
                        return True
                return False

            self.failUnless(is_updated())

    # Tests if the accepted status can be updated from too low
    def testValidMemberIncorrectUpdate(self):
        with app.test_request_context():
            # A completely unused member is used here since we need the lowest possible accapted status
            valid_member_email = TEST_MEMBERS[4][2]
            db.status_invitation_accepted(valid_member_email, VALID_GROUP)
            group = db.get_groups()[VALID_GROUP]

            # Checks if the member's status has been updated to 1
            def is_updated():
                for member in group:
                    current_member_email = member[2]
                    current_member_accepted = member[3]
                    if current_member_email == valid_member_email and current_member_accepted == 1:
                        return True
                return False

            self.failIf(is_updated())

    def tearDown(self):
        with app.test_request_context():
            db.destroy()
            db.close()


class AddToGroupTests(unittest.TestCase):
    def setUp(self):
        with app.test_request_context():
            # Sets up the test database
            db.init()
            for key in TEST_GROUPS:
                db.add_to_group(key, TEST_GROUPS[key])

    # Test to add only one member to an existing group
    def testAddOneToExisting(self):
        with app.test_request_context():
            new_member_email = INVALID_MEMBER[2]
            # The member/-s to add must be in a list
            db.add_to_group(VALID_GROUP, [INVALID_MEMBER])
            group = db.get_groups()[VALID_GROUP]

            # Checks if the member has been added to the group
            def is_added():
                for member in group:
                    current_member_email = member[2]
                    if new_member_email == current_member_email:
                        return True
                return False

            self.failUnless(is_added())

    # Test to add several members to an existing group
    def testAddSeveralToExisting(self):
        with app.test_request_context():
            members_to_add = [TEST_MEMBERS[0], TEST_MEMBERS[3]]
            new_members_email = [TEST_MEMBERS[0][2], TEST_MEMBERS[3][2]]
            db.add_to_group(VALID_GROUP, members_to_add)
            group = db.get_groups()[VALID_GROUP]

            # Checks if the member has been added to the group
            def is_added():
                counter = 0
                for member in group:
                    current_member_email = member[2]
                    if current_member_email == new_members_email[0] or current_member_email == new_members_email[1]:
                        counter += 1
                if counter == 2:
                    return True
                else:
                    return False

            self.failUnless(is_added())

    # Test if members can be duplicated in the same group
    def testDuplicatedMembers(self):
        with app.test_request_context():
            new_member_email = VALID_MEMBER[2]
            # Add the member twice to the same group
            db.add_to_group(VALID_GROUP, [VALID_MEMBER])
            db.add_to_group(VALID_GROUP, [VALID_MEMBER])
            group = db.get_groups()[VALID_GROUP]

            # Checks if VALID_MEMBER appears more than once in the group
            def is_duplicated():
                counter = 0
                for member in group:
                    current_member_email = member[2]
                    if current_member_email == new_member_email:
                        counter += 1
                if counter > 1:
                    return True
                else:
                    return False

            self.failIf(is_duplicated())

    # Test to create a new group with a few members
    def testCreateNewGroup(self):
        with app.test_request_context():
            members_to_add = [TEST_MEMBERS[0], TEST_MEMBERS[1]]
            db.add_to_group(INVALID_GROUP, members_to_add)
            groups = db.get_groups()

            # Checks if the new group has been created
            def is_created():
                for key in groups:
                    if key == INVALID_GROUP:
                        return True
                return False

            self.failUnless(is_created())

    def tearDown(self):
        with app.test_request_context():
            db.destroy()
            db.close()


class JsonSpecificGroupTests(unittest.TestCase):
    def setUp(self):
        with app.test_request_context():
            # Sets up the test database
            db.init()
            for key in TEST_GROUPS:
                db.add_to_group(key, TEST_GROUPS[key])

    # Test if an invalid group name gives the correct response
    def testInvalidGroupName(self):
        with app.test_request_context():
            assert ls.json_specific_group("ThisIsAnInvalidGroup") == "Invalid Group Name"

    def testValidGroupName(self):
        with app.test_request_context():
            member_list = []
            for member in TEST_GROUPS["Facebook"]:
                member_name = member[0] + " " + member[1]
                member_email = member[2]
                member_accepted = -1
                member_list += [{"name": member_name, "e-mail": member_email, "accepted": member_accepted}]
            assert ls.get_json_member_list("Facebook") == member_list

    def tearDown(self):
        with app.test_request_context():
            db.destroy()
            db.close()


def main():
    unittest.main()


if __name__ == "__main__":
    main()

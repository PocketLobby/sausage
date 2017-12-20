import unittest
from unittest.mock import MagicMock, patch
from vote_tallies.cmd_send_tally_emails import CmdSendTallyEmails
from vote_tallies.cons_vote_tally import ConsVoteTally
from utilities.db import DB

class CmdSendTallyEmailsTest(unittest.TestCase):

    def constituent_db_tuples(self):
        return [
            (1, 'x@rocketmail.com', 'Dude', 'Briggs', '21209', 'wrxuXX-HSlsxD', '1.00', 'venmo-id-1', 'MD', 3),
            (2, 'prunes@gmail.com', 'Doctor', 'Pepper', '11221', 'vxMuAa-klqJxN', '0.50', 'venmo-id-2', 'NY', 8),
        ]

    def args_no_test_no_email(self):
        fakeargs = MagicMock()
        fakeargs.test = False
        fakeargs.email = False

        return fakeargs

    def args_no_test_email(self):
        fakeargs = MagicMock()
        fakeargs.test = False
        fakeargs.email = True

        return fakeargs

    def args_test_no_email(self):
        fakeargs = MagicMock()
        fakeargs.test = True
        fakeargs.email = False

        return fakeargs

    def args_test_email(self):
        fakeargs = MagicMock()
        fakeargs.test = True
        fakeargs.email = True

        return fakeargs

    def simple_obj(self, cons_tuple=None, args=None):
        """Instantiate the class under test more simply"""

        cons_tuple = cons_tuple if cons_tuple else self.constituent_db_tuples()[0]
        args = args if args else self.args_no_test_no_email()
        return CmdSendTallyEmails(cons_tuple, args)

    def cons_as_send_email_to(self, cons_idx):
        """
        Given an index of the constituent_db_tuples, return a dict suitable for
        passing into the `to` argument of the _send_email method
        """

        cons = self.constituent_db_tuples()[cons_idx]
        return {"email": cons[1],
                "id": cons[0],
                "first_name": cons[2],
                }
    @property
    def email_string(self):
        """Example html returned from ConsVoteTally object"""

        return "<h1> hello world </h1>"

    def test_init_the_obj(self):
        cste = self.simple_obj()

        self.assertFalse(cste.cmd_line_args.test)
        self.assertIsNot((), cste.constituent_tuple)

    def test_execute_with_no_bills(self):
        cste = self.simple_obj()

        cste._send_email = MagicMock()

        with patch.object(ConsVoteTally, 'get_bills_updated_since_last_notification') as mocked_cvt:
            mocked_cvt.return_value = []
            cste.execute()

        cste._send_email.assert_not_called()

    def test_execute_with_bills_with_no_test_no_email(self):
        cste = self.simple_obj(args=self.args_no_test_no_email())

        cste._send_email = MagicMock()

        with patch.object(ConsVoteTally, 'get_bills_updated_since_last_notification') as mocked_cvt:
            mocked_cvt.return_value = ['hr123', 's123']

        cste.execute()

        cste._send_email.assert_not_called()

    def test_execute_with_bills_no_test_email(self):
        fake_cvt = MagicMock(spec=ConsVoteTally)
        fake_cvt.matches_to_html.return_value = self.email_string
        fake_cvt.get_bills_updated_since_last_notification.return_value = ['hr123', 's123']

        cste = self.simple_obj(args=self.args_no_test_email())
        cste._cvt = MagicMock(return_value=fake_cvt)
        cste._send_email = MagicMock(return_value=True)

        cste.execute()
        cste._send_email.assert_called_once_with(self.cons_as_send_email_to(0),
                                                 self.email_string)

    # this shouldn't really be a use case, but it's a permutation
    def test_execute_with_bills_test_no_email(self):
        fake_cvt = MagicMock(spec=ConsVoteTally)
        fake_cvt.matches_to_html.return_value = self.email_string
        fake_cvt.get_bills_updated_since_last_notification.return_value = ['hr123', 's123']

        cste = self.simple_obj(args=self.args_test_no_email())
        cste._cvt = MagicMock(return_value=fake_cvt)
        cste._send_email = MagicMock(return_value=True)

        cste.execute()
        cste._send_email.assert_not_called()

    def test_execute_with_bills_test_email(self):
        fake_cvt = MagicMock(spec=ConsVoteTally)
        fake_cvt.matches_to_html.return_value = self.email_string
        fake_cvt.get_bills_updated_since_last_notification.return_value = ['hr123', 's123']

        cste = self.simple_obj(args=self.args_test_email())
        cste._cvt = MagicMock(return_value=fake_cvt)
        cste._send_email = MagicMock(return_value=True)

        cste.execute()

        dict = self.cons_as_send_email_to(0)
        dict["email"] = cste.TEST_EMAIL_RECIPIENT

        cste._send_email.assert_called_once_with(dict, self.email_string)


    @patch("time.sleep")
    def test_call_in_test_mode(self, mock_time_sleep):
        mock_time_sleep.return_value = None

        with patch.object(DB, 'fetch_records') as mock_db:
            mock_db.return_value = self.constituent_db_tuples()

            with patch.object(CmdSendTallyEmails, "execute") as mock_method:
                mock_method.return_value = None
                mock_method.spec = CmdSendTallyEmails

                CmdSendTallyEmails.send_tally_emails(self.args_no_test_no_email())

                self.assertEqual(len(self.constituent_db_tuples()),
                                 mock_method.call_count)

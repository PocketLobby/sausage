import unittest
import pytest
from unittest.mock import MagicMock, patch

from vote_tallies.constituent_vote import ConstituentVoteCreator, ConstituentVoteConverter


class ConsitutentVoteCreatorTest(unittest.TestCase):

    def obj_creator(self, user_token="abc1232", unix_timestamp="1523904505000", bill_id="hr123-115", vote="for"):
        converters = MagicMock()
        converters.user_token_converter.return_value = 123
        converters.timestamp_converter.return_value = '2018-04-16T18:48:25'
        converters.bill_id_converter.return_value = 234

        return ConstituentVoteCreator(user_token, unix_timestamp, bill_id, vote, konverter_klass=converters), converters

    def test_init(self):

        golden_obj, converters = self.obj_creator()

        converters.user_token_converter.assert_called_once()
        converters.timestamp_converter.assert_called_once()
        converters.bill_id_converter.assert_called_once()


        # NOTE: this will fail if ValueError is not raised
        with pytest.raises(ValueError) as ve:
            self.obj_creator(vote="dude")


    def test_commit_user_vote(self):

        cvc, _ = self.obj_creator()

        # WHEN commit succeeds
        with patch('utilities.db.DB.execute') as exe:
            exe.return_value = None

            with patch("utilities.db.DB.fetch_one") as fo:
                fo.return_value = (123,)

                assert cvc.commit_user_vote() == (123,)

                exe.assert_called_once()
                fo.assert_called_once()

        # # WHEN commit fails
        with patch('utilities.db.DB.execute') as exe:
            exe.return_value = None

            with patch("utilities.db.DB.fetch_one") as fo:
                fo.return_value = None

                assert cvc.commit_user_vote() is None

                exe.assert_called_once()
                fo.assert_called_once()


class ConstituentVoteConverterTest(unittest.TestCase):

    @property
    def subject(self):
        return ConstituentVoteConverter

    def test_timestamp_converter(self):
        time_obj = self.subject.timestamp_converter("1523904505")

        assert time_obj == '2018-04-16T18:48:25'

        time_obj = self.subject.timestamp_converter("1523904505000")

        assert time_obj == '2018-04-16T18:48:25'


    def test_bill_id_converter(self):
        with patch('utilities.db.DB.fetch_one') as db:
            db.return_value = (123,)
            ret = self.subject.bill_id_converter('hr123-115')

        assert 123 == ret

        with patch('utilities.db.DB.fetch_one') as db:
            with patch('vote_tallies.constituent_vote.ConstituentVoteConverter._add_bill') as cvc:
                cvc.return_value = True

                db.side_effect = [None, (123,)]

                ret = self.subject.bill_id_converter('hr123-115')
                cvc.assert_called_once()

        assert 123 == ret

    def test_add_bill(self):
        with patch("bill_updater.tracked_bill.TrackedBill") as tb:
            instance = tb.return_value
            instance.upsert.return_value = True

            self.subject._add_bill("hr123", bill_kreator_klass=tb)
            tb.assert_called_once_with("hr123")

            instance.upsert.assert_called_once()

        # passing in bill_id with session
        with patch("bill_updater.tracked_bill.TrackedBill") as tb:
            instance = tb.return_value
            instance.upsert.return_value = True

            self.subject._add_bill("hr123-115", bill_kreator_klass=tb)
            tb.assert_called_once_with("hr123")

            instance.upsert.assert_called_once()

    def test_user_token_converter(self):

        with patch('utilities.db.DB.fetch_one') as db:
            db.return_value = (123,'abc123')

            assert self.subject.user_token_converter('abc123') == 123
            db.assert_called_once()

        with patch('utilities.db.DB.fetch_one') as db:
            db.return_value = None

            assert self.subject.user_token_converter('abc123') is None
            db.assert_called_once()

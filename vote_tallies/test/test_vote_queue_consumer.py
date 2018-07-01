import vote_tallies.vote_queue_consumer as qc
import unittest
import pytest
import json
from unittest.mock import MagicMock, patch
import logging

def setup_module(module):
    logger = logging.getLogger()
    logger.disabled = True

def teardown_module(module):
    logger = logging.getLogger()
    logger.disabled = False

@pytest.fixture(scope="module")
def expected_message_json():
    dict_json = {
        "timestamp": "1523904505000",
        "user_token": "abc123",
        "bill_opinions": [
            {
                "bill_id": "hr-123",
                "vote": "for"
            },
            {
                "bill_id": "s345",
                "vote": "against"
            }
        ]
    }

    return json.dumps(dict_json)

def message_storage_mock(msg_body):
    message_mock = MagicMock()
    message_mock.body = msg_body
    message_mock.delete.return_value = True

    return message_mock

# NOTE: expected_message_json is a fixture (I'm new at this)
def test_process_message(expected_message_json):

    # golden path
    message_mock = message_storage_mock(expected_message_json)

    with patch("unittest.mock.MagicMock") as cvc:
        instance = cvc.return_value
        # NOTE: it actually returns (123, ), a truthy value
        instance.commit_user_vote.return_value = True

        qc.process_message(message_mock, processor_klass=unittest.mock.MagicMock)

        assert 2 == instance.commit_user_vote.call_count

        message_mock.delete.assert_called_once()

    # Commit to DB goes wonky
    # wonky = user isn't in the db
    message_mock = message_storage_mock(expected_message_json)

    with patch("unittest.mock.MagicMock") as cvc:
        instance = cvc.return_value
        instance.constituent_id = None

        qc.process_message(message_mock, processor_klass=unittest.mock.MagicMock)

        instance.commit_user_vote.assert_not_called()
        message_mock.delete.assert_not_called()

    # wonky = db commit doesn't save
    message_mock = message_storage_mock(expected_message_json)

    with patch("unittest.mock.MagicMock") as cvc:
        instance = cvc.return_value
        instance.commit_user_vote.side_effect = [True, None]

        qc.process_message(message_mock, processor_klass=unittest.mock.MagicMock)

        assert 2 == instance.commit_user_vote.call_count

        message_mock.delete.assert_not_called()

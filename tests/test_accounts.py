import pytest

from binsort.accounts import Accounts


def test_accounts_are_deferred():
    with pytest.raises(NotImplementedError):
        Accounts().login("a@b.ie", "pw")
    with pytest.raises(NotImplementedError):
        Accounts().history(1)

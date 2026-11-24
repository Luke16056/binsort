"""Accounts: DEFERRED. The interface is defined but not built, as planned in D1.

Login and scan history are a Could have, so the prototype has no accounts.
"""


class Accounts:
    def login(self, email, password):
        raise NotImplementedError("Accounts are deferred in the prototype.")

    def history(self, user_id):
        raise NotImplementedError("Accounts are deferred in the prototype.")

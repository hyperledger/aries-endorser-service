from enum import Enum

from pydantic import BaseModel


class EndorserRoleType(str, Enum):
	Author = "TRANSACTION_AUTHOR"
	Endorser = "TRANSACTION_ENDORSER"


class EndorseTransactionState(str, Enum):
	transaction_created = "transaction_created"
	request_sent = "request_sent"
	request_received = "request_received"
	transaction_endorsed = "transaction_endorsed"
	transaction_refused = "transaction_refused"
	transaction_resent = "transaction_resent"
	transaction_resent_received = "transaction_resent_received"
	transaction_cancelled = "transaction_cancelled"
	transaction_acked = "transaction_acked"

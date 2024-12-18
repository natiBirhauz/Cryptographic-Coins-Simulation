import hashlib
from .utils import PublicKey, TxID, Signature
from typing import Optional


class Transaction:
    """Represents a transaction that moves a single coin
    A transaction with no source creates money. It will only be created by the bank."""

    def __init__(self, output: PublicKey, input: Optional[TxID], signature: Signature) -> None:
        # do not change the name of this field:
        self.output: PublicKey = output
        # do not change the name of this field:
        self.input: Optional[TxID] = input
        # do not change the name of this field:
        self.signature: Signature = signature

    def get_txid(self) -> TxID:
        """
        Returns the identifier of this transaction. This is the SHA256 of the transaction contents.
        """
        # Concatenate the contents of the transaction and hash them
        tx_contents = (self.input or b"") + self.output + self.signature
        return TxID(hashlib.sha256(tx_contents).digest())
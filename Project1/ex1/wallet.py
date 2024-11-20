from .utils import PrivateKey, PublicKey, Signature, sign, gen_keys
from .transaction import Transaction
from .bank import Bank
from typing import Optional, List

class Wallet:
    def __init__(self) -> None:
        """
        Initializes a new wallet with a private key and its corresponding public key.
        """
        self.private_key, self.public_key = gen_keys()  # Generate private and public keys
        self.unspent_outputs: List[Transaction] = []  # Unspent outputs the wallet can spend
        self.frozen_outputs: List[Transaction] = []  # Outputs already used but not confirmed

    def update(self, bank: Bank) -> None:
        """
        Updates the wallet's balance by querying the bank for unspent outputs.
        Processes new blocks from the bank since the last update.
        """
        all_utxo = bank.get_utxo()
        # Filter out spent transactions
        self.unspent_outputs = [tx for tx in all_utxo if tx.output == self.public_key]

    def create_transaction(self, target: PublicKey) -> Optional[Transaction]:
        """
        Creates and signs a transaction to send an unspent coin to the target address.
        If there are no available coins to spend, returns None.
        """
        # Choose an unspent transaction
        for tx in self.unspent_outputs:
            if tx not in self.frozen_outputs:
                self.frozen_outputs.append(tx)  # Mark as frozen
                # Sign the input + output as the message
                message = tx.get_txid() + target
                signature = sign(message, self.private_key)
                return Transaction(output=target, input=tx.get_txid(), signature=signature)
        return None

    def unfreeze_all(self) -> None:
        """
        Allows the wallet to attempt to re-spend outputs that it created transactions for,
        but that weren't included in a block.
        """
        self.frozen_outputs = []

    def get_balance(self) -> int:
        """
        Returns the wallet's balance, based on the last update from the bank.
        Includes coins that are frozen but not yet confirmed in a block.
        """
        return len(self.unspent_outputs)

    def get_address(self) -> PublicKey:
        """
        Returns the wallet's public address (its public key).
        """
        return self.public_key

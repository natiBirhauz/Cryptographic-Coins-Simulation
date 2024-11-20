from .utils import BlockHash
from .transaction import Transaction
from typing import List
import hashlib


class Block:
    def __init__(self, transactions: List[Transaction], prev_block_hash: BlockHash) -> None:
        """
        Initializes a new block.
        :param transactions: List of transactions in this block.
        :param prev_block_hash: Hash of the previous block in the blockchain.
        """
        self.transactions = transactions  # List of transactions in the block
        self.prev_block_hash = prev_block_hash  # Hash of the previous block

    def get_block_hash(self) -> BlockHash:
        """
        Computes and returns the hash of this block.
        """
        # Combine the hashes of the previous block and the transactions to compute the hash
        block_contents = self.prev_block_hash + b"".join(tx.get_txid() for tx in self.transactions)
        return BlockHash(hashlib.sha256(block_contents).digest())

    def get_transactions(self) -> List[Transaction]:
        """
        Returns the list of transactions in this block.
        """
        return self.transactions

    def get_prev_block_hash(self) -> BlockHash:
        """
        Gets the hash of the previous block in the chain.
        """
        return self.prev_block_hash

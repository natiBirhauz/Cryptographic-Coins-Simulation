from .utils import BlockHash, PublicKey, Signature, GENESIS_BLOCK_PREV, sign, verify, TxID
from .transaction import Transaction
from .block import Block
from typing import List, Dict, Optional


class Bank:
    def __init__(self) -> None:
        """Creates a bank with an empty blockchain and an empty mempool."""
        self.blockchain: Dict[BlockHash, Block] = {}  # Maps block hashes to Block objects
        self.mempool: List[Transaction] = []  # List of transactions waiting to be included in a block
        self.latest_hash: BlockHash = GENESIS_BLOCK_PREV  # The hash of the latest block in the chain

    def get_transaction_output(self, txid: TxID) -> Optional[PublicKey]:
        """
        Given a transaction ID, returns the public key (output) of the transaction.
        Returns None if the transaction is not found in the blockchain.
        """
        for block_hash, block in self.blockchain.items():
            for transaction in block.get_transactions():
                if transaction.get_txid() == txid:
                    return transaction.output
        return None  # No matching transaction found

    def add_transaction_to_mempool(self, transaction: Transaction) -> bool:
        """
        Adds a transaction to the mempool if it's valid.
        Returns False if:
        (i) The transaction is invalid (signature fails).
        (ii) The source doesn't have the coin they try to spend.
        (iii) There is a contradicting transaction in the mempool.
        (iv) An unauthorized attempt to create money.
        """
        # (i) Check if the signature is valid (for transactions with an input)
        if transaction.input:
            output = self.get_transaction_output(transaction.input)
            if output is None or not verify(transaction.input + transaction.output, transaction.signature, output):
                print("Invalid transaction: Signature verification failed.")
                return False

        # Ensure no double spending
        if transaction.input and any(tx.input == transaction.input for tx in self.mempool):
            print("Invalid transaction: Double spending detected.")
            return False

        # (iv) Ensure input is None only for money creation, and it must have a valid random signature
        if transaction.input is None and (not transaction.signature or len(transaction.signature) != 48):
            print("Invalid transaction: Money creation signature invalid.")
            return False

        # Add the transaction to the mempool
        self.mempool.append(transaction)
        return True

    def end_day(self, limit: int = 10) -> BlockHash:
        """
        Commits transactions from the mempool to a new block and returns its hash.
        """
        transactions = self.mempool[:limit]  # Get the first `limit` transactions
        new_block = Block(transactions, self.latest_hash)
        block_hash = new_block.get_block_hash()

        # Update blockchain and mempool
        self.blockchain[block_hash] = new_block
        self.latest_hash = block_hash
        self.mempool = self.mempool[limit:]  # Remove committed transactions

        return block_hash

    def get_block(self, block_hash: BlockHash) -> Block:
        """Returns a block object given its hash. Raises an exception if not found."""
        if block_hash not in self.blockchain:
            raise ValueError("Block not found")
        return self.blockchain[block_hash]

    def get_latest_hash(self) -> BlockHash:
        """Returns the hash of the latest block."""
        return self.latest_hash

    def get_mempool(self) -> List[Transaction]:
        """Returns the list of transactions that haven't been included in a block yet."""
        return self.mempool

    def get_utxo(self) -> List[Transaction]:
        """Returns the list of unspent transactions."""
        utxo = []
        spent = {tx.input for block in self.blockchain.values() for tx in block.get_transactions() if tx.input}
        for block in self.blockchain.values():
            for tx in block.get_transactions():
                if tx.get_txid() not in spent:
                    utxo.append(tx)
        return utxo

    def create_money(self, target: PublicKey) -> None:
        """
        Creates money out of thin air by adding a transaction to the mempool.
        """
        import secrets
        random_data = secrets.token_bytes(48)
        transaction = Transaction(output=target, input=None, signature=random_data)
        self.mempool.append(transaction)


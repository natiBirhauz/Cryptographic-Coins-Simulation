
# Cryptographic Coins Simulation
students: Nati Birhauz- 311227888
Gavriel Shalem - 205461486

## Overview
This project is a simulation of a cryptographic coin system based on UTxO (Unspent Transaction Output). The system implements basic blockchain operations, including creating wallets, making transactions, validating signatures, and managing a blockchain. The project is developed in Python and adheres to cryptographic principles.

---

## Features
- **Wallet System**: Users can create wallets with private and public keys, allowing them to make and receive transactions.
- **Transactions**: A transaction system with input validation, signature verification, and double-spend prevention.
- **Blockchain**: A simple blockchain implementation that maintains transaction records and verifies the integrity of blocks.
- **UTxO Management**: Tracks unspent transaction outputs, ensuring that coins are only spent once.
- **Secure Key Management**: Private and public keys are generated and used for signing and verifying transactions using the Ed25519 algorithm.

---

## Files
- **`__init__.py`**: Exposes core classes and functions for use in external scripts or tests.
- **`bank.py`**: Implements the `Bank` class, which manages the blockchain, validates transactions, and handles the mempool.
- **`block.py`**: Defines the `Block` class, responsible for storing transactions and linking blocks via hashes.
- **`transaction.py`**: Implements the `Transaction` class for representing transactions, including hashing and signing.
- **`utils.py`**: Provides cryptographic utilities for signing and verifying messages, and key generation.
- **`wallet.py`**: Implements the `Wallet` class, enabling users to manage keys, balances, and create transactions.
- **`requirements.txt`**: Lists required Python packages (e.g., `mypy`, `pytest`, `cryptography`).

---

## Installation
1. Clone or download the repository.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage
1. **Initialize a Bank and Wallets**:
   ```python
   from ex1 import Bank, Wallet

   bank = Bank()
   alice = Wallet()
   bob = Wallet()
   ```

2. **Create a Transaction**:
   ```python
   alice.update(bank)  # Update Alice's wallet to fetch her UTxOs
   transaction = alice.create_transaction(bob.get_address())
   bank.add_transaction_to_mempool(transaction)
   ```

3. **Commit Transactions to a Block**:
   ```python
   bank.end_day()  # Add transactions from the mempool to a new block
   ```

4. **Check Balances**:
   ```python
   alice.update(bank)
   bob.update(bank)
   print(f"Alice's Balance: {alice.get_balance()}")
   print(f"Bob's Balance: {bob.get_balance()}")
   ```

---

## Tests
The project includes a comprehensive set of tests to ensure functionality:
- Located in the `tests` directory.
- Run the tests using `pytest`:
  ```bash
  python -m pytest
  ```

### Test Coverage
- **Transaction validation**: Validates correct signatures and prevents double-spending.
- **Blockchain integrity**: Ensures all blocks are correctly linked and hashed.
- **UTxO management**: Verifies that only unspent outputs are used.

---

## Cryptographic Features
- **Ed25519 Algorithm**: Used for secure signing and verifying of messages.
- **SHA256**: Used for hashing transaction and block data.
- **UTxO-based Ledger**: Ensures secure and traceable coin transfers.

---

## Assignment Context
This project was developed as part of a cryptographic coins simulation assignment. The goal was to build a system with secure transaction handling and blockchain management, emphasizing UTxO models and signature verification.

---

## References
- [Python Cryptography Library Documentation](https://cryptography.io/en/latest/)
- [Mypy Documentation](https://mypy.readthedocs.io/en/stable/)
- [Python hashlib Library](https://docs.python.org/3/library/hashlib.html)

---

Feel free to reach out with questions or feedback. Happy coding! 🎉

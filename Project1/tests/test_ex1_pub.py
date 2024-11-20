from ex1 import *


def test_block(bank: Bank, alice_coin: Transaction) -> None:
    hash1 = bank.get_latest_hash()
    block = bank.get_block(hash1)
    assert len(block.get_transactions()) == 1
    assert block.get_prev_block_hash() == GENESIS_BLOCK_PREV

    bank.end_day()

    hash2 = bank.get_latest_hash()
    block2 = bank.get_block(hash2)
    assert len(block2.get_transactions()) == 0
    assert block2.get_prev_block_hash() == hash1


def test_create_money_happy_flow(bank: Bank, alice: Wallet, bob: Wallet, alice_coin: Transaction) -> None:
    alice.update(bank)
    bob.update(bank)
    assert alice.get_balance() == 1
    assert bob.get_balance() == 0
    utxo = bank.get_utxo()
    assert len(utxo) == 1
    assert utxo[0].output == alice.get_address()


def test_transaction_happy_flow(bank: Bank, alice: Wallet, bob: Wallet,
                                alice_coin: Transaction) -> None:
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    assert bank.add_transaction_to_mempool(tx)
    assert bank.get_mempool() == [tx]
    bank.end_day(limit=1)
    alice.update(bank)
    bob.update(bank)
    assert alice.get_balance() == 0
    assert bob.get_balance() == 1
    assert not bank.get_mempool()
    assert bank.get_utxo()[0].output == bob.get_address()
    assert tx == bank.get_block(bank.get_latest_hash()).get_transactions()[0]


def test_re_transmit_the_same_transaction(bank: Bank, alice: Wallet, bob: Wallet,
                                          alice_coin: Transaction) -> None:
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    assert bank.add_transaction_to_mempool(tx)
    assert not bank.add_transaction_to_mempool(tx)
    assert bank.get_mempool() == [tx]


def test_spend_coin_not_mine(bank2: Bank, alice: Wallet, bob: Wallet, alice_coin: Transaction) -> None:
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    assert not bank2.add_transaction_to_mempool(tx)
    assert not bank2.get_mempool()


def test_change_output_of_signed_transaction(bank: Bank, alice: Wallet, bob: Wallet, charlie: Wallet,
                                             alice_coin: Transaction) -> None:
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    tx = Transaction(output=charlie.get_address(),
                     input=tx.input, signature=tx.signature)
    assert not bank.add_transaction_to_mempool(tx)
    assert not bank.get_mempool()
    bank.end_day()
    alice.update(bank)
    bob.update(bank)
    assert alice.get_balance() == 1
    assert bob.get_balance() == 0
    assert charlie.get_balance() == 0


def test_change_coin_of_signed_transaction(bank: Bank, alice: Wallet, bob: Wallet, charlie: Wallet,
                                           alice_coin: Transaction) -> None:
    # Give Bob two coins
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    bank.add_transaction_to_mempool(tx)
    bank.create_money(bob.get_address())
    bank.end_day()
    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)
    bob_coin1, bob_coin2 = bank.get_utxo()
    # Bob gives a coin to Charlie, and Charlie wants to steal the second one
    tx = bob.create_transaction(charlie.get_address())
    assert tx is not None
    tx2 = Transaction(output=tx.output, input=bob_coin2.get_txid() if tx.input == bob_coin1.get_txid()
                      else bob_coin1.get_txid(), signature=tx.signature)
    assert not bank.add_transaction_to_mempool(tx2)
    assert not bank.get_mempool()
    assert bank.add_transaction_to_mempool(tx)
    assert bank.get_mempool()
    bank.end_day()
    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)
    assert alice.get_balance() == 0
    assert bob.get_balance() == 1
    assert charlie.get_balance() == 1


def test_double_spend_fail(bank: Bank, alice: Wallet, bob: Wallet, charlie: Wallet, alice_coin: Transaction) -> None:
    tx1 = alice.create_transaction(bob.get_address())
    assert tx1 is not None
    # make alice spend the same coin
    alice.update(bank)
    alice.unfreeze_all()
    tx2 = alice.create_transaction(charlie.get_address())
    assert tx2 is not None  # Alice will try to double spend

    assert bank.add_transaction_to_mempool(tx1)
    assert not bank.add_transaction_to_mempool(tx2)
    bank.end_day(limit=2)
    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)
    assert alice.get_balance() == 0
    assert bob.get_balance() == 1
    assert charlie.get_balance() == 0

def test_insufficient_balance(bank: Bank, alice: Wallet, bob: Wallet, alice_coin: Transaction) -> None:
    # Alice spends her only coin
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    assert bank.add_transaction_to_mempool(tx)
    bank.end_day()
    alice.update(bank)
    bob.update(bank)

    # Alice tries to create another transaction
    tx2 = alice.create_transaction(bob.get_address())
    assert tx2 is None  # Alice should not have enough balance

def test_multiple_transactions(bank: Bank, alice: Wallet, bob: Wallet, charlie: Wallet, alice_coin: Transaction) -> None:
    # Alice sends her coin to Bob
    tx1 = alice.create_transaction(bob.get_address())
    assert tx1 is not None
    assert bank.add_transaction_to_mempool(tx1)

    # Commit the transaction
    bank.end_day()
    alice.update(bank)
    bob.update(bank)  # Bob updates his wallet

    # Bob sends the coin to Charlie
    tx2 = bob.create_transaction(charlie.get_address())
    assert tx2 is not None, "Bob should have enough balance to create a transaction"
    assert bank.add_transaction_to_mempool(tx2)

    # Commit Bob's transaction
    bank.end_day()
    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)

    # Verify balances
    assert alice.get_balance() == 0
    assert bob.get_balance() == 0
    assert charlie.get_balance() == 1

def test_unauthorized_money_creation(bank: Bank, alice: Wallet) -> None:
    # Attempt to create a fake transaction
    tx = Transaction(output=alice.get_address(), input=None, signature=b"fake_signature")
    assert not bank.add_transaction_to_mempool(tx)  # Unauthorized money creation should fail
    assert not bank.get_mempool()  # Mempool should remain empty


def test_mempool_clear_after_block(bank: Bank, alice: Wallet, bob: Wallet, alice_coin: Transaction) -> None:
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    assert bank.add_transaction_to_mempool(tx)

    # Ensure transaction is in mempool
    assert bank.get_mempool() == [tx]

    # Commit the transaction
    bank.end_day()
    assert not bank.get_mempool()  # Mempool should be empty after end_day


def test_empty_block(bank: Bank) -> None:
    # End the day without any transactions
    initial_hash = bank.get_latest_hash()
    bank.end_day()
    new_hash = bank.get_latest_hash()

    # Verify blockchain state
    assert initial_hash != new_hash  # A new block was created
    block = bank.get_block(new_hash)
    assert len(block.get_transactions()) == 0  # Block should be empty

def test_blockchain_growth(bank: Bank, alice: Wallet, bob: Wallet, alice_coin: Transaction) -> None:
    # Create and commit a transaction
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    assert bank.add_transaction_to_mempool(tx)
    bank.end_day()

    # Commit an empty block
    hash1 = bank.get_latest_hash()
    bank.end_day()
    hash2 = bank.get_latest_hash()

    # Validate blockchain
    assert hash1 != hash2, "A new block should be created"
    assert len(bank.blockchain) == 3  # Genesis block + 2 new blocks

def test_reuse_address(bank: Bank, alice: Wallet, bob: Wallet, charlie: Wallet, alice_coin: Transaction) -> None:
    tx1 = alice.create_transaction(bob.get_address())
    assert tx1 is not None
    assert bank.add_transaction_to_mempool(tx1)
    bank.end_day()

    bob.update(bank)
    tx2 = bob.create_transaction(alice.get_address())
    assert tx2 is not None
    assert bank.add_transaction_to_mempool(tx2)
    bank.end_day()

    alice.update(bank)
    assert alice.get_balance() == 1

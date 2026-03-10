"""
Minebean Web3 Module
Handles connection to Base Mainnet, wallet management, and contract interactions.
"""

import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

BASE_RPC = "https://mainnet.base.org"

# Contract Addresses
GRIDMINING_ADDRESS = "0x9632495bDb93FD6B0740Ab69cc6c71C9c01da4f0"

# Minimal ABIs for what we need
GRIDMINING_ABI = [
    {
        "inputs": [{"internalType": "uint8[]", "name": "blockIds", "type": "uint8[]"}],
        "name": "deploy",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "claimETH",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "claimBEAN",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]


class MinebeanWeb3:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        self.private_key = os.getenv("PRIVATE_KEY")
        self.account = None
        self.grid_contract = None

        if self.private_key and self.private_key != "your_private_key_here":
            if not self.private_key.startswith("0x"):
                self.private_key = "0x" + self.private_key
            try:
                self.account = self.w3.eth.account.from_key(self.private_key)
                self.grid_contract = self.w3.eth.contract(
                    address=self.w3.to_checksum_address(GRIDMINING_ADDRESS),
                    abi=GRIDMINING_ABI
                )
                print(f"[Web3] Connected with wallet: {self.account.address}")
            except Exception as e:
                print(f"[Web3] Failed to load wallet: {e}")
        else:
            print("[Web3] No valid PRIVATE_KEY found in .env (View-only mode)")

    def get_address(self) -> str:
        return self.account.address if self.account else ""

    def get_eth_balance(self) -> float:
        if not self.account:
            return 0.0
        try:
            bal = self.w3.eth.get_balance(self.account.address)
            return float(self.w3.from_wei(bal, 'ether'))
        except Exception as e:
            print(f"[Web3] Balance error: {e}")
            return 0.0

    def deploy(self, block_ids: list[int], deploy_eth: float) -> str:
        """
        Deploy ETH to the GridMining contract.
        deploy_eth is the TOTAL amount. Minimum is 0.0000025 * len(block_ids)
        """
        if not self.account or not self.grid_contract:
            print("[Web3] Cannot deploy: Wallet not initialized.")
            return ""

        try:
            value_wei = self.w3.to_wei(deploy_eth, 'ether')
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # Use dynamic gas pricing from the network
            gas_price = self.w3.eth.gas_price
            
            # Build transaction
            txn = self.grid_contract.functions.deploy(block_ids).build_transaction({
                'from': self.account.address,
                'value': value_wei,
                'nonce': nonce,
                'gasPrice': gas_price,
            })
            
            # Estimate gas
            txn['gas'] = self.w3.eth.estimate_gas(txn)

            # Sign & Send
            signed_txn = self.account.sign_transaction(txn)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            hx = tx_hash.hex()
            print(f"[Web3] Deployed {deploy_eth} ETH to blocks {block_ids}. TX: {hx}")
            return hx
            
        except Exception as e:
            print(f"[Web3] Deploy error: {e}")
            return ""

    def claim_eth(self) -> str:
        """Claim pending ETH rewards."""
        if not self.account or not self.grid_contract:
            return ""
        try:
            txn = self.grid_contract.functions.claimETH().build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'maxFeePerGas': self.w3.to_wei(0.1, 'gwei'),
                'maxPriorityFeePerGas': self.w3.to_wei(0.001, 'gwei'),
            })
            signed_txn = self.account.sign_transaction(txn)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            print(f"[Web3] Claimed ETH. TX: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            print(f"[Web3] claimETH error: {e}")
            return ""

    def claim_bean(self) -> str:
        """Claim pending BEAN tokens."""
        if not self.account or not self.grid_contract:
            return ""
        try:
            txn = self.grid_contract.functions.claimBEAN().build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'maxFeePerGas': self.w3.to_wei(0.1, 'gwei'),
                'maxPriorityFeePerGas': self.w3.to_wei(0.001, 'gwei'),
            })
            signed_txn = self.account.sign_transaction(txn)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            print(f"[Web3] Claimed BEAN. TX: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            print(f"[Web3] claimBEAN error: {e}")
            return ""

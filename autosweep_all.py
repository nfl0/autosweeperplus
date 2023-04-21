from web3 import Web3
from dotenv import load_dotenv
import os
import time

load_dotenv()

INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')
COMPROMISED_PRIVATE_KEYS = os.getenv('COMPROMISED_PRIVATE_KEYS').split(',')
NEW_ETH_ADDRESS = Web3.toChecksumAddress(os.environ.get('NEW_ETH_ADDRESS'))

INFURA_RPC_URLS = {
    'mainnet': f'https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}',
    'polygon': f'https://polygon-mainnet.infura.io/v3/{INFURA_PROJECT_ID}',
    'optimism': f'https://optimism-mainnet.infura.io/v3/{INFURA_PROJECT_ID}',
    'arbitrum': f'https://arbitrum-mainnet.infura.io/v3/{INFURA_PROJECT_ID}',
    'avalanche': f'https://avalanche-mainnet.infura.io/v3/{INFURA_PROJECT_ID}',
}

def sweep_funds(network, private_key):
    w3 = Web3(Web3.HTTPProvider(INFURA_RPC_URLS[network]))

    # Get the compromised wallet's public address
    compromised_account = w3.eth.account.privateKeyToAccount(private_key)
    compromised_address = compromised_account.address

    # Get the balance and nonce of the compromised wallet
    balance = w3.eth.getBalance(compromised_address)
    nonce = w3.eth.getTransactionCount(compromised_address)

    # Set the gas price and gas limit
    gas_price = w3.eth.gasPrice
    gas_limit = 21000

    # Adjust gas settings for specific networks
    if network == 'optimism':
        gas_price = w3.toWei('0.015', 'gwei')
        gas_limit = 60000
    elif network == 'arbitrum':
        gas_limit = 1000000

    # Calculate the transfer amount (balance - gas_fee)
    transfer_amount = balance - (gas_price * gas_limit)

    if transfer_amount > 0:
        # Create and sign the transaction
        transaction = {
            'to': NEW_ETH_ADDRESS,
            'value': transfer_amount,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': w3.eth.chainId,
        }
        signed_transaction = compromised_account.signTransaction(transaction)

        # Send the transaction
        transaction_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)
        print(f'Transferred {transfer_amount} wei from {compromised_address} to {NEW_ETH_ADDRESS} on {network}.')
    else:
        print(f'No funds to sweep on {network}.')

def main():
    while True:
        for network in INFURA_RPC_URLS.keys():
            for private_key in COMPROMISED_PRIVATE_KEYS:
                try:
                    sweep_funds(network, private_key)
                except Exception as e:
                    print(f'Error on {network} for private key {private_key}: {e}')
        time.sleep(8)

if __name__ == '__main__':
    main()

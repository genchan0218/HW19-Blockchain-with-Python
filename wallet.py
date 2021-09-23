{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "64ec00cb-b57b-43e8-a86a-d9f67b33a3ae",
   "metadata": {},
   "outputs": [],
   "source": [
    "import subprocess\n",
    "import json\n",
    "import os\n",
    "from constants import BTC, BTCTEST, ETH\n",
    "from pprint import pprint\n",
    "from dotenv import load_dotenv\n",
    "load_dotenv()\n",
    "from bit import PrivateKeyTestnet\n",
    "from bit.network import NetworkAPI\n",
    "from web3 import Web3, middleware, Account\n",
    "from web3.gas_strategies.time_based import medium_gas_price_strategy\n",
    "from web3.middleware import geth_poa_middleware"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7e3aee61-8820-4e57-92e4-9e9f2a277356",
   "metadata": {},
   "outputs": [],
   "source": [
    "# connect Web3\n",
    "w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "57579978-33c3-4dd1-9ab6-8615c0b6d3e3",
   "metadata": {},
   "outputs": [],
   "source": [
    "# enable PoA middleware\n",
    "w3.middleware_onion.inject(geth_poa_middleware, layer=0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2f84b08d-684d-4116-b1ed-cf4127e19e76",
   "metadata": {},
   "outputs": [],
   "source": [
    "# set gas price strategy to built-in \"medium\" algorithm (est ~5min per tx)\n",
    "# see https://web3py.readthedocs.io/en/stable/gas_price.html?highlight=gas\n",
    "# see https://ethgasstation.info/ API for a more accurate strategy\n",
    "w3.eth.setGasPriceStrategy(medium_gas_price_strategy)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f1434124-ebb8-4b2f-a27a-42a1ee5d857d",
   "metadata": {},
   "outputs": [],
   "source": [
    "# including a mnemonic with prefunded test tokens for testing\n",
    "mnemonic = os.getenv(\"mnemonic\")\n",
    "def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):\n",
    "    command = f'php ./derive -g --mnemonic=\"{mnemonic}\" --cols=all --coin={coin} --numderive={depth} --format=json'\n",
    "    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)\n",
    "    (output, err) = p.communicate()\n",
    "    p_status = p.wait()\n",
    "    return json.loads(output)\n",
    "def priv_key_to_account(coin, priv_key):\n",
    "    if coin == ETH:\n",
    "        return Account.privateKeyToAccount(priv_key)\n",
    "    if coin == BTCTEST:\n",
    "        return PrivateKeyTestnet(priv_key)\n",
    "def create_tx(coin, account, to, amount):\n",
    "    if coin == ETH:\n",
    "        value = w3.toWei(amount, \"ether\") # convert 1.2 ETH to 120000000000 wei\n",
    "        gasEstimate = w3.eth.estimateGas({ \"to\": to, \"from\": account, \"amount\": value })\n",
    "        return {\n",
    "            \"to\": to,\n",
    "            \"from\": account,\n",
    "            \"value\": value,\n",
    "            \"gas\": gasEstimate,\n",
    "            \"gasPrice\": w3.eth.generateGasPrice(),\n",
    "            \"nonce\": w3.eth.getTransactionCount(account),\n",
    "            \"chainId\": w3.eth.chain_id\n",
    "        }\n",
    "    if coin == BTCTEST:\n",
    "        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])\n",
    "def send_tx(coin, account, to, amount):\n",
    "    if coin == ETH:\n",
    "        raw_tx = create_tx(coin, account.address, to, amount)\n",
    "        signed = account.signTransaction(raw_tx)\n",
    "        return w3.eth.sendRawTransaction(signed.rawTransaction)\n",
    "    if coin == BTCTEST:\n",
    "        raw_tx = create_tx(coin, account, to, amount)\n",
    "        signed = account.sign_transaction(raw_tx)\n",
    "        return NetworkAPI.broadcast_tx_testnet(signed)\n",
    "coins = {\n",
    "    ETH: derive_wallets(coin=ETH),\n",
    "    BTCTEST: derive_wallets(coin=BTCTEST),\n",
    "}"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

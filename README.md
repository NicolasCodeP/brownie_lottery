# Lottery Smart Contract with Brownie - Solidity 0.8

## Introduction

**Note:** Brownie is no longer actively maintained. It is recommended for new users to consider using framework such as the [Ape framework](https://github.com/ApeWorX/ape) for smart contract development and testing.

Smart Contract Application updated to solidity >=0.8.0 <0.9.0 from [Patrick Collins](https://github.com/PatrickAlphaC/smartcontract-lottery) FreeCodeCamp course: [Solidity, Blockchain, and Smart Contract Course – Beginner to Expert Python Tutorial](https://www.youtube.com/watch?v=M576WGiDBdQ&t=27270s), with comments.

This `Lottery` smart contract project is inspired by the teachings of Patrick Collins in his blockchain and smart contract development course. It has been updated to work with Solidity version 0.8.0 and higher, incorporating best practices for smart contract development with Brownie, a Python-based development and testing framework for Ethereum.

The `Lottery` contract allows for decentralized crowdfunding, where users can contribute ETH and the contract owner can withdraw the accumulated funds. This project serves as a practical example of how to build, deploy, and test a smart contract using the latest Solidity features.

Live example:  
[Lottery Contract deployed on Sepolia Testnet](https://sepolia.etherscan.io/address/0xd24b673d89d7f6fe5d8d42af41172e608db433f8)

## Features

- Decentralized lottery participation facilitated through Ethereum contributions based on a predetermined USD fee.
- Administrative control over lottery duration with transparent and auditable closure mechanisms.
- Provably fair and transparent random winner selection process.

## Prerequisites

To set up and interact with this project, you'll need:

- [Node.js and npm](https://nodejs.org/)
  - [Ganache](https://github.com/trufflesuite/ganache)
- [Python 3.6 or later](https://www.python.org/downloads/)
  - [Brownie](https://eth-brownie.readthedocs.io/en/stable/install.html)
- [MetaMask](https://metamask.io) with test ETH for deployment on testnets.

### Sepolia testnet

Sepolia testnet need to be added to [brownie network list](https://ethereum.stackexchange.com/questions/147238/infura-network-support-for-sepollia-in-brownie).  
Update `network-config.yaml` file located at ~/USERNAME/.brownie/network-config.yaml

```yaml
- name: Sepolia (Infura)
  chainid: 11155111
  explorer: https://api-sepolia.etherscan.io/api
  host: https://sepolia.infura.io/v3/$WEB3_INFURA_PROJECT_ID
  id: sepolia
  multicall2: '0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696'
  provider: infura
```

## Setup

Clone the repository and install the necessary Python dependencies:

```bash
git clone https://github.com/NicolasCodeP/brownie_fund_me.git
cd Lottery
pip install -r requirements.txt
```

## Configuration

Set up your environment variables in a `.env` file to store your Infura project ID and private key.
Ensure that you replace placeholders like `YourInfuraProjectId`, `YourWalletPrivateKey`, and `YourEtherscanToken` with your actual information.

```plaintext
export WEB3_INFURA_PROJECT_ID=`YourInfuraProjectId`
export PRIVATE_KEY=`YourWalletPrivateKey`
export ETHERSCAN_TOKEN=`YourEtherscanToken`
```

## Deployment

Deploy the `Lottery` contract on the Goerli test network with:

```bash
brownie run scripts/deploy.py --network goerli
```

## Contract Interaction

To contribute to the Lottery contract, use the `fund_and_withdraw.py` script:

```bash
brownie run scripts/fund_and_withdraw.py --network goerli
```

## Testing

Execute the following command to run automated tests:

```bash
brownie test
```

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- Patrick Collins and his educational content on Solidity and smart contract development.
- Brownie for the powerful Ethereum development framework.
- OpenZeppelin and Chainlink for their secure and reliable smart contract libraries.

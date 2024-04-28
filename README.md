# Lottery Smart Contract with Brownie - Solidity 0.8

## Introduction

**Note:** Brownie is no longer actively maintained. It is recommended for new users to consider using framework such as the [Ape framework](https://github.com/ApeWorX/ape) for smart contract development and testing.

Smart Contract Application updated to solidity >=0.8.0 <0.9.0 from [Patrick Collins](https://github.com/PatrickAlphaC/smartcontract-lottery) FreeCodeCamp course: [Solidity, Blockchain, and Smart Contract Course – Beginner to Expert Python Tutorial](https://www.youtube.com/watch?v=M576WGiDBdQ&t=27270s), with comments.

This `Lottery` smart contract project is inspired by the teachings of Patrick Collins in his blockchain and smart contract development course. It has been updated to work with Solidity version 0.8.0 and higher, incorporating best practices for smart contract development with Brownie, a Python-based development and testing framework for Ethereum.

The `Lottery` contract allows for decentralized crowdfunding, where users can contribute ETH and the contract owner can withdraw the accumulated funds. This project serves as a practical example of how to build, deploy, and test a smart contract using the latest Solidity features.

Live example:  
[Lottery Contract deployed on Sepolia Testnet]()

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

## Test

Contract deployed:
0x1981f8a75C4532c1DBBd44Ed94C8e6aE036Feae9

Running 'scripts/deploy_lottery.py::main'...
Using account: 0x1cA119EaB69935ab11064F24854806B809392A4F
Funding VRF subscription...
Subscription set and funded: 11169
Subscrition details: (0, 0, '0xbdc722bAE8Ba01c5462891FF83c7d1c010101A95', ('0x4cf5A54939FE6DdB27adE8Bc4310F2D1708204A3',))
Deploying lottery...
Transaction sent: 0xf381c818e2db58385375ab185a2a86f1b3d4bcfc4b392377c4b53fcaf4e680e6
  Gas price: 1.002742218 gwei   Gas limit: 1154627   Nonce: 21
  Lottery.constructor confirmed   Block: 5722738   Gas used: 1040238 (90.09%)
  Lottery deployed at: 0x1981f8a75C4532c1DBBd44Ed94C8e6aE036Feae9

Waiting for <https://api-sepolia.etherscan.io/api> to process contract...
Verification submitted successfully. Waiting for result...
Verification complete. Result: Pass - Verified
Adding lottery to vrf consumer...
Lottery Address: 0x1981f8a75C4532c1DBBd44Ed94C8e6aE036Feae9

From support:  
Every subscription requires a minimum balance to support consuming contracts and buffer against gas price fluctuations. When the balance falls below this threshold, requests remain pending for up to 24 hours until adequately funded. Adding sufficient LINK to the subscription allows pending requests to automatically process, provided they haven't expired.  

If you're planning to make one or a few VRF requests, you can explore Direct Funding model. This model charges at request time and is determined by the current network gas fees.  

You can read more about it: <https://docs.chain.link/vrf/v2/subscription#subscription-limits> and <https://docs.chain.link/vrf#choosing-the-correct-method>

```math
(((Gas lane maximum * (Max verification gas + Callback gas limit)) / (1,000,000,000 Gwei/ETH)) / (ETH/LINK price)) + LINK premium = Minimum LINK 

Same formula broken out into steps
Gas lane maximum * (Max verification gas + Callback gas limit) = Total estimated gas (Gwei)
Total estimated gas (Gwei) / 1,000,000,000 Gwei/ETH = Total estimated gas (ETH)
Total estimated gas (ETH) / (ETH/LINK price) = Total estimated gas (LINK)
Total estimated gas (LINK) + LINK premium = Minimum subscription balance (LINK)
```

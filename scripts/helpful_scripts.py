""" Helpful scripts """

from brownie import (
    Contract,
    network,
    accounts,
    config,
    interface,
    MockV3Aggregator,
    VRFCoordinatorV2Mock,
    # VRFCoordinatorV2Interface,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork-dev", "mainnet-fork-lottery"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

# Used to harcode price directly: 2000,00000000
DECIMAL = 8
STARTING_PRICE = 200000000000

# Used with Web3.toWei function
# DECIMAL = 18
# STARTING_PRICE = 2000


async def listen_to_event(contract, event):
    """Listen to the event of a Contract

    Access the result's 'timed_out' field to check if event trigerred
    """
    # Start listening to the event
    co = contract.events.listen(event, timeout=240)

    # Await the coroutine to get the result
    result = await co

    return result

    # Access the 'timed_out' field from the result
    timed_out = result["timed_out"]

    # Now you can use timed_out as needed
    print(f"Timed out: {timed_out}")


def int_to_uint256(val: int):
    """Encode integer to uint256

    Args:
        val (int): The integer to encode

    >>> int_to_uint256(11238)
    "0x0000000000000000000000000000000000000000000000000000000000002be6"
    """
    # Convert the integer to a 32-byte bytes object
    # With the most significant byte first (big-endian order)
    val_bytes = val.to_bytes(32, byteorder="big")

    # Convert the bytes object to a hexadecimal string
    val_hex = val_bytes.hex()

    # Add the '0x' prefix and zero-pad to 64 characters
    val_uint256 = "0x" + val_hex.zfill(64)

    return val_uint256


def get_account(index=None, id_=None):
    """Return account"""
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id_:
        return accounts.load(id_)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorV2Mock,
    # "vrf_coordinator": VRFCoordinatorV2Interface,
}


def get_contract(contract_name):
    """Grab the contract addresses from the brownie config if defined,
        otherwise, it will deploy a mock version of that contract, and return that mock contract.

    Args:
        contract_name (string)

    Returns:
        brownie.network.contract.ProjectContract:
            The most recently deployed version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
        # MockV3Aggregator[-1]

    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
        # MockV3Aggregator.abi
    return contract


def deploy_mocks():
    """Deploy mock"""
    account = get_account()
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(
            DECIMAL,
            STARTING_PRICE,
            {"from": account},
        )
    print("MockV3Aggregator deployed!")
    VRFCoordinatorV2Mock.deploy(
        # 100000, 100000, {"from": account}  # base fee  # gas price link
        100000000000000000,
        1000000000,
        {"from": account},  # base fee  # gas price link
    )
    print("VRFCoordinatorV2Mock deployed!")
    # VRFCoordinatorV2Interface.deploy({"form": account})
    print("Mocks Deployed!")


def fund_subscription(
    account=None,
    vrf_coordinator=None,
    amount=1000000000000000000,  # 1 LINK
    min_balance=5,
    force=False,
):
    """
    Transfer LINK token back to minimum balance amount.
    Use VRFCoordinatorV2Mock to fund subscription for local test.

    1 LINK = 1000000000000000000,

    Returns:
        subscription_id:
            The subscription set and funded
    """
    account = account if account else get_account()
    vrf_coordinator = (
        vrf_coordinator if vrf_coordinator else get_contract("vrf_coordinator")
    )
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        tx = vrf_coordinator.createSubscription({"from": account})
        tx.wait(1)
        subscription_id = tx.return_value
        tx = vrf_coordinator.fundSubscription(
            subscription_id, amount, {"from": account}
        )
        tx.wait(1)
    else:
        subscription_id = config["networks"][network.show_active()][
            "vrf_subscriptionId"
        ]
        subscription = vrf_coordinator.getSubscription(
            subscription_id, {"from": account}
        )
        if force:
            print(f"Transferring {(amount / (10 ** 18))} LINK...")
            fund_with_link(vrf_coordinator.address, subscription_id, account, amount)
        else:
            subscription_balance = int(subscription[0]) / (10**18)
            print(
                f"Subscription {subscription_id} balance: {subscription_balance} LINK"
            )
            if subscription_balance < min_balance:
                amount = (min_balance - subscription_balance + 1) * (10**18)
                print(
                    f"Balance insufficient, transferring {(amount / (10 ** 18))} LINK..."
                )
                fund_with_link(
                    vrf_coordinator.address, subscription_id, account, amount
                )
            else:
                print("Balance sufficient")

    subscription = vrf_coordinator.getSubscription(subscription_id, {"from": account})
    return subscription_id, subscription


def fund_with_link(
    contract_address,
    subscription_id,
    account=None,
    amount=1000000000000000000,  # 0.1 LINK
):
    """Fund VRF subscription with link token"""
    account = account if account else get_account()
    link_token_address = config["networks"][network.show_active()]["link_token"]
    erc677 = interface.IERC677(link_token_address)
    tx = erc677.transferAndCall(
        contract_address,
        amount,
        int_to_uint256(subscription_id),
        {"from": account},
    )
    tx.wait(1)
    print(f"Funded: {(amount / (10 ** 18))} LINK")

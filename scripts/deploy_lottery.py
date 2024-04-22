""" Deploy lottery script """

import asyncio
import time
from brownie import config, network, Lottery
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    fund_subscription,
    listen_to_event,
)


def deploy_lottery():
    """Deploy lottery"""
    # account = get_account(id_="freecodecamp-account")
    account = get_account()
    print(f"Using account: {account}")
    vrf_coordinator = get_contract("vrf_coordinator")
    print("Funding VRF subscription...")
    vrf_subscription_id, vrf_subscription = fund_subscription(account, vrf_coordinator)
    print(f"Subscription set and funded: {vrf_subscription_id}")
    print(f"Subscrition details: {vrf_subscription}")
    print("Deploying lottery...")
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,  # _priceFeedAddress
        vrf_coordinator.address,  # _vrfCoordinator
        vrf_subscription_id,  # _subscriptionId
        config["networks"][network.show_active()]["vrf_keyHash"],  # _keyHash
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Adding lottery to vrf consumer...")
    print(f"Lottery Address: {lottery.address}")
    tx = vrf_coordinator.addConsumer(
        vrf_subscription_id, lottery.address, {"from": account}
    )
    tx.wait(1)
    print("Lottery added to vrf consumer!")

    # Check if suscription is completed (Need to add test/check)
    vrf_subscription = vrf_coordinator.getSubscription(
        vrf_subscription_id, {"from": account}
    )
    print(f"Subscrition details: {vrf_subscription}")

    print("Lottery deployed!")
    return lottery


def start_lottery():
    """Start the lottery"""
    print("Starting lottery...")
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("The lottery is started!")


def enter_lottery():
    """Enter the lottery"""
    print("Entering lottery...")
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    """End lottery"""
    # https://stackoverflow.com/questions/70523747/smart-contract-lottery-throws-virtualmachineerror-revert-when-ending-the-lott
    print("Ending lottery...")
    account = get_account()
    lottery = Lottery[-1]
    # Fund the contract's subscription to required minimum amount
    lottery.endLottery({"from": account})

    print("Waiting for callback to announce the winner...")
    result = asyncio.run(listen_to_event(lottery, "RequestFulfilled"))

    if result["timed_out"]:
        print("Pending VRF request...\nAdding 0.1 LINK to unlock...")
        asyncio.run(
            asyncio.gather(
                listen_to_event(lottery, "RequestFulfilled"),
                asyncio.to_thread(lambda: refund_lottery(1)),
            )
        )

    print(f"{lottery.recentWinner()} is the new winner!")


def refund_lottery(amount=1000000000000000000):
    """Check and Refund Lottery to the minimum LINK token balance.
    An insufficient balance will result in a pending state"""
    account = get_account()
    vrf_coordinator = get_contract("vrf_coordinator")
    vrf_subscription_id, vrf_subscription = fund_subscription(
        account, vrf_coordinator, amount=amount, force=True
    )
    print(f"Subscription set and funded: {vrf_subscription_id}")
    print(f"Subscrition details: {vrf_subscription}")


def get_lottery_recent_winner():
    """Get the recent winnter of the lottery"""
    lottery = Lottery[-1]
    print(f"{lottery.recentWinner()} is the new winner!")


def main():
    """Main function"""
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()

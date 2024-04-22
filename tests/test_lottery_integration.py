""" Integration Tests Lottery Smart Contract """

import asyncio

import pytest
from brownie import network

from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    listen_to_event,
)


def test_can_pick_winner():
    """Test lottery can pick winner"""
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 100})
    # fund_with_link
    lottery.endLottery({"from": account})
    print("waiting for feedback")
    asyncio.run(listen_to_event(lottery, "RequestFulfilled"))

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0

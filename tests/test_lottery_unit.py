""" Unit Tests Lottery Smart Contract """

# 0.022369463 (At the time)
# 220000000000000000 ==> 1 ETH = 2,200USD

import pytest
from brownie import exceptions, network
from web3 import Web3

from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
)


def test_get_entrance_fee():
    """Test get entrance fee"""
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    # 2,200 eth / usd
    # usdEntryFee is 50
    # 2000/1 == 50/x => x == 0.025
    # 2000/1 == 1/x => x == 0.0005
    expected_entrance_fee = Web3.toWei(lottery.entryFeeInUSD() / 2000, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_update_entrance_fee():
    """Test update entrance fee"""
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    # 2,200 eth / usd
    # usdEntryFee is 50
    # 2000/1 == 50/x => x == 0.025
    # 2000/1 == 1/x => x == 0.0005
    lottery.updateEntranceFee(50, {"from": get_account()})
    expected_entrance_fee = Web3.toWei(lottery.entryFeeInUSD() / 2000, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    """Test can't enter lottery unless lottery started"""
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    """Test can start and enter lottery"""
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    """Test can end lottery"""
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.endLottery({"from": account})
    # Assert
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    """Test can pick winner correctly"""
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    account = get_account()
    lottery.startLottery({"from": account})
    starting_balance_of_account = account.balance()
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(2), "value": lottery.getEntranceFee()})
    balance_of_lottery = lottery.balance()
    transaction = lottery.endLottery({"from": account})
    transaction.wait(1)
    request_id = transaction.events["RequestSent"]["requestId"]
    print(f"Request id = {request_id}")
    static_rng = 777
    tx = get_contract("vrf_coordinator").fulfillRandomWordsWithOverride(
        request_id, lottery.address, [static_rng], {"from": account}
    )
    # tx = get_contract("vrf_coordinator").fulfillRandomWords(
    #     request_id, lottery.address, {"from": account}
    # )
    tx.wait(1)
    event_rnd_wrd_fulfilled = tx.events["RandomWordsFulfilled"]
    print(f"Sucess of fulfillRandomWorld: {event_rnd_wrd_fulfilled['success']}")

    # Assert
    # 777 % 3 = 0
    assert event_rnd_wrd_fulfilled["success"] is True
    assert lottery.balance() == 0
    assert lottery.recentWinner() == account
    assert (
        account.balance()
        == starting_balance_of_account + balance_of_lottery - lottery.getEntranceFee()
    )


def test_reset_players():
    """Test cannot reset Array of Players"""
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(2), "value": lottery.getEntranceFee()})
    # Act / Assert
    with pytest.raises(AttributeError):
        lottery.resetPlayers({"from": account})

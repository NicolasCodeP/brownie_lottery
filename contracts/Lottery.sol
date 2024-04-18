// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0 <0.9.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
// VRF
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/vrf/VRFConsumerBaseV2.sol";

contract Lottery is VRFConsumerBaseV2, Ownable {
    address payable[] public players;
    address payable public recentWinner;
    uint256 public usdEntryFee; // in Wei
    uint256 public entryFeeInUSD; // in USD
    AggregatorV3Interface private ethUsdPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    // VRF Part
    event RequestSent(uint256 requestId, uint32 numWords);
    event RequestFulfilled(uint256 requestId, uint256[] randomWords);

    struct RequestStatus {
        bool fulfilled; // whether the request has been successfully fulfilled
        bool exists; // whether a requestId exists
        uint256[] randomWords;
    }
    mapping(uint256 => RequestStatus)
        public s_requests; /* requestId --> requestStatus */

    VRFCoordinatorV2Interface COORDINATOR; // To requestRandomWords with the VRF subscription id
    uint64 s_subscriptionId; // Your subscription

    // Past requests Id.
    uint256[] public requestIds;
    uint256 public lastRequestId;

    // The gas lane to use, which specifies the maximum gas price to bump to.
    // For a list of available gas lanes on each network,
    // see https://docs.chain.link/docs/vrf/v2/subscription/supported-networks/#configurations
    bytes32 keyHash;

    // Depends on the number of requested values that you want sent to the
    // fulfillRandomWords() function. Storing each word costs about 20,000 gas,
    // so 100,000 is a safe default for this example contract. Test and adjust
    // this limit based on the network that you select, the size of the request,
    // and the processing of the callback request in the fulfillRandomWords()
    // function.
    uint32 callbackGasLimit = 100000;

    // The default is 3, but you can set this higher.
    uint16 requestConfirmations = 3;

    // Number of random values to retrieve per request.
    uint32 numWords;

    /**
     * FOR GOERLI
     * VRF COORDINATOR: 0x2Ca8E0C643bDe4C2E08ab1fA0da3401AdAD7734D
     */
    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        uint64 _subscriptionId,
        bytes32 _keyHash
    ) VRFConsumerBaseV2(_vrfCoordinator) Ownable(msg.sender) {
        lottery_state = LOTTERY_STATE.CLOSED;
        entryFeeInUSD = 1;
        usdEntryFee = entryFeeInUSD * (10 ** 18); // Add 18 Decimals (Wei)
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);

        COORDINATOR = VRFCoordinatorV2Interface(_vrfCoordinator);
        s_subscriptionId = _subscriptionId;
        keyHash = _keyHash;
        numWords = 1;
    }

    /**
     * @notice Randomness part
     * @notice Assumes the subscription is funded sufficiently.
     */
    function requestRandomWords()
        internal
        onlyOwner
        returns (uint256 requestId)
    {
        // Will revert if subscription is not set and funded.
        requestId = COORDINATOR.requestRandomWords(
            keyHash,
            s_subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );
        s_requests[requestId] = RequestStatus({
            randomWords: new uint256[](0),
            exists: true,
            fulfilled: false
        });
        requestIds.push(requestId);
        lastRequestId = requestId;
        emit RequestSent(requestId, numWords);
        return requestId;
    }

    /**
     * @notice Randomness part
     */
    function enter() public payable {
        // $1 minumum = entryFeeInUSD
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee(), "Not enough ETH!");
        players.push(payable(msg.sender));
    }

    /**
     * @notice Lottery part
     *
     * @notice Returns price in Wei
     * @notice Calculation:
     * @notice $50, Price: $2,000 / ETH
     * @notice Goal: $50 / $2,000 | But Solidity doesn't work with decimals!
     * @notice We need to multiply numerator to avoid decimals:
     * @notice 50 * 10...00 / 2,000
     */
    function getEntranceFee() public view returns (uint256) {
        // prettier-ignore
        (
            /* uint80 roundID */,
            int256 price, /* 8 decimals */
            /*uint startedAt*/,
            /*uint timeStamp*/,
            /*uint80 answeredInRound*/
        ) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price * 10 ** 10); // Add decimals to get price in Wei (8+10=18 decimals)
        uint256 costToEnter = (usdEntryFee * 10 ** 18) / adjustedPrice; // Original 10 ** 18 will be cancelled out
        return costToEnter;
    }

    /**
     * @notice Lottery part
     */
    function updateEntranceFee(uint256 _entryFeeInUSD) public onlyOwner {
        entryFeeInUSD = _entryFeeInUSD;
        usdEntryFee = entryFeeInUSD * (10 ** 18);
    }

    /**
     * @notice Lottery part
     */
    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Can't start a new lottery yet!"
        );
        // Reset players from previous lottery
        if (players.length > 0) {
            delete players;
        }
        lottery_state = LOTTERY_STATE.OPEN;
    }

    /**
     * @notice Lottery part
     */
    function endLottery() public onlyOwner {
        // pseudorandom numbers
        // uint(
        //     kecccack256(
        //         abi.encodePacked(
        //             nonce, // nonce is predictable (aka, Tx number)
        //             msg.sender, // msg.sender is predictable
        //             block.difficulty, // can actually be manipulated by the miners!
        //             block.timestamp // timestamp is predictable
        //         )
        //     )
        // ) % players.length;
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        requestRandomWords();
    }

    event ReturnedRandomness(uint256[] randomWords);
    uint256[] public s_randomWords;

    function getSizePlayers() public view returns (uint256) {
        return players.length;
    }

    /**
     * @notice Randomness part
     */
    function fulfillRandomWords(
        uint256 _requestId,
        uint256[] memory _randomWords
    ) internal override {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You aren't there yet!"
        );
        require(s_requests[_requestId].exists, "request not found");

        s_requests[_requestId].fulfilled = true;
        s_requests[_requestId].randomWords = _randomWords;
        emit RequestFulfilled(_requestId, _randomWords);

        // Get first randomWord and apply Modulo to it
        uint256 firstRandomWord = s_requests[_requestId].randomWords[0];
        uint256 indexOfWinner = firstRandomWord % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);

        lottery_state = LOTTERY_STATE.CLOSED;
    }
}

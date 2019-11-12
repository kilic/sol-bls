pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "../blsG2.sol";

contract TESTBLSG2 {

    event Debug(uint256 gasUsed);
    event DebugVerification(uint256 gasUsed, bool verified);

    function aggregatePubkeys(uint256[2][2][] calldata pubkeys)
    external view returns(uint256[2][2] memory agg){
        agg = blsG2.aggregatePubkeys(pubkeys);
    }

    function aggregatePubkeysBench(uint256[2][2][] calldata pubkeys)
    external {
        uint256 gas = gasleft();
        blsG2.aggregatePubkeys(pubkeys);
        emit Debug(gas - gasleft());
    }

    function hashToPoint(bytes calldata data)
    external view returns (uint256[2] memory point){
        point = blsG2.hashToPoint(data);
    }

    function hashToPointBench(bytes calldata data)
    external {
        uint256 gas = gasleft();
        blsG2.hashToPoint(data);
        emit Debug(gas - gasleft());
    }

    function verifySingle(uint256[2] calldata signature, uint256[2][2] calldata pubkey, uint256[2] calldata message)
    external {
        bool success;
        uint256 gas = gasleft();
        success = blsG2.verifySingle(signature, pubkey, message);
        emit DebugVerification(gas - gasleft(), success);
    }

    function verifyMultipleCommonMessage(uint256[2] calldata signature, uint256[2][2][] calldata pubkeys, uint256[2] calldata message)
    external {
        bool success;
        uint256 gas = gasleft();
        success = blsG2.verifyMultipleCommonMessage(signature, pubkeys, message);
        emit DebugVerification(gas - gasleft(), success);
    }

    function verifyMultiple(uint256[2] calldata signature, uint256[2][2][] calldata pubkeys, uint256[2][] calldata messages)
    external returns(bool){
        bool success;
        uint256 gas = gasleft();
        success = blsG2.verifyMultiple(signature, pubkeys, messages);
        emit DebugVerification(gas - gasleft(), success);
    }

    function verifyMultipleRawMessages(uint256[2] calldata signature, uint256[2][2][] calldata pubkeys, bytes[] calldata rawMessages)
    external returns(bool){
        uint256 size = rawMessages.length;
        uint256[2][] memory messages = new uint256[2][](size);
        for (uint16 i = 0; i < size; i++){
            messages[i] = blsG2.hashToPoint(rawMessages[i]);
        }
        bool success;
        uint256 gas = gasleft();
        success = blsG2.verifyMultiple(signature, pubkeys, messages);
        emit DebugVerification(gas - gasleft(), success);
    }

    function sqrt(uint256 a)
    external view returns (uint256, bool){
        return blsG2.sqrt(a);
    }

    function sqrtBench(uint256 a)
    external {
        uint256 gas = gasleft();
        blsG2.sqrt(a);
        emit Debug(gas - gasleft());
    }
}
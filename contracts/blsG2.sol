pragma solidity ^0.5.0;

import "./G2.sol";

library blsG2{

    uint256 constant N = 21888242871839275222246405745257275088696311157297823662689037894645226208583;

    uint256 constant nG2x1 = 11559732032986387107991004021392285783925812861821192530917403151452391805634;
    uint256 constant nG2x0 = 10857046999023057135944570762232829481370756359578518086990519993285655852781;
    uint256 constant nG2y1 = 17805874995975841540914202342111839520379459829704422454583296818431106115052;
    uint256 constant nG2y0 = 13392588948715843804641432497768002650278120570034223513918757245338268106653;

    function verifySingle(uint256[2] memory signature, uint256[2][2] memory pubkey, uint256[2] memory message)
    internal view
    returns(bool) {
    uint[12] memory input = [
        signature[0],
        signature[1],
        nG2x1,
        nG2x0,
        nG2y1,
        nG2y0,
        message[0],
        message[1],
        pubkey[0][1],
        pubkey[0][0],
        pubkey[1][1],
        pubkey[1][0]
    ];
    uint[1] memory out;
    bool success;
    // solium-disable-next-line security/no-inline-assembly
    assembly {
        success := staticcall(sub(gas, 2000), 8, input, 384, out, 0x20)
        switch success case 0 { invalid() }
    }
    require(success, "");
    return out[0] != 0;
    }

    function verifyMultipleCommonMessage(
        uint256[2]      memory signature,
        uint256[2][2][] memory pubkeys,
        uint256[2]      memory message)
    internal view
    returns (bool) {
        uint256[2][2] memory aggPubkey = aggregatePubkeys(pubkeys);
        uint[12] memory input = [
            signature[0],
            signature[1],
            nG2x1,
            nG2x0,
            nG2y1,
            nG2y0,
            message[0],
            message[1],
            aggPubkey[0][1],
            aggPubkey[0][0],
            aggPubkey[1][1],
            aggPubkey[1][0]
        ];
        uint[1] memory out;
        bool success;
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            success := staticcall(sub(gas, 2000), 8, input, 384, out, 0x20)
            switch success case 0 { invalid() }
        }
        require(success, "");
        return out[0] != 0;
    }


    function verifyMultiple(
        uint256[2]      memory signature,
        uint256[2][2][] memory pubkeys,
        uint256[2][]    memory messages)
    internal view
    returns (bool){
        uint256 size = pubkeys.length;
        require(size > 0, "");
        require(size == messages.length, "");
        uint256 inputSize = (size + 1) * 6;
        uint256[] memory input = new uint256[](inputSize);
        input[0] = signature[0];
        input[1] = signature[1];
        input[2] = nG2x1;
        input[3] = nG2x0;
        input[4] = nG2y1;
        input[5] = nG2y0;
        for (uint i = 0; i < size; i++) {
            input[i * 6 + 6] = messages[i][0];
            input[i * 6 + 7] = messages[i][1];
            input[i * 6 + 8] = pubkeys[i][0][1];
            input[i * 6 + 9] = pubkeys[i][0][0];
            input[i * 6 + 10] = pubkeys[i][1][1];
            input[i * 6 + 11] = pubkeys[i][1][0];
        }
        uint256[1] memory out;
        bool success;
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            success := staticcall(sub(gas, 2000), 8, add(input, 0x20), mul(inputSize, 0x20), out, 0x20)
            switch success case 0 { invalid() }
        }
        require(success, "");
        return out[0] != 0;
    }

    function aggregatePubkeys(uint256[2][2][] memory pubkeys)
    internal view
    returns (uint256[2][2] memory agg) {
    require(pubkeys.length > 1, "");
        agg[0] = pubkeys[0][0];
        agg[1] = pubkeys[0][1];
        uint256[2] memory agg_z = [uint256(0x01), uint256(0x00)];
        for (uint8 i = 1; i < pubkeys.length; i++){
            (agg[0], agg[1], agg_z) = G2._add_mixed(agg[0], agg[1], agg_z, pubkeys[i][0], pubkeys[i][1]);
        }
        G2._normalize(agg[0], agg[1], agg_z);
    }

    function hashToPoint(bytes memory data)
    internal view
    returns(uint256[2] memory p) {
        uint256 x = uint256(sha256(data)) % N;
        uint256 y;
        bool found = false;
        while (true) {
            y = mulmod(x, x, N);
            y = mulmod(y, x, N);
            y = addmod(y, 3, N);
            (y, found) = sqrt(y);
            if (found){
                p[0] = x;
                p[1] = y;
                break;
            }
            x = addmod(x, 1, N);
        }
    }

    function sqrt(uint256 xx)
    internal view
    returns (uint256 x, bool){
        bool success;
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            let freemem := mload(0x40)
            mstore(freemem, 0x20)
            mstore(add(freemem,0x20), 0x20)
            mstore(add(freemem,0x40), 0x20)
            mstore(add(freemem,0x60), xx)
            // (N + 1) / 4 = 0xc19139cb84c680a6e14116da060561765e05aa45a1c72a34f082305b61f3f52
            mstore(add(freemem,0x80), 0xc19139cb84c680a6e14116da060561765e05aa45a1c72a34f082305b61f3f52)
            // N = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47
            mstore(add(freemem,0xA0), 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47)
            success := staticcall(sub(gas, 2000), 5, freemem, 0xC0, freemem, 0x20)
            x := mload(freemem)
        }
        require(success, "");
        return (x, xx == mulmod(x, x, N));
    }
}
pragma solidity ^0.5.0;

import "../G2.sol";

contract TESTG2{

    event Debug(uint256 gasUsed);

    function normalize(uint256[2][3] calldata a)
    external view returns (uint256[2][3] memory c){
        c = a;
        G2._normalize(c[0], c[1], c[2]);
        c[2] = [uint256(1), uint256(0)];
        return c;
    }

    function normalizeBench(uint256[2][3] calldata a)
    external {
        uint256 gas = gasleft();
        G2._normalize(a[0], a[1], a[2]);
        emit Debug(gas - gasleft());
    }

    function add(uint256[2][3] calldata a, uint256[2][3] calldata b)
    external pure returns (uint256[2][3] memory c){
        (c[0], c[1], c[2]) = G2._add(a[0], a[1], a[2], b[0], b[1], b[2]);
    }

    function addBench(uint256[2][3] calldata a, uint256[2][3] calldata b)
    external {
        uint256[2][3] memory c;
        uint256 gas = gasleft();
        (c[0], c[1], c[2]) = G2._add(a[0], a[1], a[2], b[0], b[1], b[2]);
        emit Debug(gas - gasleft());
    }

    function addMixed(uint256[2][3] calldata a, uint256[2][2] calldata b)
    external pure returns (uint256[2][3] memory c){
        (c[0], c[1], c[2]) = G2._add_mixed(a[0], a[1], a[2], b[0], b[1]);
    }

    function addMixedBench(uint256[2][3] calldata a, uint256[2][2] calldata b)
    external {
        uint256[2][3] memory c;
        uint256 gas = gasleft();
        (c[0], c[1], c[2]) = G2._add_mixed(a[0], a[1], a[2], b[0], b[1]);
        emit Debug(gas - gasleft());
    }

    function double(uint256[2][3] calldata a)
    external pure returns (uint256[2][3] memory c){
        (c[0], c[1], c[2]) = G2._double(a[0], a[1], a[2]);
    }

    function doubleBench(uint256[2][3] calldata a)
    external {
        uint256[2][3] memory c;
        uint256 gas = gasleft();
        (c[0], c[1], c[2]) = G2._double(a[0], a[1], a[2]);
        emit Debug(gas - gasleft());
    }

    function fq2_add(uint256[2] calldata a, uint256[2] calldata b)
    external pure
    returns (uint256[2] memory c){
        G2.fq2add(c, a, b);
        return c;
    }

    function fq2_add_asign(uint256[2] calldata a, uint256[2] calldata b)
    external pure
    returns (uint256[2] memory){
        G2.fq2add_assign(a, b);
        return a;
    }

    function fq2_double(uint256[2] calldata a)
    external pure
    returns (uint256[2] memory c){
        G2.fq2double(c, a);
        return c;
    }

    function fq2_double_asign(uint256[2] calldata a)
    external pure
    returns (uint256[2] memory){
        G2.fq2double_assign(a);
        return a;
    }

    function fq2_sub(uint256[2] calldata a, uint256[2] calldata b)
    external pure
    returns (uint256[2] memory c){
        G2.fq2sub(c, a, b);
        return c;
    }

    function fq2_sub_asign(uint256[2] calldata a, uint256[2] calldata b)
    external pure
    returns (uint256[2] memory){
        G2.fq2sub_assign(a, b);
        return a;
    }

    function fq2_mul(uint256[2] calldata a, uint256[2] calldata b)
    external pure
    returns (uint256[2] memory c){
        G2.fq2mul(c, a, b);
        return c;
    }

    function fq2_square(uint256[2] calldata a)
    external pure
    returns (uint256[2] memory c){
        G2.fq2square(c, a);
        return c;
    }

    function fq2_inverse(uint256[2] calldata a)
    external view
    returns (uint256[2] memory c){
        G2.fq2inv(c, a);
        return c;
    }
}
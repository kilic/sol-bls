pragma solidity ^0.5.0;

library G2 {

    uint256 internal constant N = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47;
    uint256 internal constant NN = 0x60c89ce5c263405370a08b6d0302b0bb2f02d522d0e3951a7841182db0f9fa8e;

    // Taken from https://github.com/musalbas/solidity-BN256G2
    function _modInv(uint256 a, uint256 n) internal view returns (uint256 result) {
        bool success;
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            let freemem := mload(0x40)
            mstore(freemem, 0x20)
            mstore(add(freemem,0x20), 0x20)
            mstore(add(freemem,0x40), 0x20)
            mstore(add(freemem,0x60), a)
            mstore(add(freemem,0x80), sub(n, 2))
            mstore(add(freemem,0xA0), n)
            success := staticcall(sub(gas, 2000), 5, freemem, 0xC0, freemem, 0x20)
            result := mload(freemem)
        }
        require(success, "");
    }

    /*

        FQ2 Operations

    */

    function fq2mul(uint256[2] memory c, uint256[2] memory a, uint256[2] memory b) internal pure {
        // Since the cost of mulmod and addmod are the same in solidity,
        // Karatsuba multiplications is not cheaper.
        // Therefore, we favour the formula with lesser operations.
        c[0] = addmod(mulmod(a[0], b[0], N), N - mulmod(a[1], b[1], N), N);
        c[1] = addmod(mulmod(a[0], b[1], N), mulmod(a[1], b[0], N), N);
    }

    function fq2mul_assign(uint256[2] memory a, uint256[2] memory b) internal pure {
        uint256 t = addmod(mulmod(a[0], b[0], N), N - mulmod(a[1], b[1], N), N);
        a[1] = addmod(mulmod(a[0], b[1], N), mulmod(a[1], b[0], N), N);
        a[0] = t;
    }

    function fq2square(uint256[2] memory c, uint256[2] memory a) internal pure {
        c[0] = mulmod(a[0] + a[1], addmod(a[0], N - a[1], N), N);
        c[1] = mulmod(a[0] << 1, a[1], N);
    }

    function fq2square_assign(uint256[2] memory a) internal pure {
        uint256 t = mulmod(a[0] + a[1], addmod(a[0], N - a[1], N), N);
        a[1] = mulmod(a[0] << 1, a[1], N);
        a[0] = t;
    }

    function fq2mulby(uint256[2] memory c, uint256[2] memory a, uint256 b) internal pure {
        c[0] = mulmod(a[0], b, N);
        c[1] = mulmod(a[1], b, N);
    }

    function fq2mulby_assign(uint256[2] memory a, uint256 b) internal pure {
        a[0] = mulmod(a[0], b, N);
        a[1] = mulmod(a[1], b, N);
    }

    function fq2add(uint256[2] memory c, uint256[2] memory a, uint256[2] memory b) internal pure {
        c[0] = addmod(a[0], b[0], N);
        c[1] = addmod(a[1], b[1], N);
    }

    function fq2add_assign(uint256[2] memory a, uint256[2] memory b) internal pure {
        a[0] = addmod(a[0], b[0], N);
        a[1] = addmod(a[1], b[1], N);
    }


    function fq2double(uint256[2] memory c, uint256[2] memory a) internal pure {
        c[0] = addmod(a[0], a[0], N);
        c[1] = addmod(a[1], a[1], N);
    }

    function fq2double_assign(uint256[2] memory a) internal pure {
        a[0] = addmod(a[0], a[0], N);
        a[1] = addmod(a[1], a[1], N);
    }

    function fq2sub(uint256[2] memory c, uint256[2] memory a, uint256[2] memory b) internal pure {
        c[0] = addmod(a[0], N - b[0], N);
        c[1] = addmod(a[1], N - b[1], N);
    }

    function fq2sub_assign(uint256[2] memory a, uint256[2] memory b) internal pure {
        a[0] = addmod(a[0], N - b[0], N);
        a[1] = addmod(a[1], N - b[1], N);
    }

    function fq2subboth_assign(uint256[2] memory a, uint256[2] memory b0, uint256[2] memory b1) internal pure {
        a[0] = addmod(a[0], NN - (b0[0] + b1[0]), N);
        a[1] = addmod(a[1], NN - (b0[1] + b1[1]), N);
    }

    function fq2sub_twice(uint256[2] memory c, uint256[2] memory a, uint256[2] memory b) internal pure {
        c[0] = addmod(a[0], NN - (b[0] << 1), N);
        c[1] = addmod(a[1], NN - b[1] << 1, N);
    }

    function fq2sub_twice_assign(uint256[2] memory a, uint256[2] memory b) internal pure {
        a[0] = addmod(a[0], NN - b[0] << 1, N);
        a[1] = addmod(a[1], NN - b[1] << 1, N);
    }

    function fq2inv(uint256[2] memory c, uint256[2] memory a) internal view {
        uint256 inv = _modInv(addmod(mulmod(a[1], a[1], N), mulmod(a[0], a[0], N), N), N);
        c[0] = mulmod(a[0], inv, N);
        c[1] = N - mulmod(a[1], inv, N);
    }

    function fq2inv_assign(uint256[2] memory a) internal view {
        uint256 inv = _modInv(addmod(mulmod(a[1], a[1], N), mulmod(a[0], a[0], N), N), N);
        a[0] = mulmod(a[0], inv, N);
        a[1] = N - mulmod(a[1], inv, N);
    }

    /*

        G2 Operations

    */

    function _normalize(uint256[2] memory x, uint256[2] memory y, uint256[2] memory z)
    internal view {
        uint256[2] memory t;
        fq2inv_assign(z);
        fq2square(t, z);
        fq2mul_assign(x, t);
        fq2mul_assign(t, z);
        fq2mul_assign(y, t);
    }

    // http://www.hyperelliptic.org/EFD/gp/auto-shortw-jacobian-0.html#doubling-dbl-2009-l
    function _double(uint256[2] memory ax, uint256[2] memory ay, uint256[2] memory az)
    internal pure
    returns(uint256[2] memory cx, uint256[2] memory cy, uint256[2] memory cz) {
        uint256[2] memory t0;
        fq2square(t0, ax);              // A  = x^2
        fq2square(cy, ay);              // B  = y^2
        fq2square(cz, cy);              // C  = B^2
        fq2add(cy, ax, cy);             // t  = x + B
        fq2square_assign(cy);           //     t^2
        fq2subboth_assign(cy, t0, cz);  //     t^2 - (A + C)
        fq2mulby_assign(cy, 2);         // D  = 2 *(t^2 - (A + C))
        fq2mulby_assign(t0, 3);         // E  = 3 * A
        fq2square(cx, t0);              // F  = E * E
        fq2sub_twice_assign(cx, cy);    // x3 = F - 2D
        fq2sub_assign(cy, cx);          //      D - x3
        fq2mul_assign(cy, t0);          //      E * (D - x3)
        fq2mulby_assign(cz, 8);         //      8 * C
        fq2sub_assign(cy, cz);          // y3 = E * (D - x3) - 8 * C
        fq2mul(cz, az, ay);             //      z * y
        fq2mulby_assign(cz, 2);         // z3 = 2 * z * y
    }

    // http://www.hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#madd-2004-hmv"
    function _add_mixed(
        uint256[2] memory x1, uint256[2] memory y1, uint256[2] memory z1,
        uint256[2] memory x2, uint256[2] memory y2)
    internal pure
    returns(uint256[2] memory x3, uint256[2] memory y3, uint256[2] memory z3) {
        if (z1[0] == 0 && z1[1] == 0){
            x3 = x2; y3 = y2; z3[0] = 1; z3[1] = 0;
        } else if(x2[0] == 0 && y2[0] == 1){
            x3 = x1; y3 = y1; z3 = z1;
        } else {
            uint256[2] memory t1; uint256[2] memory t2;
            uint256[2] memory t3; uint256[2] memory t4;

            fq2square(t1, z1);
            fq2mul(t2, t1, z1);
            fq2mul_assign(t1, x2);
            fq2mul_assign(t2, y2);
            fq2sub_assign(t1, x1);
            fq2sub_assign(t2, y1);
            if (t1[0] == 0 && t1[1] == 0){
                if (t2[0] == 0 && t2[1] == 0) {
                    (x3, y3, z3) = _double(x1, y1, z1);
                } else{
                    x3 = t1; y3 = [uint256(1), 0]; z3 = t1;
                }
            } else {
                fq2mul(z3, z1, t1);
                fq2square(t3, t1);
                fq2mul(t4, t3, t1);
                fq2mul_assign(t3, x1);
                fq2mulby(t1, t3, 2);
                fq2square(x3, t2);
                fq2subboth_assign(x3, t1, t4);
                fq2sub_assign(t3, x3);
                fq2mul_assign(t3, t2);
                fq2mul_assign(t4, y1);
                fq2sub(y3, t3, t4);
            }
        }
    }

    // http://www.hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#add-2007-bl
    function _add(
        uint256[2] memory x1, uint256[2] memory y1, uint256[2] memory z1,
        uint256[2] memory x2, uint256[2] memory y2, uint256[2] memory z2)
    internal pure
    returns(uint256[2] memory x3, uint256[2] memory y3, uint256[2] memory z3) {
        uint256[2] memory t0; uint256[2] memory t1;
        uint256[2] memory t2; uint256[2] memory t3;
        fq2square(x3, z1);                  // z1z1 = z1 * z1
        fq2square(t0, z2);                  // z2z2 = z2 * z2
        fq2mul(y3, x1, t0);                 // U1   = x1 * z2z2
        fq2mul(t1, x2, x3);                 // U2   = x2 * z1z1
        fq2mul(t2, y1, z2);                 //        y1 * z2
        fq2mul_assign(t2, t0);              // S1   = y1 * z2 * z2z2
        fq2mul(t3, y2, z1);                 //        y2 * z1
        fq2mul_assign(t3, x3);              // S2   = y2 * z1 * z1z1
        //
        if (t1[0] == y3[0] && t1[1] == y3[1]){
            if (t1[0] == y3[0] && t1[1] == y3[1]){
                (x3, y3, z3) = _double(x1, y1, z1);
            } else {
                x3 = [uint256(0), uint256(0)];
                y3 = [uint256(1), uint256(0)];
                z3 = [uint256(0), uint256(0)];
            }
        } else {
            fq2add(z3, z1, z2);                 // z    = z1 + z2
            fq2square_assign(z3);               //        z^2
            fq2subboth_assign(z3, x3, t0);      //      = z^2 - z1z1 - z2z2
            fq2sub_assign(t1, y3);              // H    = U2 - U1
            fq2mul_assign(z3, t1);              // z3   = (z^2 - z1z1 - z2z2) * H
            //
            fq2mulby(x3, t1, 2);                //        2H
            fq2square_assign(x3);               // I    = (2 * H ) ^ 2
            fq2mul_assign(t1, x3);              // J    = H * I
            fq2sub_assign(t3, t2);              //      = (S2 - S1)
            fq2mulby_assign(t3, 2);             // r    = 2 * (S2 - S1)
            fq2mul_assign(y3, x3);              // V    = U1 * I
            fq2square(x3, t3);                  //        r^2
            fq2sub_assign(x3, t1);              //        r^2 - J
            fq2sub_twice_assign(x3, y3);        // x3   = r^2 - J - 2*V
            fq2mul_assign(t2, t1);              //        S1 * J
            fq2sub_assign(y3, x3);              //        V - x3
            fq2mul_assign(y3, t3);              //        r * (V - x3)
            fq2sub_twice_assign(y3, t2);        // y3   = r * (V - x3) - 2 * S1 * J
        }
    }

    // http://www.hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#add-2007-bl
    // function _add_unsafe(
    //     uint256[2] memory x1, uint256[2] memory y1, uint256[2] memory z1,
    //     uint256[2] memory x2, uint256[2] memory y2, uint256[2] memory z2)
    // internal pure
    // returns(uint256[2] memory x3, uint256[2] memory y3, uint256[2] memory z3) {
    //     uint256[2] memory t0;
    //     uint256[2] memory t1;
    //     fq2square(x3, z1);                  // z1z1 = z1 * z1
    //     fq2square(t0, z2);                  // z2z2 = z2 * z2
    //     fq2mul(y3, x1, t0);                 // U1   = x1 * z2z2
    //     fq2mul(t1, x2, x3);                 // U2   = x2 * z1z1
    //     fq2mul(x2, y1, z2);                 //        y1 * z2
    //     fq2mul_assign(x2, t0);              // S1   = y1 * z2 * z2z2
    //     fq2mul(y2, y2, z1);                 //        y2 * z1
    //     fq2mul_assign(y2, x3);              // S2   = y2 * z1 * z1z1
    //     //
    //     fq2add(z3, z1, z2);                 // z    = z1 + z2
    //     fq2square_assign(z3);               //        z^2
    //     fq2subboth_assign(z3, x3, t0);      //      = z^2 - z1z1 - z2z2
    //     fq2sub_assign(t1, y3);              // H    = U2 - U1
    //     fq2mul_assign(z3, t1);              // z3   = (z^2 - z1z1 - z2z2) * H
    //     //
    //     fq2mulby(x3, t1, 2);                //        2H
    //     fq2square_assign(x3);               // I    = (2 * H ) ^ 2
    //     fq2mul_assign(t1, x3);              // J    = H * I
    //     fq2sub_assign(y2, x2);              //      = (S2 - S1)
    //     fq2mulby_assign(y2, 2);             // r    = 2 * (S2 - S1)
    //     fq2mul_assign(y3, x3);              // V    = U1 * I
    //     fq2square(x3, y2);                  //        r^2
    //     fq2sub_assign(x3, t1);              //        r^2 - J
    //     fq2sub_twice_assign(x3, y3);        // x3   = r^2 - J - 2*V
    //     fq2mul_assign(x2, t1);              //        S1 * J
    //     fq2sub_assign(y3, x3);              //        V - x3
    //     fq2mul_assign(y3, y2);              //        r * (V - x3)
    //     fq2sub_twice_assign(y3, x2);        // y3   = r * (V - x3) - 2 * S1 * J
    // }
}
pragma solidity 0.8.25;

contract MyContrac5 {
    uint[] myArr; // single typed array

    function add(uint val) external {
        myArr.push(val);
    }

    function update(uint i, uint val) external {
        myArr[i] = val;
    }

    function destroy(uint i) external {
        delete myArr[i];
    }

    function removeLastVal() external {
        myArr.pop();
    }

}
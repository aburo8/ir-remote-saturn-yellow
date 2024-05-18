pragma solidity >=0.8.2 <0.9.0;

contract MyContract {
    uint a;
    function update(uint _a) external {
        a = _a;
    }

    function get() external view returns (uint) {
        return a;
    }
}
pragma solidity 0.8.25;

interface IOtherContract {
    function bar() external view returns (uint);
}


contract MyContrac3 {
    function foo() external {
        uint result = IOtherContract("HEX ADDRESS HERE FOR SMART CONTRACT").bar();
    }
}
pragma solidity 0.8.25;

contract MyContrac4 {
    function foo() external {
        // Built in variable s
        msg.sender; // called the function
        msg.value; // amount of ether sent in a transaction (can be 0)
        block.timestamp; // timestamp in seconds of the block that was mined
        address(this) // address of the smart contract
        address(this).balance // balance of the smart contract
        
    }
}
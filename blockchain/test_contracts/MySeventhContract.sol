pragma solidity 0.8.25;

contract MyContrac7 {
    address owner;
    error Unauthroized();

    constructor () {
        owner = msg.sender;
    }

    function foo() external {
        require(msg.sender == owner, "not the owner");

        if (msg.sender != owner) {
            revert Unauthorized();
        }

    }
}
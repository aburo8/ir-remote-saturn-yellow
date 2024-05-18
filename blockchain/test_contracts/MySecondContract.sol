pragma solidity 0.8.25;

contract MyContrac2 {
    address owner;

    constructor (address _owner) {
        owner = _owner;
    }

    function deposit() payable external {}

    function sendEther(address payable to, uint amount) external {
        (bool sent, bytes memory data) = to.call{value: amount}("") ;// Loadable function call
    }
}
pragma solidity 0.8.25;

contract MyContrac6 {
    mapping(address => uint) balances;

    function update(address owner, uint amount) external {
        balances[owner] = amount;
        delete balances[owner];

        balances[0x20392340]; // will return default type value if address is garbage
        // Cannot iterrate over mappings.
    }
}
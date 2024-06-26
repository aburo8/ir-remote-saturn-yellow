// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.25;

contract SmartIR {
    error Unauthorized();

    struct IRAction {
        address controller; // The controller sending the IR command
        address transmitter; // The transmitter the IR command will be transmitted from
        uint action; // The action being executed
        uint irCode; // The IR code being transmitted
    }

    struct SystemControl {
        uint parentAction; // Parent who owns the control
        bool disabled; // Is the button disabled
        uint timeout; // Timeout in seconds (0 means no timeout)
        uint timeoutAction; // Action to execute after timeout (if timeout is not 0)
        uint timestamp; // Timestamp the control was added
    }

    mapping(uint => SystemControl) public controls; // Maps actions to system controls

    IRAction[] public actions; // Immutable ledger of IR actions

    event IRActionAdded(address indexed controller, address indexed transmitter, uint action, uint irCode);
    event SystemControlAdded(uint indexed parentAction, bool disabled, uint timeout, uint timeoutAction);
    event IRActionTimeout(uint indexed parentAction, uint timeoutAction, uint timeout);

    // Function to add an IR action from a controller
    function addIRAction(address controller, address transmitter, uint action, uint irCode) external {
        // Check if the action is disabled
        SystemControl memory control = controls[action];
        if (control.disabled) {
            revert Unauthorized();
        }

        // Add the action to the actions ledger
        actions.push(IRAction(controller, transmitter, action, irCode));
        
        // Emit an event for the action added
        emit IRActionAdded(controller, transmitter, action, irCode);

        // If the action has a timeout, handle the timeout logic (if required)
        if (control.timeout > 0) {
            // Implement the timeout logic here if necessary
        }
    }

    // Function to add or update a system control for a specific action
    function addSystemControl(uint parentAction, bool disabled, uint timeout, uint timeoutAction) external {
        uint timeoutInSeconds = timeout * 60; // Convert timeout from minutes to seconds
        controls[parentAction] = SystemControl(parentAction, disabled, timeoutInSeconds, timeoutAction, block.timestamp);

        // Emit an event for the system control added
        emit SystemControlAdded(parentAction, disabled, timeout, timeoutAction);
    }

     // Function to check for timeouts and emit events
    function checkTimeouts() external {
        for (uint i = 0; i < 23; i++) {
            SystemControl memory control = controls[i];
            uint timeoutTime = control.timestamp + control.timeout;
            // Check if the control has a timeout set and if the timeout period has passed
            if (control.timeout > 0 && control.timeoutAction > 0 && block.timestamp >= timeoutTime) {
                // Emit an event for the timeout action
                emit IRActionTimeout(i, control.timeoutAction, control.timeout);
                controls[i].timeout = 0;
            }
        }
    }
    // Function to retrieve all actions (For testing/debugging)
    function getActions() external view returns (IRAction[] memory) {
        return actions;
    }
}

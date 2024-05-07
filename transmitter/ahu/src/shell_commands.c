 /** 
 **************************************************************
 * @file src/shell_commands.c
 * @author Alexander Burovanov - 46990480
 * @date 25/03/2024
 * @brief AHU Shell Commands
 * REFERENCE: None
 ***************************************************************
 */
#include <zephyr/shell/shell.h>
#include <version.h>
#include <zephyr/logging/log.h>
#include <stdio.h>
#include <stdlib.h>
#include <zephyr/bluetooth/addr.h>

#include "uart_module.h"
#include "hci.h"
#include "led_module.h"
#include "ble_module.h"
#include "ab_util.h"

// Setup logging
LOG_MODULE_DECLARE(ahu);

/**
 * Prints the Zephyr kernel version to the provided shell
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success
*/
static int cmd_version(const struct shell *sh, size_t argc, char **argv)
{
	ARG_UNUSED(argc);
	ARG_UNUSED(argv);

	shell_print(sh, "Zephyr version %s", KERNEL_VERSION_STRING);

	return 0;
}

/**
 * Prints the system uptime to the shell.
 * If the 'f' sub command is provided, the output will be formatted in HH:MM:SS
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success
*/
static int cmd_sys_time(const struct shell *sh, size_t argc, char **argv) {
	#ifdef DEBUG
	shell_print(sh, "Uptime: HH:MM:SS. Argc: %d. Arg: %s", argc, argv[0]);
	#endif
	if (argv[0][0] == 'f') {
		// This means we want to print formated time in the response
		int64_t uptime = k_uptime_get();
		uint32_t uptimeHrs = uptime / (1000 * 60 * 60);
		uptime %= (1000 * 60 * 60);

		uint32_t uptimeMins = uptime / (1000 * 60);
		uptime %= (1000 * 60);

		uint32_t uptimeSecs = uptime / (1000);

		shell_print(sh, "Uptime: %02u:%02u:%02u (HH:MM:SS)", uptimeHrs, uptimeMins, uptimeSecs);
	} else {
		// Print the time in seconds
		shell_print(sh, "Uptime: %2lld seconds", (k_uptime_get() / 1000));
	}
	return 0;
}

/**
 * Sets the AHU onboard LEDs to the provided state.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int ahu_cmd_set_leds(const struct shell *sh, size_t argc, char **argv) {
	uint8_t ret, mask = 0;

	ret = get_binary_mask(&mask, argv[1], 4);
	if (ret == 1) {
		LOG_ERR("Invalid LED Mask provided!");
		return 1;
	}

	set_leds(mask);
	
	return 0;
}

/**
 * Toggles the specified AHU onboard LEDs.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int ahu_cmd_toggle_leds(const struct shell *sh, size_t argc, char **argv) {
	uint8_t ret, mask = 0;

	ret = get_binary_mask(&mask, argv[1], 4);
	if (ret == 1) {
		LOG_ERR("Invalid LED Mask provided!");
		return 1;
	}

	toggle_leds(mask);
	
	return 0;
}

/**
 * Start receiving sensor data from the Thingy:52 sensors.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int ahu_cmd_blecon_s(const struct shell *sh, size_t argc, char **argv) {
	int ret = 0;
	bt_addr_le_t addr;
	ret = validate_ble_addr(argv[1], &addr);

	if (ret == 1) {
		LOG_ERR("blecon -s: Invalid Command - incorrect BLE address provided!");
		return 1;
	}

	// Start BLE Data Receiving
	BLECmd cmd = {BLECON_START, addr};
	k_msgq_put(ble_receive_extern, &cmd, K_NO_WAIT);
	LOG_INF("Started Listening to %s\n", argv[1]);

	return 0;
}

/**
 * Stops receiving sensor data from the Thingy:52 sensors.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int ahu_cmd_blecon_p(const struct shell *sh, size_t argc, char **argv) {
	// Stop BLE Data Receiving
	BLECmd cmd;
	cmd.bleCmd = BLECON_STOP;
	k_msgq_put(ble_receive_extern, &cmd, K_NO_WAIT);
	LOG_INF("Stopped Listening");

	return 0;
}

/**
 * Start scanning for available Bluetooth Devices.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int ahu_cmd_blescan_s(const struct shell *sh, size_t argc, char **argv) {
	// Start BLE Data Receiving
	LOG_INF("Scanning Started...\n");
	BLECmd cmd;
	cmd.bleCmd = BLESCAN_START;
	k_msgq_put(ble_receive_extern, &cmd, K_NO_WAIT);

	return 0;
}

/**
 * Stops scanning for available Bluetooth Devices.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int ahu_cmd_blescan_p(const struct shell *sh, size_t argc, char **argv) {
	// Stop BLE Data Receiving
	BLECmd cmd;
	cmd.bleCmd = BLESCAN_STOP;
	k_msgq_put(ble_receive_extern, &cmd, K_NO_WAIT);

	return 0;
}

/**
 * Start scanning for available Bluetooth Devices and filters for the specified address.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int ahu_cmd_blescan_f(const struct shell *sh, size_t argc, char **argv) {
	int ret = 0;
	bt_addr_le_t addr;
	ret = validate_ble_addr(argv[1], &addr);

	if (ret == 1) {
		LOG_ERR("blescan -s -f: Invalid Command - incorrect BLE address provided!");
		return 1;
	}

	// Start BLE Data Receiving
	BLECmd cmd = {BLESCAN_STARTF, addr};
	k_msgq_put(ble_receive_extern, &cmd, K_NO_WAIT);

	return 0;
}

// Define System Shell Commands
SHELL_STATIC_SUBCMD_SET_CREATE(sub_time,
	SHELL_CMD(f, NULL, "Prints Formated System Time - HH:MM:SS.", cmd_sys_time),
	SHELL_SUBCMD_SET_END
);
SHELL_CMD_ARG_REGISTER(time, &sub_time, "Shows the system time. \nUse `time f` for formatted time HH:MM:SS.", cmd_sys_time, 1, 1);
SHELL_CMD_ARG_REGISTER(version, NULL, "Show kernel version", cmd_version, 1, 0);

// Define AHU Shell Commands
SHELL_STATIC_SUBCMD_SET_CREATE(sub_led,
	SHELL_CMD_ARG(s, NULL, "Sets the status of the AHU onboard LEDs.\nUSAGE: led s <4-bit mask>", ahu_cmd_set_leds, 2, 0),
	SHELL_CMD_ARG(t, NULL, "Toggles the specified AHU onboard LEDs.\nUSAGE: led s <4-bit mask>", ahu_cmd_toggle_leds, 2, 0),
	SHELL_SUBCMD_SET_END
);
SHELL_CMD_ARG_REGISTER(led, &sub_led, "AHU Led Module - Controls onboard AHU LEDs using a 4-bit mask.\n", NULL, 1, 1);

SHELL_STATIC_SUBCMD_SET_CREATE(sub_blecon,
	SHELL_CMD_ARG(-s, NULL, "Starts receiving bluetooth sensor data from the Thingy:52 with the specified device address.\nUSAGE: blecon -s <BLE ADDR>", ahu_cmd_blecon_s, 2, 0),
	SHELL_CMD_ARG(-p, NULL, "Stops receiving bluetooth sensor data from the Thingy:52.\nUSAGE: blecon -p", ahu_cmd_blecon_p, 1, 0),
	SHELL_SUBCMD_SET_END
);
SHELL_CMD_ARG_REGISTER(blecon, &sub_blecon, "AHU Bluetooth Module - Receives data from AHU Bluetooth peripherals.\n", NULL, 1, 1);

SHELL_STATIC_SUBCMD_SET_CREATE(filter_blescan,
	SHELL_CMD_ARG(-f, NULL, "Filters the scan list for the specified Bluetooth Address.\nUSAGE: blescan -s -f <BLE ADDR>", ahu_cmd_blescan_f, 2, 0),
	SHELL_SUBCMD_SET_END
);
SHELL_STATIC_SUBCMD_SET_CREATE(sub_blescan,
	SHELL_CMD_ARG(-s, &filter_blescan, "Starts scanning for available Bluetooth devices.\nUSAGE: blescan -s <BLE ADDR>", ahu_cmd_blescan_s, 1, 0),
	SHELL_CMD_ARG(-p, NULL, "Stops scanning for available Bluetooth devices.\nUSAGE: blescan -p", ahu_cmd_blescan_p, 1, 0),
	SHELL_SUBCMD_SET_END
);
SHELL_CMD_ARG_REGISTER(blescan, &sub_blescan, "AHU Bluetooth Module - Scans for available Bluetooth peripherals.\n", NULL, 1, 1);

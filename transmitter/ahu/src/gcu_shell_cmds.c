 /** 
 **************************************************************
 * @file src/gcu_shell_cmds.c
 * @author Alexander Burovanov - 46990480
 * @date 25/03/2024
 * @brief GCU Shell Commands
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
 * Draws a point on the GCU
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int gcu_cmd_point(const struct shell *sh, size_t argc, char **argv)
{
	#ifdef DEBUG
	shell_print(sh, "Argc: %d. Arg: %s, %s, %s", argc, argv[0], argv[1], argv[2]);
	#endif
	if (argc != 3) {
		LOG_ERR("Point: Invalid Command");
		return 1;
	}

	// Validate cmd line args
	float x, y, ret = 0;
	ret = ret + validate_float_arg(argv[1], &x);
	ret = ret + validate_float_arg(argv[2], &y);
	if (ret > 0) {
		LOG_ERR("point: Invalid Command");
		return 1;
	}

	// Construct and send UART Packet
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_POINT, (uint8_t*)&(PointData){(float)x, (float)y});

	return 0;
}

/**
 * Draws a cirlce on the GCU
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int gcu_cmd_circle(const struct shell *sh, size_t argc, char **argv) {
	if (argc != 4) {
		LOG_ERR("circle: Invalid Command");
		return 1;
	}

	// Validate cmd line args
	float r, x, y, ret = 0;
	ret = ret + validate_float_arg(argv[1], &r);
	ret = ret + validate_float_arg(argv[2], &x);
	ret = ret + validate_float_arg(argv[3], &y);
	if (ret > 0) {
		LOG_ERR("circle: Invalid Command - incorrect args provided!");
		return 1;
	} else if (r < 0) {
		LOG_ERR("circle: Invalid Command - radius cannot be negative!");
		return 1;
	}

	// Send Packet Via UART
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_CIRCLE, (uint8_t*)&(CircleData){(float)r, (float)x, (float)y});

	return 0;
}

/**
 * Draws a cirlce on the GCU
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int gcu_cmd_lissajous(const struct shell *sh, size_t argc, char **argv) {
	// Validate cmd line args
	float a, b, t, ret = 0;
	ret = ret + validate_float_arg(argv[1], &a);
	ret = ret + validate_float_arg(argv[2], &b);
	ret = ret + validate_float_arg(argv[3], &t);
	if (ret > 0) {
		LOG_ERR("lj: Invalid Command - incorrect args provided!");
		return 1;
	}

	// Send Packet Via UART
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_LJ, (uint8_t*)&(LissajousData){(float)a, (float)b, (float)t});

	return 0;
}

/**
 * Sets the X and Y voltages on the GCU Dac.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int gcu_cmd_dac(const struct shell *sh, size_t argc, char **argv) {
	// Validate cmd line args
	float x, y, ret = 0;
	ret = ret + validate_float_arg(argv[1], &x);
	ret = ret + validate_float_arg(argv[2], &y);
	if (ret > 0) {
		LOG_ERR("dac: Invalid Command - incorrect args provided!");
		return 1;
	}

	// Send Packet Via UART
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_DAC, (uint8_t*)&(DacData){(float)x, (float)y});

	return 0;
}

/**
 * Draws a cirlce on the GCU
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int gcu_cmd_gled(const struct shell *sh, size_t argc, char **argv) {
	// Convert Argv to byte
	int len = strlen(argv[1]) + strlen(argv[2]) + strlen(argv[3]);
	if (len > 3) {
		LOG_ERR("gled: Invalid Command - incorrect args provided!");
		return 1;
	}

	// Validate cmd line args
	uint8_t r = validate_binary_arg(argv[1][0]);
	uint8_t g = validate_binary_arg(argv[2][0]);
	uint8_t b = validate_binary_arg(argv[3][0]);

	if ((r + g + b) > 3) {
		LOG_ERR("gled: Invalid Command - incorrect args provided!");
		return 1;
	}

	// Send Packet Via UART
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_GLED, (uint8_t*)&(RGBData){(uint8_t)r, (uint8_t)g, (uint8_t)b});

	return 0;
}

static int gcu_cmd_gpb(const struct shell *sh, size_t argc, char **argv) {
	// Send Packet Via UART
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_GPB, NULL);

	return 0;
}

/**
 * Draws a graph of the specified sensor on the GCU.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int gcu_cmd_gcugraph(const struct shell *sh, size_t argc, char **argv) {
	// Validate cmd line args
	int deviceId, ret = 0;
	ret = ret + validate_int_arg(argv[1], &deviceId);
	if (ret > 0) {
		LOG_ERR("gcugraph: Invalid Command - incorrect args provided!");
		return 1;
	}

	if (validate_device_id(deviceId)) {
		LOG_ERR("gcugraph: Invalid deviceId specified!");
		return 1;
	}

	if (get_scanning_state() == 0 || get_scanning_state() == 2) {
		// Not listening for Thing52 iBeacon
		LOG_WRN("gcugraph: Not connected to iBeacon!");
	}

	// Send Packet Via UART
	// print_contents(CMD_GRAPH, (uint8_t*)&(DeviceIdData){(uint8_t)deviceId});
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_GRAPH, (uint8_t*)&(DeviceIdData){(uint8_t)deviceId});

	return 0;
}


/**
 * Draws a meter of the specified sensor on the GCU.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int gcu_cmd_gcumeter(const struct shell *sh, size_t argc, char **argv) {
	// Validate cmd line args
	int deviceId, ret = 0;
	ret = ret + validate_int_arg(argv[1], &deviceId);
	if (ret > 0) {
		LOG_ERR("gcumeter: Invalid Command - incorrect args provided!");
		return 1;
	}

	if (validate_device_id(deviceId)) {
		LOG_ERR("gcumeter: Invalid deviceId specified!");
		return 1;
	}

	if (get_scanning_state() == 0 || get_scanning_state() == 2) {
		// Not listening for Thing52 iBeacon
		LOG_WRN("gcumeter: Not connected to iBeacon!");
	}

	// Send Packet Via UART
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_METER, (uint8_t*)&(DeviceIdData){(uint8_t)deviceId});

	return 0;
}

/**
 * Draws a numeric (SSD) of the specified sensor on the GCU.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int gcu_cmd_gcunumeric(const struct shell *sh, size_t argc, char **argv) {
	// Validate cmd line args
	int deviceId, ret = 0;
	ret = ret + validate_int_arg(argv[1], &deviceId);
	if (ret > 0) {
		LOG_ERR("gcunumeric: Invalid Command - incorrect args provided!");
		return 1;
	}

	if (validate_device_id(deviceId)) {
		LOG_ERR("gcunumeric: Invalid deviceId specified!");
		return 1;
	}

	if (get_scanning_state() == 0 || get_scanning_state() == 2) {
		// Not listening for Thing52 iBeacon
		LOG_WRN("gcunumeric: Not connected to iBeacon!");
	}

	// Send Packet Via UART
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_NUMERIC, (uint8_t*)&(DeviceIdData){(uint8_t)deviceId});

	return 0;
}

/**
 * Starts recording data to the SD card.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int gcu_cmd_gcurec_s(const struct shell *sh, size_t argc, char **argv) {
	// Validate cmd line args
	int deviceId, ret = 0;
	char fileName[FILE_NAME_MAX_LEN];
	ret = ret + validate_int_arg(argv[1], &deviceId);
	if (ret > 0) {
		LOG_ERR("gcurec: Invalid Command - incorrect args provided!");
		return 1;
	}

	// Validate fileName value
	ret = validate_file_name(argv[2]);
	if (ret == 1) {
		LOG_ERR("gcurec: Invalid filename - name too long!");
		return 1;
	} else if (ret == 2) {
		LOG_ERR("gcurec: Invalid filename!");
		return 1;	
	} else if (ret == 3) {
		LOG_ERR("gcurec: Invalid extension! Only .csv is accepted!");
		return 1;
	}
	memcpy(fileName, argv[2], strlen(argv[2]));

	// Validate device id value
	if (validate_device_id(deviceId)) {
		LOG_ERR("gcurec: Invalid deviceId specified!");
		return 1;
	}

	// Check scanning state
	if (get_scanning_state() == 0 || get_scanning_state() == 2) {
		// Not listening for Thing52 iBeacon
		LOG_WRN("gcurec: Not connected to iBeacon!");
	}

	// Send Packet Via UART
	strcpy((char*)fileNameG, argv[2]);
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_REC, (uint8_t*)&(RecData){(uint8_t)GCU_REC_S, deviceId, fileName});
	return 0;
}

/**
 * Stops recording data to the SD card.
 * 
 * sh: shell
 * argc: number of args
 * argv: provided args
 * 
 * Returns: 0 on success, 1 on failure
*/
static int gcu_cmd_gcurec_p(const struct shell *sh, size_t argc, char **argv) {
	// Check scanning state
	if (get_scanning_state() == 0 || get_scanning_state() == 2) {
		// Not listening for Thing52 iBeacon
		LOG_WRN("gcurec: Not connected to iBeacon!");
	}

	// Stop BLE Data Receiving
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_REC, (uint8_t*)&(RecData){(uint8_t)GCU_REC_P});

	return 0;
}

// Define GCU Shell Commands
SHELL_CMD_ARG_REGISTER(point, NULL, "Draws a point on the Graphical Plotter Display.\nUSAGE: point <x> <y>\n<x> - x position, <y> - y position", gcu_cmd_point, 3, 0);
SHELL_CMD_ARG_REGISTER(circle, NULL, "Draws a circle on the Graphical Plotter Display.\nUSAGE: circle <r> <x> <y>\n<r> - radius, <x> - x position, <y> - y position", gcu_cmd_circle, 4, 0);
SHELL_CMD_ARG_REGISTER(lj, NULL, "Draws a lissajous curve on the Graphical Plotter Display.\nUSAGE: circle <a> <b> <t>\n<a> - amplitude 1, <b> - amplitude 2, <t> - phase shift (deg)", gcu_cmd_lissajous, 4, 0);
SHELL_CMD_ARG_REGISTER(dac, NULL, "Sets the X and Y DAC voltages on the Graphical Plotter Display.\nUSAGE: dac <x> <y>\n<x> - x voltage, <y> - y voltage", gcu_cmd_dac, 3, 0);
SHELL_CMD_ARG_REGISTER(gled, NULL, "Toggles the onboard device LEDs on the Graphical Plotter Display.\nUSAGE: gled <r> <g> <b>\n<r> - red led, <g> - green led, <b> - blue led", gcu_cmd_gled, 4, 0);
SHELL_CMD_ARG_REGISTER(gpb, NULL, "Read the pushbutton state from the GCU.", gcu_cmd_gpb, 1, 0);
SHELL_CMD_ARG_REGISTER(gcugraph, NULL, "Draws a graph with the specified sensor data on the Graphical Plotter Display.\nUSAGE: gcugraph <device id>\n<device id> - specified sensor", gcu_cmd_gcugraph, 2, 0);
SHELL_CMD_ARG_REGISTER(gcumeter, NULL, "Draws a meter with the specified sensor data on the Graphical Plotter Display.\nUSAGE: gcumeter <device id>\n<device id> - specified sensor", gcu_cmd_gcumeter, 2, 0);
SHELL_CMD_ARG_REGISTER(gcunumeric, NULL, "Draws a SSD numeric with the specified sensor data on the Graphical Plotter Display.\nUSAGE: gcunumeric <device id>\n<device id> - specified sensor", gcu_cmd_gcunumeric, 2, 0);
SHELL_STATIC_SUBCMD_SET_CREATE(sub_gcurec,
	SHELL_CMD_ARG(-s, NULL, "Starts recording the Plot values to the SD card.\nUSAGE: gcurec -s <device id> <file name>", gcu_cmd_gcurec_s, 3, 0),
	SHELL_CMD_ARG(-p, NULL, "Stops recording the Plot values to the SD card..\nUSAGE: gcurec -p", gcu_cmd_gcurec_p, 1, 0),
	SHELL_SUBCMD_SET_END
);
SHELL_CMD_ARG_REGISTER(gcurec, &sub_gcurec, "Records the Graphical Plotter Display values to the onboard SD Card.\n", NULL, 1, 1);

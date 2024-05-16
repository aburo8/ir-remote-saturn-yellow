 /** 
 **************************************************************
 * @file src/main.c
 * @author Alexander Burovanov - 46990480
 * @date 01052023
 * @brief Application Host Unit (AHU) Entry Point
 * REFERENCE: csse4011_prac1_ahu.pdf 
 ***************************************************************
 */

#include <stdio.h>
#include <zephyr/kernel.h>
#include <zephyr/sys_clock.h>
#include <zephyr/device.h>
#include <zephyr/sys/sys_heap.h>
#include "ahu.h"
#include "led_module.h"
#include "uart_module.h"
#include "ble_module.h"
#include "pc_module.h"
#include "ir_module.h"

// Define Priorities
#define UART_PRIORITY 2
#define AHU_PRIORITY 3
#define BLE_PRIORITY 3
#define PC_PRIORITY 3
#define IR_TX_PRIORITY 1

// Define Stack Sizes
#define UART_STACK_SIZE 1024
#define AHU_STACK_SIZE 2048
#define BLE_STACK_SIZE 4096
#define PC_STACK_SIZE 8192
#define IR_TX_STACK_SIZE 2048

// Create threads
K_THREAD_DEFINE(ahu_id, AHU_STACK_SIZE, ahu_handler, NULL, NULL, NULL,
		AHU_PRIORITY, 0, 0);
K_THREAD_DEFINE(uart_id, UART_STACK_SIZE, uart_handler, NULL, NULL, NULL,
		UART_PRIORITY, 0, 0);
K_THREAD_DEFINE(ble_id, BLE_STACK_SIZE, ble_handler, NULL, NULL, NULL,
		BLE_PRIORITY, 0, 0);
K_THREAD_DEFINE(pc_transmit_id, PC_STACK_SIZE, pc_comms_transmit_handler, NULL, NULL, NULL,
		PC_PRIORITY, 0, 0);
K_THREAD_DEFINE(pc_receive_id, PC_STACK_SIZE, pc_comms_receive_handler, NULL, NULL, NULL,
		PC_PRIORITY, 0, 0);		
K_THREAD_DEFINE(ir_tx_id, IR_TX_STACK_SIZE, ir_transmission_handler, NULL, NULL, NULL,
		IR_TX_PRIORITY, 0, 0);

/**
 * Application entry point
 * 
 * Returns: 0 upon exit
*/
int main(void) {

	// Initialise Hardware
	init_leds();
	init_ble();
	init_ir_module();

	return 0;
}

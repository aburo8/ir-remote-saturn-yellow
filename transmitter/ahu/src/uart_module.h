 /** 
 **************************************************************
 * @file src/uart_module.h
 * @author Alexander Burovanov - 46990480
 * @date 01052023
 * @brief UART Module
 * REFERENCE: csse4011_prac1_ahu.pdf 
 ***************************************************************
 */
#ifndef AB_UART_MODULE_H_
#define AB_UART_MODULE_H_

#include <zephyr/drivers/uart.h>

// UART Setup
#define UART_GCU_NODE DT_ALIAS(uart_test)
static const struct device *const uart_dev = DEVICE_DT_GET(UART_GCU_NODE);

// Default Message Buffer Size
#define MSG_SIZE 32

// Receive Message Queue
extern struct k_msgq* uart_receive_msgq_extern;

/**
 * UART message controller. Sends and receives UART message between the peripherals.
 * 
 * Returns: 0 upon exit
*/
extern int uart_handler();

#endif


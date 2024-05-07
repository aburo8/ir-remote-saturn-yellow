 /** 
 **************************************************************
 * @file src/uart_module.c
 * @author Alexander Burovanov - 46990480
 * @date 01052023
 * @brief UART Module
 * REFERENCE: csse4011_prac1_ahu.pdf 
 ***************************************************************
 */
#include <stdio.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/sys/sys_heap.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include "uart_module.h"
#include "hci.h"

// Setup logging
LOG_MODULE_DECLARE(ahu);

/* receive buffer used in UART ISR callback */
static char rx_buf[MSG_SIZE];
static int rx_buf_pos;

// Create the uart message queue
K_MSGQ_DEFINE(uart_receive_msgq, MSG_SIZE, 10, 4);

// Used to extern the uart msgq for use in other threads
struct k_msgq* uart_receive_msgq_extern = &uart_receive_msgq;

/*
 * Read characters from UART until line end is detected. Afterwards push the
 * data to the message queue.
 * 
 * Returns: void
 */
void serial_cb(const struct device *dev, void *user_data)
{
	uint8_t c;

	if (!uart_irq_update(uart_dev)) {
		return;
	}

	if (!uart_irq_rx_ready(uart_dev)) {
		return;
	}

	/* read until FIFO empty */
	while (uart_fifo_read(uart_dev, &c, 1) == 1) {
		if ((c == '\n' || c == '\r') && rx_buf_pos > 0) {
			/* terminate string */
			rx_buf[rx_buf_pos] = '\0';

			/* if queue is full, message is silently dropped */
			k_msgq_put(&uart_receive_msgq, &rx_buf, K_NO_WAIT);

			/* reset the buffer (it was copied to the msgq) */
			rx_buf_pos = 0;
		} else if (rx_buf_pos < (sizeof(rx_buf) - 1)) {
			rx_buf[rx_buf_pos++] = c;
		}
		/* else: characters beyond buffer size are dropped */
	}
}

/**
 * UART message controller. Sends and receives UART message between the peripherals.
 * 
 * Returns: 0 upon exit
*/
int uart_handler(void) {

	// Setup GCU Uart
	if (!device_is_ready(uart_dev)) {
		printk("UART device not found!");
		return 0;
	}

	int ret = uart_irq_callback_user_data_set(uart_dev, serial_cb, NULL);
	if (ret < 0) {
		if (ret == -ENOTSUP) {
			printk("Interrupt-driven UART API support not enabled\n");
		} else if (ret == -ENOSYS) {
			printk("UART device does not support interrupt-driven API\n");
		} else {
			printk("Error setting UART callback: %d\n", ret);
		}
		return 0;
	}
	uart_irq_rx_enable(uart_dev);

	// Send a packet to init uart
	send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_DAC, (uint8_t*)&(DacData){(float)0.5, (float)0.5});

	// Uart buffer
	char tx_buf[MSG_SIZE];

	// Handle Sending here
	while (k_msgq_get(uart_receive_msgq_extern, &tx_buf, K_FOREVER) == 0) {
		// Receive & Process UART Packets
		Packet packet = receive_uart_packet(tx_buf);
		#ifdef DEBUG
			printk("RECEIVED DATA:\n");
			printk("Preamble: %X\n", packet.preamble);
			printk("typeAndLength: %X\n", packet.typeAndLength);
			printk("command: %X\n", packet.command);
			print_contents(packet.command, packet.data);
		#endif
		if (packet.command == CMD_GPB) {
			// Print out the push button state
			PBResponse* res = (PBResponse*)(packet.data);
			if (res->status.resCode == RES_OK) {
				printk("GCU Push Button State = %d\n", res->state);
			} else {
				LOG_ERR("Invalid PB State Received! Failed to interpret response.");
			}
		}
		k_free(packet.data);
	}
	return 0;
}
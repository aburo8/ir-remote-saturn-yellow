 /** 
 **************************************************************
 * @file src/pc_module.c
 * @author Alexander Burovanov - 46990480
 * @date 11042024
 * @brief PC Controller
 * REFERENCE: NA 
 ***************************************************************
 */
#include <zephyr/logging/log.h>
#include <zephyr/kernel.h>
#include <zephyr/drivers/uart.h>
#include <pb_encode.h>
#include <pb_decode.h>
#include <zephyr/sys/dlist.h>
#include "pc_module.h"
#include "src/pc.pb.h"
#include "ab_util.h"

// Register Logger
LOG_MODULE_REGISTER(pc_module, 4);

// PC Message transmission message queue
K_MSGQ_DEFINE(pc_transmit, PCMessage_size, 10, 64);
K_MSGQ_DEFINE(pc_receive, PCMessage_size, 10, 64);

// Used to extern the uart msgq for use in other threads
struct k_msgq* pc_transmit_extern = &pc_transmit;
struct k_msgq* pc_receive_extern = &pc_receive;

/* receive buffer used in UART ISR callback */
static char rx_buf1[PCMessage_size];
static int rx_buf_pos1;
static int rx_size;

/**
 * Prints a PC Message to the console
 * 
 * Returns: void
*/
void print_pc_message(PCMessage msg) {
	printk("CMD: %d, beaconID: 0x%X\n", msg.cmd);
}

/**
 * Encodes a PCMessage into a protocol buffer.
 * 
 * message: the message to encode
 * buffer: a pointer to a buffer to store the result
 * buffer_size: the number of bytes to encode
 * message_length: a pointer to store the size of the encoded 
 * 
 * Returns: true if successful, false otherwise
*/
bool encode_pc_message(PCMessage* message, uint8_t* buffer, size_t buffer_size, size_t* message_length)
{
	bool status;

	// Create a stream that will write to our buffer.
	pb_ostream_t stream = pb_ostream_from_buffer(buffer, buffer_size);

	// Now we are ready to encode the message!
	status = pb_encode(&stream, PCMessage_fields, message);
	*message_length = stream.bytes_written;

	if (!status) {
		printk("Encoding failed: %s\n", PB_GET_ERROR(&stream));
	}

	return status;
}

/**
 * Decodes a PCMessage into a protocol buffer.
 * 
 * message: the resulting message
 * buffer: a pointer to a buffer to containing the string to decode
 * message_length: the number of bytes to decode
 * 
 * Returns: true if successful, false otherwise
*/
bool decode_pc_message(PCMessage* message, uint8_t *buffer, size_t message_length)
{
	bool status;

	/* Create a stream that reads from the buffer. */
	pb_istream_t stream = pb_istream_from_buffer(buffer, message_length); // dummy
	PCMessage msgLocal = PCMessage_init_zero;

	/* Now we are ready to decode the message. */
	status = pb_decode(&stream, PCMessage_fields, message);

	/* Check for errors... */
	if (status) {
		/* Print the data contained in the message. */
		print_pc_message(*message);
		printk("\n");

		// Process Message
		switch (message->cmd) {
			case PCCommand_PC_CMD_IRCODE:

				// There is no case where the PC is sending data back to the board
				break;
			default:
				LOG_INF("Received some unexpected data from PC!");
		}
	} else {
		printk("Decoding failed: %s\n", PB_GET_ERROR(&stream));
	}

	return status;
}

/**
 * PC GUI Communication Controller. Sends and receives protocol buffers between the PC Software and the Device.
 * 
 * Returns: 0 upon exit
*/
int pc_comms_transmit_handler() {
	// Setup PC Software Uart
	if (!device_is_ready(pc_dev)) {
		LOG_ERR("UART device not found!");
		return 0;
	}

    // Message received
    PCMessage* message = k_malloc(PCMessage_size);

    while (k_msgq_get(&pc_transmit, message, K_FOREVER) == 0) {
		// Send protobuf's to the PC Software
        uint8_t msgBuffer[PCMessage_size];
        size_t msgLength;

        // Encode the Message
        if (!encode_pc_message(message, msgBuffer, sizeof(msgBuffer), &msgLength)) {
            LOG_ERR("Failed to encode PC Message!");
            continue;
	    }

        // Transmit the Message
        LOG_DBG("Transmitting Message! %d bytes", msgLength);
		for (size_t i = 0; i < msgLength; i++) {
			uart_poll_out(pc_dev, msgBuffer[i]);
		}
        // Transmit a newline character to indicate the software the transmission is complete
		uart_poll_out(pc_dev, '\n');
		k_sleep(K_MSEC(100));
	}
	return 0;
}

/*
 * Read characters from UART until line end is detected. Afterwards push the
 * data to the message queue.
 * 
 * Returns: void
 */
void serial_cb_pc(const struct device *dev, void *user_data)
{
	uint8_t c;

	if (!uart_irq_update(pc_dev)) {
		return;
	}

	if (!uart_irq_rx_ready(pc_dev)) {
		return;
	}
	
	/* read until FIFO empty */
	while (uart_fifo_read(pc_dev, &c, 1) == 1) {
		if ((c == '\n' || c == '\r') && rx_buf_pos1 > 0) {
			/* terminate string */
			rx_buf1[rx_buf_pos1] = '\0';

			/* if queue is full, message is silently dropped */
			k_msgq_put(&pc_receive, &rx_buf1, K_NO_WAIT);

			/* reset the buffer (it was copied to the msgq) */
			rx_size = rx_buf_pos1;
			rx_buf_pos1 = 0;
		} else if (rx_buf_pos1 < (sizeof(rx_buf1) - 1)) {
			rx_buf1[rx_buf_pos1++] = c;
		}
		/* else: characters beyond buffer size are dropped */
	}
}

/**
 * PC GUI Receiver. Receives protocol buffers between the PC Software and the Device.
 * 
 * Returns: 0 upon exit
*/
int pc_comms_receive_handler() {
	// Setup PC Software Uart
	if (!device_is_ready(pc_dev)) {
		LOG_ERR("UART device not found!");
		return 0;
	}
	
	int ret = uart_irq_callback_user_data_set(pc_dev, serial_cb_pc, NULL);
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
	uart_irq_rx_enable(pc_dev);

    // Message received
    PCMessage* message = malloc(PCMessage_size);
	// Since using malloc override with memset initialisation
	PCMessage template = PCMessage_init_zero;
	memcpy(message, &template, PCMessage_size);

	char msgBuffer[PCMessage_size];
	memset(msgBuffer, '\0', PCMessage_size);
	while (k_msgq_get(&pc_receive, &msgBuffer, K_FOREVER) == 0) {
		// Send protobuf's to the PC Software
		LOG_DBG("Received PC MESSAGE");
		LOG_DBG("Length: %d", rx_size);

		// Decode the Message
		if (!decode_pc_message(&message, msgBuffer, rx_size)) {
            LOG_ERR("Failed to decode PC Message!");
            continue;
	    }

		memset(msgBuffer, '\0', PCMessage_size);
	}
	return 0;
}
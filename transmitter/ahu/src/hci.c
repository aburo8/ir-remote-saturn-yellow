 /** 
 **************************************************************
 * @file src/hci.c
 * @author Alexander Burovanov - 46990480
 * @date 01052023
 * @brief Host Controller Communication Protocol
 * REFERENCE: csse4011_prac1_hci.pdf 
 ***************************************************************
 */
#include <zephyr/kernel.h>
#include <zephyr/sys/sys_heap.h>
#include "hci.h"

#define AHU
#ifdef AHU
// Register the logger if you are on the AHU device
#include <zephyr/logging/log.h>
LOG_MODULE_REGISTER(hci, 3);
#endif

// NOTE UART features are gated by UART_MODULE_ENABLED flag
#ifdef UART_MODULE_ENABLED
#include "uart_module.h"
#endif

// File Name Placeholder
char fileNameG[FILE_NAME_MAX_LEN];

/**
 * Combines the type and data length arguments into a single byte.
 * 
 * type: the packet type
 * length: the length of the packet data
 * 
 * Returns: the combined byte
*/
uint8_t combine_type_and_length(uint8_t type, uint8_t length) {
    uint8_t typeAndLength = length;
    typeAndLength |= (type << 4);
    return typeAndLength;
}

/**
 * Determines the size of the data contents based on the command.
 * 
 * cmd: the provided command
 * 
 * Returns: the size of the data contents associated to the command. 0 if no command found.
*/
uint8_t determine_contents_size(uint8_t cmd) {
    switch (cmd) {
        case CMD_POINT:
            return sizeof(PointData);
            break;
        case CMD_CIRCLE:
            return sizeof(CircleData);
            break;
        case CMD_LJ:
            return sizeof(LissajousData);
            break;
        case CMD_DAC:
            return sizeof(DacData);
            break;
        case CMD_GLED:
            return sizeof(RGBData);
            break;
        case CMD_GPB:
            return sizeof(PBResponse);
            break;
        case CMD_GRAPH:
            return sizeof(DeviceIdData);
            break;
        case CMD_METER:
            return sizeof(DeviceIdData);
            break;
        case CMD_NUMERIC:
            return sizeof(DeviceIdData);
            break;
        case CMD_REC:
            return sizeof(RecData);
            break;
        case CMD_SENSOR:
            return sizeof(SensorData);
            break;
        default:
            return 0;
    }
}

/**
 * Prints the data contents of each command
 * 
 * cmd: the command associated to the data
 * data: the data to print
 * 
 * Returns: void
*/
void print_contents(uint8_t cmd, uint8_t* data) {
    switch (cmd) {
        case CMD_POINT:
            printk("x: %f\ny: %f\n", (double)((PointData*)data)->x, (double)((PointData*)data)->y);
            break;
        case CMD_CIRCLE:
            printk("r: %f\nx: %f\ny: %f\n", (double)((CircleData*)data)->r, (double)((CircleData*)data)->x, (double)((CircleData*)data)->y);
            break;
        case CMD_LJ:
            printk("a: %f\nb: %f\nt: %f\n", (double)((LissajousData*)data)->a, (double)((LissajousData*)data)->b, (double)((LissajousData*)data)->t);
            break;
        case CMD_DAC:
            printk("x: %f\ny: %f\n", (double)((DacData*)data)->x, (double)((DacData*)data)->y);
            break;
        case CMD_GLED:
            printk("r: %d\ng: %d\nb: %d\n", ((RGBData*)data)->r, ((RGBData*)data)->g, ((RGBData*)data)->b);
            break;
        case CMD_GPB:
            return;
            break;
        case CMD_GRAPH:
            printk("deviceId: %d\n", ((DeviceIdData*)data)->deviceId);
            break;
        case CMD_METER:
            printk("deviceId: %d\n", ((DeviceIdData*)data)->deviceId);
            break;
        case CMD_NUMERIC:
            printk("deviceId: %d\n", ((DeviceIdData*)data)->deviceId);
            break;
        case CMD_REC:
            printk("cmd: %d\ndeviceId: %d\nfileName: %s\n", ((RecData*)data)->cmd, ((RecData*)data)->deviceId, ((RecData*)data)->fileName);
            break;
        case CMD_SENSOR:
            printk("deviceId: %d\ndata: %f\n", ((SensorData*)data)->deviceId, (double)(((SensorData*)data)->data));
            break;
        default:
            return;
    }
}

#ifdef UART_MODULE_ENABLED
/**
 * Sends a packet via UART
 * 
 * uartdev: UART device node
 * preamble: packet preamble
 * packetType: the packet type (request/response)
 * command: the command executed
 * data: the content for the relevant command.
 * NOTE: it is the caller's responsibity to ensure the content data type matches the command provided.
 * 
 * Returns: void * 
*/
void send_uart_packet(uint8_t preamble, uint8_t packetType, uint8_t command, uint8_t* data) {
    // Determine the content length & construct packet
    uint8_t contentSize = determine_contents_size(command);
    StrippedPacket packet = {preamble, combine_type_and_length(packetType, contentSize), command};
	// Create the bytestream
	size_t bufferSize = sizeof(packet) + contentSize;
    #ifdef AHU
	LOG_DBG("Buffer Size: %u\n", bufferSize);
    #endif
	uint8_t *byte_stream = k_malloc(bufferSize);

	// Place the Packet Struct into the bytestream
	memcpy(byte_stream, &packet, sizeof(packet));

	// Place the contents struct into the bytestream 
	memcpy(&byte_stream[sizeof(packet)], data, contentSize);

    // Inject File Name
    if (packet.command == CMD_REC) {
        // TODO: Fix update filename handling
        // RecData* recdata = (RecData*)data;
        // memcpy(&byte_stream[sizeof(packet) + 3], recdata->fileName, strlen(recdata->fileName));
        memcpy(&byte_stream[sizeof(packet) + 2], fileNameG, strlen(fileNameG));
    }

	// Send the byte stream over UART
	for (size_t i = 0; i < bufferSize; i++) {
        #ifdef AHU
		LOG_DBG("Send 0x%X\n", byte_stream[i]);
        #endif
		uart_poll_out(uart_dev, byte_stream[i]);
	}
		uart_poll_out(uart_dev, '\n');
	k_free(byte_stream);
    #ifdef AHU
	LOG_DBG("Packet Sent!");
    #endif
}

/**
 * Receives and processes a packet from UART.
 * 
 * buffer: the buffer of received bytes
 * 
 * Returns: a ptr to a packet
 * NOTE: this function will allocate memory for the data contents. It is the responsibility
 *       of the caller to free this memory after use by calling `k_free()`.
*/
Packet receive_uart_packet(uint8_t* buffer) {
    // The receivedPacket
    StrippedPacket receivedPacket;
    
    // Extract the packet from the received bytes
    memcpy(&receivedPacket, buffer, sizeof(StrippedPacket));

    // Determine which command is being used and the subsequent contents size
    uint8_t contentSize = determine_contents_size(receivedPacket.command);
    uint8_t* contents = (uint8_t*)k_malloc(contentSize);

    // Extract the contents from the received bytes
    memcpy(contents, &buffer[sizeof(StrippedPacket)], contentSize);

    // Link the contents to the packet
    Packet fullPacket = {receivedPacket.preamble, receivedPacket.typeAndLength, receivedPacket.command, contents};

    return fullPacket;
}
#endif
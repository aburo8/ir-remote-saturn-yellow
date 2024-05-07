 /** 
 **************************************************************
 * @file src/pc_module.h
 * @author Alexander Burovanov - 46990480
 * @date 11042024
 * @brief PC Controller
 * REFERENCE: NA 
 ***************************************************************
 */
#ifndef AB_PC_MODULE_H_
#define AB_PC_MODULE_H_
#include <stdint.h>
#include <pb_encode.h>
#include <pb_decode.h>
#include <zephyr/sys/dlist.h>
#include "src/pc.pb.h"

// Device Configuration
#define UART_PC_SOFTWARE DT_ALIAS(pc_software)
static const struct device *const pc_dev = DEVICE_DT_GET(UART_PC_SOFTWARE);

// Used to extern the uart msgq for use in other threads
extern struct k_msgq* pc_transmit_extern;
extern struct k_msgq* pc_receive_extern;

// Linked list to store the iBeacon nodes
extern sys_dlist_t ibeaconNodes;

/**
 * iBeacon node structure
*/
typedef struct iBeaconNode {
	PCMessage data;
	sys_dnode_t node;
};

/**
 * PC GUI Communication Controller. Sends and receives protocol buffers between the PC Software and the Device.
 * 
 * Returns: 0 upon exit
*/
extern int pc_comms_transmit_handler();

/**
 * PC GUI Receiver. Receives protocol buffers between the PC Software and the Device.
 * 
 * Returns: 0 upon exit
*/
extern int pc_comms_receive_handler();

#endif
 /** 
 **************************************************************
 * @file src/ble_module.h
 * @author Alexander Burovanov - 46990480
 * @date 01052023
 * @brief Bluetooth Module
 * REFERENCE: csse4011_prac2_ahu.pdf 
 ***************************************************************
 */
#ifndef AB_BLE_MODULE_H_
#define AB_BLE_MODULE_H_
#include <zephyr/bluetooth/bluetooth.h>

// BLE MESSAGE QUEUE'S
extern struct k_sem* blecon_sem_extern;
extern struct k_msgq* ble_receive_extern;

// Fixed Addresses
const static char* THINGY_STR = "fe:95:bb:55:92:ef";
static bt_addr_le_t THINGY52_ADDR;

// BLE CMDS
#define BLECON_START 0x01
#define BLECON_STOP 0x02
#define BLESCAN_START 0x03
#define BLESCAN_STARTF 0x04
#define BLESCAN_STOP 0x05

// BLE CMD Type
typedef struct {
    uint8_t bleCmd;
    bt_addr_le_t addr;
} BLECmd;

/**
 * Initialises BLE Hardware
 * 
 * Returns: 0 on success
*/
extern int init_ble();

/**
 * UART message controller. Sends and receives UART message between the peripherals.
 * 
 * Returns: 0 upon exit
*/
extern int ble_handler();

/**
 * Returns the current BLE Scanning State of the Application
 * 
 * Returns: 0 if not scanning. 1 if blecon. 2 if blescan. 3 if both.
*/
extern int get_scanning_state();

#endif


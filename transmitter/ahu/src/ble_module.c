 /** 
 **************************************************************
 * @file src/ble_module.c
 * @author Alexander Burovanov - 46990480
 * @date 01052023
 * @brief Bluetooth Module
 * REFERENCE: csse4011_prac2_ahu.pdf 
 ***************************************************************
 */
#include <stdio.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/hci.h>
#include <zephyr/sys/byteorder.h>
#include "hci.h"
#include "ble_module.h"
#include "pc_module.h"
#include "src/pc.pb.h"

// Setup logging
LOG_MODULE_REGISTER(ble_module, 4);

// Blecon semaphore
K_SEM_DEFINE(blecon_sem, 0, 1);
struct k_sem* blecon_sem_extern = &blecon_sem;

// Create the uart message queue
K_MSGQ_DEFINE(ble_receive, sizeof(BLECmd), 10, 4);

// Used to extern the uart msgq for use in other threads
struct k_msgq* ble_receive_extern = &ble_receive;

#define NAME_LEN 30
#define BLE_SCANNING() bleconActive || blescanActive

// BLE States
static uint8_t blescanActive = 0;
static uint8_t bleconActive = 0;
static uint8_t scanFilteringActive = 0;
bt_addr_le_t BLESCAN_FILTER_ADDR;
bt_addr_le_t BLECON_FILTER_ADDR;

/**
 * Returns the current BLE Scanning State of the Application
 * 
 * Returns: 0 if not scanning. 1 if blecon. 2 if blescan. 3 if both.
*/
int get_scanning_state() {
	if (blescanActive && bleconActive) {
		return 3;
	} else if (blescanActive) {
		return 2; 
	} else if (bleconActive) {
		return 1;
	} else {
		return 0;
	}
}

/**
 * Returns the mac address of a beacon based on id 
 * 
 * id: beacon id
 * mem: the memory location to store the returned string
 * 
 * Returns: the mac address string
*/
char* beacon_mac_from_id(uint8_t id, char* mem) {
	// Compare the received address to the available iBeacon node addresses.
	if (id == 1) {
		strcpy(mem, CSSE_4011_A_STR);
		return CSSE_4011_A_STR;
	} else if (id == 2) {
		strcpy(mem, CSSE_4011_B_STR);
		return CSSE_4011_B_STR;
	} else if (id == 3) {
		strcpy(mem, CSSE_4011_C_STR);
		return CSSE_4011_C_STR;
	} else if (id == 4) {
		strcpy(mem, CSSE_4011_D_STR);
		return CSSE_4011_D_STR;
	} else if (id == 5) {
		strcpy(mem, CSSE_4011_E_STR);
		return CSSE_4011_E_STR;
	} else if (id == 6) {
		strcpy(mem, CSSE_4011_F_STR);
		return CSSE_4011_F_STR;
	} else if (id == 7) {
		strcpy(mem, CSSE_4011_G_STR);
		return CSSE_4011_G_STR;
	} else if (id == 8) {
		strcpy(mem, CSSE_4011_H_STR);
		return CSSE_4011_H_STR;
	} else if (id == 9) {
		strcpy(mem, CSSE_4011_I_STR);
		return CSSE_4011_I_STR;
	} else if (id == 10) {
		strcpy(mem, CSSE_4011_J_STR);
		return CSSE_4011_J_STR;
	} else if (id == 11) {
		strcpy(mem, CSSE_4011_K_STR);
		return CSSE_4011_K_STR;
	} else if (id == 12) {
		strcpy(mem, CSSE_4011_L_STR);
		return CSSE_4011_L_STR;
	}
	return "00:00:00:00:00:00";
}

/**
 * Callback function which executes everytime a BT device is found
 * 
 * addr: bt address
 * rssi: bt rssi
 * type: packet type
 * ad: advertising data
 * 
 * Returns: void
*/
static void device_found(const bt_addr_le_t *addr, int8_t rssi, uint8_t type,
			 struct net_buf_simple *ad)
{
	char addr_str[BT_ADDR_LE_STR_LEN];
	int ret;
	bt_addr_le_to_str(addr, addr_str, sizeof(addr_str));

	if (blescanActive) {
		// Show all found devices
		if (scanFilteringActive) {
			// ret = bt_addr_le_cmp(&BLECON_FILTER_ADDR, addr);
			ret = bt_addr_cmp(&BLESCAN_FILTER_ADDR.a, &addr->a);
			if (ret == 0) {
				printk("blescan (f): %s (RSSI %d), type %u, AD data len %u\n", addr_str, rssi, type, ad->len);
			}
		} else {
			printk("blescan (all): %s (RSSI %d), type %u, AD data len %u\n", addr_str, rssi, type, ad->len);
		}
	}
	
	if(bleconActive) {
		// Record the data from the Thingy:52 Packets
		// ret = bt_addr_le_cmp(&BLECON_FILTER_ADDR, addr);
		ret = bt_addr_cmp(&BLECON_FILTER_ADDR.a, &addr->a);
		if (ret != 0) {
			// Not a Thingy:52 Packet
			return;
		}

		// Send the data via UART
		uint8_t did = ad->data[IBEACON_MAJOR_IDX - 1];
		uint8_t data3 = ad->data[IBEACON_MAJOR_IDX];
		uint8_t data2 = ad->data[IBEACON_MAJOR_IDX + 1];
		uint8_t data1 = ad->data[IBEACON_MINOR_IDX];
		uint8_t data0 = ad->data[IBEACON_MINOR_IDX + 1];
		uint32_t dataf;
		dataf = (data3 << 24) | (data2 << 16) | (data1 << 8) | data0;
		float dataF;;
		memcpy(&dataF, &dataf , sizeof(float));

		if (did == DID_RSSI || did == DID_TEMP || did == DID_HUM || did == DID_AP || did == DID_TVOC) {
			if (did == DID_RSSI) {
				// This is RSSI ranging information from the mobile node
				int dataBeacon = ad->data[IBEACON_MAJOR_IDX + 1];
				int8_t dataRssi = ad->data[IBEACON_MINOR_IDX + 1];
				LOG_DBG("DID: %d, BeaconID: %d, RSSI: %d\n", did, dataBeacon, dataRssi);
				
				// Filter the Packet (based on the filter list)
				sys_dnode_t* node;
				struct iBeaconNode template;
				int counter = 0;
				ret = 1;
				bt_addr_t temp1;
				bt_addr_t temp2;
				char addr1[20];
				for (node = sys_dlist_peek_head(&ibeaconNodes); node != NULL; node = sys_dlist_peek_next(&ibeaconNodes, node)) {
					// Get the container structure
					struct iBeaconNode* beaconNode = SYS_DLIST_CONTAINER(node, &template, node);
					addr = beacon_mac_from_id(dataBeacon, addr1);
					bt_addr_from_str(addr1, &temp1);
					bt_addr_from_str(beaconNode->data.bleMac, &temp2);

					// printk("ADDR1: %s\n", addr1);
					// printk("ADDR2: %s\n", beaconNode->data.bleMac);

					if (!bt_addr_cmp(&temp1, &temp2)) {
						ret = 0;
						break;
					}
					counter++;
				}

				// Send this information to the PC for processing
				if (!ret) {
					PCMessage* msgMalloc = k_malloc(PCMessage_size);
					msgMalloc->cmd = PCCommand_PC_CMD_RSSI;
					msgMalloc->beacon_id = dataBeacon;
					msgMalloc->rssi = dataRssi;
					k_msgq_put(pc_transmit_extern, (uint8_t*)msgMalloc, K_FOREVER);
					k_free(msgMalloc);
					// k_sleep(K_MSEC(100));
				}
			} else {
				// This is a sensor data packet
				LOG_DBG("DID: %d, Data: [%X %X %X %X], %f\n", did, data3, data2, data1, data0, (double)dataF);
				// LOG_DBG("blecon: %s (RSSI %d), type %u, AD data len %u\n", addr_str, rssi, type, ad->len);

				SensorData data = {did, (float)dataF};
				send_uart_packet(PACKET_PRE, PACKET_REQ, CMD_SENSOR, (uint8_t*)&data);
			}
		}
	}
}

/**
 * Start BLE Scanning
 *  
 * Returns: void
*/
int start_ble_scanning() {
	// Note: set .options to 0 for normal operation (without whitelist)
	struct bt_le_scan_param scan_param = {
		.type       = BT_LE_SCAN_TYPE_PASSIVE,
		.options    = BT_LE_SCAN_OPT_FILTER_ACCEPT_LIST,
		.interval   = BT_GAP_SCAN_FAST_INTERVAL,
		.window     = BT_GAP_SCAN_FAST_WINDOW,
	};

	int err;

	bt_addr_le_from_str(THINGY_STR, "random", &THINGY52_ADDR);

	err = bt_le_whitelist_add(&THINGY52_ADDR);
    if (err) {
        LOG_ERR("Failed to add address to the whitelist (err %d)\n", err);
        return err;
    }

    err = bt_le_scan_start(&scan_param, device_found);
	if (err) {
		LOG_ERR("Start scanning failed (err %d)\n", err);
		return err;
	}

	return 0;
}

/**
 * BLE message controller. Sends and receives UART message between the peripherals.
 * 
 * Returns: 0 upon exit
*/
int ble_handler(void) {
	
	// Init Delay
	k_sleep(K_MSEC(100));

	BLECmd bleCmd;
	char addr_str[BT_ADDR_STR_LEN];
	while (k_msgq_get(&ble_receive, &bleCmd, K_FOREVER) == 0) {
		// Process BLE Commands as they are received
		switch (bleCmd.bleCmd) {
			case BLECON_START:
				// Start Receiving Data from the Thingy:52
				if (!BLE_SCANNING()) {
					start_ble_scanning();
				}
				bleconActive = 1;
				if (!bt_addr_cmp(&bleCmd.addr.a, &BLECON_FILTER_ADDR.a)) {
					bt_addr_to_str(&BLECON_FILTER_ADDR.a, addr_str, sizeof(addr_str));
					LOG_WRN("Sensor data from BT Address [%s] is already being captured.\n", addr_str);
				}
				BLECON_FILTER_ADDR = bleCmd.addr;

				break;
			case BLECON_STOP:
				// Stop Receiving Data from the Thingy:52
				if (!BLE_SCANNING()) {
					LOG_WRN("Bluetooth scanning is not currently active.");
				}
				bleconActive = 0;
				if (!BLE_SCANNING()) {
					bt_le_scan_stop();
				}
				
				break;
			case BLESCAN_START:
				// Start BLE Scanning (without filtering)
				if (!BLE_SCANNING()) {
					start_ble_scanning();
				}
				blescanActive = 1;

				break;
			case BLESCAN_STARTF:
				if (!BLE_SCANNING()) {
					start_ble_scanning();
				}
				if (!bt_addr_cmp(&bleCmd.addr.a, &BLESCAN_FILTER_ADDR.a)) {
					bt_addr_to_str(&BLESCAN_FILTER_ADDR.a, addr_str, sizeof(addr_str));
					LOG_WRN("Packets from BT Address [%s] are already being filtered.\n", addr_str);
				}
				blescanActive = 1;
				scanFilteringActive = 1;
				BLESCAN_FILTER_ADDR = bleCmd.addr;

				break;
			case BLESCAN_STOP:
				// Stop BLE Scanning
				if (!BLE_SCANNING()) {
					LOG_WRN("Bluetooth scanning is not currently active.");
				}
				blescanActive = 0;
				scanFilteringActive = 0;
				if (!BLE_SCANNING()) {
					bt_le_scan_stop();
				}
				
				break;
		}
	}
	return 0;
}

/**
 * Initialises BLE Hardware
 * 
 * Returns: 0 on success
*/
int init_ble() {
    int err;

	LOG_DBG("Initialising BLE\n");

	/* Initialize the Bluetooth Subsystem */
	err = bt_enable(NULL);
	if (err) {
		printk("Bluetooth init failed (err %d)\n", err);
		return 0;
	}

	return 0;
}
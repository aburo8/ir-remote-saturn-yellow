 /** 
 **************************************************************
 * @file src/ab_util.h
 * @author Alexander Burovanov - 46990480
 * @date 25/03/2024
 * @brief AB's Utility Library
 * REFERENCE: None
 ***************************************************************
 */
#ifndef AB_UTIL_H_
#define AB_UTIL_H_
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

/**
 * Validates a floating point argument
 * 
 * value: the value to validate
 * returnLoc: a pointer to the return location
 * 
 * Returns: 0 on success, otherwise 1.
*/
extern int validate_float_arg(char* value, float* returnLoc);

/**
 * Validates an integer argument
 * 
 * value: the value to validate
 * returnLoc: a pointer to the return location
 * 
 * Returns: 0 on success, otherwise 1.
*/
extern int validate_int_arg(char* value, int* returnLoc);

/**
 * Validates a provided binary command line argument
 * 
 * value: the character to validate
 * 
 * Returns: 0 if value is 0, 1 if value is 1, 2 on error.
*/
extern int validate_binary_arg(char value);

/**
 * Gets a binary mask from a mask string
 * 
 * mask: a ptr to store the resulting mask
 * value: a string mask. E.g. "0010"
 * length: the length of the target mask E.g. 4
 * 
 * Returns: 0 on success, otherwise 1.
*/
extern uint8_t get_binary_mask(uint8_t* mask, char *value, uint8_t length);

/**
 * Validates a device id argument.
 * 
 * did: device id to verify
 * 
 * Result: 0 if valid, 1 otherwise.
*/
extern int validate_device_id(uint8_t did);

/**
 * Validates a provided filename arguments
 * 
 * fileName: filename being validated
 * 
 * Returns: 0 if valid. 1 if the filename is too long. 2 if the filename is invalid. 3 if the extension is invalid.
 * 
*/
extern int validate_file_name(char* fileName);

/**
 * Validates an BLE Address argument
 * 
 * value: the value to validate
 * returnLoc: a pointer to the return location
 * 
 * Returns: 0 on success, otherwise 1.
*/
extern int validate_ble_addr(char* value, bt_addr_le_t* returnLoc);

#endif
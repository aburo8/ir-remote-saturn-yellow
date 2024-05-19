 /** 
 **************************************************************
 * @file src/ab_util.c
 * @author Alexander Burovanov - 46990480
 * @date 25/03/2024
 * @brief AB's Utility Library
 * REFERENCE: None
 ***************************************************************
 */
#include "ab_util.h"

/**
 * Validates a floating point argument
 * 
 * value: the value to validate
 * returnLoc: a pointer to the return location
 * 
 * Returns: 0 on success, otherwise 1.
*/
int validate_float_arg(char* value, float* returnLoc) {
	*returnLoc = strtof(value, NULL);
	if (*returnLoc == (float)0 && value[0] != '0') {
		// Invalid input
		return 1;
	}
	return 0;
}

/**
 * Validates an integer argument
 * 
 * value: the value to validate
 * returnLoc: a pointer to the return location
 * 
 * Returns: 0 on success, otherwise 1.
*/
int validate_int_arg(char* value, int* returnLoc) {
	long res = strtol(value, NULL, 10);
	if (res == (long)0 && value[0] != '0') {
		// Invalid input
		return 1;
	}

	if (res > 255) {
		return 2;
	}

	*returnLoc = (int)res;
	return 0;
}

/**
 * Validates a provided binary command line argument
 * 
 * value: the character to validate
 * 
 * Returns: 0 if value is 0, 1 if value is 1, 2 on error.
*/
int validate_binary_arg(char value) {
	if (value == '0') {
		return 0;
	} else if (value == '1') {
		return 1;
	} else {
		return 2;
	}
}

/**
 * Gets a binary mask from a mask string
 * 
 * mask: a ptr to store the resulting mask
 * value: a string mask. E.g. "0010"
 * length: the length of the target mask E.g. 4
 * 
 * Returns: 0 on success, otherwise 1.
*/
uint8_t get_binary_mask(uint8_t* mask, char *value, uint8_t length) {
	// Convert Argv to byte
	int len = strlen(value);
	if (len > length) {
		return 1;
	}
	
	for (int i = len - 1; i >= 0; i--) {
		uint8_t ret = validate_binary_arg(value[i]);
		if (ret == 2) {
			return 1;
		}

		*mask |= (ret << (len - (i + 1)));
	}
	return 0;
}

/**
 * Validates a device id argument.
 * 
 * did: device id to verify
 * 
 * Result: 0 if valid, 1 otherwise.
*/
int validate_device_id(uint8_t did) {
	if (did == DID_TEMP || did == DID_HUM || did == DID_AP || did == DID_TVOC) {
		return 0;
	}
	return 1;
}


/**
 * Validates a provided filename arguments
 * 
 * fileName: filename being validated
 * 
 * Returns: 0 if valid. 1 if the filename is too long. 2 if the filename is invalid. 3 if the extension is invalid.
 * 
*/
int validate_file_name(char* fileName) {
	int len = strlen(fileName);
	if (len >= FILE_NAME_MAX_LEN) {
		// Invalid Length
		return 1; 
	}

	int alpha = 0, decimalChar = 0, extension  = 0;
	for (int i = 0; i < len; i++) {
		if (fileName[i] == '.') {
			// Decimal point
			if (decimalChar) {
				// Two decimal points detected
				return 2; // Invalid filename
			}
			decimalChar = i + 1;
		}
	}
	alpha = decimalChar - 1;
	extension = len - decimalChar;
	if (alpha > 5) {
		return 1; // Filename too long
	}

	if (extension != 3) {
		return 3; // Invalid extension
	}

	return 0;
}

/**
 * Validates an BLE Address argument
 * 
 * value: the value to validate
 * returnLoc: a pointer to the return location
 * 
 * Returns: 0 on success, otherwise 1.
*/
int validate_ble_addr(char* value, bt_addr_le_t* returnLoc) {
	int res = bt_addr_le_from_str(value, "random-id", returnLoc);
	if (res < 0) {
		return 1;
	}
	return 0;
}
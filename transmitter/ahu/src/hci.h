 /** 
 **************************************************************
 * @file src/hci.h
 * @author Alexander Burovanov - 46990480
 * @date 01052023
 * @brief Host Controller Communication Protocol
 * REFERENCE: csse4011_prac1_hci.pdf 
 ***************************************************************
 */
#ifndef COMMS_H_
#define COMMS_H_

#include <stdint.h>
#include <zephyr/drivers/uart.h>
#define UART_MODULE_ENABLED

// Packet Type
#define PACKET_REQ 0x01
#define PACKET_RES 0x02
#define PACKET_PRE 0xAA

// Command Types
#define CMD_POINT 0x01
#define CMD_CIRCLE 0x02
#define CMD_LJ 0x03
#define CMD_DAC 0x04
#define CMD_GLED 0x05
#define CMD_GPB 0x06
#define CMD_GRAPH 0x07 // Draw graph plot on GCU
#define CMD_METER 0x08 // Draw meter on GCU
#define CMD_NUMERIC 0x09 // Draw SSD value on GCU
#define CMD_REC 0x10 // Start/Stop Recording
#define CMD_SENSOR 0x11 // Sensor Data

// Device IDs
#define DID_LEDS 1
#define DID_PB 2
#define DID_DAC 3
#define DID_LJP 4
#define DID_TEMP 5 // Temperature Sensor
#define DID_HUM 6 // Humidity Sensor
#define DID_AP 7 // Air Pressure Sensor
#define DID_TVOC 8 // Organic Compound Sensor
#define DID_SD 13 // SD Card Writer
#define DID_RSSI 9 // RSSI Mobile Node

// iBeacon Node Names
#define IBEACON_CSSE_4011_A 1
#define IBEACON_CSSE_4011_B 2
#define IBEACON_CSSE_4011_C 3
#define IBEACON_CSSE_4011_D 4
#define IBEACON_CSSE_4011_E 5
#define IBEACON_CSSE_4011_F 6
#define IBEACON_CSSE_4011_G 7
#define IBEACON_CSSE_4011_H 8
#define IBEACON_CSSE_4011_I 9
#define IBEACON_CSSE_4011_J 10
#define IBEACON_CSSE_4011_K 11
#define IBEACON_CSSE_4011_L 12

// iBeacon Addresses
const static char* CSSE_4011_A_STR = "F5:75:FE:85:34:67";
const static char* CSSE_4011_B_STR = "E5:73:87:06:1E:86";
const static char* CSSE_4011_C_STR = "CA:99:9E:FD:98:B1";
const static char* CSSE_4011_D_STR = "CB:1B:89:82:FF:FE";
const static char* CSSE_4011_E_STR = "D4:D2:A0:A4:5C:AC";
const static char* CSSE_4011_F_STR = "C1:13:27:E9:B7:7C";
const static char* CSSE_4011_G_STR = "F1:04:48:06:39:A0";
const static char* CSSE_4011_H_STR = "CA:0C:E0:DB:CE:60";
const static char* CSSE_4011_I_STR = "D4:7F:D4:7C:20:13";
const static char* CSSE_4011_J_STR = "F7:0B:21:F1:C8:E1";
const static char* CSSE_4011_K_STR = "FD:E0:8D:FA:3E:4A";
const static char* CSSE_4011_L_STR = "EE:32:F7:28:FA:AC";

// Response Types
#define RES_OK 0x01
#define RES_FAIL 0x02

// PB States
#define PB_ON 0x01
#define PB_OFF 0x02

// File Name Length
#define FILE_NAME_MAX_LEN 10 // Including '\n' character
#define GCU_REC_S 0x01 // Start SD Card Recording
#define GCU_REC_P 0x02 // Stop SD Card Recording
extern char fileNameG[FILE_NAME_MAX_LEN]; // File Name Placeholder

// BLE MACROS
#define IBEACON_MAJOR_IDX 25
#define IBEACON_MINOR_IDX 27

// THINGY52 Modes
#define SENSOR_MODE 1
#define RANGING_MODE 2
const static uint8_t mode = RANGING_MODE;

// Packet & Associated Data Types
/**
 * A HCI data packet.
*/
typedef struct __attribute__((__packed__)) {
    uint8_t preamble;
    uint8_t typeAndLength;
    uint8_t command;
    uint8_t* data; // Note flatten this out of the struct before sending via uart
} Packet;

/**
 * A  HCI data packet which does not point to data contents - suitable for uart transmission.
*/
typedef struct __attribute__((__packed__)) {
    uint8_t preamble;
    uint8_t typeAndLength;
    uint8_t command;
} StrippedPacket;

/**
 * A XY data packet
*/
typedef struct __attribute__((__packed__)) {
    float x;
    float y;
} XYData;

/**
 * A Point data packet
*/
typedef XYData PointData;

/**
 * A DAC data packet
*/
typedef XYData DacData;

/**
 * A Circle data packet
*/
typedef struct __attribute__((__packed__)) {
    float r;
    float x;
    float y;
} CircleData;

/**
 * A Lissajous data packet
*/
typedef struct __attribute__((__packed__)) {
    float a;
    float b;
    float t;
} LissajousData;

/**
 * A RGB data packet
*/
typedef struct __attribute__((__packed__)) {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} RGBData;

/**
 * A DeviceId data packet
*/
typedef struct __attribute__((__packed__)) {
    uint8_t deviceId;
} DeviceIdData;

/**
 * A Sensor data packet
*/
typedef struct __attribute__((__packed__)) {
    uint8_t deviceId;
    float data;
} SensorData;

/**
 * A RSSI data packet
*/
typedef struct __attribute__((__packed__)) {
    uint8_t deviceId;
    uint8_t beacon;
    int8_t rssi;
} RSSIData;

/**
 * SD Recording data packet
*/
typedef struct __attribute__((__packed__)) {
    uint8_t cmd;
    uint8_t deviceId;
    uint8_t fileName[FILE_NAME_MAX_LEN];
} RecData;

/**
 * A generic response packet
*/
typedef struct __attribute__((__packed__)) {
    uint8_t resCode;
} GeneralResponse;

/**
 * A push button state response packet
*/
typedef struct __attribute__((__packed__)) {
    GeneralResponse status;
    uint8_t state;
} PBResponse;

// Function Definitions
/**
 * Combines the type and data length arguments into a single byte.
 * 
 * type: the packet type
 * length: the length of the packet data
 * 
 * Returns: the combined byte
*/
extern uint8_t combine_type_and_length(uint8_t type, uint8_t length);

/**
 * Determines the size of the data contents based on the command.
 * 
 * cmd: the provided command
 * 
 * Returns: the size of the data contents associated to the command. 0 if no command found.
*/
extern uint8_t determine_contents_size(uint8_t cmd);

/**
 * Prints the data contents of each command
 * 
 * cmd: the command associated to the data
 * data: the data to print
 * 
 * Returns: void
*/
extern void print_contents(uint8_t cmd, uint8_t* data);

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
extern void send_uart_packet(uint8_t preamble, uint8_t packetType, uint8_t command, uint8_t* data);

/**
 * Receives and processes a packet from UART.
 * 
 * buffer: the buffer of received bytes
 * 
 * Returns: a ptr to a packet
 * NOTE: this function will allocate memory for the data contents. It is the responsibility
 *       of the caller to free this memory after use by calling `k_free()`.
*/
extern Packet receive_uart_packet(uint8_t* buffer);
#endif

#endif
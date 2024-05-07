 /** 
 **************************************************************
 * @file src/ir_transmitter_module.h
 * @author Alexander Burovanov - 46990480
 * @date 07/05/2024
 * @brief IR Transmitter Driver
 * REFERENCE: none
 ***************************************************************
 */
#ifndef AB_IR_TRANS_MODULE_H_
#define AB_IR_TRANS_MODULE_H_
#include <stdint.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>

// IR Transmitter Setup
#define IR_TRANS_NODE DT_ALIAS(ir_trans)
static const struct device *const ir_trans_dev = DEVICE_DT_GET(IR_TRANS_NODE);

extern int init_ir_transmitter();

#endif
 /** 
 **************************************************************
 * @file src/ir_receiver_module.h
 * @author Alexander Burovanov - 46990480
 * @date 04/05/2024
 * @brief IR Receiver Driver
 * REFERENCE: none
 ***************************************************************
 */
#ifndef AB_IR_REC_MODULE_H_
#define AB_IR_REC_MODULE_H_
#include <stdint.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>

// IR Receiver Setup
#define IR_REC_NODE DT_ALIAS(ir_rec)
static const struct device *const ir_rec_dev = DEVICE_DT_GET(IR_REC_NODE);

extern int init_ir_receiver();

#endif
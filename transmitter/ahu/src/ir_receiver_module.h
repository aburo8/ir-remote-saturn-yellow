#ifndef AB_IR_REC_MODULE_H_
#define AB_IR_REC_MODULE_H_
#include <stdint.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>

// UART Setup
#define IR_REC_NODE DT_ALIAS(ir_rec)
static const struct device *const ir_rec_dev = DEVICE_DT_GET(IR_REC_NODE);

extern int init_ir_receiver();

#endif
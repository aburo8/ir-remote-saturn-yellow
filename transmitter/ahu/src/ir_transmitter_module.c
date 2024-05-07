 /** 
 **************************************************************
 * @file src/ir_transmitter_module.c
 * @author Alexander Burovanov - 46990480
 * @date 07/05/2024
 * @brief IR Transmitter Driver
 * REFERENCE: none
 ***************************************************************
 */
#include "ir_transmitter_module.h"
#include <stdio.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/logging/log.h>

// Init Logging Module
LOG_MODULE_REGISTER(ir_transmitter_module);

// Define the GPIO pin connected to the k851262 transmitter output
#define ZEPHYR_USER_NODE DT_PATH(zephyr_user)
#define TRANSMITTER_GPIO_DEV_NAME "&k851262_gpio_pin"
#define TRANSMITTER_GPIO_PIN 26

static const struct gpio_dt_spec ir_transmit = GPIO_DT_SPEC_GET(ZEPHYR_USER_NODE, ts1838_gpios);

/**
 * Initialises the IR transmitter
 * 
 * Returns: 0 on success
 * 
*/
int init_ir_transmitter() {

    uint8_t ret = 0;

    // Configure GPIO pin
	if (!gpio_is_ready_dt(&ir_transmit)) {
        LOG_ERR("Failed to initalise TS1838!");
        return 1;
	}
    ret = ret + gpio_pin_configure_dt(&ir_transmit, GPIO_INPUT);
    if (ret > 0) {
        LOG_ERR("Failed to initalise LEDS!");
        return 1;
    }

    // Get the GPIO device	
    const struct device *gpio_dev = ir_trans_dev;
    if (!gpio_dev) {
        printk("Could not get GPIO device\n");
        return -ENODEV;
    }
    // struct gpio_callback gpio_cb;

    // // Set up a callback for IR signal detection
    // gpio_init_callback(&gpio_cb, ir_signal_callback, BIT(TS1838_GPIO_PIN));
    // ret = gpio_add_callback(gpio_dev, &gpio_cb);west flash
    
    // if (ret < 0) {
    //     LOG_ERR("Failed to set up callback: %d", ret);
    //     return ret;
    // }

    // // Enable interrupt on rising edge (or falling edge, depending on IR sensor)
    // ret = gpio_pin_interrupt_configure_dt(&ir_transmit, GPIO_INT_EDGE_FALLING);
    // if (ret < 0) {
    //     LOG_ERR("Failed to configure interrupt: %d", ret);
    //     return ret;
    // }

    // Wait for the IR signal to stabilize
    LOG_INF("k851262 IR Transmitter initialized");

    return 0;
}

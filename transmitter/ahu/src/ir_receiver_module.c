 /** 
 **************************************************************
 * @file src/ir_receiver_module.c
 * @author Alexander Burovanov - 46990480
 * @date 04/05/2024
 * @brief IR Receiver Driver
 * REFERENCE: none
 ***************************************************************
 */
#include "ir_receiver_module.h"
#include <stdio.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/logging/log.h>

// Init Logging Module
LOG_MODULE_REGISTER(ir_receiver_module);

// Define the GPIO pin connected to the TS1838 sensor output
#define ZEPHYR_USER_NODE DT_PATH(zephyr_user)
#define TS1838_GPIO_DEV_NAME "&ts1838_gpio_pin"
#define TS1838_GPIO_PIN 27
#define TS1838_SIGNAL_STABILIZATION_TIME_MS 50

static const struct gpio_dt_spec ir_rec = GPIO_DT_SPEC_GET(ZEPHYR_USER_NODE, ts1838_gpios);

static void ir_signal_callback(const struct device *dev, struct gpio_callback *cb,
                               uint32_t pins)
{
    // Handle IR signal detection here
    LOG_INF("IR signal detected!");
}

int init_ir_receiver() {

    uint8_t ret = 0;

    // Configure GPIO pin
	if (!gpio_is_ready_dt(&ir_rec)) {
        LOG_ERR("Failed to initalise TS1838!");
        return 1;
	}
    ret = ret + gpio_pin_configure_dt(&ir_rec, GPIO_INPUT);
    if (ret > 0) {
        LOG_ERR("Failed to initalise LEDS!");
        return 1;
    }

    // Get the GPIO device	
    const struct device *gpio_dev = ir_rec_dev;
    if (!gpio_dev) {
        printk("Could not get GPIO device\n");
        return -ENODEV;
    }
    struct gpio_callback gpio_cb;

    // Set up a callback for IR signal detection
    gpio_init_callback(&gpio_cb, ir_signal_callback, BIT(TS1838_GPIO_PIN));
    ret = gpio_add_callback(gpio_dev, &gpio_cb);
    if (ret < 0) {
        LOG_ERR("Failed to set up callback: %d", ret);
        return ret;
    }

    // Enable interrupt on rising edge (or falling edge, depending on IR sensor)
    ret = gpio_pin_interrupt_configure_dt(&ir_rec, GPIO_INT_EDGE_BOTH);
    if (ret < 0) {
        LOG_ERR("Failed to configure interrupt: %d", ret);
        return ret;
    }

    // Wait for the IR signal to stabilize
    k_msleep(TS1838_SIGNAL_STABILIZATION_TIME_MS);

    LOG_INF("TS1838 IR receiver initialized");

    return 0;
}

int ts1838_read(const struct device *dev, uint32_t *data, uint8_t pinNumber) {
    // Read GPIO pin state
    const struct device *gpio_dev = dev;
    if (!gpio_dev) {
        printk("Could not get GPIO device\n");
        return -ENODEV;
    }

    int value = gpio_pin_get(gpio_dev, pinNumber);
    if (value < 0) {
        printk("Failed to read GPIO pin (%d)\n", value);
        return value;
    }

    *data = (uint32_t)value;

    return 0;
}

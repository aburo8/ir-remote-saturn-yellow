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

// Define IR signal state and data structures
static uint32_t ir_data = 0;
static uint16_t pulseCount = 0;
static uint8_t timerMs = 0;

#define TIMER_TIMEOUT 150 // The timer is automatically stopped if it ticks for more than 150ms

// Function Prototypes
void increment_timer(struct k_work *work);

// System worker thread to execute timer operations
K_WORK_DEFINE(my_work, increment_timer);

/**
 * Timer handler which triggers when the timer expires
 * Calls increment_timer to perform the counting operation
 * 
 * Returns: void
 * 
*/
static void ir_timer_step_handler(struct k_timer *timer_id) {
    k_work_submit(&my_work);
}

/**
 * Resets the timer when it is stopped
 * 
 * Returns: void
 * 
*/
static void ir_timer_stop_handler(struct k_timer *timer_id) {
    // If the timer times out then reset the pulse count
    pulseCount = 0;
    timerMs = 0;
    LOG_INF("Timer Stopped");
}

// IR timeout timer to track the time differences between IR pulses
K_TIMER_DEFINE(ir_timeout_timer, ir_timer_step_handler, ir_timer_stop_handler);

/**
 * Increments the ir_timeout_timer
 * 
 * Returns: void
*/
void increment_timer(struct k_work *work)
{
    if (timerMs >= TIMER_TIMEOUT) {
        LOG_INF("Timer Timed Out");
        k_timer_stop(&ir_timeout_timer);
    }
    timerMs++;
}

/**
 * Checks to see if the provided pulse is a data bit
 * 
 * Returns: True if the pulse is a data pulse, False otherwise
 * 
*/
static bool is_bit_pulse(uint16_t pulse) {
    return 3 <= pulse && pulse <= 34;
}

/**
 * Checks to see if the provided pulse is the end of a message
 * 
 * Returns: True if the message is complete, False otherwise
 * 
*/
static bool is_message_pulse(uint16_t pulse) {
    return pulse == 34;
}

/**
 * GPIO Callback function - executes on falling GPIO falling edge triggers
 * 
 * Returns: void
 * 
*/
static void ir_signal_callback(const struct device *dev, struct gpio_callback *cb, uint32_t pins) {
    // Check if the GPIO pin triggered the callback
    if (pins & BIT(TS1838_GPIO_PIN)) {
        // Read IR Receiver Pin
        int pin_value = gpio_pin_get(dev, TS1838_GPIO_PIN);
        if (pin_value < 0) {
            LOG_ERR("Error reading GPIO pin: %d", pin_value);
            return;
        }
        pulseCount++;

        // Check if the current falling edge is a bit pulse
        if (is_bit_pulse(pulseCount)) {
            // Decode Bit Value
            ir_data <<= 1;
            printk("Pulse Count: %d, Timer: %d\n", pulseCount, timerMs);
            ir_data += (timerMs >= 2) ? 1 : 0;
        }

        // Measure
        if (is_message_pulse(pulseCount)) {
            // TODO: save to a queue/send to PC
            k_timer_stop(&ir_timeout_timer);
            LOG_INF("IR Data 0x%x", ir_data);
        }

        timerMs = 0;
        k_timer_start(&ir_timeout_timer, K_MSEC(1), K_MSEC(1));
    }
}

/**
 * Initialises the IR Receiver
 * 
 * Returns: 0 on success
 * 
*/
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
    ret = gpio_pin_interrupt_configure_dt(&ir_rec, GPIO_INT_EDGE_FALLING);
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

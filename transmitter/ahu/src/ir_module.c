 /** 
 **************************************************************
 * @file src/ir_module.c
 * @author Alexander Burovanov - 46990480
 * @date 04/05/2024
 * @brief IR RX/TX Driver
 * REFERENCE: none
 ***************************************************************
 */
#include "ir_module.h"
#include <stdio.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/logging/log.h>
#include "hci.h"

// Init Logging Module
LOG_MODULE_REGISTER(ir_module, 4);

// Define the GPIO pins connected to RX/TX
#define ZEPHYR_USER_NODE DT_PATH(zephyr_user)
#define IR_RX_GPIO_PIN 27
#define IR_TX_GPIO_PIN 26
#define TS1838_SIGNAL_STABILIZATION_TIME_MS 50
static const struct gpio_dt_spec ir_rx_pin = GPIO_DT_SPEC_GET(ZEPHYR_USER_NODE, ts1838_gpios);
static const struct gpio_dt_spec ir_tx_pin = GPIO_DT_SPEC_GET(ZEPHYR_USER_NODE, k851262_gpios);

// Define IR RX signal state and data structures
static uint32_t ir_data = 0;
static uint16_t pulseCount = 0;
static uint8_t rxTimerMs = 0;
static float txTimerUs = 0;

#define RX_TIMER_TIMEOUT 150 // The timer is automatically stopped if it ticks for more than 150ms
#define TX_TIMER_TIMEOUT 68 * 1000 * 1000 // (68ms => ns)
// IR Transmit transmission message queue
K_MSGQ_DEFINE(ir_transmit_q, sizeof(IRData), 10, 1);

// Used to extern the uart msgq for use in other threads
struct k_msgq* ir_transmit_q_extern = &ir_transmit_q;

// Function Prototypes
void increment_rx_timer(struct k_work *work);
void increment_tx_timer(struct k_work *work);

// System worker thread to execute timer operations
K_WORK_DEFINE(rx_timer_work, increment_rx_timer);
K_WORK_DEFINE(tx_timer_work, increment_tx_timer);

/**
 * Timer handler which triggers when the timer expires
 * Calls increment_rx_timer to perform the counting operation
 * 
 * Returns: void
 * 
*/
static void ir_rx_timer_step_handler(struct k_timer *timer_id) {
    k_work_submit(&rx_timer_work);
}

/**
 * Resets the timer when it is stopped
 * 
 * Returns: void
 * 
*/
static void ir_rx_timer_stop_handler(struct k_timer *timer_id) {
    // If the timer times out then reset the pulse count
    pulseCount = 0;
    rxTimerMs = 0;
    LOG_INF("Timer Stopped");
}

/**
 * Timer handler which triggers when the timer expires
 * Calls increment_rx_timer to perform the counting operation
 * 
 * Returns: void
 * 
*/
static void ir_tx_timer_step_handler(struct k_timer *timer_id) {
    k_work_submit(&tx_timer_work);
}

/**
 * Resets the timer when it is stopped
 * 
 * Returns: void
*/
static void ir_tx_timer_stop_handler(struct k_timer *timer_id) {
    txTimerUs = 0;
    LOG_INF("Tx Timer Stopped");
}

// IR timeout timer to track the time differences between IR pulses
K_TIMER_DEFINE(ir_rx_timeout_timer, ir_rx_timer_step_handler, ir_rx_timer_stop_handler);
K_TIMER_DEFINE(ir_tx_timeout_timer, ir_tx_timer_step_handler, ir_tx_timer_stop_handler);

/**
 * Increments the ir_rx_timeout_timer
 * 
 * Returns: void
*/
void increment_rx_timer(struct k_work *work)
{
    if (rxTimerMs >= RX_TIMER_TIMEOUT) {
        LOG_INF("Timer Timed Out");
        k_timer_stop(&ir_rx_timeout_timer);
    }
    rxTimerMs++;
}

/**
 * Increments the ir_tx_timeout_timer
 * 
 * Returns: void
*/
void increment_tx_timer(struct k_work *work)
{
    // if (timerMs >= TX_TIMER_TIMEOUT) {
    //     LOG_INF("Timer Timed Out");
    //     k_timer_stop(&ir_rx_timeout_timer);
    // }
    txTimerUs += 0.5;
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
    if (pins & BIT(IR_RX_GPIO_PIN)) {
        // Read IR Receiver Pin
        int pin_value = gpio_pin_get(dev, IR_RX_GPIO_PIN);
        if (pin_value < 0) {
            LOG_ERR("Error reading GPIO pin: %d", pin_value);
            return;
        }
        pulseCount++;

        // Check if the current falling edge is a bit pulse
        if (is_bit_pulse(pulseCount)) {
            // Decode Bit Value
            ir_data <<= 1;
            printk("Pulse Count: %d, Timer: %d\n", pulseCount, rxTimerMs);
            ir_data += (rxTimerMs >= 2) ? 1 : 0;
        }

        // Measure
        if (is_message_pulse(pulseCount)) {
            // TODO: save to a queue/send to PC
            k_timer_stop(&ir_rx_timeout_timer);
            LOG_INF("IR Data 0x%x", ir_data);
	        k_msgq_put(&ir_transmit_q, &ir_data, K_FOREVER);
        }

        rxTimerMs = 0;
        k_timer_start(&ir_rx_timeout_timer, K_MSEC(1), K_MSEC(1));
    }
}

/**
 * Initialises the IR Rx & Tx
 * 
 * Returns: 0 on success
 * 
*/
int init_ir_module() {

    uint8_t ret = 0;

    // Configure Receiver
    // Configure RX GPIO pin
	if (!gpio_is_ready_dt(&ir_rx_pin)) {
        LOG_ERR("Failed to initialise TS1838!");
        return 1;
	}
    ret = ret + gpio_pin_configure_dt(&ir_rx_pin, GPIO_INPUT);
    if (ret > 0) {
        LOG_ERR("Failed to initalise LEDS!");
        return 1;
    }

    // Get the GPIO device
    const struct device *gpio_dev = ir_dev;
    if (!gpio_dev) {
        printk("Could not get GPIO device\n");
        return -ENODEV;
    }
    struct gpio_callback gpio_cb;

    // Set up a callback for IR signal detection
    gpio_init_callback(&gpio_cb, ir_signal_callback, BIT(IR_RX_GPIO_PIN));
    ret = gpio_add_callback(gpio_dev, &gpio_cb);
    if (ret < 0) {
        LOG_ERR("Failed to set up callback: %d", ret);
        return ret;
    }

    // Enable interrupt on rising edge (or falling edge, depending on IR sensor)
    ret = gpio_pin_interrupt_configure_dt(&ir_rx_pin, GPIO_INT_EDGE_FALLING);
    if (ret < 0) {
        LOG_ERR("Failed to configure interrupt: %d", ret);
        return ret;
    }

    // Configure Transmitter
    // Configure Tx GPIO pin
	if (!gpio_is_ready_dt(&ir_tx_pin)) {
        LOG_ERR("Failed to initialise IR transmitter!");
        return 1;
	}
    ret = ret + gpio_pin_configure_dt(&ir_tx_pin, GPIO_OUTPUT_ACTIVE | GPIO_OPEN_DRAIN | GPIO_OUTPUT_LOW);
    if (ret > 0) {
        LOG_ERR("Failed to initialise IR transmitter!");
        return 1;
    }

    // Wait for the IR rx signal to stabilize
    k_msleep(TS1838_SIGNAL_STABILIZATION_TIME_MS);

    LOG_DBG("IR RX & TX initialised!");

    return 0;
}

#define NEC_HEADER_HIGH_US 9000 - 87 
#define NEC_HEADER_LOW_US 4500 - 87
#define NEC_BIT_HIGH_US 560 - 87
#define NEC_BIT_ONE_LOW_US 1990 - 87
#define NEC_BIT_ZERO_LOW_US 560 - 87

void ir_transmit_pulse(uint32_t highDurationUs, uint32_t lowDurationUs) {
    const struct device *gpio_dev = DEVICE_DT_GET(DT_ALIAS(ir_tx));
    // Check IR Device is ready
	if (!device_is_ready(gpio_dev)) {
		LOG_ERR("IR device not found!");
		return;
	}

    gpio_pin_configure(gpio_dev, 26, GPIO_OUTPUT_ACTIVE);

    gpio_pin_set(gpio_dev, 26, 1);
    k_sleep(K_USEC(highDurationUs));
    gpio_pin_set(gpio_dev, 26, 0);
    k_sleep(K_USEC(lowDurationUs));
}

int transmit_ir_packet(IRData irData) {
    // Transmit an NEC Packet
    switch (irData.protocol) {
        case IR_PROTO_NEC:
            /**
             * The NEC protocol consists of the following
             * 1. 9ms leading high
             * 2. 4.5ms low
             * 3. 8-bit address
             * 4. 8-bit logical inverse address
             * 5. 8-bit command
             * 6. 8-bit logical inverse commands
             * 7. Final 562.5us pulse
             * 
             * Logical 0 = 562.5us pulse followed by 562.5us space
             * Logical 1 = 562.5us pulse burst followed by a 1.6875ms pulse space
            */
            // Transmit the header
            LOG_INF("NEC PROTOCOL IDENTIFIED");
            ir_transmit_pulse(NEC_HEADER_HIGH_US, NEC_HEADER_LOW_US);

            // Transmit Data
            for (int i = 31; i >= 0; i--) {
                uint32_t bit = (irData.data >> i) & 0x01;
                printk("%x\n", bit);
                if (bit) {
                    // Transmit a logical 1
                    ir_transmit_pulse(NEC_BIT_HIGH_US, NEC_BIT_ONE_LOW_US);
                } else {
                    // Transmit a logical 0
                    ir_transmit_pulse(NEC_BIT_HIGH_US, NEC_BIT_ZERO_LOW_US);
                }
            }

            // const struct device *gpio_dev = DEVICE_DT_GET(DT_ALIAS(ir_tx));
            // Check IR Device is ready
            // if (!device_is_ready(gpio_dev)) {
            // 	LOG_ERR("IR device not found!");
            // 	return;
            // }
            // // gpio_pin_configure(gpio_dev, 26, GPIO_OUTPUT_ACTIVE);
            // gpio_pin_set(gpio_dev, 26, 1);
            // k_sleep(K_USEC(1000000));
            // gpio_pin_set(gpio_dev, 26, 0);
            // // Start the transmission timer
            // bool timerActive = true;
            // k_timer_start(&ir_tx_timeout_timer, K_NSEC(500), K_NSEC(500)); // Timer should fire every 500ns
            // while (timerActive) {
            //     // Implement each of the phases
            //     if (txTimerUs < 9000) {
            //         // Hold Output Pin High
            //         gpio_pin_set_dt(&ir_tx_pin, 1);
            //     } else if (txTimerUs >= 9000 && txTimerUs < 13500) {
            //         gpio_pin_set_dt(&ir_tx_pin, 0);
            //     } else {
            //         timerActive = false;
            //     }
            // } 
            // k_timer_stop(&ir_tx_timeout_timer);
            // gpio_pin_set_dt(&ir_tx_pin, 0);
            break;
        default:
            LOG_ERR("IR Protocol Not Identified!");
            break;
    }

    LOG_DBG("Message Transmitted!");
    return 0;
}

int ir_transmission_handler() {
	// Init Delay
	k_sleep(K_MSEC(200));

    // Check IR Device is ready
	if (!device_is_ready(ir_dev)) {
		LOG_ERR("IR device not found!");
		return 0;
	}

    // Transmit Incoming Messages
    IRData message;
    while (k_msgq_get(&ir_transmit_q, &message, K_FOREVER) == 0) {
        // Transmit the message
        uint8_t ret;
        IRData irdata = {IR_PROTO_NEC, 0xf7a05f};
        ret = transmit_ir_packet(irdata);
    }
    return 0;
}

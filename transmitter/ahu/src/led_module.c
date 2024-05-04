 /** 
 **************************************************************
 * @file src/led_module.c
 * @author Alexander Burovanov - 46990480
 * @date 01052023
 * @brief LED Controller
 * REFERENCE: csse4011_prac1_hci.pdf 
 ***************************************************************
 */
#include <stdio.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/logging/log.h>

// Init Logging Module
LOG_MODULE_REGISTER(led_module);

// The devicetree node identifiers for the LED aliases.
#define LED0_NODE DT_ALIAS(led0)
#define LED1_NODE DT_ALIAS(led1)
#define LED2_NODE DT_ALIAS(led2)
#define LED3_NODE DT_ALIAS(led3)

// LED GPIO Structs
static const struct gpio_dt_spec led0 = GPIO_DT_SPEC_GET(LED0_NODE, gpios);
static const struct gpio_dt_spec led1 = GPIO_DT_SPEC_GET(LED1_NODE, gpios);
static const struct gpio_dt_spec led2 = GPIO_DT_SPEC_GET(LED2_NODE, gpios);
static const struct gpio_dt_spec led3 = GPIO_DT_SPEC_GET(LED3_NODE, gpios);

/**
 * Intialises the onboard device LEDs
 * 
 * Returns: 0 on success, otherise 1.
*/
int init_leds() {
    uint8_t ret = 0;

	if (!gpio_is_ready_dt(&led0) && !gpio_is_ready_dt(&led1) && !gpio_is_ready_dt(&led2) && !gpio_is_ready_dt(&led3)) {
        LOG_ERR("Failed to initalise LEDS!");
        return 1;
	}

    ret = ret + gpio_pin_configure_dt(&led0, GPIO_OUTPUT_ACTIVE);
    ret = ret + gpio_pin_configure_dt(&led1, GPIO_OUTPUT_ACTIVE);
    ret = ret + gpio_pin_configure_dt(&led2, GPIO_OUTPUT_ACTIVE);
    ret = ret + gpio_pin_configure_dt(&led3, GPIO_OUTPUT_ACTIVE);
    if (ret > 0) {
        LOG_ERR("Failed to initalise LEDS!");
        return 1;
    }
    
    // Toggle LEDs off
    gpio_pin_set_dt(&led0, 0);
    gpio_pin_set_dt(&led1, 0);
    gpio_pin_set_dt(&led2, 0);
    gpio_pin_set_dt(&led3, 0);

    LOG_DBG("Led init OK");

    return 0;
}

/**
 * Sets the onboard device LEDs based on the provided LED Mask
 * 
 * mask: the set mask. E.g 0b1110 would set LEDs 1-3 on, and LED4 off.
 * 
 * Returns: 0 upon successful set, otherwise 1.
*/
int set_leds(uint8_t mask) {
    // Check LED mask is only 4-bits
    if (mask > 0xF) {
        LOG_ERR("Invalid LED Mask Provided!");
        return 1;
    }

	if (!gpio_is_ready_dt(&led0) && !gpio_is_ready_dt(&led1) && !gpio_is_ready_dt(&led2) && !gpio_is_ready_dt(&led3)) {
		LOG_ERR("GPIO Ports Not Ready! Try again later!");
        return 1;
	}

    uint8_t ret = ((mask >> 3) & 0x1);
    if (ret == gpio_pin_get_dt(&led0)) {
        // Led 1 is already in this state
        if (ret == 1) {
            LOG_WRN("Led 1 is already set to ON!");
        } else {
            LOG_WRN("Led 1 is already set to OFF!");
        }
    }
    
    ret = ((mask >> 2) & 0x1);
    if (ret == gpio_pin_get_dt(&led1)) {
        // Led 2 is already in this state
        if (ret == 1) {
            LOG_WRN("Led 2 is already set to ON!");
        } else {
            LOG_WRN("Led 2 is already set to OFF!");
        }
    }

    ret = ((mask >> 1) & 0x1);
    if (ret == gpio_pin_get_dt(&led2)) {
        // Led 3 is already in this state
        if (ret == 1) {
            LOG_WRN("Led 3 is already set to ON!");
        } else {
            LOG_WRN("Led 3 is already set to OFF!");
        }
    }

    ret = ((mask >> 0) & 0x1);
    if (ret == gpio_pin_get_dt(&led3)) {
        // Led 4 is already in this state
        if (ret == 1) {
            LOG_WRN("Led 4 is already set to ON!");
        } else {
            LOG_WRN("Led 4 is already set to OFF!");
        }
    }

    // Set LEDs
    gpio_pin_set_dt(&led0, ((mask >> 3) & 0x1));
    gpio_pin_set_dt(&led1, ((mask >> 2) & 0x1));
    gpio_pin_set_dt(&led2, ((mask >> 1) & 0x1));
    gpio_pin_set_dt(&led3, ((mask >> 0) & 0x1));

    return 0;
}

/**
 * Toggles the onboard device LEDs based on the provided LED Mask
 * 
 * mask: the toggle mask. E.g 0b1110 would toggle LEDs 1-3
 * 
 * Returns: 0 upon successful toggle, otherwise 1.
*/
int toggle_leds(uint8_t mask) {
    // Check LED mask is only 4-bits
    if (mask > 0xF) {
        LOG_ERR("Invalid LED Mask Provided!");
        return 1;
    }

	if (!gpio_is_ready_dt(&led0) && !gpio_is_ready_dt(&led1) && !gpio_is_ready_dt(&led2) && !gpio_is_ready_dt(&led3)) {
		LOG_ERR("GPIO Ports Not Ready! Try again later!");
        return 1;
	}
    
    if (mask & 0x00) {
        LOG_WRN("No LEDS have been selected for toggling.");
    } 
    if (mask & 0x8) {
        // Toggle LED 1
        gpio_pin_toggle_dt(&led0);
    } 
    if (mask & 0x4) {
        // Toggle LED 2
        gpio_pin_toggle_dt(&led1);
    }
    if (mask & 0x2) {
        // Toggle LED 3
        gpio_pin_toggle_dt(&led2);
    }
    if (mask & 0x1) {
        // Toggle LED 4
        gpio_pin_toggle_dt(&led3);
    }

    return 0;
}
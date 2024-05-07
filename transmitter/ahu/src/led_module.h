 /** 
 **************************************************************
 * @file src/led_module.h
 * @author Alexander Burovanov - 46990480
 * @date 01052023
 * @brief LED Controller
 * REFERENCE: csse4011_prac1_hci.pdf 
 ***************************************************************
 */
#ifndef AB_LED_MODULE_H_
#define AB_LED_MODULE_H_
#include <stdint.h>

/**
 * Intialises the onboard device LEDs
 * 
 * Returns: 0 on success, otherise 1.
*/
extern int init_leds();

/**
 * Sets the onboard device LEDs based on the provided LED Mask
 * 
 * mask: the set mask. E.g 0b1110 would set LEDs 1-3 on, and LED4 off.
 * 
 * Returns: 0 upon successful set, otherwise 1.
*/
extern int set_leds(uint8_t mask);

/**
 * Toggles the onboard device LEDs based on the provided LED Mask
 * 
 * mask: the toggle mask. E.g 0b1110 would toggle LEDs 1-3
 * 
 * Returns: 0 upon successful toggle, otherwise 1.
*/
extern int toggle_leds(uint8_t mask);

#endif
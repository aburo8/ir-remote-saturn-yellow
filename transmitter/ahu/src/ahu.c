 /** 
 **************************************************************
 * @file src/ahu.c
 * @author Alexander Burovanov - 46990480
 * @date 01052023
 * @brief Application Host Unit Module
 * REFERENCE: csse4011_prac1_ahu.pdf 
 ***************************************************************
 */
#include <zephyr/kernel.h>
#include <zephyr/shell/shell.h>
#include <zephyr/logging/log.h>
#include <zephyr/logging/log_ctrl.h>
#include <zephyr/drivers/uart.h>

#include "ahu.h"
#include "hci.h"
#include "uart_module.h"
#include "pc_module.h"
#include "src/pc.pb.h"
#include "ble_module.h"

// Register Logger
LOG_MODULE_REGISTER(ahu);

/* 1000 msec = 1 sec */
#define SLEEP_TIME_MS   1000

/**
 * Initialises the runtime logging levels for the project
 * 
 * Returns: 0 on exit
*/
static int initalise_log_levels(const struct device *dev) {
    ARG_UNUSED(dev);

	LogModule log_modules[] = {
		{"hci", LOG_LEVEL_INF},
        {"led_module", LOG_LEVEL_INF}
	};

	for (uint8_t i = 0; i < ARRAY_SIZE(log_modules); i++) {
		int sourceId = log_source_id_get(log_modules[i].module);
        if (sourceId < 0) {
            printk("Error: Log module %s not found\n", log_modules[i].module);
            continue;
        }
		log_filter_set(NULL, 0, sourceId, log_modules[i].level);
	}
    return 0;
}

SYS_INIT(initalise_log_levels, APPLICATION, CONFIG_APPLICATION_INIT_PRIORITY);

/**
 * AHU handler - handles the shell and interacts with the UART
 * 
 * Returns: 0 upon exit
*/
int ahu_handler(void) {
    const struct device *dev;
	uint32_t dtr = 0;

	dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_shell_uart));
	if (!device_is_ready(dev)) {
		return 0;
	}

	while (!dtr) {
		#ifdef UART_SHELL
		uart_line_ctrl_get(dev, UART_LINE_CTRL_DTR, &dtr);
		k_sleep(K_MSEC(100));
		#endif

		#ifndef UART_SHELL
		// Automatically start listening for the Thingy52
		bt_addr_le_from_str(THINGY_STR, "random", &THINGY52_ADDR);
		BLECmd cmd = {BLECON_START, THINGY52_ADDR};
		k_msgq_put(ble_receive_extern, &cmd, K_NO_WAIT);
		LOG_INF("Automatically Started Listening for Thingy52 - %s\n", THINGY_STR);
		return 0;
		#endif
	}

    return 0;
}
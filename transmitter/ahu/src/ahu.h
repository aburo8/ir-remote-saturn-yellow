 /** 
 **************************************************************
 * @file src/ahu.h
 * @author Alexander Burovanov - 46990480
 * @date 01052023
 * @brief Application Host Unit Module
 * REFERENCE: csse4011_prac1_ahu.pdf 
 ***************************************************************
 */
#ifndef AHU_H_
#define AHU_H_

// Groups a log module with an associated severity
typedef struct {
    const char* module;
    uint32_t level;
} LogModule;

// UART SHELL CONTROL
// Activate UART shell logic, otherwise default to using UART for GUI connection
// #define UART_SHELL

/**
 * AHU handler which handles the shell
 * 
 * Returns: 0 upon exit
*/
extern int ahu_handler(void);

#endif
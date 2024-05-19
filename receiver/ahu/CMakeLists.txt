# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(receiver)

list(APPEND CMAKE_MODULE_PATH ${ZEPHYR_BASE}/modules/nanopb)
include(nanopb)
zephyr_nanopb_sources(app src/pc.proto)
FILE(GLOB app_sources src/*.c)

target_sources(app PRIVATE ${app_sources})

# ORIGINAL Targets (No NanoPB)
# target_sources(app PRIVATE src/main.c)
# zephyr_sources(src/shell_commands.c)
# zephyr_sources(src/hci.c)
# zephyr_sources(src/led_module.c)
# zephyr_sources(src/uart_module.c)
# zephyr_sources(src/ahu.c)
# zephyr_sources(src/ble_module.c)
# zephyr_sources(src/gcu_shell_cmds.c)
# zephyr_sources(src/ab_util.c)
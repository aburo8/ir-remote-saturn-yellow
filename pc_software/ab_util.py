"""
A series of utility functions written by AB
"""
def bit_reverse_32_bit(hex_str):
    # Convert hex string to 32-bit binary string
    binary_str = bin(int(hex_str, 16))[2:].zfill(32)

    # Reverse the binary string
    reversed_binary_str = binary_str[::-1]

    # Convert the reversed binary string back to hex
    reversed_hex_str = hex(int(reversed_binary_str, 2))

    # Ensure the hex string has the '0x' prefix
    if len(reversed_hex_str) % 2 == 0:
        reversed_hex_str = '0x' + reversed_hex_str[2:].zfill(len(reversed_hex_str) - 2)
    else:
        reversed_hex_str = '0x' + reversed_hex_str[2:]

    return reversed_hex_str

def formatIrCode(hexString):
    formatted = bit_reverse_32_bit(hexString)

    return formatted

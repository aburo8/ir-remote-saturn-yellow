# Smart IR Software

The Smart IR PC Software is a python application which has been bundled using PyInstaller. This allows the application to be easily run as an executable.

## Building the Executable (Windows)

Within the `pc_software` directory there is a `smart_ir.spec` file. This file is used to generate the executable using the `pyinstaller` package.

To get started, first ensure you have installed all of the pre-requisite libraries to build the project -

- numpy
- paho-mqtt
- pyserial
- pyqt5
- pyinstaller
- google
- protobuf

Once installed, open a `Powershell` (or `bash` window) and navigate to the `ir-remote-saturn-yellow/pc_software` directory.

Run one of the following commands (ensure you python environment is activated) -

```bash
# To create the executable with source files extracted into a directory
pyinstaller smart_ir.spec

# To create a single file executable (which contains all source files)
pyinstaller smart_ir_onefile.spec
```

Note: that creating a single file executable will incur a longer launch time since the relevant libraries must be dynamically extracted from the executable and placed into a temporary folder when the program starts.

Once the script finishes running, a `dist` and `build` folder will appear inside the `pc_software` directory. The `dist` directory will contain the bundled executable.

## Running on Unix

To run the application on unix simply install the following python packages into your python environment -

- numpy
- paho-mqtt
- pyserial
- pyqt5
- pyinstaller
- google
- protobuf

Then run the `smart_ir.py` file.

Note: that this is a desktop application, so ensure you have a desktop manager installed on your unix distribution.

CC = gcc
CFLAGS = -I/usr/include/SDL2 -Wall -Werror -g
LDFLAGS = -lSDL2 -lm -lyaml

# Target executable name
TARGET = display.exe

# Path to the configuration file
PIPELINE_CFG = ../../configuration/pipeline.yaml
PLAYAREA_CFG = ../../configuration/playarea.yaml

# Extract configuration values from the YAML file using grep and awk
CPU_IP := $(shell grep 'CPU:' -A 1 $(PIPELINE_CFG) | grep 'IP:' | sed 's/.*"\(.*\)".*/\1/')
SNN_GPU_IP=$(shell grep 'SNN_Accelerator:' -A 15 $(PIPELINE_CFG) | grep 'GPU:' -A 1 | grep 'IP:' | sed 's/.*"\(.*\)".*/\1/')
SNN_SPINNAKER_IP=$(shell grep 'SNN_Accelerator:' -A 15 $(PIPELINE_CFG) | grep 'SpiNNaker:' -A 1 | grep 'IP:' | sed 's/.*"\(.*\)".*/\1/')
SNN_SPINNAKER_SCNN_IP=$(shell grep 'SNN_Accelerator:' -A 15 $(PIPELINE_CFG) | grep 'Convolutioner:' -A 1 | grep 'IP:' | sed 's/.*"\(.*\)".*/\1/')
SNN_SPINNAKER_MAP_IP=$(shell grep 'SNN_Accelerator:' -A 15 $(PIPELINE_CFG) | grep 'Mapper:' -A 1 | grep 'IP:' | sed 's/.*"\(.*\)".*/\1/')
SNN_SPINNAKER_PROJ_IP=$(shell grep 'SNN_Accelerator:' -A 15 $(PIPELINE_CFG) | grep 'Projector:' -A 1 | grep 'IP:' | sed 's/.*"\(.*\)".*/\1/')

VIS_RAW_PORT=$(shell grep 'Visualizers:' -A 15 $(PIPELINE_CFG) | grep 'Raw_data:' -A 1 | grep 'Port:' | sed 's/.*Port: \([0-9]*\).*/\1/')
VIS_FAST_PORT=$(shell grep 'Visualizers:' -A 15 $(PIPELINE_CFG) | grep 'Fast_SCNN:' -A 1 | grep 'Port:' | sed 's/.*Port: \([0-9]*\).*/\1/')
VIS_MEDIUM_PORT=$(shell grep 'Visualizers:' -A 15 $(PIPELINE_CFG) | grep 'Medium_SCNN:' -A 1 | grep 'Port:' | sed 's/.*Port: \([0-9]*\).*/\1/')
VIS_SLOW_PORT=$(shell grep 'Visualizers:' -A 15 $(PIPELINE_CFG) | grep 'Slow_SCNN:' -A 1 | grep 'Port:' | sed 's/.*Port: \([0-9]*\).*/\1/')


CTRL_PUCK_PORT=$(shell grep 'Controller:' -A 15 $(PIPELINE_CFG) | grep 'Puck_current:' -A 1 | grep 'Port:' | sed 's/.*Port: \([0-9]*\).*/\1/')
CTRL_PADDLE_CUR_PORT=$(shell grep 'Controller:' -A 15 $(PIPELINE_CFG) | grep 'Paddle_current:' -A 1 | grep 'Port:' | sed 's/.*Port: \([0-9]*\).*/\1/')
CTRL_PADDLE_DES_PORT=$(shell grep 'Controller:' -A 15 $(PIPELINE_CFG) | grep 'Paddle_desired:' -A 1 | grep 'Port:' | sed 's/.*Port: \([0-9]*\).*/\1/')
CTRL_PADDLE_CON_PORT=$(shell grep 'Controller:' -A 15 $(PIPELINE_CFG) | grep 'Paddle_consolidated:' -A 1 | grep 'Port:' | sed 's/.*Port: \([0-9]*\).*/\1/')


BOARD_WIDTH=$(shell grep 'Play_Area:' -A 1 $(PLAYAREA_CFG) | grep 'Width:' -A 1 | sed 's/.*Width: \([0-9]*\).*/\1/')
BOARD_HEIGHT=$(shell grep 'Play_Area:' -A 2 $(PLAYAREA_CFG) | grep 'Height:' -A 1 | sed 's/.*Height: \([0-9]*\).*/\1/')
KERNEL_SIZE=$(shell grep 'Kernel:' -A 1 $(PLAYAREA_CFG) | grep 'Size:' -A 1 | sed 's/.*Size: \([0-9]*\).*/\1/')

# Print the extracted configuration values
$(info CPU_IP = $(CPU_IP))
$(info SNN_GPU_IP = $(SNN_GPU_IP))
$(info SNN_SPINNAKER_IP = $(SNN_SPINNAKER_IP))
$(info SNN_SPINNAKER_SCNN_IP = $(SNN_SPINNAKER_SCNN_IP))
$(info SNN_SPINNAKER_MAP_IP = $(SNN_SPINNAKER_MAP_IP))
$(info SNN_SPINNAKER_PROJ_IP = $(SNN_SPINNAKER_PROJ_IP))
$(info VIS_RAW_PORT = $(VIS_RAW_PORT))
$(info VIS_FAST_PORT = $(VIS_FAST_PORT))
$(info VIS_MEDIUM_PORT = $(VIS_MEDIUM_PORT))
$(info VIS_SLOW_PORT = $(VIS_SLOW_PORT))
$(info CTRL_PUCK_PORT = $(CTRL_PUCK_PORT))
$(info CTRL_PADDLE_CUR_PORT = $(CTRL_PADDLE_CUR_PORT))
$(info CTRL_PADDLE_DES_PORT = $(CTRL_PADDLE_DES_PORT))
$(info CTRL_PADDLE_CON_PORT = $(CTRL_PADDLE_CON_PORT))

$(info BOARD_WIDTH = $(BOARD_WIDTH))
$(info BOARD_HEIGHT = $(BOARD_HEIGHT))
$(info KERNEL_SIZE = $(KERNEL_SIZE))

# Set up preprocessor macros
CFLAGS += -DCPU_IP=\"$(CPU_IP)\" \
		  -DSNN_GPU_IP=\"$(SNN_GPU_IP)\" \
		  -DSNN_SPINNAKER_IP=\"$(SNN_SPINNAKER_IP)\" \
		  -DSNN_SPINNAKER_SCNN_IP=\"$(SNN_SPINNAKER_SCNN_IP)\" \
		  -DSNN_SPINNAKER_MAP_IP=\"$(SNN_SPINNAKER_MAP_IP)\" \
		  -DSNN_SPINNAKER_PROJ_IP=\"$(SNN_SPINNAKER_PROJ_IP)\" \
		  -DVIS_RAW_PORT=$(VIS_RAW_PORT) \
		  -DVIS_FAST_PORT=$(VIS_FAST_PORT) \
		  -DVIS_MEDIUM_PORT=$(VIS_MEDIUM_PORT) \
		  -DVIS_SLOW_PORT=$(VIS_SLOW_PORT) \
		  -DCTRL_PUCK_PORT=$(CTRL_PUCK_PORT) \
		  -DCTRL_PADDLE_CUR_PORT=$(CTRL_PADDLE_CUR_PORT) \
		  -DCTRL_PADDLE_DES_PORT=$(CTRL_PADDLE_DES_PORT) \
		  -DCTRL_PADDLE_CON_PORT=$(CTRL_PADDLE_CON_PORT) \
		  -DBOARD_WIDTH=$(BOARD_WIDTH) \
		  -DBOARD_HEIGHT=$(BOARD_HEIGHT) \
		  -DKERNEL_SIZE=$(KERNEL_SIZE)

# Source files
SRCS = display.c

# Object files (replace .c with .o for all sources)
OBJS = $(SRCS:.c=.o)

# Default target
all: $(TARGET)

# How to compile the target
$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS) $(LDFLAGS)

# Rule to create object files from C source files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean up generated files
clean:
	rm -f $(OBJS) $(TARGET)

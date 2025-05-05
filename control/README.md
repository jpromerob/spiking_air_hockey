# Control

A 5-bar planar manipulator, depicted in the figure below, is a robotic mechanism consisting of five rigid links (four moving links and one base link) connected by five joints, forming a kinematic chain operating in a two-dimensional plane. This system features three passive joints and two actuated joints, each one controlled by a servomotor Dynamixel XM430-W210-T . The servomotors, positioned at the base, enable precise end-effector positioning through coordinated movements, making the manipulator particularly suited for tasks such as path following. Although this design offers relatively high precision and structural rigidity, it is constrained by a limited workspace and requires non-trivial control algorithms for accurate performance.

On the motor-output side, the CPU receives events representing the robot paddle’s desired X- and Y-coordinates from the SNN accelerator. Manipulator control is achieved by translating such events into end-effector positions and, ultimately, into individual motor commands, i.e. angular positions, for accurate kinematic transformations.

![](https://github.com/jpromerob/spiking_air_hockey/blob/main/description/Manipulator.png)
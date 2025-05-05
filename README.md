# Spiking Air-Hockey Player

A closed-loop system was implemented to enable interaction between a human player and an automated opponent on an air-hockey board. The automated opponent utilizes spiking neural networks (SNNs) instantiated on SNN accelerators to process event-based data from an event camera, also known as dynamic vision sensor (DVS). The DVS captures real-time visual input by detecting changes in the scene, mainly  around the puck's position, allowing the system to efficiently compute relevant information. The spiking neural network processes this data to determine the puck's trajectory and control a 5-bar planar manipulator, which serves as the robotic opponent's actuator. The manipulator is tasked with preventing the human player from scoring by intercepting the puck, demonstrating fast reactive real-time decision-making and motor control. This system showcases the application of neuromorphic computing in a highly interactive and dynamic environment requiring high-speed sensory processing and actuation.

<p align="left">
  <img src="https://github.com/jpromerob/spiking_air_hockey/blob/main/description/RealTimeAirHockeyGame.gif" width="1000"/>
</p>
 
# Ground Truth
Ground truth refers to the actual position of the puck at any given moment. Accurately determining the ground truth is essential for evaluating the performance of any object tracking algorithm. We pursued two separate approaches to obtain ground-truth puck positions: (1) generating and streaming synthetic data, where the puck’s position is precisely known; and (2), recording real-world playing sequences, followed by offline calculation of the ground truth for each recording. 

     
## Synthetic Data
To simulate puck movement, we generate trajectories to replicate the behavior of a real puck as it travels within the playing area and bounces off the boundaries. Every 0.5ms, we position the puck’s kernel at the given coordinates specified by the generated trajectory. Instead of sending events for all active pixels in the kernel, we sampled and streamed a subset of them, with the number of sampled pixels increasing with the puck's simulated speed. The part a) of the following figure shows a trail of synthetic events and a zoom-in view of the events corresponding to the last 1ms of data.

![](https://github.com/jpromerob/spiking_air_hockey/blob/main/description/Data_Syn_vs_Rec.png)
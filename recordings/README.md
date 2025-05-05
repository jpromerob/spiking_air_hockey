# Ground Truth

Ground truth refers to the actual position of the puck at any given moment. Accurately determining the ground truth is essential for evaluating the performance of any object tracking algorithm. We pursued two separate approaches to obtain ground-truth puck positions: (1) generating and streaming synthetic data, where the puck’s position is precisely known; and (2), recording real-world playing sequences, followed by offline calculation of the ground truth for each recording. 

## Recorded Data

Although synthetic data is valuable, capturing real-world events is essential for achieving higher fidelity to actual puck motion. To acquire these events, we instructed a human player to continuously strike the puck against the board’s edges. We created recordings in 3-second intervals, which were replayed and streamed to the SNN accelerator. During replay, we compiled raw events into 1ms frames. After completing each recording replay, we applied a non-spiking CNN to these frames to obtain an estimate of the puck’s XY positions. The part b) of the following figure shows a trail of real events from a recording and a zoom-in view of the events corresponding to the last 1ms of data.

![](https://github.com/jpromerob/spiking_air_hockey/blob/main/description/Data_Syn_vs_Rec.png)
# Calibration

In the data streaming process, the CPU captured information from the event camera and transmitted it via UDP packets to the SNN accelerator housed in a server room. This streaming is facilitated by the software tool [AEstream](https://github.com/aestream/aestream). Before transmission, the raw visual event data undergo several preprocessing transformations, including lens un-distortion, perspective warping, spatial subsampling, and cropping. The influence of these transformations on the original pixel space is depicted the figure below: the transformed output is a perpendicular, de-warped, top-down view of the playing area with a resolution of 256x165 pixels. In this work we perform these transformations by means of a look-up table (LUT) obtained during system calibration. 

## Transformation of Event-Data

![](https://github.com/jpromerob/spiking_air_hockey/blob/main/description/CamDataTransformation.png)
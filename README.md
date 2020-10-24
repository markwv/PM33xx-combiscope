# PM33xx-combiscope

Python GPIB wrapper for Fluke/Philips combiscopes PM3370, PM3380, PM3390, PM3384, and PM3394.

Only tested on PM3394B and PM3384B, Your miles may vary on other scopes. All command are based on the SCPI Users Manual. 

The example shows how to configure the scope (channels, probes, timebase, and trigger), initialize a measurement, and read back the traces. The PM33xx python module does not perform any configuration error checking, this is up to you.

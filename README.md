# GC-Utils
Scripts, metrics, processors, and snippets used in association with Golden Cheetah.

## GC functions
**Weather** Uses [synopticdata](https://api.synopticdata.com/v2/) weather API to gather data from beacons throughout an activity. All weather data necessary for chung aero analysis is included. This can be saved and run as a python processor within GC.

**Auto Download/Cleanup for Garmin Connect** Personal functions that are used to download the most recent data form Garmin Connect and organize a directory for import to Golden Cheetah. This makes sure that you get the full FIT files and will also allow for clean auto-imports without the need to repeatedly roll thorough past activities. Lots of room for personal customization in how this acts.

**Symlinks** Allows you to create system links between local directories and a cloud based file system. This ensures parity with multiple access points.

## Lactate solver
Takes vectors from a lactate step test (power, hr, lactate) and provides multiple LT solving options. Prefered option in Dmax Modified[1].


# References
[1] [The Modified Dmax Method is Reliable to Predict the Second Ventilatory Threshold in Elite Cross-Country Skiers](https://journals.lww.com/nsca-jscr/Fulltext/2010/06000/The_Modified_Dmax_Method_is_Reliable_to_Predict.16.aspx)
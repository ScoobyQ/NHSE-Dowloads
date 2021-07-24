Various async scripts for downloading NHSE files.

## RttDownloads.py

1) Visits https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/

2) Gets the most recent 3 Financial Year links under Latest Data e.g. 2021-22 RTT waiting times data. It is expected

3) Visits those three links and downloads all files which match the specified regex pattern. The regex pattern uses alternation to extract hrefs which contains specified MMMYY patterns e.g. links that contains May21. If var revisions is set to True then all files between the rev_start and rev_end specified dates will be returned, in addition to the 
curr_period. 

4) User specified variables:

    curr_period = Latest expected month year period for files in format MMMYY
    rev_start = Expected start month year period for revised files in format MMMYY
    rev_end = Expected end month year period for revised files in format MMMY
    OUTPUT_FOLDER = Destination folder for file downloads. This path should end with a "\".




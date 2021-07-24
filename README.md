Various async scripts for downloading NHSE files.

## RttDownloads.py

1) Visits https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/

2) Gets the most recent 3 Financial Year links under Latest Data e.g. 2021-22 RTT waiting times data. It is expected that any specified revisions periods will be within this range.

3) Visits those three links and downloads all files which match the specified regex pattern. The regex pattern uses alternation to extract hrefs which contains specified MMMYY patterns (prefixed with "-") e.g., links that contains -May21. If var revisions is set to True then all files between the rev_start and rev_end specified dates will be returned, in addition to the 
curr_period. Links containing `time` are filtered out.

4) User specified variables:

    curr_period = String date in format MMMYY. Latest expected month year period for files.<br>
    revisions = Boolean True | False.<br>
    rev_start = String date in format MMMYY. Expected start month year period for revised files.<br>
    rev_end = String date in format MMMYY. Expected end month year period for revised files.<br>
    OUTPUT_FOLDER = Destination folder for file downloads. This path should end with a "\\".




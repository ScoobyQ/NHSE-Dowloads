Various async scripts for downloading NHSE files.

## trioAsyncRttDownloads.py

1) Visits https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/

2) Gets the most recent 3 Financial Year links under Latest Data e.g. 2021-22 RTT waiting times data. It is expected that any specified revision periods will be within this range.

3) Visits those three links and downloads all files which match the specified regex pattern. The regex pattern uses alternation to extract hrefs which contains specified MMMYY patterns (prefixed with "-") e.g., links that contains -May21. If var revisions is set to True then all files between the rev_start and rev_end specified dates will be returned, in addition to the 
curr_period. Links containing `time` are filtered out.

4) User updated variables:

    curr_period = String date in format MMMYY. Latest expected month year period for files.<br>
    revisions = Boolean True | False.<br>
    rev_start = String date in format MMMYY. Expected start month year period for revised files.<br>
    rev_end = String date in format MMMYY. Expected end month year period for revised files.<br>
    
5) Folder Rtt will be created if not already present.
   
## trioAsyncCwtMonthlyDownloads.py

tbc

## trioAsyncDiagnosticsMonthlyDownloads.py

tbc

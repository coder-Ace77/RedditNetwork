Steps to Run After Cloning this repo

0. Install the necessary [requirements](/requirements.txt)

1. In the Source Directory, Create an empty folder titled output/

2. Downloading Files - Add the list of subreddits to [sublist.csv](Scripts/sublist.csv) and run [FileDownload.py](Scripts/FileDownload.py) from the src folder.

3. Fetching the Data - Run the File [filter_file.py](/Scripts/filter_file.py) after finshing step 2. The file will be exported to the newly created output folder.

4. If you have multiple json graphml files and want to merge them, change their names and list them in [graphml_files.csv](utils/graphml_files.csv) and run this [code](utils/mergegml.py). Move these renamed files to utils folder


[Link to Available Sublist](https://docs.google.com/spreadsheets/d/1KMybtp6lWoG154eiNmh-FWVlCs40z8NnljzhYfHPM2c/edit?gid=952481735#gid=952481735)

[Link to Doc](https://docs.google.com/document/d/1GeB1Ji9qhLvGSaW175c7pY75rD81mBwAudBi1SpCxBg/edit?tab=t.1687nqsr0gjy)

[Top Subreddits list by members](https://docs.google.com/spreadsheets/d/1E5PU18h8G-GGRYponNVJ_Crhu5LkyEnOXQr7Vie353A/edit?usp=sharing)


[FinaList](https://docs.google.com/spreadsheets/d/1oT-zug2Rv-x4MXzl_3ykpTg8_wSVj2f8ZTKANL40TSc/edit?usp=sharing)
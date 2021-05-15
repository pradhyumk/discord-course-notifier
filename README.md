![ViewCount](https://views.whatilearened.today/views/github/pradhyumk/discord-course-notifier.svg)

# Discord Course Notifier
Posts a notification in a Discord server when a class has an available section.

## Ingesting Data (`ingest_db.py`)
It would be a waste of time searching through a large dump file every time a course is added to notify. The MongoDB database ingests only necessary information (and some optional for future enhancements) for fast access times.  

Run `python3 ingest_db.py --help` for arguments.

## Endpoints
Rutgers uses the following endpoints in the [Schedule of Classes](https://sis.rutgers.edu/soc/):
### Course Information:  
`https://sis.rutgers.edu/soc/api/courses.json?year=YEAR&term=TERM&campus=CAMPUS`  

### Open Courses  
Responds with a list containing index numbers for open sections.  
`https://sis.rutgers.edu/soc/api/openSections.json?year=YEAR&term=TERM&campus=CAMPUS`


### URL Parameters:  

`TERM` (Integer):
* `1` - Spring
* `7` - Summer
* `9` - Fall
* `0` - Winter  

*Don't ask me why these numbers are random.*
  
`YEAR` (Integer)
* A year.

`CAMPUS` (String):
* `NB` - New Brunswick
* `NK` - Newark
* `CM` - Camden
* `ONLINE_NB` - New Brunswick - Online and Remote Instruction Courses
* `ONLINE_NK` - Newark - Online and Remote Instruction Courses
* `ONLINE_CM` - Camden - Online and Remote Instruction Courses
* `B` - Burlington County Community College - Mt Laurel
* `CC` - Camden County College - Blackwood Campus
* `H` - County College of Morris
* `CU` - Cumberland County College
* `MC` - Denville - RU-Morris
* `WM` - Freehold WMHEC - RU-BCC
* `L` - Lincroft - RU-BCC
* `AC` - Mays Landing - RU-ACCC
* `J` - McGuire-Dix-Lakehurst RU-JBMDL
* `D` - Mercer County Community College
* `RV` - North Branch - RU-RVCC

## Webhook (`webhook.py`)
A simple script which checks the active requests in the database to see if any of the sections are open, and if so, notify the user in the Discord channel.  

To-do: Companion bot to add/remove requests and choose term/year.

# License
The source code for this project is licensed under the MIT License.
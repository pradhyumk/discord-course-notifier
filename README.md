# Discord Course Notifier
Posts a notification in a Discord server when a class has an available section.

## Ingesting Data (`ingest_db.py`)
It would be a waste of time searching through a large dump file every time a course is added to notify. The MongoDB database ingests only necessary information (and some optional for future enhancements) for fast access times.  

Run `python3 ingest_db.py --help` for arguments.

## Webhook
To do next.


# License
This source code for this project is licensed under MIT License.
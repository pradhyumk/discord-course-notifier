import json
import os
import pymongo
import requests
import multiprocessing
import logging
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt=f"%m/%d/%Y %H:%M:%S %Z")
scheduler = BlockingScheduler()
logger = logging.getLogger("Discord Webhook")

# All of the databases
mongo_client = pymongo.MongoClient(os.environ.get("MONGODB"))
soc_db = mongo_client['fall_2021']
snipes = soc_db['snipes']
courses = soc_db['courses']
sections = soc_db['sections']
url = os.environ.get("WEBHOOK")


def notify_section_availability(section: dict):
    """Notifies user that their requested course section is available on Discord"""
    try:
        section_info = sections.find_one({'_id': section['index']})
        course_info = courses.find_one({'_id': section_info['courseString']})
    except Exception as e:
        logger.error(e)
        return

    notify_users = ""
    for user in section['users']:
        notify_users += f"<@{user}> "

    payload = {
        "content": notify_users,
        "embeds": [{"title": "Section open!",
                    "timestamp": f"{datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}",
                    "color": 2150418,
                    "fields":
                        [{
                            "name": "Course",
                            "value": f"{section_info['courseString']}",
                            "inline": True
                        },
                            {
                                "name": "Section",
                                "value": f"{section_info['section_number']}",
                                "inline": True
                            },
                            {
                                "name": "Index",
                                "value": f"{section['index']}",
                                "inline": True
                            },
                            {
                                "name": "Course Name",
                                "value": f"{course_info['title'].title()}",
                                "inline": True
                            },
                            {
                                "name": "Instructor",
                                "value": f"{section_info['instructorsText'].title()}",
                                "inline": True
                            },
                            {
                                "name": "**Register**",
                                "value": "[WebReg](https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&"
                                         f"semesterSelection=92021&indexList={section['index']})",
                                "inline": False
                            }
                        ]}]}

    payload = {'payload_json': json.dumps(payload)}
    requests.post(url, data=payload)
    logger.info(f"Notified users for index {section['index']}.")


@scheduler.scheduled_job('interval', seconds=6)
def check_active_courses():
    pthreads = []
    x = 0

    try:
        open_sections = requests.get("https://sis.rutgers.edu/soc/api/openSections.json?year=2021&term=9&campus=NB")\
            .json()
    except Exception as e:
        logger.error(e)
        return

    for request in snipes.find():
        if request['index'] not in open_sections and request['status'] == 'open':
            logger.info(f"Index {request['index']} has been closed :(")
            snipes.update_one({"index": request['index']}, {"$set": {"status": "closed"}})
            continue
        elif request['index'] not in open_sections and request['status'] == 'closed':
            logger.info(f"Index {request['index']} is currently closed.")
            continue
        elif request['index'] in open_sections and request['status'] == 'open':
            logger.info(f"Notified users already that index {request['index']} is open.")
            continue
        else:
            snipes.update_one({"index": request['index']}, {"$set": {"status": "open"}})
        pthreads.append(multiprocessing.Process(target=notify_section_availability, args=(request,)))
        pthreads[x].start()
        x += 1

    for thread in pthreads:
        thread.join()


if __name__ == '__main__':
    logger.info("The webhook has started.")
    check_active_courses()
    scheduler.start()

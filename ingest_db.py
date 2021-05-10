import pymongo
import os
import argparse
import requests
import logging


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        prog="ingest_db",
        description='Ingests Rutgers course and section information to a MongoDB database.',
        add_help=True,
        allow_abbrev=True
    )

    argparser.add_argument(
        '--year',
        '-Y',
        type=int,
        help='Year to query'
    )

    argparser.add_argument(
        '--term',
        '-T',
        type=int,
        help='Term to query'
    )

    argparser.add_argument(
        '--campus',
        '-C',
        type=str,
        default='NB',
        help='Campus to query'
    )

    argparser.add_argument(
        '--database',
        '-D',
        type=str,
        help='MongoDB (Python 3.6 or higher) connection string.'
    )

    args = argparser.parse_args()

    mongo_client = pymongo.MongoClient(args.database)
    fall2021_db = mongo_client['fall_2021']
    courses = fall2021_db['courses']
    sections = fall2021_db['sections']

    year = args.year
    term = args.term
    campus = args.campus
    url = f"https://sis.rutgers.edu/soc/api/courses.json?year={year}&term={term}&campus={campus}"

    r = requests.post(url)
    dump = r.json()

    for course in dump:
        add_to_db = {}

        # skip if the course is already in the database
        if courses.find_one({"_id": course['courseString']}):
            continue

        if "courseString" in course:
            add_to_db["_id"] = course['courseString']
        if "title" in course:
            add_to_db["title"] = course['title']
        if "school" in course and 'code' in course['school']:
            add_to_db["school_code"] = course['school']['code']
        if "credits" in course:
            add_to_db["credits"] = course['credits']
        if "subjectDescription" in course:
            add_to_db["subjectDescription"] = course['subjectDescription']
        if "expandedTitle" in course:
            add_to_db["expandedTitle"] = course['expandedTitle']
        if "mainCampus" in course:
            add_to_db["mainCampus"] = course['mainCampus']
        if "courseNumber" in course:
            add_to_db["courseNumber"] = course['courseNumber']
        if "subjectNotes" in course:
            add_to_db["subjectNotes"] = course['subjectNotes']

        # added courses to db
        courses.insert_one(add_to_db)

        # on to the sections
        for section in course['sections']:
            add_to_db = {}

            if "index" in section:
                add_to_db["_id"] = section['index']
            if "courseString" in course:
                add_to_db["courseString"] = course['courseString']
            if 'instructors' in section:
                i = []
                for person in section['instructors']:
                    i.append(person['name'])
                add_to_db["instructors"] = i
            if 'number' in section:
                add_to_db['section_number'] = section['number']
            if 'instructorsText' in section:
                add_to_db['instructorsText'] = section['instructorsText']

            sections.insert_one(add_to_db)

        logging.info(f"Added {course['title']}")

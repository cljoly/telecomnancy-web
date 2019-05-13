from math import ceil
import time
from database.db_objects import Activity, Repository
from main import db
from sqlalchemy import func
from main import current_user

PER_PAGE = 10


class Pagination(object):
    """Helper class for pagination - used in the activity table"""

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def __iter__(self, left_edge=2, left_current=1, right_current=2, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (self.page - left_current - 1 < num < self.page + right_current) or \
                    num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
                

## Groupes


class Group:
    def __init__(self, name, repository):
        self.name = name
        self.repository = repository
        self.nb_commits = 1
        self.last_commit = time.strftime("%d/%m/%Y")
        self.stat_link = "/"


def get_groups_for_page(page, all_groups, count):
    return [all_groups[i] for i in range((page - 1) * PER_PAGE, min((page - 1) * PER_PAGE + PER_PAGE, count))]


## Activités


class ActivityDisplay:
    """Regroupe les informations correspondantes à une activitée"""

    def __init__(self, name, count, c_date=time.strftime("%d/%m/%Y"), d_date="None", link='/activity'):
        self.c_date = c_date  # the name of the activity
        self.name = name  # date of creation
        self.count = count  # due date
        self.d_date = d_date  # nb of members
        self.link = link  # link to the activity page


def get_activities_for_page(page, count):
    """Effectue les requêtes necessaires pour récupérer les infos de Activities correspondantes à la page page"""
    result = db.session.query(
        Activity.name, func.count(Repository.id).label("count"), Activity.start_date, Activity.end_date, Activity.id
    ).filter(
        Activity.id == Repository.activity_id and
        Activity.teacher_id == current_user.id
    ).group_by(
        Activity.name
    )
    return [ActivityDisplay(result[i].name,
                            result[i].count,
                            result[i].start_date.strftime("%d/%m/%Y"),
                            result[i].end_date.strftime("%d/%m/%Y"),
                            "/activity/%s" % result[i].id)
            for i in range((page - 1) * PER_PAGE, min((page - 1) * PER_PAGE + PER_PAGE, count))]

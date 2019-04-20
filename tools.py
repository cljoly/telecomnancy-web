from math import ceil
import time
from database.db_objects import *
from main import db
from sqlalchemy import func

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


class Group:
    def __init__(self, name, count, c_date=time.strftime("%d/%m/%Y"), d_date="None", link='/activity'):
        self.c_date = c_date                        # the name of the activity
        self.name = name                            # date of creation
        self.count = count                          # due date
        self.d_date = d_date                        # nb of members
        self.link = link                            # link to the activity page

def get_activities_for_page(page, count):
    #result = Activity.query.filter(Activity.id.between((page - 1) * PER_PAGE, min((page - 1) * PER_PAGE + PER_PAGE, count)))
    result = db.session.query(Activity.name, func.count(Repository.id), Activity.start_date, Activity.end_date).filter(Activity.id == Repository.activity_id).group_by(Activity.name)
    return [Group(result[i].name, result[i].count, result[i].start_date, result[i].end_date) for i in range((page - 1) * PER_PAGE, min((page - 1) * PER_PAGE + PER_PAGE, count))]
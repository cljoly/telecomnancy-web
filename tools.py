from math import ceil
import time

from flask import request, url_for

PER_PAGE = 10


class Pagination(object):

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

    def __iter__(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
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

    def __init__(self, name, count, d_date=time.strftime("%d/%m/%Y"), link='/groups/default'):
        self.c_date = time.strftime("%d/%m/%Y")     # the name of the group
        self.name = name                            # date of creation
        self.count = count                          # due date
        self.d_date = d_date                        # nb of members
        self.link = link                            # link to the group page


def get_groups_for_page(page, all_groups, count):
    return [all_groups[i] for i in range((page - 1) * PER_PAGE, min((page - 1) * PER_PAGE + PER_PAGE, count))]
import sched
import time
from model.config import config
import datetime
from dateutil import relativedelta

from model.mmr_season import querySeason, backupLeaderboardForNewSeason, incrementSeason


class SeasonScheduler:

    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def newSeason(self):
        seasonNumber = querySeason()
        backupLeaderboardForNewSeason(seasonNumber)
        incrementSeason()
        self.scheduleSeason()

    def scheduleSeason(self):
        currentMonth = datetime.datetime.now().month
        modMonth = (currentMonth % config["season-every"])
        delta = relativedelta.relativedelta(months=config["season-every"] - modMonth, day=1)
        now = datetime.datetime.now()
        next_season = (now + delta).replace(microsecond=0, second=0, minute=0, hour=0, day=1)

        wait_seconds = max((next_season - now).total_seconds(), 0)
        self.scheduler.enter(wait_seconds, 1, self.newSeason)
        self.scheduler.run(blocking=False)

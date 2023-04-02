import sched
import time
from model.config import config
import datetime
from dateutil import relativedelta

from model.mmr_season import querySeason, backupLeaderboardForNewSeason, incrementSeason


def longSleep(sleepTime):
    while sleepTime > 0.0:
        time.sleep(min(600.0, sleepTime))
        sleepTime -= 600.0


scheduler = sched.scheduler(time.time, longSleep)


def newSeason():
    seasonNumber = querySeason()
    print(f"Updating to season {seasonNumber + 1} from {seasonNumber}")
    backupLeaderboardForNewSeason(seasonNumber)
    incrementSeason()
    scheduleSeason()


def scheduleSeason():
    seconds = getNextSeason()
    scheduler.enter(seconds, 1, newSeason)
    scheduler.run(blocking=True)


def getNextSeason():
    currentMonth = datetime.datetime.now().month
    modMonth = (currentMonth % config["season-every"])
    delta = relativedelta.relativedelta(months=config["season-every"] - modMonth, day=1)
    now = datetime.datetime.now()
    next_season = (now + delta).replace(microsecond=0, second=0, minute=0, hour=0, day=1)
    seconds = max((next_season - now).total_seconds(), 0)
    return seconds

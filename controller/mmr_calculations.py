from model.config import config


def mmr_calc(leaderboardEntry1, leaderboardEntry2, victory, updateStats):
    maxDiff = config["mmr-points-bet"]
    divider = config["mmr-elo-divide"]
    power = config["mmr-power"]

    p1Adjustments = getAdjustments(leaderboardEntry1.elo)
    p2Adjustments = getAdjustments(leaderboardEntry2.elo)

    r1 = power ** (leaderboardEntry1.elo / divider)
    r2 = power ** (leaderboardEntry2.elo / divider)

    if r1 == 0.0 and r2 == 0.0:  # Prevent division by 0
        r1 = 0.001
        r2 = 0.001
    e1 = r1 / (r1 + r2)
    e2 = r2 / (r1 + r2)

    s1 = 0.5
    s2 = 0.5
    if victory == 1:
        s1 = 1.0 + p1Adjustments[0]
        s2 = 0.0 + p2Adjustments[1]
        if updateStats:
            leaderboardEntry1.gamesThisSeasonWon += 1
    elif victory == 2:
        s1 = 0.0 + p1Adjustments[1]
        s2 = 1.0 + p2Adjustments[0]
        if updateStats:
            leaderboardEntry2.gamesThisSeasonWon += 1
    diff1 = maxDiff * (s1 - min(1.0, max(0.0, e1)))
    diff2 = maxDiff * (s2 - min(1.0, max(0.0, e2)))
    leaderboardEntry1.elo += diff1
    leaderboardEntry2.elo += diff2
    if config["mmr-minimum-enabled"]:
        if leaderboardEntry1.elo < config["mmr-minimum"]:
            leaderboardEntry1.elo = config["mmr-minimum"]
        if leaderboardEntry2.elo < config["mmr-minimum"]:
            leaderboardEntry2.elo = config["mmr-minimum"]
    if updateStats:
        leaderboardEntry1.gamesThisDecay += 1
        leaderboardEntry2.gamesThisDecay += 1
        leaderboardEntry1.gamesThisSeason += 1
        leaderboardEntry2.gamesThisSeason += 1

    if leaderboardEntry1.elo > leaderboardEntry1.seasonHigh:
        leaderboardEntry1.seasonHigh = leaderboardEntry1.elo

    if leaderboardEntry2.elo > leaderboardEntry2.seasonHigh:
        leaderboardEntry2.seasonHigh = leaderboardEntry2.elo

    leaderboardEntry1.updateUser()
    leaderboardEntry2.updateUser()


def getAdjustments(elo):
    scales = config["mmr-scales"]
    victoryAdjustment = 0.0
    defeatAdjustment = 0.0
    for scale in scales:
        for scaleName in scale:
            scaleObj = scale[scaleName]
            if elo >= scaleObj["start"]:
                victoryAdjustment = scaleObj["winner"]
                defeatAdjustment = scaleObj["loser"]

    return victoryAdjustment, defeatAdjustment



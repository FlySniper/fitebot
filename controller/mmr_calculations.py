def mmr_calc(config, leaderboardEntry1, leaderboardEntry2, victory, updateStats):
    maxDiff = config["mmr-points-bet"]
    divider = config["mmr-elo-divide"]
    power = config["mmr-power"]

    p1Adjustments = getAdjustments(config, leaderboardEntry1.elo)
    p2Adjustments = getAdjustments(config, leaderboardEntry2.elo)

    r1 = (leaderboardEntry1.elo / divider) ** power
    r2 = (leaderboardEntry2.elo / divider) ** power

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


def getAdjustments(config, elo):
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



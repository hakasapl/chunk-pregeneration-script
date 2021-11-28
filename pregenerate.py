import argparse
import math
import time
import pexpect
import os
import datetime

def main():
    # Handle cli arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delay", help="Time between delays", type=float, default=0.1, required=False)
    parser.add_argument("-m", "--memory", help="Memory to allocate to JVM", type=int, default=2048, required=False)
    parser.add_argument("player", help="Player name to expect on server")
    parser.add_argument("server", help="Path to minecraft server.jar")
    parser.add_argument("radius", help="Radius of blocks from spawn to generate", type=int)
    args = parser.parse_args()

    PARAM_DELAY = args.delay
    PARAM_MEMORY = args.memory
    PARAM_PLAYER = args.player
    PARAM_JARPATH = args.server
    PARAM_RADIUS = args.radius

    # checks
    if not os.path.exists(PARAM_JARPATH):
        print("JAR path does not exist.")
        exit(1)

    if PARAM_RADIUS % 1024 != 0:
        print("Please use a radius which is a multiple of 1024.")
        exit(1)

    startCoord = -1 * PARAM_RADIUS
    endCoord = PARAM_RADIUS

    PARAM_GAP = 256

    totalChunks = math.floor(PARAM_RADIUS**2 * 4)
    print("Required generation of %i chunks" % totalChunks)

    totalLogicalChunks = math.floor((PARAM_RADIUS / PARAM_GAP)**2 * 4)
    estimatedTime = totalLogicalChunks * PARAM_DELAY * 4 / 3600
    print("Estimated to take at least %.2f hours" % estimatedTime)
    input("Press any key to start the server and begin pregeneration...")

    jar_dir = os.path.dirname(PARAM_JARPATH)
    jar_name = os.path.basename(PARAM_JARPATH)

    launch_command = "java -Xms" + str(PARAM_MEMORY) + "M -Xmx" + str(PARAM_MEMORY) + "M -jar " + jar_name + " nogui"
    print("Spawning server...")
    child = pexpect.spawn(launch_command, cwd=jar_dir)  # spawn minecraft server
    child.expect("Done", timeout=300)  # wait for server to start
    print("Waiting for %s to join server..." % PARAM_PLAYER)
    child.expect("%s joined the game" % PARAM_PLAYER, timeout=300)  # wait for player to join
    child.sendline("gamemode creative %s" % PARAM_PLAYER)  # set gamemode to creative
    child.sendline("gamerule doDaylightCycle false")  # set gamemode to creative
    child.sendline("gamemode doWeatherCycle false")  # set gamemode to creative
    child.sendline("gamemode doMobSpawning false")  # set gamemode to creative
    
    print("Starting chunk pregeneration...")

    begin_time = datetime.datetime.now()

    # start pregeneration
    chunkRange = range(startCoord, endCoord, PARAM_GAP)
    count = 0
    lastFloor = -1
    opposite = 1
    lastPerc = -1
    for x_coord in chunkRange:
        for z_coord in chunkRange:
            z_coord = z_coord * opposite

            child.sendline('tp %s %i 255 %i 0 45' % (PARAM_PLAYER, x_coord, z_coord))
            child.expect('Teleported %s' % PARAM_PLAYER)
            time.sleep(PARAM_DELAY)
            child.sendline('tp %s %i 255 %i -90 45' % (PARAM_PLAYER, x_coord, z_coord))
            child.expect('Teleported %s' % PARAM_PLAYER)
            time.sleep(PARAM_DELAY)
            child.sendline('tp %s %i 255 %i -180 45' % (PARAM_PLAYER, x_coord, z_coord))
            child.expect('Teleported %s' % PARAM_PLAYER)
            time.sleep(PARAM_DELAY)
            child.sendline('tp %s %i 255 %i -90 45' % (PARAM_PLAYER, x_coord, z_coord))
            child.expect('Teleported %s' % PARAM_PLAYER)
            time.sleep(PARAM_DELAY)

            count = count + 1
            perc = round((float(count) / float(totalLogicalChunks)) * 100, 2)
            if perc != lastPerc:
                print("%.2f Percent Done" % perc)
                lastPerc = perc

            #time.sleep(PARAM_DELAY)
        opposite = opposite * -1

    elapsed = datetime.datetime.now() - begin_time
    print("Chunk pregeneration took " + str(elapsed))

    child.sendline("gamerule doDaylightCycle true")  # set gamemode to creative
    child.sendline("gamemode doWeatherCycle true")  # set gamemode to creative
    child.sendline("gamemode doMobSpawning true")  # set gamemode to creative

    input("Press any key to close the server...")

if __name__ == '__main__':
    main()
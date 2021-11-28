import argparse
import math
import time
import pexpect
import os

def main():
    # Handle cli arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delay", help="Time between delays", type=float, default=0.2, required=False)
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

    startCoord = -1 * PARAM_RADIUS
    endCoord = PARAM_RADIUS

    totalChunks = math.floor(PARAM_RADIUS**2 * 4 / 16)
    print("Required generation of %i chunks" % totalChunks)

    estimatedTime = totalChunks * PARAM_DELAY / 3600
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
    
    print("Starting chunk pregeneration...")

    # start pregeneration
    chunkRange = range(startCoord, endCoord, 16)
    count = 0
    lastFloor = -1
    for x_coord in chunkRange:
        for z_coord in chunkRange:
            child.sendline('tp %s %i 255 %i' % (PARAM_PLAYER, x_coord, z_coord))
            child.expect('Teleported %s' % PARAM_PLAYER)

            count = count + 1
            perc = (float(count) / float(totalChunks)) * 100
            print("%.2f Percent Done" % perc)

            time.sleep(PARAM_DELAY)

    print("Chunk Pregeneration Done, stopping server")

if __name__ == '__main__':
    main()
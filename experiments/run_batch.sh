#!/usr/bin/env bash

START_RUN=1
END_RUN=50

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPERIMENTS_WS="$SCRIPT_DIR"
CATKIN_WS="$(cd "$EXPERIMENTS_WS/../catkin_ws" && pwd)"

for i in $(seq "$START_RUN" "$END_RUN"); do

    RUN_ID="run_$(printf "%03d" "$i")"
    echo "=============================="
    echo "STARTING $RUN_ID"
    echo "=============================="

    # -------------------------------------------------
    # 1. Launch ROS / Gazebo
    # -------------------------------------------------
    terminator -e "bash -lc 'cd \"$CATKIN_WS\" && ./launch.sh \"$RUN_ID\"'" &
    LAUNCH_PID=$!

    sleep 2

    # -------------------------------------------------
    # 2. Launch SMACH
    # -------------------------------------------------
    terminator -e "bash -lc 'cd \"$CATKIN_WS\" && ./launch_smach.sh \"$RUN_ID\"'" &
    SMACH_TERM_PID=$!

    sleep 2

    # -------------------------------------------------
    # 3. Launch Java (Gwendolen)
    # -------------------------------------------------
    terminator -e "java ail.mas.AIL $AJPF_HOME/src/examples/gwendolen/refcase/remote-inspection.ail" &
    JAVA_TERM_PID=$!

    # -------------------------------------------------
    # 4. WAIT FOR SMACH TO FINISH
    # -------------------------------------------------
    SMACH_PROCESS=$(pgrep -f "smach_integrated.py")

    echo "Waiting for SMACH to finish..."

    while kill -0 $SMACH_PROCESS 2>/dev/null; do
        sleep 1
    done

    echo "SMACH finished → stopping experiment"

    # -------------------------------------------------
    # 5. CLEAN SHUTDOWN
    # -------------------------------------------------
    kill -TERM $(pgrep -f "ail.mas.AIL") 2>/dev/null
    kill -TERM $(pgrep -f "gazebo") 2>/dev/null

    sleep 5

    kill -9 $(pgrep -f "ail.mas.AIL") 2>/dev/null
    kill -9 $(pgrep -f "gazebo") 2>/dev/null
    killall gzserver gzclient 2>/dev/null
    fuser -k 9090/tcp 2>/dev/null

    echo "$RUN_ID complete"

done
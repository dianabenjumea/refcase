# Experiments Workspace

This directory contains the experiment runner and metrics post-processing tools for the SRAS state machine in `refcase_ws` and the SS (Gwendolen agent) `MCAPL`.

## What this does

`run_batch.sh` launches the combined experiment from the `experiments` workspace while targeting the `refcase_ws` Catkin workspace. It starts:

- the ROS/Gazebo environment via `catkin_ws/launch.sh`
- the SMACH state machine via `catkin_ws/launch_smach.sh`
- the Gwendolen agent via `java ail.mas.AIL` using the remote inspection AIL file

The experiment waits for SMACH to finish, then performs a clean shutdown of the Java and Gazebo processes.

## Prerequisites

- `bash` / Unix shell environment
- ROS Melodic with the `refcase_ws` (`catkin_ws`) workspace built and sourced by its launch scripts
- Gazebo installed and configured for the `scout_gazebo_sim` launch
- `terminator` terminal emulator available on the system
- `AJPF_HOME` environment variable set for the Gwendolen/AJPF runtime
- Java available on `PATH`


## How to run the experiment

From this directory:

```bash
cd ~/experiments
./run_batch.sh
```

Note: The script assumes `refcase_ws` is located next to `experiments` at `../catkin_ws`.

## Expected output

The experiment should produce a CSV file named `ss_metrics.csv` containing the recorded Safety System metrics.

Existing processed output files in this directory may include:

- `metrics_summary.csv`
- `metrics_detailed.csv`
- `metrics_table4.csv`
- `metrics_table5.csv`
- `metrics_table6.csv`

## Processing the metrics

### Using the Python script

Run the metrics processor from this same directory:

```bash
cd ~/experiments
python3 aggregate_metrics.py ss_metrics.csv
```

If the script does not accept the file name, simply place `ss_metrics.csv` in this directory and run:

```bash
python3 aggregate_metrics.py
```

### Using the Jupyter notebook

Open `aggregate_metrics.ipynb` in Jupyter:

```bash
cd ~/experiments
jupyter notebook aggregate_metrics.ipynb
```

Then run the notebook cells. The notebook reads `ss_metrics.csv` by default and can be edited to point to a different CSV path if needed.

## Notes

- This README is intended for running experiments from the `experiments` folder, not directly from `catkin_ws`.
- The state machine is launched from `catkin_ws`, but the orchestration script lives in `experiments`.
- If the recorded metrics file is generated elsewhere, copy it into this directory or update the Python/notebook path accordingly.

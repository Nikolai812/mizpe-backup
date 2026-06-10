#!/bin/bash
echo "================================"
echo "Start at $(date +%Y%m%d_%H%M%S)"
echo "================================"
#########################################

# Get this script's process ID
pid=$$
echo "process id is $pid"

output_file="/lustre1/home/makias/nikolair/CRON_MIZPE_BCK/OUTPUTS/bbb_$(date +%Y%m%d_%H%M%S)_${pid}.txt"
echo "writing output to file: $output_file"

######## Load required modules ##########
. /etc/profile.d/modules.sh # Required line for modules environment to work
module load python/3.9 # Load modules that are required by your program
#########################################

### Below is program job command for downloading MIZPE backup for H80 telescope ###
#python mizpe_dwn.py
python /lustre1/home/makias/nikolair/CRON_MIZPE_BCK/mizpe_dwn.py >>  "$output_file" 2>&1 

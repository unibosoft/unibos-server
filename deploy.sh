#!/bin/bash
# UNIBOS Quick Deploy to Rocksteady
# Ultra-simple one-liner deployment

# The cleanest one-liner deployment
rsync -avz --exclude-from=.rsync-exclude . rocksteady:~/unibos/ && \
ssh rocksteady "cd ~/unibos && chmod +x unibos.sh && ./unibos.sh"
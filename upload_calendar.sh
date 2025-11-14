#!/bin/bash

# Recording Calendar Upload Script
# Generates calendar events from ClickUp and uploads to S3

set -e  # Exit on error

echo "============================================"
echo "📅 Recording Calendar Upload"
echo "============================================"

# Step 1: Generate calendar events
echo ""
echo "📝 Step 1: Generating calendar events..."
uv run python -m clickuphelper.task_batch_processor --output calendar_events.json

if [ ! -f calendar_events.json ]; then
    echo "❌ Error: calendar_events.json not generated"
    exit 1
fi

echo "✅ Calendar events generated successfully"

# Step 2: Upload to S3
echo ""
echo "☁️  Step 2: Uploading to S3..."
S3_BUCKET="ai-first-show-assets"
S3_KEY="preproduction_calendar.json"
S3_PATH="s3://${S3_BUCKET}/${S3_KEY}"

aws s3 cp calendar_events.json "${S3_PATH}" \
    --profile cf2 \
    --content-type "application/json"

# Step 3: Print public URL
echo ""
echo "✅ Upload complete!"
echo ""
echo "📡 Public URL:"
echo "https://${S3_BUCKET}.s3.amazonaws.com/${S3_KEY}"
echo ""
echo "============================================"

#!/bin/bash

# Project Configuration
PROJECT_NAME="modera"
SUPABASE_URL="https://kvbexxpebpvoxbabotjl.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt2YmV4eHBlYnB2b3hiYWJvdGpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5MzYxMzMsImV4cCI6MjA0OTUxMjEzM30.KZZ4DiLL4bJT3Sz65Sk6UNoj_ku46zBay1_ZWDWXnwk"

# Build Web Version
flutter clean
flutter pub get
flutter build web \
  --dart-define=SUPABASE_URL=$SUPABASE_URL \
  --dart-define=SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY

# Deploy to AWS S3
aws s3 sync build/web s3://modera.erarta.ai --delete
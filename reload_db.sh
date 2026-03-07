#!/bin/bash
# Reload database with schema + data. Run from project root.
# Usage: ./reload_db.sh   (or: bash reload_db.sh)
# Add -p after -u root if MySQL needs a password.

DB=library_system
USER=root

echo "Loading schema..."
mysql -u $USER $DB < db_proof/schema.sql

echo "Loading data..."
mysql -u $USER $DB < db_proof/data.sql

echo "Loading triggers (if exists)..."
[ -f triggers.sql ] && mysql -u $USER $DB < triggers.sql

echo "Loading views (if exists)..."
[ -f views.sql ] && mysql -u $USER $DB < views.sql

echo "Done. Database reloaded."

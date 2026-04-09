# Reload database with schema + data + views + triggers. YOU MUST RUN THIS FROM THE PROJECT ROOT.
# In the terminal run: ./reload_db.sh
# Press enter when prompted for the password.

DB=library_system
USER=root

echo "Loading schema..."
mysql -u $USER $DB < db_proof/schema.sql

echo "Loading data..."
mysql -u $USER $DB < db_proof/data.sql

echo "Loading views..."
[ -f backend/views.sql ] && mysql -u $USER $DB < backend/views.sql

echo "Loading triggers..."
[ -f backend/triggers.sql ] && mysql -u $USER $DB < backend/triggers.sql

echo "Done. Database reloaded."

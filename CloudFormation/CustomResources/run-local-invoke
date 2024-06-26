#!/bin/bash


EVENTS_DIR='events'

EVENT_FILES=(
    'event-consume-from-map.json'
    'event-consume-from-list.json'
    'event-consume-from-map-retrieval-error.json'
    'event-consume-from-list-retrieval-error.json'
    'event-empty-json-data-input.json'
    'event-empty-search-input.json'
    'event-invalid-json-data-input.json'
    'event-invalid-search-input.json'
)


run_local_invoke() {
    echo "**** Invoking event from file: $event_file ****"
    sam local invoke --event $EVENTS_DIR/$event_file
    echo '-----------------------------'
}


cat <<EOF

Note: unless you've done this already, you might want to temporarily
set:

LOGGER.setLevel(logging.DEBUG)

in getfromjson.py for testing with this script in DEBUG mode.

Current logging settings:
EOF
grep 'LOGGER.setLevel' src/getfromjson.py
echo


cd src/
for event_file in "${EVENT_FILES[@]}"; do
    run_local_invoke
    read -p 'Press RETURN to continue, or CONTROL-c to end: '
done

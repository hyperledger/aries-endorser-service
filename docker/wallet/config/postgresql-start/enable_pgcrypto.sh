if [ "${PGCRYPTO_EXTENSION}" = "Y" ]; then
    echo  "Installing pgcrypto extension on ${POSTGRESQL_DATABASE} ..."
    psql -d ${POSTGRESQL_DATABASE} -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
else
    echo "Skipping installation of pgcrypto extension ..."
fi
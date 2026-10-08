import toggl_to_sqlite as sql
import dotenv
import os

def fn_update_toggl_database(
    drop_db: bool = False
):
    db_path = dotenv.get_key('.env', 'DB_PATH')
    if drop_db and os.path.exists(db_path):
        os.remove(db_path)
    #
    sql.fn_write_toggl_time_entries_to_sqlite(
        df_timelog=sql.fn_get_toggl_time_entries(
            api_values={
                'API_URL': "https://api.track.toggl.com/reports/api/v2/details",
                'API_KEY': dotenv.get_key('.env', 'TOGGL_KEY_ADAM'),
                'ORG_ID': dotenv.get_key('.env', 'TOGGL_ORG_ID'),
                'WS_ID': dotenv.get_key('.env', 'TOGGL_WORKSPACE_ID')
            },
            start_date='2026-08-01',
            end_date='2026-10-31'
        ),
        db_path=db_path
    )
    #
    sql.fn_write_toggl_time_entries_to_sqlite(
        df_timelog=sql.fn_get_toggl_time_entries(
            api_values={
                'API_URL': "https://api.track.toggl.com/reports/api/v2/details",
                'API_KEY': dotenv.get_key('.env', 'TOGGL_KEY_DANN'),
                'ORG_ID': dotenv.get_key('.env', 'TOGGL_ORG_ID'),
                'WS_ID': dotenv.get_key('.env', 'TOGGL_WORKSPACE_ID')
            },
            start_date='2026-08-01',
            end_date='2026-10-31'
        ),
        db_path=db_path
    )


if __name__ == "__main__":
    fn_update_toggl_database(drop_db=False)
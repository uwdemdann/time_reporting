import toggl_functions as t
import polars as pl
import dotenv


api_values = {
    'API_URL': "https://api.track.toggl.com/reports/api/v2/details",
    # 'API_KEY': dotenv.get_key('.env', 'TOGGL_KEY_DANN'),
    'API_KEY': dotenv.get_key('.env', 'TOGGL_KEY_ADAM'),
    'ORG_ID': dotenv.get_key('.env', 'TOGGL_ORG_ID'),
    'WS_ID': dotenv.get_key('.env', 'TOGGL_WORKSPACE_ID')
}

df_logged_time = t.fn_parse_toggl_time_entries(t.fn_get_toggl_time_entries(
    api_values=api_values,
    start_date='2026-08-01',
    end_date='2026-09-30'
))
dict_static_tables = t.fn_get_toggl_static_files(api_values=api_values)


df_timelog = df_logged_time.join(
    pl.from_pandas(dict_static_tables['df_projects']),
    on='project_id',
    how='left'
).join(
    pl.from_pandas(dict_static_tables['df_clients']),
    on='client_id',
    how='left'
).join(
    pl.from_pandas(dict_static_tables['df_users']),
    on='toggl_user_id',
    how='left'
).filter(
    pl.col('duration') > 0
)


# by_project = df_timelog.group_by(['toggl_user_name', 'month', 'client_name', 'project_name']).agg((pl.col('duration').sum() / 3600).alias('hours'))
# by_mission = df_timelog.group_by(['toggl_user_name', 'month', 'client_name']).agg((pl.col('duration').sum() / 3600).alias('hours'))



db_path = dotenv.get_key('DB_PATH')

try:
    existing_ids = pl.read_database_uri(
        'select id from time_entries',
        f"sqlite:///{db_path}"
    ).get_column('id').to_list()
except Exception as e:
    print(f"Error getting existing IDs from Toggl database: {e}")
    existing_ids = []


try:
    df_timelog.filter(
        ~pl.col('id').is_in(existing_ids)
    ).write_database(
        table_name="time_entries",
        connection=f"sqlite:///{db_path}",
        if_table_exists="append",  # options: "fail", "replace", "append"
        engine="adbc"         # native ingestion via PyArrow ADBC
    )
    print("Data written to SQLite successfully.")
except Exception as e:
    print(f"Error writing to database: {e}")





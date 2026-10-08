import toggl_functions as t
import polars as pl
import dotenv


def fn_get_toggl_time_entries(
    api_values: dict[str, str, str, str],
    start_date: str,
    end_date: str
) -> pl.DataFrame:
    df_logged_time = t.fn_parse_toggl_time_entries(t.fn_get_toggl_time_entries(
        api_values=api_values,
        start_date='2026-08-01',
        end_date='2026-10-31'
    ))
    dict_static_tables = t.fn_get_toggl_static_files(api_values=api_values)
    #
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
    #
    return df_timelog

def fn_write_toggl_time_entries_to_sqlite(
    df_timelog: pl.DataFrame,
    db_path: str,
) -> None:
    try:
        existing_ids = pl.read_database_uri(
            'select id from time_entries',
            f"sqlite:///{db_path}"
        ).get_column('id').to_list()
    except Exception as e:
        print(f"Error getting existing IDs from Toggl database: {e}")
        existing_ids = []
    #
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







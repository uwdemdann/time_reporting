import dotenv
import polars as pl
import plotnine as pn

# from run_toggl_to_sql import fn_update_toggl_database
# fn_update_toggl_database(drop_db=True)


db_path = dotenv.get_key('.env', 'DB_PATH')

try:
    df_time_entries = pl.read_database_uri(
        'select * from time_entries',
        f"sqlite:///{db_path}"
    )
except Exception as e:
    print(f"Error getting time entries from Toggl database: {e}")

# Data Integrity Checks
df_entries_to_fix = df_time_entries.filter(
    pl.col('client_name').eq('') |
    pl.col('client_name').is_null()
).select(['id', 'toggl_user_name', 'description', 'start', 'project_name'])
df_entries_to_fix

df_time_entries.filter(
    ~pl.col('client_name').is_in([
        "Research: Externally Funded",
        "Education",
        "Administrative/Leadership",
        "Research: UW/DEM Funded",
        "Clinical",
        "PTO"
    ])
)

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

df_gg_by_da_client = df_time_entries.group_by(
    ['toggl_user_name', 'client_name']
).agg(
    (pl.sum('duration') / 3600).alias('hours')
)

df_gg_by_month_client = df_time_entries.group_by(
    ['month', 'client_name']
).agg(
    (pl.sum('duration') / 3600).alias('hours')
)

gg_by_month_client = pn.ggplot(
    df_gg_by_month_client,
    pn.aes(
        x='month',
        y='hours',
        fill='client_name')
) + pn.geom_bar(
    stat='identity',
    position='stack'
)

gg_by_month_client.show()




df_gg_by_da_client.filter(
    ~pl.col('client_name').is_null()
).select(
    pl.col('toggl_user_name').alias('Analyst'),
    pl.col('client_name').alias('Mission'),
    pl.col('hours'),
    (pl.col('hours') / pl.sum('hours').over('toggl_user_name')).alias('percent')
).pivot(
    on='Analyst',
    index='Mission',
    values='percent'
)
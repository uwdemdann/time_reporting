import requests
import dotenv
import pandas as pd
import polars as pl



# api_values = {
#     'API_URL': "https://api.track.toggl.com/reports/api/v2/details",
#     #'API_KEY': dotenv.get_key('.env', 'TOGGL_KEY_DANN'),
#     'API_KEY': dotenv.get_key('.env', 'TOGGL_KEY_ADAM'),
#     'ORG_ID': dotenv.get_key('.env', 'TOGGL_ORG_ID'),
#     'WS_ID': dotenv.get_key('.env', 'TOGGL_WORKSPACE_ID')
# }

def fn_get_toggl_time_entries(
    api_values: dict[str, str, str, str],
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    params = {
        'date_from': f"{start_date}T00:00:00+06:00",
        'date_to': f"{end_date}T23:59:59+06:00",
        'include_taskless': 'true',
        'per_page': 100,
        'page': 0
    }
    more_pages = True
    while more_pages:
        params['page'] = params['page']+1
        resp_timelog = requests.get(
            f"https://focus.toggl.com/api/organizations/{api_values['ORG_ID']}/workspaces/{api_values['WS_ID']}/time-entries",
            params=params,
            headers={
                'content-type': 'application/json',
                'Authorization': f"Bearer {api_values['API_KEY']}",
            },
        )
        df_logged_time_page = pd.DataFrame(resp_timelog.json().get('data'))
        if df_logged_time_page.empty:
            more_pages = False
            break
        if 'df_logged_time' in locals():
            df_logged_time = pd.concat([df_logged_time, df_logged_time_page], axis=0, join='outer', ignore_index=True)
        else:
            df_logged_time = df_logged_time_page
    return df_logged_time


def fn_parse_toggl_time_entries(df_logged_time: pd.DataFrame) -> pl.DataFrame:
    df_ret = pl.from_pandas(df_logged_time[['id', 'project_id', 'type', 'toggl_user_id', 'start', 'duration', 'description', 'tags']])
    df_ret = df_ret.with_columns(
        month=pl.col('start').str.to_datetime(time_zone='America/Chicago').dt.month_start().dt.date(),
        tags=pl.col('tags').list.eval(pl.element().struct.field('name')).list.join(';'),
        project_id=pl.col('project_id').cast(pl.Int64)
    )
    return df_ret

def fn_get_toggl_static_files(api_values: dict[str, str, str, str]) -> dict[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Projects
    resp_projects = requests.get(
        f"https://focus.toggl.com/api/organizations/{api_values['ORG_ID']}/workspaces/{api_values['WS_ID']}/projects",
        headers={
            'content-type': 'application/json',
            'Authorization': f"Bearer {api_values['API_KEY']}",
        },
    )
    df_projects = pd.DataFrame(resp_projects.json().get('data'))
    # Clients
    resp_clients = requests.get(
        f"https://focus.toggl.com/api/workspaces/{api_values['WS_ID']}/clients",
        headers={
            'content-type': 'application/json',
            'Authorization': f"Bearer {api_values['API_KEY']}",
        },
    )
    df_clients = pd.DataFrame(resp_clients.json().get('data'))
    # Users - Hard-coded for now
    df_users = pd.DataFrame({
        'toggl_user_id': [7660114, 7671570],
        'toggl_user_name': ['Dann', 'Adam']
    }).convert_dtypes()
    ret_dict = {
        'df_projects': df_projects[['id', 'name', 'client_id']].rename(columns={'id': 'project_id', 'name': 'project_name'}),
        'df_clients': df_clients[['id', 'name']].rename(columns={'id': 'client_id', 'name': 'client_name'}),
        'df_users': df_users
    }
    return ret_dict

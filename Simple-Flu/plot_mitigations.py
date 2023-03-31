import pandas as pd
import numpy as np

def get_states(job):
    states = pd.DataFrame()
    states['sim_date']=job.get_job_date_table().sim_date
    for x in ["Exposed", "InfectiousSymptomatic", "InfectiousAsymptomatic", "Recovered"]:
        counts = job.get_job_state_table(
            condition="RESP_DISEASE",
            state=x,
            count_type="new",)

        counts.rename(columns={'new':x},inplace=True)
        states = pd.merge(states, counts[x], left_index=True, right_index=True)

    states.rename(
        columns={'InfectiousAsymptomatic':'InfectiousA',
                 'InfectiousSymptomatic':'InfectiousS'},
        inplace=True)
    return states

def get_explocs(job):
    exp_data = job.runs[1].get_csv_output("exposure_locs.csv")
    exp_data['today'] = pd.to_datetime(exp_data['today'],format="%Y%m%d")
    exp_data["simday"] = (pd.to_datetime(exp_data.today) - pd.to_datetime("2022-01-01")).dt.days
    exp_data = exp_data.assign(ExposureLocation = exp_data.my_resp_exp_loc.map({-1:'InitialExposure', 0:'Other', 
                               1:'Household', 2:'BlockGroup', 3:'CensusTract',
                               4:'County', 5:'School', 6:'Workplace'},))
    return exp_data

def get_expmap_data(job):
    exp_data = get_explocs(job)
    exposure_locations = exp_data[exp_data.my_exp_lat!=0].groupby(["my_exp_lat", "my_exp_lon", "ExposureLocation"]).size().to_frame().reset_index().rename(columns={0:"NumberExposed"})
    exposure_locations = exposure_locations.assign(exp_scale=np.log10(exposure_locations.NumberExposed+0.5))
    return exposure_locations
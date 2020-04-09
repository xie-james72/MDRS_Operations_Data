import re

import bs4
import pandas as pd
import requests

# Initialize data arrays and parameters
pages = 53

(report_date, sol, writer, Non_Nom_Sys, Non_Nom_Notes, Generator, Solar, Diesel, Propane, Gasoline, Water_Loft,
 Water_Meter, Water_Tank, Pump_Use, Water_Greenhab, Water_Science, Toilet_Emptied, Perseverance, Sojourner, Spirit,
 Opportunity, Curiosity, Deimos, Rover_Notes, ATV_Use, HabCar, CrewCar, General_Notes, Internet_State, Suits_State,
 Obs_State, HS_State, HAB_Ops, Green_Ops, Science_Ops, RAM_Ops, Questions) = ([] for i in range(37))

data = [report_date, sol, writer, Non_Nom_Sys, Non_Nom_Notes, Generator, Solar, Diesel, Propane, Gasoline,
        Water_Loft, Water_Meter, Water_Tank, Pump_Use, Water_Greenhab, Water_Science, Toilet_Emptied, Perseverance,
        Sojourner, Spirit, Opportunity, Curiosity, Deimos, Rover_Notes, ATV_Use, HabCar, CrewCar, General_Notes,
        Internet_State, Suits_State, HAB_Ops, Green_Ops, Science_Ops, Obs_State, RAM_Ops, HS_State, Questions]

srchtxt = ['Operations Report', 'SOL:', 'Name of', 'Non-nominal', 'Notes on non', 'Generator:', 'Solar', 'Diesel',
           'Propane', 'Ethanol', 'loft tank', 'Water Meter', 'static tank', 'static to loft pump', 'Water in GreenHab',
           'Water in ScienceDome', 'Toilet tank', 'Perseverance', 'Sojourner', 'Spirit', 'Opportunity', 'Curiosity',
           'Deimos', 'Notes on rovers', ['ATVs', 'ATV’s'], 'HabCar', 'CrewCar', 'General notes', 'internet',
           'suits and radios', 'Summary of Hab', 'Summary of GreenHab', 'Summary of ScienceDome', 'Summary of any',
           'Summary of RAM', 'Summary of health', 'Questions']

def tstrp(txtstr, *args):
    # This function will remove the first instance of each supplied *args string as well as any non-alphanumeric
    # characters except _, -, ., and %
    # Next stept to also reformatting data to be useful, e.g. Nominal = Nothing to Report = N/A = Yes = 1; no = 0
    # If no txtstr is supplied, then nothing will happen
    if txtstr is None:
        return txtstr

    result = re.sub(r'[^\w.%]', ' ', txtstr)
    for spltstr in args:
        result = re.sub(spltstr, '', result, 1, flags=re.I)
    return result.strip()

def datxt(darr, dsoup, txtstr):
    # This function searches for the first instance of any strings in *args in a soup entry
    # and appends it to a given array
    j = 0
    if type(txtstr) is str:
        txtstr = [txtstr]
    while True:
        textstring = dsoup.find(text=re.compile(txtstr[j], re.I))
        j += 1
        if textstring is not None or j >= len(txtstr):
            darr.append(textstring)
            break
    return

# Data scraping loop
for pagenumber in range(pages):
    print('Scraping page ' + str(pagenumber) + '...')
    url = 'https://mdrs.marssociety.org/category/operations-report/page/' + str(pagenumber)
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser").find_all('div', attrs={'class': "entry-content"})

    for entry in soup:
        if not entry.find_all('pre'):
            for t, col in enumerate(data):
                datxt(col, entry, srchtxt[t])
            # extract crew, date from report header?
            # missing: hours run, from what time last night to what time this morning, any additional daytime hours
            # missing hours, beginning charge, ending charge, and currently charging
            # all of these should be sibling tags in the soup
            # locate each rover's tag then proceed down siblings
            # missing reason for use, oil added?, fuel use, hours of use, other notes
        else:
            # for those entries which are just one large block of text, we forget them and just append a space.
            for col in data:
                col.append('')

# Cleaning data entries of unnecessary text
report_date = [tstrp(i, 'Operations Report') for i in report_date]
sol = [tstrp(i, 'SOL') for i in sol]
writer = [tstrp(i, 'Name of person filing report') for i in writer]
Non_Nom_Sys = [tstrp(i, 'Non nominal systems') for i in Non_Nom_Sys]
Non_Nom_Notes = [tstrp(i, 'Notes on non nominal systems') for i in Non_Nom_Notes]
Generator = [tstrp(i, 'Generator') for i in Generator]
Solar = [tstrp(i, 'Solar', 'Before', 'the', 'generator is run at night', r'(\s)SOC\S+', 'SOC', 'SOC %', '% ') for i in
         Solar]
Diesel = [tstrp(i, 'Diesel', 'Reading') for i in Diesel]
Propane = [tstrp(i, 'Station', 'Propane', 'Reading') for i in Propane]
Gasoline = [
    tstrp(i, 'Ethanol', 'Free', 'Gasoline', 'ATV Fuel', 'gallons', '5 Gallon containers for ATV') for i in Gasoline]
Water_Loft = [tstrp(i, 'Water', 'loft tank', r'(\s)gal\w+', 'gal') for i in Water_Loft]
Water_Meter = [tstrp(i, 'Water Meter', 'units') for i in Water_Meter]
Water_Tank = [tstrp(i, 'Water', 'static tank', r'(\s)gal\w+', 'gal') for i in Water_Tank]
Pump_Use = [tstrp(i, 'Static to Loft Pump used') for i in Pump_Use]
Water_Greenhab = [tstrp(i, 'Water in GreenHab', r'(\s)gal\w+', 'gal') for i in Water_Greenhab]
Water_Science = [tstrp(i, 'Water in ScienceDome', 'gallons') for i in Water_Science]
Toilet_Emptied = [tstrp(i, 'Toilet tank emptied') for i in Toilet_Emptied]
Perseverance = [tstrp(i, 'Perseverance rover used') for i in Perseverance]
Sojourner = [tstrp(i, 'Sojourner rover used') for i in Sojourner]
Spirit = [tstrp(i, 'Spirit', 'rover', 'used') for i in Spirit]
Opportunity = [tstrp(i, 'Opportunity', 'rover', 'used') for i in Opportunity]
Curiosity = [tstrp(i, 'Curiosity rover used') for i in Curiosity]
Deimos = [tstrp(i, 'Deimos', 'rover', 'used') for i in Deimos]
Rover_Notes = [tstrp(i, 'Notes on', 'rovers') for i in Rover_Notes]
ATV_Use = [
    tstrp(i, 'ATV s', 'Used', 'Notes on', 'ATVs', 'Hours the', 'were', 'today', 'Reason for use') for i in ATV_Use]
HabCar = [tstrp(i, 'HabCar', 'used', 'and why  where') for i in HabCar]
CrewCar = [tstrp(i, 'CrewCar used and why  where') for i in CrewCar]
General_Notes = [tstrp(i, 'General notes and comments') for i in General_Notes]
Internet_State = [tstrp(i, 'Summary', 'of', 'the', 'internet') for i in Internet_State]
Suits_State = [tstrp(i, 'Summary of suits and radios') for i in Suits_State]
Obs_State = [tstrp(i, 'Summary of any observatory issues') for i in Obs_State]
HS_State = [tstrp(i, 'Summary of health and safety issues') for i in HS_State]
HAB_Ops = [tstrp(i, 'Summary', 'of', 'Hab', 'operations') for i in HAB_Ops]
Green_Ops = [tstrp(i, 'Summary of GreenHab operations') for i in Green_Ops]
Science_Ops = [tstrp(i, 'Summary of ScienceDome operations') for i in Science_Ops]
RAM_Ops = [tstrp(i, 'Summary of', 'RAMM', 'RAM', 'operations') for i in RAM_Ops]
Questions = [tstrp(i, 'Questions  concerns', 'and requests to Mission Support') for i in Questions]

# Exporting data
df = pd.DataFrame({'Report Date': report_date, 'Sol': sol, 'Writer': writer, 'Non-Nominal Systems': Non_Nom_Sys,
                   'Notes on Non-Nom. Sys': Non_Nom_Notes, 'Generator': Generator, 'Solar (SOC%)': Solar,
                   'Diesel': Diesel, 'Propane': Propane, 'Ethanol-Free Gasoline (gal)': Gasoline,
                   'Water: Loft Tank (gal)': Water_Loft, 'Water: Meter (units)': Water_Meter,
                   'Water: Static Tank (gal)': Water_Tank, 'Pump Use': Pump_Use,
                   'Water in GreenHab (gal)': Water_Greenhab, 'Water in ScienceDome (gal)': Water_Science,
                   'Toilet Emptied?': Toilet_Emptied, 'Perseverance': Perseverance, 'Sojourner': Sojourner,
                   'Spirit': Spirit, 'Opportunity': Opportunity, 'Curiosity': Curiosity, 'Deimos': Deimos,
                   'Rover Notes': Rover_Notes, 'ATV': ATV_Use, 'HabCar': HabCar, 'CrewCar': CrewCar,
                   'General Notes': General_Notes, 'Internet Status': Internet_State,
                   'Suits & Radio Status': Suits_State, 'Observatory': Obs_State, 'Health & Safety': HS_State,
                   'HAB Notes': HAB_Ops, 'GreenHab Notes': Green_Ops, 'ScienceDome Notes': Science_Ops,
                   'RAM Notes': RAM_Ops, 'Questions': Questions})

df.to_csv('MDRS_Operations.csv', index=False, encoding='utf-8')

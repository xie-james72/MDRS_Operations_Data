import re

import bs4
import pandas as pd
import requests

# What analysis can we do with this data?
# Efficiency of the rovers over time
# water usage over time
# power usage over time

# Next steps to also reformatting data to be useful, e.g. Nominal = Nothing to Report = N/A = Yes = 1; no = 0

# Initialize data arrays and parameters
pages = 52


class rover:
    def __init__(self, Rover_name):
        self.hours = []
        self.charge_start = []
        self.charge_end = []
        self.charge_status = []
        self.name = Rover_name

    def populate(self, dsoup):
        rover_text = dsoup.find(text=re.compile(self.name))

        if rover_text is not None:
            self.hours.append(rover_text.findNext(text=re.compile('Hours')))
            self.charge_start.append(rover_text.findNext(text=re.compile('Beginning')))
            self.charge_end.append(rover_text.findNext(text=re.compile('Ending')))
            self.charge_status.append(rover_text.findNext(text=re.compile('Currently')))
        else:
            self.hours.append('')
            self.charge_start.append('')
            self.charge_end.append('')
            self.charge_status.append('')

    def cleanup(self):
        self.hours = [tstrp(i, ['Hours']) for i in self.hours]
        self.charge_start = [tstrp(i, ['Beginning charge']) for i in self.charge_start]
        self.charge_end = [tstrp(i, ['Ending charge']) for i in self.charge_end]
        self.charge_status = [tstrp(i, ['Currently charging']) for i in self.charge_status]


def datxt(darr, dsoup, txtstr):
    # This function searches for the first instance of a string in *args in a soup entry and appends it to a given array
    flag = 0
    for j in range(len(txtstr)):
        textstring = dsoup.find(text=re.compile(txtstr[j], re.I))
        if textstring is not None:
            darr.append(textstring)
            flag = 1
            break
    if flag == 0:
        darr.append('')
    return


def tstrp(input_string, removal_string):
    # This function will remove the first instance of each supplied *args string as well as any non-alphanumeric
    # characters except _, -, ., and %. If no string is supplied, nothing will happen.
    if input_string is None:
        return input_string
    result = re.sub(r'[^\w.%]', ' ', input_string)
    for spltstr in removal_string:
        result = re.sub(spltstr, '', result, 1, flags=re.I)
    return result.strip()


def txtclean(darr, txtstr):
    darr = [tstrp(i, txtstr) for i in darr]
    return darr


(report_date, sol, writer, Non_Nom_Sys, Non_Nom_Notes, Generator, Solar, Diesel, Propane, Gasoline, Water_Loft,
 Water_Meter, Water_Tank, Pump_Use, Water_Greenhab, Water_Science, Toilet_Emptied, Perseverance, Sojourner, Spirit,
 Opportunity, Curiosity, Deimos, Rover_Notes, ATV_Use, HabCar, CrewCar, General_Notes, Internet_State, Suits_State,
 Obs_State, HS_State, HAB_Ops, Green_Ops, Science_Ops, RAM_Ops, Questions) = ([] for i in range(37))

data = [report_date, sol, writer, Non_Nom_Sys, Non_Nom_Notes, Generator, Solar, Diesel, Propane, Gasoline,
        Water_Loft, Water_Meter, Water_Tank, Pump_Use, Water_Greenhab, Water_Science, Toilet_Emptied, Perseverance,
        Sojourner, Spirit, Opportunity, Curiosity, Deimos, Rover_Notes, ATV_Use, HabCar, CrewCar, General_Notes,
        Internet_State, Suits_State, HAB_Ops, Green_Ops, Science_Ops, Obs_State, RAM_Ops, HS_State, Questions]

srchtxt = [['Operations Report'], ['SOL:'], ['Name of'], ['Non-nominal'], ['Notes on non'], ['Generator:'], ['Solar'],
           ['Diesel'], ['Propane'], ['Ethanol'], ['loft tank'], ['Water Meter'], ['static tank'],
           ['static to loft pump'], ['Water in GreenHab'], ['Water in ScienceDome'], ['Toilet tank'], ['Perseverance'],
           ['Sojourner'], ['Spirit'], ['Opportunity'], ['Curiosity'], ['Deimos'], ['Notes on rovers'],
           ['ATVs', 'ATV’s'], ['HabCar'], ['CrewCar'], ['General notes'], ['internet'], ['suits and radios'],
           ['Summary of Hab'], ['Summary of GreenHab'], ['Summary of ScienceDome'], ['Summary of any'],
           ['Summary of RAM'], ['Summary of health'], ['Questions']]

cleaning_text = [['Operations Report'], ['SQL'], ['Name of person filing report'], ['Non nominal systems'],
                 ['Notes on non nominal systems'], ['Generator'],
                 ['Solar', 'Before', 'the', 'generator is run at night', r'(\s)SOC\S+', 'SOC', 'SOC %', '% '],
                 ['Diesel', 'Reading'], ['Station', 'Propane', 'Reading'],
                 ['Ethanol', 'Free', 'Gasoline', 'ATV Fuel', 'gallons', '5 Gallon containers for ATV'],
                 ['Water', 'loft tank', r'(\s)gal\w+', 'gal'], ['Water Meter', 'units'],
                 ['Water', 'static tank', r'(\s)gal\w+', 'gal'], ['Static to Loft Pump used'],
                 ['Water in GreenHab', r'(\s)gal\w+', 'gal'], ['Water in ScienceDome', 'gallons'],
                 ['Toilet tank emptied'], ['Perseverance rover used'], ['Sojourner rover used'],
                 ['Spirit', 'rover', 'used'], ['Opportunity', 'rover', 'used'], ['Curiosity rover used'],
                 ['Deimos', 'rover', 'used'], ['Notes on', 'rovers'],
                 ['ATV s', 'Used', 'Notes on', 'ATVs', 'Hours the', 'were', 'today', 'Reason for use'],
                 ['HabCar', 'used', 'and why  where'], ['CrewCar used and why  where'], ['General notes and comments'],
                 ['Summary', 'of', 'the', 'internet'], ['Summary of suits and radios'],
                 ['Summary', 'of', 'Hab', 'operations'], ['Summary of GreenHab operations'],
                 ['Summary of ScienceDome operations'], ['Summary of any observatory issues'],
                 ['Summary of', 'RAMM', 'RAM', 'operations'], ['Summary of health and safety issues'],
                 ['Questions  concerns', 'and requests to Mission Support']]

Deimos_data = rover('Deimos')
Curiosity_data = rover('Curiosity')
Spirit_data = rover('Spirit')
Sojourner_data = rover('Sojourner')
Opportunity_data = rover('Opportunity')
Perseverance_data = rover('Perseverance')

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
            # missing reason for use, oil added?, fuel use, hours of use, other notes
            Deimos_data.populate(entry)
            Curiosity_data.populate(entry)
            Spirit_data.populate(entry)
            Sojourner_data.populate(entry)
            Opportunity_data.populate(entry)
            Perseverance_data.populate(entry)


# Cleaning data entries of unnecessary text
for t, col in enumerate(data):
    data[t] = txtclean(col, cleaning_text[t])

Deimos_data.cleanup()
Curiosity_data.cleanup()
Spirit_data.cleanup()
Sojourner_data.cleanup()
Opportunity_data.cleanup()
Perseverance_data.cleanup()


# Exporting data
df = pd.DataFrame({'Report Date': data[0], 'Sol': data[1], 'Writer': data[2], 'Non-Nominal Systems': data[3],
                   'Notes on Non-Nom. Sys': data[4], 'Generator': data[5], 'Solar (SOC%)': data[6],
                   'Diesel': data[7], 'Propane': data[8], 'Ethanol-Free Gasoline (gal)': data[9],
                   'Water: Loft Tank (gal)': data[10], 'Water: Meter (units)': data[11],
                   'Water: Static Tank (gal)': data[12], 'Pump Use': data[13], 'Water in GreenHab (gal)': data[14],
                   'Water in ScienceDome (gal)': data[15], 'Toilet Emptied?': data[16], 'Perseverance': data[17],
                   'Sojourner': data[18], 'So_Hours': Sojourner_data.hours,
                   'So_Charge_Start': Sojourner_data.charge_start, 'So_Charge_End': Sojourner_data.charge_end,
                   'So_Charge_Status': Sojourner_data.charge_status, 'Spirit': data[19], 'Sp_Hours': Spirit_data.hours,
                   'Sp_Charge_Start': Spirit_data.charge_start, 'Sp_Charge_End': Spirit_data.charge_end,
                   'Sp_charge_Status': Spirit_data.charge_status, 'Opportunity': data[20],
                   'O_Hours': Opportunity_data.hours, 'O_charge_start': Opportunity_data.charge_start,
                   'O_charge_end': Opportunity_data.charge_end, 'O_charge_status': Opportunity_data.charge_status,
                   'Curiosity': data[21], 'C_Hours': Curiosity_data.hours,
                   'C_charge_start': Curiosity_data.charge_start, 'C_charge_end': Curiosity_data.charge_end,
                   'C_charge_status': Curiosity_data.charge_status, 'Deimos': data[22], 'D_Hours': Deimos_data.hours,
                   'D_Charge_Start': Deimos_data.charge_start, 'D_Charge_End': Deimos_data.charge_end,
                   'D_Charge_Status': Deimos_data.charge_status, 'Rover Notes': data[23], 'ATV': data[24],
                   'HabCar': data[25], 'CrewCar': data[26], 'General Notes': data[27], 'Internet Status': data[28],
                   'Suits & Radio Status': data[29], 'Observatory': data[30], 'Health & Safety': data[31],
                   'HAB Notes': data[32], 'GreenHab Notes': data[33], 'ScienceDome Notes': data[34],
                   'RAM Notes': data[35], 'Questions': data[36]})

df.to_csv('MDRS_Operations.csv', index=False, encoding='utf-8')

# Close CRM Search & Find duplicate Leads

A Simple Python script that helps to find duplicate Leads within the Close CRM. It compares Name, phone and email in any variation. 

## Usage
To use it you will need to place your API-Key from Close in line 7 of the search_dups.py. The API-Key can be generated in Close Settings->Developer->+New API Key.

Also you might have to adjust the limit of fetched Leads in Line 121. Currently its set to 4000 Leads.

To run the script install the dependencies from the requirements.txt with `pip install -r requirements.txt`. Then run the script using: `python search_dups.py`

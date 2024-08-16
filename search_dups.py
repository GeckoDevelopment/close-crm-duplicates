import requests
from requests.auth import HTTPBasicAuth
from itertools import combinations
from urllib.parse import urlparse, parse_qs, urlunparse

# Replace 'YOUR_API_KEY' with your actual Close CRM API key
API_KEY = ''
BASE_URL = 'https://api.close.com/api/v1/lead/'


def fetch_leads(limit=200):
    leads = []
    has_more = True
    offset = 0

    while has_more and len(leads) < limit:
        response = requests.get(
            BASE_URL,
            auth=HTTPBasicAuth(API_KEY, ''),
            params={'_skip': offset, '_limit': min(100, limit - len(leads))}
        )
        
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print("Response content:", response.content)
            break
        
        data = response.json()
        
        if 'data' not in data:
            print("Error: 'data' key not found in the response")
            print("Response content:", data)
            break
        
        leads.extend(data['data'])
        has_more = data.get('has_more', False)
        offset += len(data['data'])

    return leads[:limit]

def normalize_phone(phone):
    """Normalize phone numbers by removing formatting characters"""
    return ''.join(filter(str.isdigit, phone))

def normalize_url(url):
    """Normalize URL by removing query parameters and fragment"""
    parsed_url = urlparse(url)
    normalized_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    return normalized_url.lower()

def find_duplicates(leads):
    duplicates = {
        'name': {},
        'phone': {},
        'email': {},
        'url': {}
    }
    lead_details = {}  # To store full lead details keyed by lead_id

    for lead in leads:
        lead_id = lead['id']
        lead_details[lead_id] = lead  # Store full lead details

        contacts = lead.get('contacts', [])
        lead_urls = [lead.get('url', '').strip().lower()] if lead.get('url') else []
        #lead_urls.extend(url.get('url').strip().lower() for contact in contacts for url in contact.get('integration_links', []))
        lead_urls = list(filter(None, lead_urls))  # Remove empty URLs
        lead_urls = [normalize_url(url) for url in lead_urls]  # Normalize URLs

        for contact in contacts:
            names = [contact.get('display_name', '').strip().lower()]
            phones = [normalize_phone(phone['phone']) for phone in contact.get('phones', []) if phone.get('phone')]
            emails = [email.get('email', '').strip().lower() for email in contact.get('emails', [])]

            # Detect duplicate names
            for name in names:
                if name:
                    if name in duplicates['name']:
                        duplicates['name'][name].add(lead_id)
                    else:
                        duplicates['name'][name] = {lead_id}

            # Detect duplicate phones
            for phone in phones:
                if phone:
                    if phone in duplicates['phone']:
                        duplicates['phone'][phone].add(lead_id)
                    else:
                        duplicates['phone'][phone] = {lead_id}

            # Detect duplicate emails
            for email in emails:
                if email:
                    if email in duplicates['email']:
                        duplicates['email'][email].add(lead_id)
                    else:
                        duplicates['email'][email] = {lead_id}

        # Detect duplicate URLs
        for url in lead_urls:
            if url:
                if url in duplicates['url']:
                    duplicates['url'][url].add(lead_id)
                else:
                    duplicates['url'][url] = {lead_id}

    return duplicates, lead_details

def print_duplicates(duplicates, lead_details):
    print("Duplicate Leads Found:")

    for category, items in duplicates.items():
        for key, lead_ids in items.items():
            if len(lead_ids) > 1:
                print(f"\nDuplicate {category.capitalize()}: {key}")
                for lead_id in lead_ids:
                    lead = lead_details[lead_id]
                    print(f"- Lead ID: {lead['id']}, Name: {lead.get('display_name', 'N/A')}, URL: {lead.get('url', 'N/A')}")

if __name__ == '__main__':
    leads = fetch_leads(limit=4000)
    if leads:
        duplicates, lead_details = find_duplicates(leads)
        print_duplicates(duplicates, lead_details)

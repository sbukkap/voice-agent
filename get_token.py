import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# The permission scope needed to create calendar events
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def main():
    creds = None
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

    # This opens your browser to log in and grant permission
    creds = flow.run_local_server(port=0)

    # Save the credentials for the FastAPI server to use
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    print("Success! token.json has been created.")

if __name__ == '__main__':
    main()
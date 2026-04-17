from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret_2_223778784289-9cv97snbb1tuennjbdqqkaj60ol40d4e.apps.googleusercontent.com.json',
    scopes=['https://www.googleapis.com/auth/adwords']
)
creds = flow.run_local_server(port=0)
print(creds.refresh_token)

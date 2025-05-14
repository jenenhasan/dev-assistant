#from google.oauth2 import credentials 
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from typing import Dict , List , Optional
from datetime import datetime , timedelta




class EmailManager: 
    def __init__(self , token_file = 'token.json' , creds_file = 'credentials.json') :
        self.SCOPES = ['https://mail.google.com/',  # Full access scope that covers everything
            'https://www.googleapis.com/auth/contacts.readonly'
       
        ]
        #self.creds = self.authentication()
        self.token_file = token_file
        self.creds_file = creds_file
        self.creds = self.authentication()
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.contacts_service = build('people', 'v1', credentials=self.creds)


    def authentication(self) : 
        creds = None 
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file , self.SCOPES)

        if not creds or not creds.valid : 
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else : 
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_file , 'w') as token : 
                token.write(creds.to_json())

        return creds
    
    def find_email_by_name(self , name , max_results=5):
        try:
            contacts = set()
            inbox = self.service.users().messages().list(userId='me', maxResults=50).execute()
            inbox_mssg = inbox.get('messages' , [])

            for msg in inbox_mssg : 
                msg_details = self.service.users().messages().get(userId = 'me' , id=msg['id'] , format='metadata' , metadataHeaders=['From']).execute()
                headers=msg_details['payload']['headers']
                for header in headers:
                    if header['name'] == 'From':
                        contacts.add(header['value'])


            sent = self.service.users().messages().list(userId='me', labelIds=['SENT'], maxResults=50).execute()
            sent_messages = sent.get('messages' , [])
            for msg in sent_messages:
                msg_detail = self.service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['To']).execute()
                headers = msg_detail['payload']['headers']
                
                for header in headers:
                    if header['name'] == 'To':
                        contacts.add(header['value'])

            searched_contacts = []
            for contact in contacts :
                if name.lower() in contact.lower():
                    searched_contacts.append(contact)
            return searched_contacts[:max_results]
        except Exception as e :
            print ("An error occured:" , str(e))
            return {'success': False, 'error': str(e)}


    
    ###
    def send_email(self , to , body: str , schedule_time : Optional[datetime] = None)-> Dict :
        
        to_email = self.find_email_by_name(to)
        if not to_email:
            return {'success': False, 'error': 'No email address found for the recipient.'}
        message = self._create_message(to_email[0], body) 
        if schedule_time : 
            return self._schedule_send(message , schedule_time)
        try : 
            sent = self.service.users().messages().send(
                userId='me',
                body={'raw': message}
            ).execute()
            return {'success': True, 'message_id': sent['id']}
        except Exception as e : 
            return  {'success': False, 'error': str(e)}
        

    def _schedule_send(self , message , send_time: datetime) : 
        try:
            # Gmail API only supports future scheduling
            if send_time < datetime.now() + timedelta(minutes=1):
                return {'success': False, 'error': 'Schedule time must be at least 1 minute in future'}
            
            # This requires Gmail API with scheduled send enabled
            sent = self.service.users().messages().send(
                userId='me',
                body={
                    'raw': message,
                    'internalDate': int(send_time.timestamp() * 1000)
                }
            ).execute()
            return {'success': True, 'message_id': sent['id']}
        except Exception as e:
            return {'success': False, 'error': str(e)}


    def _create_message(self , to , body) :
        from email.mime.text import MIMEText
        import base64
        message = MIMEText(body)
        
        message['to'] = to
        message['body'] = body 
       # message['subject'] = subject 
        return base64.urlsafe_b64encode(message.as_bytes()).decode()

    ##read just the headlines for in the inbox 
    def read_emails_headlines(self , max_results=10) : 
        results = self.service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD'],
            maxResults=max_results,
            #fields='messages(id,payload/headers)'
        ).execute()
        
        emails = []
        for msg in results.get('messages', []):
            full_msg = self.service.users().messages().get(
                userId='me',
                id=msg['id']

            ).execute()
            payload = full_msg.get('payload')
            headers_list = payload.get('headers')
            headers = {h['name']: h['value'] for h in headers_list if h['name'] in ['From', 'Subject']}
            emails.append({
                'id': msg['id'],
                'from': headers.get('From', 'Unknown'),
                'subject': headers.get('Subject', 'No Subject')
            })
        return emails
    
    def search_email_by_subject(self , query) :
        results = self.service.users().messages().list(
            userId='me',
            q=f"subject:{query}",
            
        ).execute()
        emails= []
        for msg in results.get('messages' , []):
            full_msg =  self.service.users().messages().get(
                userId = 'me', 
                id = msg['id']
            ).execute()

            payload = full_msg.get('payload')
            if not payload : 
                continue
            header_list = payload.get('headers')
            if not header_list: 
                continue 
            headers = {h['name']: h['value'] for h in header_list if h['name'] in ['From', 'Subject']}
            emails.append({
                'id' : msg['id'],
                'from': headers.get('From', 'Unknown'),
                'subject': headers.get('Subject', 'No Subject')

            }
            )
        return emails

       
        


    def filter_emails(self):
        pass


    
        

if __name__ == "__main__":
    # First-run will open browser for authentication
    email_manager = EmailManager()
    
    # Test reading subjects
    print("Unread emails:")
    for email in email_manager.read_emails_headlines(max_results=3):
        print(f"From: {email['from']}, Subject: {email['subject']}")
    
    # Test searching
    print("\nSearch results:")
    for email in email_manager.search_email_by_subject("important"):
        print(f"From: {email['from']}, Subject: {email['subject']}")

    for email in email_manager.send_email('jenenhasan77@gmail.com' ,'reminder', 'replay to my email' ,):
        print("send sucessfully")


    result = email_manager.find_email_by_name('jenen')
   
    print("Search result:", result)


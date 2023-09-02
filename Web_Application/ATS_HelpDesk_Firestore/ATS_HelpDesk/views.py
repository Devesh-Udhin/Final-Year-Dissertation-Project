import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import date
from google.cloud import firestore as gc_firestore

# Firebase admin config
key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred)
db = firestore.client()
# End of Firebase admin config


# Authentication by pyrebase
import pyrebase

config = {
     "apiKey": "AIzaSyCJM6fqkODVsErEDkA1MxCR2zDld9jVMqg",
     "authDomain": "ats-helpdesk.firebaseapp.com",
     "databaseURL": "https://ats-helpdesk-default-rtdb.asia-southeast1.firebasedatabase.app",
     "projectId": "ats-helpdesk",
     "storageBucket": "ats-helpdesk.appspot.com",
     "messagingSenderId": "782388218722",
     "appId": "1:782388218722:web:aead06c84fae82f445ba3b",
     "measurementId": "G-YRKXS4GX4P"
}

pyrebase_firebase = pyrebase.initialize_app(config)
pyrebase_auth = pyrebase_firebase.auth()
pyrebase_database = pyrebase_firebase.database()
# End of Authentication by pyrebase

techDisctionary = {
     "GRP_0": "tech0@gmail.com",
     "GRP_1": "tech1@gmail.com",
     "GRP_2": "tech2@gmail.com",
     "GRP_3": "tech3@gmail.com",
     "GRP_4": "tech4@gmail.com",
     "GRP_5": "tech5@gmail.com",
     "GRP_6": "tech6@gmail.com",
     "GRP_7": "tech7@gmail.com",
}

# =============================================Start Sign in=======================================

def sign_in(email, password):
     try:
          pyrebase_auth.sign_in_with_email_and_password(email, password)
          return True
     except:
          return False

# =============================================End Sign in=========================================

# =============================================Start Tickets Table=================================

def DisplayTicket(caller):
     results = []
     docs = db.collection('Tickets').where('Caller', '==', caller).get()
     for doc in docs:
          data = doc.to_dict()
          data['id'] = doc.id
          results.append(data)
     return results

def DisplayTicketDetails(ticketID):
     result = db.collection('Tickets').document(ticketID).get()
     ticket = result.to_dict()
     ticket['id'] = result.id
     
     return ticket

def DeleteTickets(ticketID):
     db.collection('Tickets').document(ticketID).delete()
     return

def CreateTicket(ticketID, title, description, date, status, techAssigned, caller):
     
     data = {'Title':title, 'Description':description, 'Caller':caller, 'Date':date, 'TechAssigned':techAssigned, 'Status':status}
     db.collection('Tickets').document(ticketID).set(data)
     
def GetTechTickets(techEmail):
     results = []
     assignedTickets = db.collection('Tickets').where('TechAssigned', '==', techEmail).get()
     
     for assignedTicket in assignedTickets:
          data = assignedTicket.to_dict()
          data['id'] = assignedTicket.id
          results.append(data)
     
     return results

# =============================================End Tickets Table===================================

# =============================================Start Resolved Table======================================

def DisplayTechResolvedTicket(Tech):
     results = []
     docs = db.collection('ResolvedTickets').where('TechResolved', '==', Tech).get()
     for doc in docs:
          data = doc.to_dict()
          data['id'] = doc.id
          results.append(data)
     return results

def DisplayTicketFeedback(caller):
     results = []
     docs = db.collection('ResolvedTickets').where('Caller', '==', caller).get()
     for doc in docs:
          data = doc.to_dict()
          data['id'] = doc.id
          results.append(data)
     return results

def GetResolvedTicket(ticketID):
     result = db.collection('ResolvedTickets').document(ticketID).get()
     ticket = result.to_dict()
     ticket['id'] = result.id
     return ticket

def UpdateResolvedTable(ticketID, Caller, Title, Description, Status, TechResolved, DateCreated, comment, how_ticket_was_resolve):
     DateResolved = date.today()
     # Convert the date to a Firestore timestamp
     DateResolved = gc_firestore.SERVER_TIMESTAMP if isinstance(DateResolved, type(date.today())) else DateResolved

     data = {'Caller':Caller, 'Title':Title, 'Description':Description, 'Status':Status, 'TechResolved':TechResolved, 'DateCreated':DateCreated, 'DateResolved':DateResolved, 'Comments':comment, 'HowTicketWasResolve':how_ticket_was_resolve}
     db.collection('ResolvedTickets').document(ticketID).set(data)

def DeleteResolvedTickets(ticketID):
     db.collection('ResolvedTickets').document(ticketID).delete()
     return

# =============================================End Resolved Table======================================

# ========================================Start Attention Required Table===============================

def DisplayAttentionRequiredTicket(caller):
     results = []
     docs = db.collection('AttentionRequiredTickets').where('Caller', '==', caller).where('Status', '==', 'Attention_Required').get()
     for doc in docs:
          data = doc.to_dict()
          data['id'] = doc.id
          results.append(data)
     return results

def DisplayAllAttentionRequiredTicket(ticketID):
     result = db.collection('AttentionRequiredTickets').document(ticketID).get()
     ticket = result.to_dict()
     ticket['id'] = result.id
     return ticket

def UpdateAttentionRequiredTable(ticketID, Caller, Title, Description, Status, TechAssigned, DateCreated, request_message):
     DateReturned = date.today()
     # Convert the date to a Firestore timestamp
     DateReturned = gc_firestore.SERVER_TIMESTAMP if isinstance(DateReturned, type(date.today())) else DateReturned

     data = {'Caller':Caller, 'Title':Title, 'Description':Description, 'Status':Status, 'TechAssigned':TechAssigned, 'DateCreated':DateCreated, 'DateReturned':DateReturned, 'Questions':request_message}
     db.collection('AttentionRequiredTickets').document(ticketID).set(data)
     
def DeleteAtentionRequiredTickets(ticketID):
     db.collection('AttentionRequiredTickets').document(ticketID).delete()
     return

# ========================================End Attention Required Table=================================

# ==========================================Start Responded Table======================================

def DisplayReturnedTicket(tech):
     results = []
     docs = db.collection('RespondedTickets').where('TechAssigned', '==', tech).where('Status', '==', 'Returned').get()
     for doc in docs:
          data = doc.to_dict()
          data['id'] = doc.id
          results.append(data)
     return results

def DisplayAllReturnedTicket(ticketID):
     result = db.collection('RespondedTickets').document(ticketID).get()
     ticket = result.to_dict()
     ticket['id'] = result.id
     return ticket
     
def UpdateReturnedTable(ticketID, Caller, Title, Description, TechAssigned, DateCreated, TechComment, UserComment):
     DateReturned = date.today()
     # Convert the date to a Firestore timestamp
     DateReturned = gc_firestore.SERVER_TIMESTAMP if isinstance(DateReturned, type(date.today())) else DateReturned

     data = {'Caller':Caller, 'Title':Title, 'Description':Description, 'Status':"Returned", 'TechAssigned':TechAssigned, 'DateCreated':DateCreated, 'DateReturned':DateReturned, 'TechComment':TechComment, 'UserComment':UserComment}
     db.collection('RespondedTickets').document(ticketID).set(data)

def DeleteReturnedTickets(ticketID):
     db.collection('RespondedTickets').document(ticketID).delete()
     return

# ==========================================End Responded Table========================================

# ============================================Start Escalated Table====================================

def DisplayTechEscalatedTicket(tech):
     results = []
     docs = db.collection('EscalatedTickets').where('TechTransferTo', '==', tech).get()
     for doc in docs:
          data = doc.to_dict()
          data['id'] = doc.id
          results.append(data)
     return results

def GetEscalatedTicket(ticketID):
     result = db.collection('EscalatedTickets').document(ticketID).get()
     ticket = result.to_dict()
     ticket['id'] = result.id
     return ticket

def UpdateEscalatedTable(ticketID, Caller, Title, Description, Status, TechEscalatedFrom, TechEscalatedTo, DateCreated, TechComment):
     DateEscalated = date.today()
     # Convert the date to a Firestore timestamp
     DateEscalated = gc_firestore.SERVER_TIMESTAMP if isinstance(DateEscalated, type(date.today())) else DateEscalated

     data = {'Caller':Caller, 'Title':Title, 'Description':Description, 'Status':Status, 'TechEscalatedFrom':TechEscalatedFrom, 'TechEscalatedTo':techDisctionary[TechEscalatedTo], 'DateCreated':DateCreated, 'DateEscalated':DateEscalated, 'TechComment':TechComment}
     db.collection('EscalatedTickets').document(ticketID).set(data)

def DeleteEscalatedTickets(ticketID):
     db.collection('EscalatedTickets').document(ticketID).delete()
     return

# ============================================End Escalated Table====================================

# =========================================Start Active Count========================================
def UpdateActiveCount(technician, action):

     transaction = db.transaction()
     # Reference to the document you want to update
     doc_ref = db.collection('Technicians').document(technician)

     if(action == 'increment'):
          # Define the increment amount
          value = 1
     else:
          # Define the increment amount
          value = -1
          
     # Use a transaction to increment the value
     @firestore.transactional
     def transaction_callback(transaction, doc_ref):
         snapshot = doc_ref.get(transaction=transaction)
         new_value = snapshot.get('ActiveCount') + value
         transaction.update(doc_ref, {'ActiveCount': new_value})

     transaction_callback(transaction, doc_ref)

def UpdateResolveCount(technician, action):

     transaction = db.transaction()
     # Reference to the document you want to update
     doc_ref = db.collection('Technicians').document(technician)

     if(action == 'increment'):
          # Define the increment amount
          value = 1
     else:
          # Define the increment amount
          value = -1
          
     # Use a transaction to increment the value
     @firestore.transactional
     def transaction_callback(transaction, doc_ref):
         snapshot = doc_ref.get(transaction=transaction)
         new_value = snapshot.get('ResolvedTicketCount') + value
         transaction.update(doc_ref, {'ResolvedTicketCount': new_value})

     transaction_callback(transaction, doc_ref)

# =========================================End Active Count========================================     

# =========================================Start Users Table=========================================

def GetUserType(email):
     userType = db.collection('Users').document(email).get()
     userType = userType.to_dict()
     return userType

# =========================================End Users Table=========================================

# =========================================Start Info Table=========================================

def GetTechList():
     techLists = db.collection('Info').document('Technicians').get()
     techListsDict = techLists.to_dict()

     tech_array_data = techListsDict.get('ListOfTechnicians', [])

     return tech_array_data

# =========================================End Info Table========================================     
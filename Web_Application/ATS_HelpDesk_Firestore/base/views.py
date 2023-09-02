from django.shortcuts import render, redirect
from . import data_preprocessing
import keras
import pandas as pd
import numpy as np
import os
from ATS_HelpDesk import views as firestore
from datetime import date
from google.cloud import firestore as gc_firestore
from django.contrib.auth import logout

# =============================================Start Login=======================================================

def Login(request):
     global caller
     caller = None
     logout(request)

     if request.method == 'POST':
          
          email = request.POST.get('email')
          password = request.POST.get('password')
          
          if firestore.sign_in(email, password) == True:
               user = firestore.GetUserType(email)
               request.session['user_email'] = email
               request.session['user_type'] = user['UserType']
               
               if request.session['user_type'] == "User":
                    return redirect('create_ticket/')
               
               elif request.session['user_type'] == "Technician":
                    return redirect('tech_dashboard/')
               
               elif request.session['user_type'] == "Admin":
                    return redirect('admin/')
          
          elif firestore.sign_in(email, password) == False:
               context = {'message': 'Invalid Credentials'}
               return render(request, 'base/login.html', context)
          
          else:
               return render(request, 'base/login.html')
          
     return render(request, 'base/login.html')

# =============================================End Login=========================================================

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Start User's Side<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# =============================================Start User's Pending Tickets list=================================

def TicketList(request):
     
     ticketLists = firestore.DisplayTicket(request.session['user_email'])
     
     return render(request, 'base/ticket_list.html', {'ticketLists':ticketLists})

# =============================================End User's Pending Tickets list===================================

# =============================================Start User's Create Ticket======================================
# load model
model_path = os.path.join(os.path.dirname(__file__), 'model.h5')
model = keras.models.load_model(model_path)

def CreateTicket(request):
     tech =''
     description = None
     title = None
     todayDate = None
     
     if request.method == 'POST':
          description = request.POST.get('description')
          title = request.POST.get('title')
          
          if description is None or title is None:
               return render(request, 'base/create_ticket.html')
          else: 
               preProcessDescription = data_preprocessing.pre_process_data(description)
               
               empty_list_of_lists = []
               empty_list_of_lists.append(preProcessDescription)
               
               vectorized_desc = data_preprocessing.getData(empty_list_of_lists)

               pred = model.predict(vectorized_desc)
               # df_pred = pd.DataFrame(pred, columns=['tech1@gmail.com', 'tech2@gmail.com', 'tech3@gmail.com', 'tech4@gmail.com', 'tech5@gmail.com', 'tech6@gmail.com', 'tech7@gmail.com', 'tech8@gmail.com'])
               
               final_pred = [i.argmax() for i in pred]
               # tech = "tech" + str(final_pred[0]) + "@gmail.com"

               # Use argsort to get the indices in descending order
               indices_descending = np.argsort(pred[0])[::-1]

               # Create a new list with "tech" before each index and "@gmail.com" after
               prediction_list = ["tech" + str(index) + "@gmail.com" for index in indices_descending]
               
               read()
               
               todayDate = date.today()
               # Convert the date to a Firestore timestamp
               timestamp = gc_firestore.SERVER_TIMESTAMP if isinstance(todayDate, type(date.today())) else todayDate
               status = 'Pending'
               caller = request.session.get('user_email')
     
               firestore.UpdateAllPredictionsTable(ticketID, prediction_list)
               maxActiveCount = firestore.GetMaxActiveCount()
               techActiveCountInRange = firestore.GetTechActiveCount(maxActiveCount['MaxCount'])
               
               key_to_compare = "id"
               
               for i in prediction_list:
                    for tech in techActiveCountInRange:
                         if i == tech.get(key_to_compare):
                              firestore.CreateTicket(ticketID, title, description, timestamp, status, tech, caller)
                              firestore.UpdateActiveCount(tech, "increment")
                              write()
                              return render(request, 'base/create_ticket.html')
               
     
     return render(request, 'base/create_ticket.html')

# =============================================End User's Create Ticket======================================

# =============================================Start User's Resolve Ticket===================================

def Resolve(request):
     
     ticketLists = firestore.DisplayTicketFeedback(request.session['user_email'])
     
     return render(request, 'base/resolve.html', {'ticketLists':ticketLists})

def ResolveDetails(request, ticketID):
     
     if request.method == 'POST':
          button_action = request.POST.get('button_action')
          
          if(button_action == 'back'):
               return redirect('/resolve/')
          
          elif(button_action == 're-send'):
               
               UserComment = request.POST.get('comment')
               ticket = firestore.GetResolvedTicket(ticketID)
               
               firestore.UpdateReturnedTable(ticketID, ticket['Caller'], ticket['Title'], ticket['Description'], ticket['TechResolved'], ticket['DateCreated'], ticket['Comments'], UserComment)
               firestore.DeleteResolvedTickets(ticketID)
               return redirect('/resolve/')
               
     
     ticketDetails = firestore.GetResolvedTicket(ticketID)
     
     return render(request, 'base/resolve_details.html', {'ticketDetails':ticketDetails})

# =============================================End User's Resolve Ticket=====================================

# ========================================Start User's Attention Required Ticket=============================

def AttentionRequired(request):
     
     ticketLists = firestore.DisplayAttentionRequiredTicket(request.session['user_email'])
     
     return render(request, 'base/attention_required.html', {'ticketLists':ticketLists})

def AttentionRequiredDetails(request, ticketID):
     
     if request.method == 'POST':
          button_action = request.POST.get('button_action')
          
          if(button_action == 'back'):
               return redirect('/attention_required/')
          
          elif(button_action == 'respond'):
               UserComment = request.POST.get('responce')
               ticket = firestore.DisplayAllAttentionRequiredTicket(ticketID)
               firestore.UpdateReturnedTable(ticketID, ticket['Caller'], ticket['Title'], ticket['Description'], ticket['TechAssigned'], ticket['DateCreated'], ticket['TechComment'], UserComment)
               firestore.DeleteAtentionRequiredTickets(ticketID)
               return redirect('/attention_required/')
          
     
     ticketDetails = firestore.DisplayAllAttentionRequiredTicket(ticketID)
     
     return render(request, 'base/attention_required_details.html', {'ticketDetails':ticketDetails})

# ========================================End User's Attention Required Ticket====================================

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>End User's Side<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Start Technicians's Side<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# =============================================Start Tech Dashboard================================================

def TechDashboard(request):

     techAssignedTickets = firestore.GetTechTickets(request.session['user_email'])
     
     return render(request, 'base/tech_dashboard.html', {'techAssignedTickets': techAssignedTickets, 'cuurentTech': techDisctionary[request.session['user_email']]})

def TechDashboardDetails(request, ticketID):
     if request.method == 'POST':
          button_action = request.POST.get('button_action')
     
          if button_action == 'back':
               return redirect('/tech_dashboard/')
          
          elif button_action == 'resolve':
               how_ticket_was_resolve = request.POST.get('how_ticket_was_resolve')
               comment = request.POST.get('comment')
               ticket = firestore.DisplayTicketDetails(ticketID)
               firestore.UpdateResolvedTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Resolved", ticket['TechAssigned'], ticket['Date'], comment, how_ticket_was_resolve)
               
               firestore.DeleteTickets(ticketID)
               # update active count
               firestore.UpdateActiveCount(ticket['TechAssigned'], "decrement")
               # update resolve count
               firestore.UpdateResolveCount(ticket['TechAssigned'], "increment")
               
               return redirect('/tech_dashboard/')
          
          elif button_action == 'transfer':
               TechComment = request.POST.get('TechComment')
               TechEscalatedTo = request.POST.get('selected_technician')
               ticket = firestore.DisplayTicketDetails(ticketID)
               firestore.UpdateEscalatedTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Escalated", ticket['TechAssigned'], TechEscalatedTo, ticket['Date'], TechComment)
               firestore.DeleteTickets(ticketID)
               
               # update active count
               firestore.UpdateActiveCount(ticket['TechAssigned'], "decrement")
               firestore.UpdateActiveCount(techDisctionary2[TechEscalatedTo], "increment")
               return redirect('/tech_dashboard/')
               
          elif button_action == 'auto_transfer':
               TechComment = request.POST.get('TechComment')
               predictions = firestore.GetPredictionsList(ticketID)
               maxActiveCount = firestore.GetMaxActiveCount()
               techActiveCountInRange = firestore.GetTechActiveCount(maxActiveCount['MaxCount'])
               
               key_to_compare = "id"
               ticket = firestore.DisplayTicketDetails(ticketID)
               
               for i in predictions:
                    for tech in techActiveCountInRange:
                         if i == tech.get(key_to_compare) and i != ticket['TechAssigned']:
                              TechEscalatedTo = i
                              firestore.UpdateAutoEscalatedTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Escalated", ticket['TechAssigned'], TechEscalatedTo, ticket['Date'], TechComment)
                              firestore.DeleteTickets(ticketID)
                              firestore.UpdateActiveCount(ticket['TechAssigned'], "decrement")
                              firestore.UpdateActiveCount(TechEscalatedTo, "increment")
                              return redirect('/tech_dashboard/')

               return redirect('/tech_dashboard/')
          
          elif button_action == 'request':
               request_message = request.POST.get('request_message')
               ticket = firestore.DisplayTicketDetails(ticketID)
               firestore.UpdateAttentionRequiredTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Attention_Required", ticket['TechAssigned'], ticket['Date'], request_message)
               firestore.DeleteTickets(ticketID)
               
               # update active count
               firestore.UpdateActiveCount(ticket['TechAssigned'], "decrement")

               return redirect('/tech_dashboard/')
     
     ticketDetails = firestore.DisplayTicketDetails(ticketID)
     techLists = firestore.GetTechList()
     ticketDetail = {'ticketDetail': ticketDetails, 'techLists': techLists}
     
     return render(request, 'base/tech_dashboard_details.html', ticketDetail)

# =============================================End Tech Dashboard================================================

# ========================================Start Tech's Resolved Ticket===========================================
def TechResolvedTickets(request):
     
     currentTech = request.session['user_email']
     
     # isdigit id used to check if a string is a number
     # TechNumber = ''.join(filter(str.isdigit, currentTech))
     
     ticketDetails = firestore.DisplayTechResolvedTicket(currentTech)
     
     return render(request, 'base/tech_resolved_tickets.html', {'ticketDetails':ticketDetails})

def TechResolvedTicketsDetails(request, ticketID):
     
     if request.method == 'GET':
          return redirect('/tech_resolved_tickets/')
     
     ticketDetails = firestore.GetResolvedTicket(ticketID)
     
     return render(request, 'base/tech_resolved_tickets_details.html', {'ticketDetails':ticketDetails})

# ========================================End Tech's Resolved Ticket===============================================

# ========================================Start Tech Escalated Tickets=============================================
def TechEscalatedTicket(request):
     
     ticketLists = firestore.DisplayTechEscalatedTicket(request.session['user_email'])
     
     return render(request, 'base/escalated.html', {'ticketLists':ticketLists, 'cuurentTech': techDisctionary[request.session['user_email']]})

def TechEscalatedTicketDetails(request, ticketID):
          
     if request.method == 'POST':
          button_action = request.POST.get('button_action')

          if button_action == 'back':
               return redirect('/escalated/')

          elif button_action == 'resolve':
               how_ticket_was_resolve = request.POST.get('how_ticket_was_resolve')
               comment = request.POST.get('comment')
               ticket = firestore.GetEscalatedTicket(ticketID)
               firestore.UpdateResolvedTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Resolved", ticket['TechTransferTo'], ticket['DateCreated'], comment, how_ticket_was_resolve)

               firestore.DeleteEscalatedTickets(ticketID) 
               # update active count
               firestore.UpdateActiveCount(ticket['TechTransferTo'], "decrement")
               # update resolve count
               firestore.UpdateResolveCount(ticket['TechTransferTo'], "increment")

               return redirect('/escalated/')

          elif button_action == 'transfer':
               TechComment = request.POST.get('TechComment')
               TechEscalatedTo = request.POST.get('selected_technician')
               ticket = firestore.GetEscalatedTicket(ticketID)
               firestore.UpdateEscalatedTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Escalated", ticket['TechTransferTo'], TechEscalatedTo, ticket['DateCreated'], TechComment)

               # update active count
               firestore.UpdateActiveCount(ticket['TechTransferTo'], "decrement")
               firestore.UpdateActiveCount(techDisctionary2[TechEscalatedTo], "increment")
               
               return redirect('/escalated/')

          elif button_action == 'auto_transfer':
               TechComment = request.POST.get('TechComment')
               predictions = firestore.GetPredictionsList(ticketID)
               maxActiveCount = firestore.GetMaxActiveCount()
               techActiveCountInRange = firestore.GetTechActiveCount(maxActiveCount['MaxCount'])
               
               key_to_compare = "id"
               ticket = firestore.GetEscalatedTicket(ticketID)
               
               for i in predictions:
                    for tech in techActiveCountInRange:
                         if i == tech.get(key_to_compare) and i != ticket['TechTransferTo']:
                              TechEscalatedTo = i
                              firestore.UpdateAutoEscalatedTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Escalated", ticket['TechTransferTo'], TechEscalatedTo, ticket['DateCreated'], TechComment)
                              firestore.UpdateActiveCount(ticket['TechTransferTo'], "decrement")
                              firestore.UpdateActiveCount(TechEscalatedTo, "increment")
                              return redirect('/escalated/')

               return redirect('/escalated/')

          elif button_action == 'request':
               request_message = request.POST.get('request_message')
               ticket = firestore.GetEscalatedTicket(ticketID)
               firestore.UpdateAttentionRequiredTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Attention_Required", ticket['TechTransferTo'], ticket['DateCreated'], request_message)
               firestore.DeleteEscalatedTickets(ticketID)

               # update active count
               firestore.UpdateActiveCount(ticket['TechTransferTo'], "decrement")
               
               return redirect('/escalated/')

     
     ticketDetails = firestore.GetEscalatedTicket(ticketID)
     techLists = firestore.GetTechList()
     ticketDetail = {'ticketDetail': ticketDetails, 'techLists': techLists}
     return render(request, 'base/escalated_details.html', ticketDetail)

# ========================================End Tech Escalated Tickets=============================================

# ========================================Start Tech's Returned Ticket===========================================
def TechReturnedTicket(request):
     
     ticketLists = firestore.DisplayReturnedTicket(request.session['user_email'])
     
     return render(request, 'base/return.html', {'ticketLists':ticketLists, 'cuurentTech': techDisctionary[request.session['user_email']]})

def TechReturnedTicketDetails(request, ticketID):
          
     if request.method == 'POST':
          button_action = request.POST.get('button_action')

          if button_action == 'back':
               return redirect('/return/')

          elif button_action == 'resolve':
               how_ticket_was_resolve = request.POST.get('how_ticket_was_resolve')
               comment = request.POST.get('comment')
               ticket = firestore.DisplayAllReturnedTicket(ticketID)
               firestore.UpdateResolvedTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Resolved", ticket['TechAssigned'], ticket['DateCreated'], comment, how_ticket_was_resolve)

               firestore.DeleteReturnedTickets(ticketID) 
               # update active count
               firestore.UpdateActiveCount(ticket['TechAssigned'], "decrement")
               # update resolve count
               firestore.UpdateResolveCount(ticket['TechAssigned'], "increment")

               return redirect('/return/')

          elif button_action == 'transfer':
               TechComment = request.POST.get('TechComment')
               TechEscalatedTo = request.POST.get('selected_technician')
               ticket = firestore.DisplayAllReturnedTicket(ticketID)
               firestore.UpdateEscalatedTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Escalated", ticket['TechAssigned'], TechEscalatedTo, ticket['DateCreated'], TechComment)
               firestore.DeleteReturnedTickets(ticketID)

               # update active count
               firestore.UpdateActiveCount(ticket['TechAssigned'], "decrement")
               firestore.UpdateActiveCount(techDisctionary2[TechEscalatedTo], "increment")
               
               return redirect('/return/')

          elif button_action == 'auto_transfer':
               TechComment = request.POST.get('TechComment')
               predictions = firestore.GetPredictionsList(ticketID)
               maxActiveCount = firestore.GetMaxActiveCount()
               techActiveCountInRange = firestore.GetTechActiveCount(maxActiveCount['MaxCount'])
               
               key_to_compare = "id"
               ticket = firestore.DisplayAllReturnedTicket(ticketID)
               
               for i in predictions:
                    for tech in techActiveCountInRange:
                         if i == tech.get(key_to_compare) and i != ticket['TechAssigned']:
                              TechEscalatedTo = i
                              firestore.UpdateAutoEscalatedTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Escalated", ticket['TechAssigned'], TechEscalatedTo, ticket['DateCreated'], TechComment)
                              firestore.DeleteReturnedTickets(ticketID)
                              firestore.UpdateActiveCount(ticket['TechAssigned'], "decrement")
                              firestore.UpdateActiveCount(TechEscalatedTo, "increment")
                              return redirect('/return/')

               return redirect('/return/')

          elif button_action == 'request':
               request_message = request.POST.get('request_message')
               ticket = firestore.DisplayAllReturnedTicket(ticketID)
               firestore.UpdateAttentionRequiredTable(ticket['id'], ticket['Caller'], ticket['Title'], ticket['Description'], "Attention_Required", ticket['TechAssigned'], ticket['DateCreated'], request_message)
               firestore.DeleteReturnedTickets(ticketID)

               # update active count
               firestore.UpdateActiveCount(ticket['TechAssigned'], "decrement")
               
               return redirect('/return/')

     
     ticketDetails = firestore.DisplayAllReturnedTicket(ticketID)
     techLists = firestore.GetTechList()
     ticketDetail = {'ticketDetail': ticketDetails, 'techLists': techLists}
     
     return render(request, 'base/return_details.html', ticketDetail)

# ========================================End Tech's Returned Ticket=======================================

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>End Technicians's Side<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

caller = None
ticketID = ''

def read():
     # Open the file in write mode
     file_path = os.path.join(os.path.dirname(__file__), 'TicketID.txt')
     file = open(file_path, 'r')
     # Read content from the file
     global ticketID
     ticketID = file.read()
     # Close the file
     file.close()
     
def write():
     # Open the file in write mode
     file_path = os.path.join(os.path.dirname(__file__), 'TicketID.txt')
     file = open(file_path, 'w')
     # Update the integer value
     new_value = int(ticketID) + 1
     file.write(str(new_value))
     # Close the file
     file.close()
     
techDisctionary = {
     "tech0@gmail.com": 'Technician GRP 0',
     "tech1@gmail.com": 'Technician GRP 1',
     "tech2@gmail.com": 'Technician GRP 2',
     "tech3@gmail.com": 'Technician GRP 3',
     "tech4@gmail.com": 'Technician GRP 4',
     "tech5@gmail.com": 'Technician GRP 5',
     "tech6@gmail.com": 'Technician GRP 6',
     "tech7@gmail.com": 'Technician GRP 7',
}

techDisctionary2 = {
     "GRP_0": "tech0@gmail.com",
     "GRP_1": "tech1@gmail.com",
     "GRP_2": "tech2@gmail.com",
     "GRP_3": "tech3@gmail.com",
     "GRP_4": "tech4@gmail.com",
     "GRP_5": "tech5@gmail.com",
     "GRP_6": "tech6@gmail.com",
     "GRP_7": "tech7@gmail.com",
}

# 1. Create active ticket count for each technician ==============DONE============
# 2. Increament and decrement active ticket count accordingly ========DONE============
# 3. Update db for additional fields like comment etc ==============DONE============
# 4. Create table for all resolved tickets and how it was resolved ==============DONE============
# 5. Create table for all pending tickets ==============DONE============
# 6. User can re-submit tickets if problem was not solved ==============DONE============
# 7. Escalate tickets *** ==============DONE============
# 9. Notify technician when ticket is assigned to them
# 10 Translation
# 8. Create reporting tool for admin ***

# when a ticket is resubmitted, shouyld add it on the pending ticket list for user
# try to add an accept button for resolved page on user side

# Pending tickets -> Resolved, Request, transfer, auto-transfer
# Returned tickets -> Resolved, Request, transfer, auto-transfer
# Escalated tickets -> Resolved, request, transfer, auto-transfer
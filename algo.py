from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta




def main(UUID):
    
    today = datetime.now()
    
    employeeInput, leaves = employee_inputs(UUID)
    # print(employeeInput)
    # print(leaves)
    
    territoryConfig = territory_config(UUID)
    # print(territoryConfig)
    
    keyDates = key_dates(employeeInput, leaves, territoryConfig, today)
    # print(keyDates)
    
    accrualHistory = accrual_history(keyDates, territoryConfig, employeeInput)
        
    
    
# acquire the employee inputs
def employee_inputs(UUID): 
    
    employeeData = {}
    
    # Input date in the format "dd/mm/yyyy"
    input_date_str1 = "16/09/2020"
    # Convert the input date string to a datetime object
    input_date1 = datetime.strptime(input_date_str1, "%d/%m/%Y")

    employeeData['Entitlement'] = 24
    employeeData['Start Date'] = input_date1
    
    # fetch employee leave objects
    leaves = employee_leave(UUID)
    
    return employeeData, leaves
    
    
# return list of leaves  
def employee_leave(UUID):
    # create leave objects
    leaveobject1 = {'Application Date': datetime.strptime("01/03/2021", "%d/%m/%Y"), 'Duration': 12}
    leaveobject2 = {'Application Date': datetime.strptime("01/05/2023", "%d/%m/%Y"), 'Duration': 3}
    
    # create a list of leaves
    leavelist = []
    leavelist.append(leaveobject1)
    leavelist.append(leaveobject2)
    # print(leavelist)
    
    return leavelist
    
def territory_config(UUID):
    # leaveAccrualPeriod (type = Beginning_Of_Year/Specific_Month/Employee_Start)
    
    territoryConfig = {'leaveAccrualPeriod': 'Beginning_Of_Year', 'carryOver': False, 'carryOverLimit': False, 'carryOverLimitAmount': None, 'Expiry': False, 'ExpiryNumber': None, 'ExpiryUnit': None}
    return territoryConfig
    
def key_dates(employeeInput, leaves, territoryConfig, today):
    
    # determine key dates
    keyDates = []
    
    # employee start date
    keyDates.append({'Date': employeeInput['Start Date'], 'Description': "Start Date", 'Balance': 0})
    
    # today
    keyDates.append({'Date': today, 'Description': "Today", 'Balance': 0})
    
    # leave application dates
    for leave in leaves:
        keyDates.append({'Date': leave['Application Date'], 'Description': "Leave", 'Duration': leave['Duration'], 'Balance Before': 0, 'Balance': 0})
    
    # accrual period start dates + accrual period end dates + expiry dates
    current_date = employeeInput['Start Date']
    
    while current_date <= today:
        if territoryConfig['leaveAccrualPeriod'] == "Beginning_Of_Year":     
            if current_date.month == 1 and current_date.day == 1:
                keyDates.append({'Date': current_date, 'Description': "Leave Accrual Period Start Date", 'Balance': 0})
                if territoryConfig['Expiry'] == True:
                    if territoryConfig['ExpiryUnit'] == 'years':
                        keyDates.append({'Date': current_date + relativedelta(years =+ territoryConfig['ExpiryNumber']), 'Period Start': current_date, 'Description': "Expiry", 'Balance Before': 0,'Balance': 0})

                    elif territoryConfig['ExpiryUnit'] == 'months':
                        keyDates.append({'Date': current_date + relativedelta(months =+ territoryConfig['ExpiryNumber']), 'Period Start': current_date, 'Description': "Expiry", 'Balance Before': 0, 'Balance': 0})
                    else:
                        keyDates.append({'Date': current_date + relativedelta(days =+ territoryConfig['ExpiryNumber']), 'Period Start': current_date, 'Description': "Expiry", 'Balance Before': 0, 'Balance': 0})
                    
            if current_date.month == 12 and current_date.day == 31:
                keyDates.append({'Date': current_date, 'Description': "Leave Accrual Period End Date", 'Balance': 0})
                
                                    
        # elif territoryConfig['leaveAccrualPeriod'] == "Employee_Start":
        #    if current_date.month == employeeInput['Start Date'].month and current_date.day == employeeInput['Start Date'].day:
        #         keyDates.append({'Date': current_date, 'Description': "Leave Accrual Period Start Date", 'Balance': None})
        #     # This needs fixing, we need to store the day before the employee's start date in territoryConfig
        #    if current_date.month == employeeInput['Start Date'].month - 1 and current_date.day == 31:
        #         keyDates.append({'Date': current_date, 'Description': "Leave Accrual Period End Date", 'Balance': None})
        # else:
        #     print("From Specific Month")
        
        current_date += timedelta(days=1)
    sortedKeyDates = sorted(keyDates, key=lambda x: x['Date'])
    return sortedKeyDates
    
def accrual_history(keyDates, territoryConfig, employeeInput):
    
    accrualRatepd = employeeInput['Entitlement']/365
    
    for i in range(len(keyDates)):

        if i > 0:
            # find duration
            duration = keyDates[i]['Date'] - keyDates[i - 1]['Date']
            # find accrual
            accruedLeave = duration.total_seconds()*accrualRatepd/(3600*24)
        else:
            accruedLeave = 0
        
        if keyDates[i]['Description'] == 'Leave Accrual Period End Date':            
            # find new balance
            keyDates[i]['Balance'] = accruedLeave + keyDates[i - 1]['Balance']
            
        elif keyDates[i]['Description'] == 'Leave Accrual Period Start Date':
            if territoryConfig['carryOver'] == False:               
                # find new balance
                keyDates[i]['Balance'] = accruedLeave
            
            elif territoryConfig['carryOver'] == True:  
                if territoryConfig['carryOverLimit'] == True:
                    if keyDates[i - 1]['Balance'] >  territoryConfig['carryOverLimitAmount']:      
                        # find new balance
                        keyDates[i]['Balance'] = accruedLeave + territoryConfig['carryOverLimitAmount']
                    else:
                        keyDates[i]['Balance'] = accruedLeave + keyDates[i - 1]['Balance']
                        
                else:
                    # find new balance
                    keyDates[i]['Balance'] = accruedLeave + keyDates[i - 1]['Balance']
                                
        elif keyDates[i]['Description'] == 'Leave':           
            # find new balance before
            keyDates[i]['Balance Before'] = accruedLeave + keyDates[i - 1]['Balance']
            # find new balance 
            keyDates[i]['Balance'] = keyDates[i]['Balance Before'] - keyDates[i]['Duration']
                        
        elif keyDates[i]['Description'] == 'Today':
            # find new balance
            keyDates[i]['Balance'] = accruedLeave + keyDates[i - 1]['Balance']

        elif keyDates[i]['Description'] == 'Expiry':
            # find new balance before
            keyDates[i]['Balance Before'] = accruedLeave + keyDates[i - 1]['Balance']
            
            leaveTaken = 0
            
            for date in keyDates:
                if date['Date'] >= keyDates[i]['Period Start'] and date['Date'] < keyDates[i]['Date'] and date['Description'] == 'Leave':
                    leaveTaken += date['Duration']
                    
                if leaveTaken >= territoryConfig['carryOverLimitAmount']:
                    keyDates[i]['Balance'] = keyDates[i]['Balance Before']
                else:
                    keyDates[i]['Balance'] = keyDates[i]['Balance Before'] - territoryConfig['carryOverLimitAmount'] + leaveTaken
        
        print()
        print('Key Date Number:', i, '- Accrual:', accruedLeave, '- Key Date:', keyDates[i])    

    return keyDates
    
if __name__ == "__main__":
    main(123)
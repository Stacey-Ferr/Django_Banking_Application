from django.shortcuts import render
from .models import Banking
from datetime import date, datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import pandas as pd
import numpy as np
from django.utils.datastructures import MultiValueDictKeyError
import warnings
from scipy.spatial.distance import cdist

@login_required
# @permission_required('banking.add_banking')d:
def upload_csv(request):

    # Retrieving user details to check if user has appropriate permissions
    user = User.objects.get(username=request.user.username)

    if user.has_perm('banking.add_banking'):
        try:
            # Reading the csv file that was uploaded
            csv = request.FILES["csv"]
            csv_content = csv.read().decode("utf-8")
            lines = csv_content.split("\n")[1:-1]
            # Converting the datatype from string to the datatype that the model accepts
            for line in lines:
                columns = line.split(",")
                columns[0] = int (columns[0])
                columns[1] = datetime.strptime(columns[1], "%Y-%m-%d").date()
                columns[3] = float (columns[3])
            
                # Creating a new entry of 'Banking' and storing it in the database
                transaction = Banking(account_number=columns[0], date=columns[1], transaction_type=columns[2], amount_usd=columns[3])
                transaction.save()
        except (NameError, MultiValueDictKeyError):
            print("MultiValueDictKeyError occurred...")
        
        return render(request, 'uploadCsv.html', {})

    else:
        return render(request, 'notAuthorized.html', {})

@login_required
# @permission_required('banking.view_banking')
def similar_transaction(request):
    
    # Ignoring warnings
    warnings.filterwarnings('ignore')

    # Retrieving user details to check if user has appropriate permissions
    user = User.objects.get(username=request.user.username)

    if user.has_perm('banking.view_banking'):
        # Retrieving the data from the database and updating the data in order to use
        db_records = Banking.objects.all().values()
        db_records = pd.DataFrame.from_records(db_records)
        one_hot = pd.get_dummies(db_records['transaction_type'])
        temp_df = db_records.drop('id', axis=1)
        db_records = db_records.drop(['id', 'transaction_type'], axis=1)
        vector1 = pd.concat([db_records, one_hot], axis=1).to_numpy()
        numeric_dates = pd.to_datetime(vector1[:, 1]).astype(int)
        vector1 = np.column_stack((vector1[:, 0], numeric_dates, vector1[:, 2:]))
        vector1 = np.ascontiguousarray(vector1).astype('float32')

        try:
            # Creating a new array to store the data entered
            new_array = []
            new_array.append(int(request.POST["account_no"]))
            new_array.append(request.POST["date"])
            if request.POST["transaction_type"] == "deposit":
                new_array.extend([1, 0, 0])
            elif request.POST["transaction_type"] == "transfer":
                new_array.extend([0, 1, 0])
            else:
                new_array.extend([0, 0, 1])
            new_array.append(float(request.POST["amount_usd"]))
            
            # Updating the new array to use
            vector2 = np.array(new_array)
            vector2 = vector2.reshape(1, -1)
            date_to_int = pd.to_datetime(vector2[:, 1]).astype(int)
            vector2 = np.column_stack((vector2[:, 0], date_to_int, vector2[:, 2:])).astype('float32')

            euclidean_dist = cdist(vector1, vector2, metric='euclidean')
            euclidean_dist = pd.DataFrame(euclidean_dist)
            indexes = euclidean_dist.nsmallest(4, 0).index
            similar_transactions = []
            for index in indexes:
                similar_transactions.append(temp_df.iloc[index])


            context = {'similar_transactions': similar_transactions}
            return render(request, 'similarTransaction.html', context)
        except (NameError, MultiValueDictKeyError):
            print("MultiValueDictKeyError occurred...")
        
        return render(request, 'similarTransaction.html', {})
    
    else:
        return render(request, 'notAuthorized.html', {})
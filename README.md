# Django_Banking_Application

This is a simple django project used to find similar transactions based on the transaction searched, using eucliean distance. It also provides the capability to upload a csv file containing transactional records. You may upload a csv file containing records with the following format:

Account_Number,Date,Transaction_Type,Amount_(USD)
123456789,2022-01-01,Deposit,1000.00
987654321,2022-01-02,Deposit,5000.00
567890123,2022-01-03,Deposit,750.00

While creating users you will need to specify the particular permissions that they have in order to view pages of the application.

After cloning the repository you will need to run these commands:
- python -m venv venv
- venv\Scripts\activate
- pip install -r requirements.txt
- python manage.py makemigrations
- python manage.py migrate
- python manage.py createsuperuser
- create additional users from the admin page and specify their permissions

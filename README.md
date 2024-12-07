#how to test this ?

Follow these steps in terminal for setting up this service 

Step 1: git clone https://github.com/ayshabaij/ai_service.git
Step 2: source venv/bin/activate
Step 3: python app.py


Download post man 

Step 1) register user

POST http://127.0.0.1:5000/register

Body , form-data 

Key                          Value

name         Text            (give name) 
image        file            (upload image)



Step 2) recognize user 

POST http://127.0.0.1:5000/recognize

Body , form-data 


Key                          Value


image        file            (upload image)


if already registered user , the name and successfull message will be shown . 
Try different pic of the same user and it will do the face recognization. 
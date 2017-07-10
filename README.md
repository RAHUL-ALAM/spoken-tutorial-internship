# spoken-tutorial-internship
contains the code from the fossee summer intership of spoken tutorial

Step1: Create Virtual Environment
- pip install virtualenv
- on desired directory type 'virtualenv <desired folder name>'
- to activate virtualenv type 'source <desired folder name>/bin/activate'

Step2: Install django and other dependencies
- pip install -r requirements.txt

Step3: Run server
- pyhton manage.py makemigrations reg_log
- pyhton manage.py makemigrations TRAINING
- pyhton manage.py migrate
- python manage.py runserver


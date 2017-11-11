## Multi-tenant Django app

This is a demo app to implement Craig's [blog
post](https://www.citusdata.com/blog/2016/08/10/sharding-for-a-multi-tenant-app-with-postgres/).
You can deploy it locally to try the Citus + Django ORM mix.

### Installation

1. Create a single machine Citus [development cluster](http://docs.citusdata.com/en/v5.2/installation/development.html)
1. Clone this repo
1. Get a new version of python with pyenv
1. `pip install -r requirements.txt`
1. Get the db ready
   ```bash
   createdb -p 5432 django_multitenant
   createdb -p 5433 django_multitenant
   createdb -p 5434 django_multitenant
   psql -p 5432 -d django_multitenant -c "CREATE EXTENSION citus;"
   psql -p 5433 -d django_multitenant -c "CREATE EXTENSION citus;"
   psql -p 5434 -d django_multitenant -c "CREATE EXTENSION citus;"
   ```

1. Create user `django_admin` and give it all privileges to the new db
1. Migrate the database and run the server
   ```bash
   # our django db config consults these vars
   export CITUS_DB_NAME=django_multitenant
   export CITUS_DB_USER=django_admin
   export CITUS_DB_PASSWORD=<whatever you chose>

   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

1. Visit http://127.0.0.1:8000/admin/stores/

Now you should be able to view and modify the data.

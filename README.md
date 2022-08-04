# GitLab Customer View

Goal of this project is to provide a simple web service that provides a view for customers or managers with information on the project status with is managed using the GitLab tools.

## Setup

Follow the [Django Setup Guide](https://docs.djangoproject.com/en/4.1/intro/tutorial01/) to prepare your environment. After installing Django do the migrations and remove the `.example` ending from you `main/local.py.example` after adjusting the settings in it. You may change the CACHE setting to use redis, memcached or any other caching backend. By default the database cache is activated - you need to run ´python manage.py createcachetable´ to create the caching table.

### Create first project

1. Create a superuser and log in to the django admin panel.
2. Add a customer with a valid email address using
3. Create a project and assign it to the customer
4. [Create a project access token](https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html) and add it to the project. If your are on trial plan or on any tier below "Premium" you may have to use the personal access token instead. If you use a project access token assign it the role "reporter" and allow access to "api". No other permissions are needed.
5. Save and login by entering your email address

## Contribution

Feel free to send merge requests when you find bugs or want to add features to this project.

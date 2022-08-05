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

## Custom designs
Please do not add custom themes / designs in this repository! 

Create your own repo and add your own ´base.html´ (you might want to copy and change or [extend](https://docs.djangoproject.com/en/4.0/ref/templates/language/) ´../base/base.html´).
Load your custom theme as a submodule with `git submodules add {url} /GitLabCustomerView/userinterface/template/{theme-name}`.
Go to local.py and change the name of the active theme to the {theme-name}.

Whenever you want to overwrite a template or any block inside a template create a file with the same name inside your theme. [Extend](https://docs.djangoproject.com/en/4.0/ref/templates/language/) the original file from the base template and overwirte the blocks you want to change inside it.

Whenever a file or block is not present in your individual them the default from the base theme is used.

## Contribution

Feel free to send merge requests when you find bugs or want to add features to this project.

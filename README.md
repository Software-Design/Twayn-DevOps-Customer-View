# GitLab Customer View

The GitLab Customer View is a simple web portal that provides a quick overview and access to progress and status information of tickets and milestones as well as the wiki for projects managed with GitLab.

Given a Project ID and a GitLab Acces Token this UI provides authenticated users a couple of views and functions to view and create tickets (issues) and track on the current project status. Furthermore it provides readable access to the time tracking feature of GitLab and the projects documentation hosted inside the GitLab Wiki. The Webinterface itselfs is designed to store as little information as possible inside it's own database but using the GitLab API and a caching infrastructure to provide the information given.

## Setup

Follow the [Django Setup Guide](https://docs.djangoproject.com/en/4.1/intro/tutorial01/) to prepare your environment. We recommend using a virtuale environment to install the dependencies from our ´requirements.txt´.

After installing Django do the migrations and remove the `.example` ending from your `main/local.py.example` and adjust the settings according to your needs. If you need to change other settings copy the corresponding section from `main/settings.py` to your ´local.py´ instead of manipulating the ´settings.py´ itself.

You may change the CACHE setting to use redis, memcached or any other caching backend. By default the database cache is activated - you need to run ´python manage.py createcachetable´ to create and use the caching table, if you want to stay with database caching.

### Create first project

1. [Create a superuser](https://docs.djangoproject.com/en/4.1/intro/tutorial01/), start your server and log in to the django admin panel.
2. Add a customer with a valid email address using the django admin panel.
3. Create a new project and assign it to the customer. Add the project ID - you find a GitLab projects ID within the "Settings > General" section.
4. [Create a project access token](https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html) and add it to the project. If your are on trial plan or on any tier below "Premium" you may have to use the personal access token instead. If you create your access token assign it the role "reporter" and allow access to "api". No other permissions are needed.
5. Save and login by entering the email address of your customer.

## Custom themes
Please do not add custom themes / designs / template in this repository! 

Create your own repo and add your own ´base.html´ (you might want to copy and modify or prefferably [extend](https://docs.djangoproject.com/en/4.0/ref/templates/language/) ´/userinterface/templates/base/base.html´).
Go to the project root of your GitLab Customer View and load your custom theme as a submodule with `git submodule add {url} ./GitLabCustomerView/userinterface/template/{theme-name}`.

Go to local.py and change the name of the active theme to the `{theme-name}`.

Whenever you want to overwrite a template or a block inside a template create a file with the same name inside your theme. [Extend](https://docs.djangoproject.com/en/4.0/ref/templates/language/) the original file from the base template and overwirte the blocks you want to change inside it.

Whenever a template file is not present in your individual theme the default from the base theme is being used.

## Author
This project is maintained by the [SD Software-Design GmbH](https://software-design.de) - a software development company based in Freiburg, Germany.

## License 
This software is provided and maintained under the [MIT License](/LICENSE).
We kindly ask to send merge requests to our public repo in case you are adding features to your invidividual copy of this software.

## Contribution
We are happy to review your merge requests when you feel that you can contribute to, extend or improved the software in any way.

Please make sure that you make use of our aproach to allow custom themes and modifications as described within the [custom themes](#custom-themes) section of this page.
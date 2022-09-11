# Twayn - The DevOps Customer View

Our "DevOps Customer View" is a simple web portal that collects information from DevOps tools like GitHub and GitLab (_more to follow_) and provides a quick overview of progress, status, tickets, and milestones as well as the documentation for projects managed within these tools.

### The problem with DevOp tools
DevOp tools are (obviously) built for developers, engineers, product owner, admins or other people working in "tech". Often they are too complex and powerful for "non-techies" to understand and work with. They often do not provide views oder interfaces for customers as they are not the intended users group - but they are loved by developers for their comprehensive features.

_Note: Some DevOps tools actually do provied features like the [GitLab Service Desk](https://docs.gitlab.com/ee/user/project/service_desk.html) but they are very limited in the functionality_

### The problem with Management tools
Management tools that project managers, business economists, sales teams or customers/consumers prefer are more focused on visualizing information, progress, relations, numbers and charts. Details of technical processes, the implementation or the actual work that is done in the hidden usually cannot be fully represented.

When the management or the customers require developers to use these tools in order to be able to view and interact with the progress and processes this ofteam means that they have to maintain or track information different tools or transfer information.

The other way round explaining customers or managers how to properly use DevOp tools can be challenging.

---

**Our goal is to allow developers to continue using their most beloved DevOps tools and generated a simple interfaces that provides customers and other people with no technical perspective on the project with information on the progress.**


Given a Project ID and an Acces Token this UI provides authenticated users a couple of views and functions to view and create tickets (issues) and track the current project status (using GitLab, GitHub *following soon*). Furthermore it provides readable access to the time tracking feature of those tools and the projects documentation hosted inside the corresponding wiki. The Webinterface itselfs is designed to store as little information as possible inside it's own database but using APIs and a caching infrastructure to provide the information given.

## Getting started

Follow the [Django Setup Guide](https://docs.djangoproject.com/en/4.1/intro/tutorial01/) to prepare your environment. We recommend using a virtuale environment to install the dependencies from our `requirements.txt`.

After installing Django do the migrations and remove the `.example` ending from your `main/local.py.example` and adjust the settings according to your needs. If you need to change other settings copy the corresponding section from `main/settings.py` to your `local.py` instead of manipulating the `settings.py` itself.

You may change the CACHE setting to use redis, memcached or any other caching backend. By default the database cache is activated - you need to run `python manage.py createcachetable` to create and use the caching table, if you want to stay with database caching.

### Create first project

1. [Create a superuser](https://docs.djangoproject.com/en/4.1/ref/django-admin/#createsuperuser), start your server and log in to the django admin panel.
2. Add a `User` with a valid email address using the django admin panel.
3. Create a new `Project` and assign it to the user. Add the project ID - for GitLab you find the project ID within the "Settings > General" section.
4.[Create a project access token (*[GitLab Help](https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html)). See additional notes below.
5. Create an `UserProjectAssignment` and chose the already created `User` and `Project`. Add the access token created in step 4.
6. Save and login by entering the email address and password of your user.

#### **Some notes on GitLab access tokens:**
If your are on trial plan or on any tier below "Premium" you may have to use the personal access token instead. 

Please note that the name of the access token is used and shown as author / editor in comments or logs. So if you create a projects access it should have your customers / managers name.

Assign it the role "reporter" to your acces token and allow access to "api".
No other permissions are needed. 

## Custom themes
Please do not add custom themes / designs / template in this repository! 

Create your own repo and add your own `base.html` (you might want to copy and modify or prefferably [extend](https://docs.djangoproject.com/en/4.0/ref/templates/language/) `/userinterface/templates/base/base.html`).
Go to the project root of your Twayn instance and load your custom theme as a submodule with `git submodule add -f {url} ./GitlabCustomerView/userinterface/templates/{theme-name}`.

Go to local.py and change the name of the active theme to the `{theme-name}`.

Whenever you want to overwrite a template or a block inside a template create a file with the same name inside your theme. [Extend](https://docs.djangoproject.com/en/4.0/ref/templates/language/) the original file from the base template and overwirte the blocks you want to change inside it.

Whenever a template file is not present in your individual theme the default from the base theme is being used.

## Author
This project is maintained by the [SD Software-Design GmbH](https://software-design.de) - a software development company based in Freiburg, Germany.
Any other authors, contributors and volunteers are welcome.

## License 
This software is provided and maintained under the [MIT License](/LICENSE).
We kindly ask to send merge requests to our public repo in case you are adding features to your invidividual copy of this software.

## Contribution
We are happy to review your merge requests when you feel that you can contribute to, extend or improved the software in any way.
Please make sure that you make use of our aproach to allow custom themes and modifications as described within the [custom themes](#custom-themes) section of this page and the following principles.

#### Notes on basic priciples and design choices
1. Respect the API Terms (see [GitLab Terms](https://about.gitlab.com/handbook/legal/api-terms/))
There are terms and conditions when using APIs - respect them.
2. Store / manage as little data as possible.
Since this project is meant to be an interface it should mainly use the DevOp tools as a data source and store as little information as poissble within its own database.
3. Don't break the permission and access control features of the DevOp tools - use them! 
Assign individual tokens to each user and don't use any method that allows access beyond the token-based permissions.

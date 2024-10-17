# ED RMA Project

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Main Project](#main-project)
- [Applications](#applications)
    - [Account App](#account-app)
    - [Common App](#common-app)
    - [RMA App](#rma-app)
- [Static media and Templates](#static-media-and-templates)
- [Caching and Logging](#caching-and-logging)
- [Additional Resources](#additional-resources)
- [Potential Enhancement Scope](#potential-enhancement-scope)
- [Needed for deploying](#needed-for-deploying)

## Overview
The **ED** project is a Django-based WSGI web application that provides RMA ecosystem for customer and store admin. It includes user account management, Return Merchandise Authorization (RMA) processing, and additional site-specific functionalities.

## Requirements
```txt
- Python 3.10
- Django 4.2                                            # if you are planning to go with django > 5 , please check suported MariaDB Version
- Other dependencies as listed in `requirements.txt`.
- Bootstrap 5.3
- Jquery 3.7.0
- HTMX 2.0                                              # Using During RMA submission by customer. 
- AOS.js 2.3.1                                          # Not used yet.
```
## Project Structure
```base
    ED/
    ├── account/           # Account management app
    ├── cached/            # Caching files for current file based caching
    ├── ed/                # Main project directory
    ├── logs/              # Log files directory
    ├── media/             # User-uploaded media files
    ├── rma/               # RMA (Return Merchandise Authorization) app
    ├── static/            # Static files (CSS, JavaScript, images)
    ├── templates/         # HTML templates
    ├── .gitignore         # Git ignore file
    ├── manage.py          # Django management script
    ├── ads.txt            # Ads.txt file for web crawlers
    ├── robots.txt         # Robots.txt file for web crawlers
    ├── README.md          # Project README file
    ├── .env               # Project README file
    └── requirements.txt   # Project requirements files
```

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/kabitagorain/sd.git
   cd ED
   ```

2. **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```


4. **Set up the database:**
    ```bash
    create database and keep ready the credentials
    ```

## Configuration

5. **Update .env:**
    ```bash
    ED_SECRET_KEY='secret key'
    DEBUG=True                                                      # for production make false, if collectstatic throwing error by mentioning STATIC_ROOT required evenif after setting of it, then try to edit in the settings file directly.
    ALLOWED_HOSTS=127.0.0.1:8000,http://127.0.0.1:8000,127.0.0.1    # comma separated allowed host

    ED_DB_NAME=edsystem                                             # any name you may choose
    ED_DB_USER=root
    ED_DB_PASSWORD='password'
    ED_DB_HOST=localhost
    ED_DB_PORT=3306

    RECAPTCHA_PUBLIC_KEY=MyRecaptchaKey123                          # it is for testing environment, please colelct domain abse key from the google interface.
    RECAPTCHA_PRIVATE_KEY=MyRecaptchaPrivateKey456                  # it is for testing environment, please colelct domain abse key from the google interface.

    DEFAULT_FROM_EMAIL=noreply@email.com
    EMAIL_HOST=mail.edsystemsinc.com                                # It is suggested by email provider or server
    EMAIL_PORT=465                                                  # It is suggested by email provider or server
    EMAIL_HOST_USER=noreply@email.com
    EMAIL_HOST_PASSWORD=emailpassword


    ADMIN=admin@email.com,admin2@email.com                          # Comma separated admin email
    ```
6. **Migrate the database:**
    ```bash
    python manage.py migrate
    ```
7. **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

## Running the Project

8. **Create a superuser:**
    ```bash
    python manage.py runserver
    ```
9. **Access the application**

    visit `http://127.0.0.1:8000/`



## **Main Project:**

`ed` is the main project directory. Does not change `__init__` of the directory where have:


```python

Ensures that the RMA status includes "rma_sent" in the settings configuration.

This function checks whether the tuple ("rma_sent", "RMA Sent") is present in the 
`settings.RMA_STATUS` configuration. The "rma_sent" status is mandatory for sending 
emails from the admin interface when reviewing the RMA (Return Merchandise Authorization). 
Changing the status to "rma_sent" allows sending instruction emails to the customer, 
thereby ensuring that the RMA process is correctly configured.

Raises:
    ValueError: If the tuple ("rma_sent", "RMA Sent") is not found in `settings.RMA_STATUS`.
```

Adjust `CACHE` in `settings.py` file of this main project directory as per you cache requirements. Currntly here utilized filebase caching. `CACHE` being served from the `cache` directory of the root directory.

### **Admin Interface Configuration**

Admin Interface: The Django admin interface is customized with the following configurations in the `urls.py` of the `ed` project directory:
- site_header: "ED System admin"
- site_title: "ED System admin"
- index_title: "ED System administration"
- empty_value_display: "Empty" for fields with no value

### **URL Structure**
The structure can be found in the main project dir `ed`'s `urls.py`
- `admin/`: Access the Django admin interface.
- `/`: Includes URLs for common application functionalities from the `common` app. As there is no other route, RMA request are pointed here.
- `account/`: Manages user accounts currently `abstracted` from built-in `User` model of Django.
- `rma/`: Dedicated to manages the RMA process. Currently the RMA request process in the frontend are serving from `common` app as common app does not have any route yet.

## Applications
## Account App

The `account` app is a customizable user authentication module for the Django project. It allows for user management and serves as a foundation for future customization of the user model and authentication mechanisms.

### Overview

- The `User` model in this app extends Django's built-in `AbstractUser` model. This makes it easy to add custom fields or methods to the user model in the future while maintaining compatibility with Django's authentication system.
- Admin registration is configured to enable user management through the Django admin interface.

### Modules and Files

- `models.py`: Contains the `User` model, which extends the `AbstractUser` class.
- `admin.py`: Registers the `User` model with the Django admin site.
- `urls.py`: Sets up the URL configuration for the app (currently empty).
- `views.py`: Placeholder for future view implementations (currently not used).

### Future Enhancements

- Implement custom user fields (e.g., profile picture, phone number).
- Add user authentication and management views.
- Configure additional URL patterns.
- Implement Login, Signup, password reset, password confirmation, profile, payment etc


## Common App 

### Overview

The `common` app provides shared utilities and configurations, including:

- Admin registration for `Site` and `SiteMeta` models.
- Context processor for adding site metadata to the request context by utilizing cache.
- Utility functions for sending RMA-related emails.
- Caching mechanisms for performance optimization.

### Modules and Files

- `admin.py`: Registers `Site` and `SiteMeta` models with the Django admin. Unregisters and then re-registers `Site` for custom handling.
- `context_processor.py`: Defines a `site_info()` function to retrieve cached site metadata and a `sd_context()` function to make site metadata available in templates. currently below are avialable in templates. To access use as per example `{{ site_data.name }}`. Now all the field are using as site meta data for search engine. Also usning as `site_data = site_info()` by importing where necessary from this `context_processor.py`. The site data also being edit in the view to update route based site meta information like `site_data['title'] = 'Custom Title'`.
    ``` python
    data = {
        'name': meta_data.site.name,
        'title': meta_data.title,
        'domain': meta_data.site.domain,
        'description': meta_data.description,
        'keywords': meta_data.keywords, 
        'logo': meta_data.logo.url if meta_data.logo else '', 
        'og_image': meta_data.social_logo.url if meta_data.social_logo else '',
        'return_address' : meta_data.return_address, # it is used in the email address when sending instriction email by updating RMA status.
        'facebook': meta_data.facebook,
        'x_twitter': meta_data.x_twitter,
        'linkedin': meta_data.linkedin,
        'instagram': meta_data.instagram,
    }
    ```
    if you want to enhance, then first update the `models.py` of this app then add/remove the fields here inside `data` dict. Enter Data from the admin inteface, Then delete the `cache` like `cache.delete('site_data')`. The enhancement are avialable on the template.
- `models.py`: Defines the `SiteMeta` model, which extends `Site` with fields such as title, description, social media links, and logos. For enhancement just add new fields and run `makemigrations` then `migrate` then add the new field acording to described in the `context_processor.py` above.
- `urls.py`: Provides a placeholder URL pattern for future extensions.
- `utils.py`: Contains the `SdMailService` class for sending emails related to RMA requests, including RMA generation notifications and return instructions. There is two method which is being used like below:
    ``` python
    mail_service = SdMailService()
    cache.set(f'rma_{rma_id}', rma_obj, timeout=900)
    mail_service.send_rma_genaration_email(rma_id)   
    mail_service.sent_rma_instruction_to_customer(rma_id)   
    ```
    before calling the functions setting cache is importent in the mentioned formate.



## RMA App

### Overview

This app handles the Return Merchandise Authorization (RMA) process, allowing customers to submit requests for returning products. The RMA system enables administrators to review and approve requests, and automatically notify customers via email based on the status of their request.

### RMA Workflow
- Customer submite RMA request from the frontend. After successfull submission an RMA number will display on the screen with message.
- During submission it will check duplicate RMA for same product of same order by same email. If duplicate found an error message will display on the screen and RMA will not be submitted.
- Once submitted system will send email to:

All listed email-addresses in the site settings as below:
```txt
Subject: [ED System Inc] New RMA Submitted for Product SKU #76543

Dear Admin,

A new Return Merchandise Authorization (RMA) request has been submitted. Here are the details:

RMA Number: RMA-00009
Customer Name: Kabita
Email: kabitagorain6@gmail.com
Phone: 324234
Product SKU: 76543
Reason for Return: Just Testing
Submitted On: Oct. 17, 2024, 6:02 p.m.

Please log in to the admin panel to review and process this request.

Thank you,
ED System Inc

```
The customer who submitted RMA:
```txt
Subject: [ED System Inc] We Have Received Your RMA for Product SKU #76543

Dear Kabita,

Thank you for submitting your Return Merchandise Authorization (RMA) request. We have received your request, and your RMA number is: RMA-00009.

Here are the details of your request:
Product SKU: 76543
Reason for Return: Just Testing
Submitted On: Oct. 17, 2024, 6:02 p.m.

Our team will review your request and get back to you with further instructions shortly. If you have any questions, please don't hesitate to contact us.

Thank you for choosing ED System Inc.

Best regards,
ED System Inc Support Team
```
- Now time to review RMA request by the admin from admin panel. If RMA status changed to 'Sent RMA' then instruction email mentioned in the next will go to the customer.

### Modules and Files

- `admin.py`: Register `RmaRequests` with the django admin. Configurd `list_display` to decide which fields to show on the list, `list_filter` to filter RMAs by status, set `date_hierarchy` which enhance datewise filtering, configured `ordering` to display decending manner of RMA creation. RMA can be searched by decided filed in `search_fields` which is `"rma_number", "order_ref", "product_sku", "email"`, an instruction has been added in the admin inteface about the facilated field under the search box. Also here ensured that RMA can not be edited once submitted, except `rma_instructions` and `status` field. When review and updating RMA:
    - Set instruction acording to the instruction mentioned under `RMA instruction` field, but keep `'$rma_number'` as it is included in the default instruction, which will replace by the related RMA number in the email body. The instruction will be included in the middle of email body in place of 4 point mentioned in the below current email body:
    ```txt
    Dear [Customer Name],

    We have reviewed your Return Merchandise Authorization (RMA) request and would like to provide you with the instructions for returning your product.

    RMA Number: [RMA Number]
    Product SKU: [Product SKU]
    Reason for Return: [Return Reasons]
    Submitted On: Oct. 17, 2024, 6:02 p.m.

    Please follow these instructions to complete your return:

    1. Carefully pack the item in its original packaging, including all accessories and documentation.
    2. Clearly mark the RMA number ['RMA-00009', it is replaced by '$rma_number'] on the outside of the package.
    3. Ship the package to the following address.
    4. Once the return is processed, we will notify you of the status and any further steps, if necessary.

    Return Address:
        E.D. Systems Tech Center
    3798 Oleander Ave #2
    Fort Pierce, Florida 34982
    United States.

    If you have any questions or need additional assistance, please feel free to contact us at ED System Inc.

    Thank you for your cooperation.

    Best regards, 
    ED System Inc Support Team
    ```
    Here `Return Address` Coming from the site meta, also other data retriving autometically from system.
    - if status set to `RMA sent` and click on the save button, an automatic email will be send to the customer which is given as example above.    

- `models.py`: The `RmaRequests` model is used to store RMA requests submitted by customers. It tracks customer information, order details, the reason for return, and the current status of the RMA request. Once an RMA request is submitted, the admin reviews it and can approve it.
- `urls.py`: Sets up the URL configuration for the app.
- `utils.py`: Contains the `generate_rma_number` function to generate unique and formated RMA number while customer submite RMA request. 
- `views.py` : The `rma_request_view` function handles the Return Merchandise Authorization (RMA) form submission process. It allows customers to request an RMA by filling out a form, and upon successful submission, generates a unique RMA number and sends an email notification to the customer.

## Static media and Templates

- `static` dir serves all static file, including `favicon`
- `media` dir ready to serve all file will be uploaded by customer
- `templates` dir serving all HTML and txt templates files for `email` and `frontend`.

## Caching and Logging
- Currently system serving filebasecache from `cache` dir of the root. Recomended to use redis cache if suporting resources avialable.
- System logging can be found in the `logs` dir of the root.

## Additional Resources
- `ads.txt` included.
- `robots.txt` included with the confguration of accepting all search engine.


## Potential Enhancement Scope

Below are some potential enhancements that could be considered, depending on your business requirements:

- Implement email notifications for when a returned product is received from the customer, or if the RMA request is rejected.
- Add user authentication functionalities such as login, signup, password reset, password confirmation, user profile management, and payment handling.
- Create a sitemap for SEO purposes and enhance the application by making it a Progressive Web App (PWA) with a manifest file.
- Use Redis and Celery to improve scalability for large user bases, managing cache and handling email queues efficiently.
- Integrate with the eCommerce system’s API to validate whether an order, product, or email exists.
- Allow users to track their submitted RMA requests directly from their account dashboard.
- Enhance the system by adding a feature for customers to upload documents related to their RMA requests.
- Custom CMS


## Needed for deploying

- Google recaptcha key
- Admin email list, default website list, email configuration to setup
- Hosting
    
    








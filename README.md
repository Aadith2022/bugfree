# BugFree
## Website Link: https://bugtrackerproj-e0ecfff13106.herokuapp.com/
Hello, welcome to BugFree. This is a client based Bug Tracking Website where clients can submit tickets to an Institution's projects, providing the users of that Institution to have an organized view of the tickets associated with their projects based on varying ticket priority, type, and status

This website features 4 main roles: Admin, Project Manager, Developer, and Submitter

* Admin:


* Project Manager:


* Developer:


* Submitter:


## Load Page:

This is how the website looks upon loading, it has links for Home and Login  

![image](https://github.com/Aadith2022/bugfree/assets/113648765/c0b4ded2-8748-4561-8216-a71c28bb1f75)

## Home Page:

Upon Clicking the Home Link, you will see a small description of the Website in addition to a video tutorial to help new users navigate the site

![image](https://github.com/Aadith2022/bugfree/assets/113648765/fb9cfebd-b89b-4a83-b668-3b69c22afa61)


## Login Page:

### Upon Clicking the Login page, you will be presented with the following. 

On this page, a User can login if they already have an existing account. If a user is an administrator for an Institution, they can provide that Intitution's 'Admin Password' on login to be taken to their adminstator account. If a user who is not an admin gets a hold of the Admin Password, that user will get a error message and the admin of the Institution will be notified that their secure password has been leaked.

![image](https://github.com/Aadith2022/bugfree/assets/113648765/162735f5-eb00-40de-88c6-5cf718619ba1)

Here, users can register to join to an exisiting Institution

![image](https://github.com/Aadith2022/bugfree/assets/113648765/2cbdd025-9a6f-45a1-9078-f9bb953e2c50)

Finally, here users have the ability to register a new Instituion that other users can join as well

The user that is registering the new Institution will automatically be added to the list of Admin for that Institution. It is up to them to set up an 'Admin Password' for the Insittution, which is an additional password reserved only for admin of the Insittution. Users can can enter this additional password at the Login page in order to be taken to their adminstator acount.

![image](https://github.com/Aadith2022/bugfree/assets/113648765/94f20b91-1347-403c-89f9-31ddb851c5c0)


## Registration

After registering to join an Institution, a user will be presented with the following page, instructing them to wait until their request to join the Institution has been accepted by an administrator

![image](https://github.com/Aadith2022/bugfree/assets/113648765/6c8ab271-1935-4d24-8641-2bc43482afe9)

This is what it looks like for the Admin when a user submits a join request to the Institution. The admin have the option to either accept or deny each request.

![image](https://github.com/Aadith2022/bugfree/assets/113648765/cfce1fbd-1e85-4e6b-b1c7-4d6ee908c1ee)

## Manage Users Section

Once the Admin has accepted some join request, the 'Manage Users' section will show a table of all of the users, excluding other admin, in the Institution. As the admin, a user has the ability to edit the roles of other users, or remove others from the Institution entirely

![image](https://github.com/Aadith2022/bugfree/assets/113648765/e4beadf1-9850-48fe-a503-af0745153298)

## View Projects Section

When an Institution does not have any projects created yet, the 'View Projects' page will instruct you to create a new project to get started

Both the Project Manager and Admin have the ability to create new projects, where they can include a title, description, as well as a list of other users that they would like to include in the project

![image](https://github.com/Aadith2022/bugfree/assets/113648765/2e0c64f8-28d5-4f88-a70d-b3d9faa75cfd)

Once an Institution has some projects, the 'View Projects' section will be updated with additional information

* For Admin, this page will display all of the projects for the Institution
* For Project Managers, they will only be able to view projects that they have been assigned to
* This page is not available to view for Submitters and Developers

![image](https://github.com/Aadith2022/bugfree/assets/113648765/e7058fb6-6753-4cae-8f62-db66c8a609b6)


## Manage Project Users

This section is available to both Admins and Project Managers

Admin and Project Managers have the ability to edit the roles of the users within the project, remove specific users, or add new users to this project

![image](https://github.com/Aadith2022/bugfree/assets/113648765/e9e7a3b1-7f92-496d-a46a-29402255cf99)


## Project Details

In this section, Admin and Project Managers can see all of the information associated with this project, such as assigned personnel as well as tickets

![image](https://github.com/Aadith2022/bugfree/assets/113648765/d67ed5a7-5e2d-4442-bb71-55fe97be1ee7)


## View Tickets Section

If there are no tickets for an Institution, this page will instruct users to wait until a Submitter has submitted new tickets

For a Submitter, this page will display all of the tickets that they have created, if there are none, they will be instructed to create a new ticket

When creating a ticket, a submitter can include the following information: title, description, type, priority (which can be either Low, Medium, or High), as well the project that they want this project to be associated with. Whenever a ticket is created, its default status is 'New', this can be changed by the Developer, which will be discussed later

![image](https://github.com/Aadith2022/bugfree/assets/113648765/d096e2af-36b5-4fb2-9973-2f05f2cd484a)


After tickets have been created, the 'View Tickets' section will display additional informationn depending on the role of the user that is logged in:

* For admin, this section will display all of the tickets that are in this Institution
* For Project Managers, this section will display only the tickets that are associated with the projects that they are the managers of
* For Developers, this section will only show the tickets that they have been explicitly assigned to (More on this later)

![image](https://github.com/Aadith2022/bugfree/assets/113648765/92309c7d-7dbf-498d-99fe-0c5c45425de8)


## Update Tickets

Admins, Project Managers, and Developers have the ability to update tickets. Admins and Project Managers have the ability can update every aspect of a ticket, weheras developers can only update the status and priority of tickets. The Admin, Project Managers, and Developers all have the power to change the status of a ticket to one of the following: New, Open, In Progress, Resolved, and Additional Information Required

By default, when Tickets are created they do not have a devloper assigned to them, so it is up to either the Admin or the Project Manager to assign a deveoper to a given ticket

This is how updating a ticket looks for both the Admin and Project Manager:

![image](https://github.com/Aadith2022/bugfree/assets/113648765/dcdd565b-f2d1-49da-a304-fa4db49c5d16)

This is how it looks on the developer side:

![image](https://github.com/Aadith2022/bugfree/assets/113648765/16ae7978-f7de-4308-bc04-7bc8382d1722)


## Ticket Details

In the View Tickets section, users have the ability to view additional details of that ticket, such as when it was created as well as all of the history associated with that ticket. Additionally, in this section, users have the ability to leave comments on a ticket

![image](https://github.com/Aadith2022/bugfree/assets/113648765/049ed445-a56f-4d82-a236-63b998c610da)

![image](https://github.com/Aadith2022/bugfree/assets/113648765/4142af0a-daf6-42d9-ac1b-7cedc10b5e1e)


## Notifications

Whenever a user leaves a comment on a ticket, both the developer and submitter of the ticket will be notified of the comment. Users can see that they have new notifications when the Notification logo turns white, as follows

![image](https://github.com/Aadith2022/bugfree/assets/113648765/856ca453-e0b9-448f-9c69-a3c149163d2a)

Upon pressing it, a user can see all of their notifications as well as when the notification was sent

![image](https://github.com/Aadith2022/bugfree/assets/113648765/c8b95b4f-a8a1-4f6f-9c67-a2d61f6bc8ad)

When the status of a Ticket turns to 'Additional Information Required', the Submitter of that ticket will get a ticket informing them to provide additional information on that ticket immediately

![image](https://github.com/Aadith2022/bugfree/assets/113648765/be61a3fc-1062-419b-b536-c759e4ae7f66)

Then when that Submitter looks at the 'View Tickets' page again, they will see that their ticket will be labeled as 'Action Required', where they are required to change either the title or the description of the ticket, otherwise they will get an error

![image](https://github.com/Aadith2022/bugfree/assets/113648765/610a6b4e-9010-4f70-bac0-d413d650351d)

![image](https://github.com/Aadith2022/bugfree/assets/113648765/33044e26-c64a-4e1d-8a92-bd9ba0e4e2f2)


## Dashboard Home

Once tickets have been created, the 'Dashboard Home' section will also be updated, and it will display different information based on the role of the user that is logged in

* Admin will see graphs breaking down all of the tickets in the Institution
* Project Managers and Developers will see a breakdown of the tickets associated with the projects they're on
* Submitters will see a breakdown of all of the tickets that they have created
* Developers will see a breakdown of the tickets that they are assigned to

![image](https://github.com/Aadith2022/bugfree/assets/113648765/f444e267-e9b1-47d0-8a74-a9e7f3af263f)


## Backend Architecture with Django and SQLite Database

![image](https://github.com/Aadith2022/bugfree/assets/113648765/d809487d-2161-4421-97f6-a0fcc12916bd)

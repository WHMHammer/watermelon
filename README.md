# The Watermeton Project

We are currently at phase 1. Please see `prototype-master` branch.

## Project Description

This project is originally derived from [the Cantaloupe project](https://github.com/DevPSU/Attendance-Manager). I used to be the back-end software engineer of [the Cantaloupe project](https://github.com/DevPSU/Attendance-Manager). However, there came to disagreements between me and other team members on multiple security and technical issues. As a result, I resigned from [the Cantaloupe project](https://github.com/DevPSU/Attendance-Manager) team, built up my own, and extended the functionality of the project.

The final goal of the Watermelon Project is to enable users to register for accounts, and set up and subsribe from "events" following the structure presented below:

- Event
    - Event Name
    - Event Owner(s)
    - Event Subscriber(s)
    - Time Period
    - Geographical Location
    - Child event(s)
    - Parent event

Event owners will set up these attributes when creating new events. They will then be able to alter these attributes and to publish announcements, and check subsribers' attendence records, etc. Event subscribers will be able to read announcements, and check their own attendence records, etc.

## Development Plan

### Phase 1 - Prototype (Jan. 2019 - Present)

In this phase, we plan to build a functional prototype with mainly plain CSS, HTML, JavaScript, SQL, and Python scripts. All features will be implemented.

### Phase 2 - Polishing

In this phase, we plan to polish the API we designed in Phase 1. Also, we will rewrite codes with libraries and structures like Bootstrap, Flask, jQuery, etc.

### Phase 3 - Mobile Platforms

In this phase, we plan to develop clients for Android and iOS systems. The signing up for attendence feature will be available only on mobile clients (removed from browser client). All other features will be kept.

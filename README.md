<h1 style="text-align: center;">INTRODUCTION</h1>

Autonomous systems are devices or systems capable of operating independently, without the need for direct human control. These systems can be implemented in various contexts, such as autonomous vehicles, drones, industrial robots, and many other sectors. The key to autonomous systems is the ability to perceive the surrounding environment, make decisions, and adapt and/or modify their behavior without constant human intervention. This category of systems also includes proactive systems, i.e., systems capable of predicting the trend of environmental parameters and implementing adaptations before these parameters exceed defined thresholds.
Autonomous systems and their components are based on the MAPE-K cycle.
This document details the development project of a proactive autonomous system for air purification in an industrial environment. The system aims to monitor and manage levels of critical air pollutants, including carbon monoxide (CO), carbon dioxide (CO2), fine dust, and humidity (which affects fine dust concentration), in different sections of the industrial environment.
The system consists of sensors placed in each section of the plant, which constantly detect the levels of the aforementioned components. Simultaneously, actuators are used to remove the detected pollutants, ensuring a safe and healthy working environment.

For more details see the documentation file: AIR POLLUTION MONITORING AND CONTROL SYSTEM


<h1 style="text-align: center;">TECHNOLOGIES USED</h1>

The software has been entirely implemented using the Python programming language and the following technologies:
- **Message Broker: MQTT**

  MQTT, which stands for Message Queuing Telemetry Transport, is a lightweight and scalable messaging protocol. We used the MQTT protocol to obtain data from sensors and enable communication between some of the components of the MAPE-K cycle. This data was sent through Python on the dedicated topic and subsequently processed by other components.

  Our topics are:

  - **industry**: topic within which data obtained through sensors are published. Specifically, the topic is defined by:
    - *industry*: fixed part indicating the main topic;
    - *sectionName*: name of the section with which the values are associated;
    - *parameter*: parameter whose values are published. The possible parameters are CO, CO2, fineDust, and Humidity.
    
    Example topic: `industry/Section_a/fineDust`
  
  - **status**: topic within which data obtained after analysis of parameter values are published. Specifically, the topic is defined by:
    - *status*: fixed part indicating the main topic;
    - *sectionName*: name of the section with which the values are associated.
      
    Example topic: `status/Section_a/`
  
  - **plans**: topic within which the adaptation plans for each section are posted. Specifically, the topic is defined by:
    - *plans*: fixed part indicating the main topic;
    - *sectionName*: name of the section with which the values are associated.
    
    Example topic: `plans/Section_a/`
  
  - **executions**: topic within which messages about actions to be performed by actuators are posted. Specifically, the topic is defined by:
    - *executions*: fixed part indicating the main topic;
    - *sectionName*: name of the section with which the values are associated.
    
    Example topic: `executions/Section_a/`


- **Database: InfluxDB**
 
  This database was chosen for its ability to handle large volumes of data from environmental sensors and other data sources. InfluxDB proved to be reliable and flexible, allowing efficient data analysis and management within our project, with the advantage of easy reads and writes using Python files.

- **Grafana (Dashboard)**

  Grafana is used primarily as a graphical user interface and was therefore used to visualize and understand the data. The main advantage of Grafana that we found is that, in addition to providing better visualization, it provides a way to create multiple dashboards simultaneously and allowed us to better manage information.


<h1 style="text-align: center;">SYSTEM ARCHITECTURE</h1>

![Logo GitHub](https://github.com/sicchio99/SE4AS/blob/main/SystemArchitecture.png)



<h1 style="text-align: center;">MAPE-K LOOP IMPLEMENTATION</h1>

![Logo GitHub](https://github.com/sicchio99/SE4AS/blob/main/Mape-KLoop.png)

Our system is based on the Mape-K Loop, using a container system to ensure clear separation between each element of the loop. Components are deployed on separate containers, which are managed through the use of Docker, and which communicate through the use of a Message Broker and Knowledge. The components that describe the data flow are:

- **MONITOR:** Component responsible for collecting data obtained from sensors (CO2, CO, humidity, and fine dust) and writing these values into the knowledge.

- **KNOWLEDGE:** Component responsible for storing collected data realtive to the measured parameters, alarm status (general and specific for each parameter), and safety limits for each parameter.

- **ANALYZER:** Component whose role is to retrieve parameter data from Knowledge, predict a trend by exploiting the past values, and compare the predictions with the threshold limits (also retrieved from Knowledge). Then the determined symptoms are communicated to the Planner through specific messages (one for each symptom) using the MQTT Message Broker.

- **PLANNER:** Component responsible for formulating adaptation strategies, making decisions and implementing policies necessary to bring the value of parameters back within safe thresholds. The strategy is defined based on the symptoms calculated by the Analyzer and published in the relevant topic. Through the MQTT broker, this component, retrieves the symptoms and then publishes the defined adaptation plans.

- **EXECUTOR:** This component based on what is decided and planned works to execute the plan through the use of actuators. Through the use of the MQTT broker, actuators are activated or deactivated.


<h1 style="text-align: center;">INTSTRUCTIONS</h1>

Prerequisites: having Docker installed.
Run on your prompt the command: **git clone https://github.com/sicchio99/SE4AS.git**
- Enter the directory cmd and run the command: **docker compose build**
- Execute the command: **docker compose up**
In order to view dashboards on Grafana:
- Open Grafana through the link:  **http://localhost:3000**
- Log in by entering as username and password: **admin**.
- Go to the Dashboards section and select the section of interest.

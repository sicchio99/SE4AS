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

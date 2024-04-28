import time
import paho.mqtt.client as mqtt
import numpy as np
from sklearn.linear_model import LinearRegression
from database import Database


def predictNextValues(values, window_size, num_predictions):
    """
    Predicts multiple successive values in the sequence using linear regression with a moving window.
    """

    # Convert list of values to a NumPy array
    values_array = np.array(values)

    # Prepare the data for linear regression
    X = []
    y = []

    # Create the data windows and corresponding targets
    for i in range(len(values_array) - window_size - num_predictions + 1):
        X.append(values_array[i:i + window_size])  # Use the values passed as features
        y.append(values_array[
                 i + window_size:i + window_size + num_predictions])  # The values are the targets to be predicted

    X = np.array(X)
    y = np.array(y)

    # Transform X into a two-dimensional array
    X = X.reshape(-1, window_size)

    # Create a linear regression model
    model = LinearRegression()

    # Train the model on the prepared data
    model.fit(X, y)

    # Predict the next values in the sequence
    last_window = values_array[-window_size:]  # Take the last elements as a moving window
    next_values = model.predict(last_window.reshape(1, -1))

    return next_values.flatten()


def checkLimits(parameters_data, limits, dangers, safe_values, section_alarm):
    parameter_status = {}

    for section_name, section_values in parameters_data.items():
        for parameter, data in section_values.items():
            print(f"{section_name}-{parameter}: {data}")
            predicted_values = predictNextValues(data, window_size=3, num_predictions=2)

            # 0 -> Parameter in the safe range
            # 1 -> Parameter higher than the limit
            # 2 -> Parameter higher than the danger value
            # 3 -> Parameter lower than the minimum

            tolerance = 2
            print("Predicted value: ", predicted_values[1])
            if section_alarm[section_name][parameter] is False:
                if predicted_values[1] > (limits[parameter] - tolerance) and predicted_values[1] < (
                        dangers[parameter] - tolerance):
                    print(f"{parameter} in {section_name} - Greater than the maximum")
                    parameter_status[parameter] = f'{parameter}-1'
                elif predicted_values[1] > (dangers[parameter] - tolerance):
                    print(f"{parameter} in {section_name} - Greater than the danger limit! DANGER")
                    parameter_status[parameter] = f'{parameter}-2'
                elif parameter == "humidity" and predicted_values[1] < (limits["lower humidity"] + tolerance):
                    print(f"{parameter} in {section_name} - Lower than the the minimum value")
                    parameter_status[parameter] = f'{parameter}-3'
                else:
                    print(f"{parameter} in {section_name} - OK")
                    parameter_status[parameter] = f'{parameter}-0'
            else:
                if predicted_values[1] <= (safe_values[parameter] + tolerance):
                    print(f"{parameter} in {section_name} - No more danger")
                    parameter_status[parameter] = f'{parameter}-0'
                else:
                    print(f"{parameter} in {section_name} - Greater than the danger limit! DANGER")
                    parameter_status[parameter] = f'{parameter}-2'

        # Conversion of the dictionary to a string in the x/y/z/k format where:
        # x = co - state
        # y = co2 - state
        # z = fineDust - state
        # k = humidity - state
        parameter_status_value = parameter_status.values()
        status_string = "/".join(parameter_status_value)

        client_mqtt.publish(f"status/{section_name}", status_string)


def checkAlarmActive(dangers_data):
    for section_name, alarm_state in dangers_data.items():
        if alarm_state != 'False':
            return True
    return False


if __name__ == '__main__':

    # Database connection
    database = Database()
    # Message Broker connection
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)

    # Recovery of section names and parameters from database
    sections, parameters = database.getSectionsAndParameters()
    print("SECTIONS:" + str(sections))
    print("PARAM:" + str(parameters))

    alarm_active = False  # Initially alarms off

    while True:
        # Dictionary that will contain the data retrieved from the DB
        parameters_data = {}
        # Dictionary that will contain the status of alarms
        dangers_data = {}
        # Dictionary that will contain the parameter alarms for each section
        section_alarm = {}

        # Retrieve data from database
        for section in sections:
            dangers_data[section] = database.getSectionAlarm(section, "alarmState")
            section_alarm[section] = database.getSectionAlarm(section, "alarmType")
            section_values = {}
            for parameter in parameters:
                data = []
                while len(data) < 5:
                    data = database.getParametersData(section, parameter)
                    if len(data) < 5:
                        print("The data list has less than 5 elements. Trying again...")
                section_values[parameter] = data
            parameters_data[section] = section_values

        print(f"Alarm state {section}: {str(dangers_data)}")
        print(f"Alarm type {section}: {str(section_alarm)}")

        alarm_active = checkAlarmActive(dangers_data)  # Check to see if any of the 3 sections have the alarm activated

        # Retrieve limits from database
        limits, dangers, safe_values = database.getParametersLimit()
        print("Limits:" + str(limits))
        print("Dangers:" + str(dangers))
        print("SafeValues:" + str(safe_values))

        # Limit control and status publication
        checkLimits(parameters_data, limits, dangers, safe_values, section_alarm)

        if alarm_active:
            print("Sampling time = 2")
            time.sleep(2)  # Check every 2 seconds whether the alarm is active in 1 of the 3 sections
        else:
            time.sleep(4)  # Check every 4 seconds if the alarm is not active
            print("Sampling time = 4")

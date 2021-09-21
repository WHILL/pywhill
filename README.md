# pywhill
pywhill is a WHILL Model CR SDK for Python. <br>
We also have [Model CR Technical Support repository](https://github.com/WHILL/Model_CR_Technical_Support) for current and potential Model CR users. <br>
For general questions and requests, please visit our [product page](https://whill.inc/jp/model-cr) .

<img src="https://user-images.githubusercontent.com/2618822/45492944-89421c00-b7a8-11e8-9c92-22aa3f28f6e4.png" width=30%>


## Requirements
- WHILL **Model CR**  (Normal **Model C** does not support serial communication.)
- Python3.6 or later
- pySerial (https://github.com/pyserial/pyserial)

## OS Support
- Windows 10
- MacOS X
- Ubuntu 16.04
- Ubuntu 18.04

## Getting Started
Clone or download this repository at any place you want, or this package is avalable on [PyPI](https://pypi.org/project/whill/).

```
python3 -m pip install whill
```

## APIs

### Initialize

```python
from whill import ComWHILL
<your_obj_name> = ComWHILL(port=<Your COM Port>)
```
Initialize WHILL instance with SoftwareSerial.

### Communication

```python
<your_obj_name>.start_data_stream(interval_msec=<update interval in millisecond>)
```
Command WHILL to start reporting WHILL status.

```python
<your_obj_name>.refresh()
```
Fetch serial interface and do internal process.


```python
<your_obj_name>.stop_data_stream()
```
Command WHILL to stop report WHILL status.


### Manipulation

```python
<your_obj_name>.set_joy_stick(front=<Integer -100~100>, side=<Integer -100~100>)
```
Manipulate a WHILL via this command.
Both `front` and `side` are integer values with range -100 ~ 100.


```python
<your_obj_name>.send_power_on()
<your_obj_name>.send_power_off()
<your_obj_name>.set_power(power_state_command=<True/False>)

```
Turn on/off a WHILL. `power_state_command` is a bool with `True` to power WHILL on.

```python
<your_obj_name>.set_battery_voltage_output_mode(vbatt_on_off=<True/False>)
```
Enable/Disable power supply to the interface connector. `True` to enable power supply.


### Sensors and Status

### Accelerometer **(deprecated)**
Accelerometer API has been disabled since v1.2.0.

#### Gyro **(deprecated)**
Gyro API has been disabled since v1.2.0.

#### Battery
```python
<your_obj_name>.battery
```
Remaining battery level[%] and consumpting current[mA].


#### Motor State
```python
<your_obj_name>.left_motor
<your_obj_name>.right_motor
```
Motors angle and speed. The angle range is -PI to +PI, Speed unit is km/h.
**Note that the speed value is low-pass filterd.**

#### Speed Mode
```python
<your_obj_name>.speed_mode_indicator
```
Current selected speed mode.

### Callback
```python
<your_obj_name>.register_callback(event=<either 'data_set_0' or 'data_set_1', func=<your callback function>)
```
By registering callback functions, You can hook at status is updated.
See Example: [cr_example3_callback.py](https://github.com/WHILL/pywhill/blob/master/example/cr_example3_callback.py)

## License
MIT License

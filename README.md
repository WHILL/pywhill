# pywhill
"pywhill" is a Python SDK for WHILL Model CR series. <br>
We also have [Model CR Series Technical Support](https://github.com/WHILL/Model_CR_Technical_Support) for current and potential Model CR series users. <br>
For general questions and requests, please visit our [product page](https://whill.inc/jp/model-cr2) .

<img src="https://user-images.githubusercontent.com/2618822/45492944-89421c00-b7a8-11e8-9c92-22aa3f28f6e4.png" width=30%>

**Note:** "Model CR series" refers to Model CR and Model CR2.

## Requirements
- WHILL **Model CR / CR2**  (Normal **Model C / C2** does not support serial communication.)
- Python3.6 or later
- pySerial (https://github.com/pyserial/pyserial)

## OS Support
- Windows 10 / 11
- MacOS X
- Ubuntu 16.04
- Ubuntu 18.04

## Installation
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


### Power Control
```python
<your_obj_name>.send_power_on()
<your_obj_name>.send_power_off()
<your_obj_name>.set_power(power_state_command=<True/False>)
```
Turn on/off a WHILL. `power_state_command` is a bool with `True` to power WHILL on.

```python
<your_obj_name>.set_battery_voltage_output_mode(vbatt_on_off=<True/False>)
```
Enable/Disable power supply to the interface connector. `True` to enable power supply. **For Model CR only.**

```python
<your_obj_name>.set_battery_saving(low_battery_level=<Integer -100~100>, sounds_buzzer=<True/False>)
```
Configure battery protection settings. **For Model CR2 only.**
`low_battery_level` is battery charge level to engage the standby mode with range 1 ~ 90.
`sounds_buzzer` is Enable/Disable a buzzing sound at the battery charge level of `low_battery_level` + 10 percentage points. `True` to enable a buzzing sound when battery level low.
As default, `low_battery_level` is 19 and `sounds_buzzer` is True.

### Motor Control
```python
<your_obj_name>.send_joystick(front=<Integer -100~100>, side=<Integer -100~100>)
```
Manipulate a WHILL via this command.
Both `front` and `side` are integer values with range -100 ~ 100.


```python
<your_obj_name>.send_velocity(front=<Integer -500~1500>, side=<Integer -750~750>)
```
Control the speed of a WHILL directly via this command. (Available since v1.3.0)
`front` is  integer values with range -500 ~ 1500 [0.004km/h].
`side` is integer values with range -750 ~ 750 [0.004km/h].
**Attention:**
WHILL moves so quickly using SetVelocity command and so pay enough attention to use SetVelocity command. Basically, send this command to increase speed gradually.



### Data Fetching

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


### Data Reference
You can refer to the value fetched by the above command (Data Fetching).

#### Accelerometer **(deprecated)**
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
By registering callback functions, you can hook at status is updated.
See Example: [cr_example3_callback.py](https://github.com/WHILL/pywhill/blob/master/example/cr_example3_callback.py)

## License
MIT License

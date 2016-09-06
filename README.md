# Freebox-OS-munin
*Freebox Revolution & Freebox 4K's stats monitoring using munin*

| ![freebox-traffic](doc/freebox_traffic-day.png) | ![freebox-xdsl](doc/freebox_xdsl-day.png) | (missing graph) | ![freebox-temp](doc/freebox_temp-day.png) | ![freebox-switch1](doc/freebox_switch1-day.png) | ... | ![freebox-switch4](doc/freebox_switch4-day.png) | ![freebox-switch4](doc/freebox_df-day.png) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| freebox-traffic | freebox-xdsl | freebox-xdsl-errors | freebox-temp | freebox-switch1 | ... | freebox-switch4 | freebox-df |

## Usage

0. This plugin relies on `requests`:

    ```bash
    pip3 install requests
    ```

1. Clone this project on your server:
    
    ```bash
    git clone https://github.com/chteuchteu/Freebox-OS-munin.git && cd Freebox-OS-munin
    clone_path=$(pwd)
    ```

2. Launch authorization script

    ```bash
    ./main.py authorize
    ```

3. Install the plugins

> Tip: you don't have to symlink each mode. Skip some if you don't need all information

    ```bash
    ln -s "$clone_path"/main.py /etc/munin/plugins/freebox-traffic
    ln -s "$clone_path"/main.py /etc/munin/plugins/freebox-temp
    ln -s "$clone_path"/main.py /etc/munin/plugins/freebox-xdsl
    ln -s "$clone_path"/main.py /etc/munin/plugins/freebox-xdsl-errors
    ln -s "$clone_path"/main.py /etc/munin/plugins/freebox-switch1
    ln -s "$clone_path"/main.py /etc/munin/plugins/freebox-switch2
    ln -s "$clone_path"/main.py /etc/munin/plugins/freebox-switch3
    ln -s "$clone_path"/main.py /etc/munin/plugins/freebox-switch4
    ln -s "$clone_path"/main.py /etc/munin/plugins/freebox-df
    
    service munin-node restart
    ```

4. Test it

    ```
    munin-run freebox-traffic
    ```

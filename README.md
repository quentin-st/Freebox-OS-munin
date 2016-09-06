# Freebox-OS-munin
*Freebox Revolution & Freebox 4K's stats monitoring using munin*

| ![freebox-traffic](doc/freebox_traffic-day.png) | ![freebox-xdsl](doc/freebox_xdsl-day.png) | ![freebox-xdsl](doc/freebox_xdsl_errors-day.png) | ![freebox-temp](doc/freebox_temp-day.png) | ![freebox-switch1](doc/freebox_switch1-day.png) | ... | ![freebox-switch4](doc/freebox_switch4-day.png) | ![freebox-df](doc/freebox_df-day.png) | ![freebox-hddspin](doc/freebox_hddspin-day.png) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| freebox-traffic | freebox-xdsl | freebox-xdsl-errors | freebox-temp | freebox-switch1 | ... | freebox-switch4 | freebox-df | freebox-hddspin |

## Usage

1. This plugin relies on `requests`:

    ```bash
    pip3 install requests
    ```

2. Clone this project on your server:
    
    ```bash
    git clone https://github.com/chteuchteu/Freebox-OS-munin.git && cd Freebox-OS-munin
    clone_path=$(pwd)
    ```

3. Launch authorization script

    ```bash
    ./main.py authorize
    ```

4. Install the plugins

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
    ln -s "$clone_path"/main.py /etc/munin/plugins/freebox-hddspin
    
    service munin-node restart
    ```

5. Add plugin configuration to `/etc/munin/plugin-conf.d/munin-node`
   ```bash
   sudo nano /etc/munin/plugin-conf.d/munin-node
   ```

   Insert :
   ```bash
   [freebox*]
   user root
   ```

   Restart munin node service
   ```bash
   sudo service munin-node restart
   ```

6. Test it

    ```
    munin-run freebox-traffic
    ```

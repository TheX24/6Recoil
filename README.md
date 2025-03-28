<img src="/6ecoil.png?raw=true" width="192" />

# r6recoil
a python program made by my beloved chatgpt to control the recoil in the famous tom clancy's book game adaptation\
the code is available to the public and i included all of the weapons in r6

## features
- start/stop button
- caps lock to toggle the script
- able to set custom amount of recoil control
- turns off when switching to secondary (toggleable)
- always on top (toggleable)
- turns off caps lock when writing in chat (toggleable)
- auto writes glhf, ggwp, nt, nice team, good job in chat with f1-f5 keys 
- random operator select for fun

## setup to use my guns config
1. download and open program
2. go into shooting range
3. select an operator
4. select the operator's gun in the program
5. adjust the sleep duration until there's no recoil (increase if its pulling down too much and decrease if pulling down too little)
6. save it
7. now everytime you run it you wont have to change anything

## usage
1. open program
2. click start
3. scroll on the box or select the current gun (automatically applies)
4. turn on caps lock
5. ads and shoot

## build
1. download repository as zip or clone with git
2. install dependecies
3. build with either pyinstaller with this command: `pyinstaller --name "6Recoil" --windowed --icon=icon.ico --add-data "attack_operators.txt;." --add-data "defense_operators.txt;." --add-data "speed_options.txt;." --add-data "icon.ico;." --add-data "config.ini;." 6Recoil_v1.3.pyw`
4. or build it with your favourite builder

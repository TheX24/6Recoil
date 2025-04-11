<img src="/6Recoil.png?raw=true" width="192" />

# 6Recoil
a free python program to control the recoil

## features
- start/stop button
- caps lock to toggle the script
- able to set custom amount of recoil control
- turns off when switching to secondary (toggleable)
- always on top (toggleable)
- turns off caps lock when writing in chat (toggleable)
- auto writes glhf, ggwp, nt, nice team, good job in chat with f1-f5 keys (customizable)
- random operator select for fun

## setup
1. download and open program
2. go into shooting range
3. select an operator
4. turn on custom speed
5. put the gun's rpm
6. adjust the values until there's no recoil (vert: increase if there's recoil; horiz: positive moves to the right, negative moves to the left)
7. open the _internal folder
8. open speed_options_new.txt
9. delete everything
10. add the guns using this format: `{name} = {vertical}, {horizontal}, {rpm}`
12. save it
13. now everytime you run it you wont have to change anything

## usage
1. open program
2. click start
3. scroll on the box or select the current gun (automatically applies)
4. turn on caps lock
5. ads and shoot

## build
1. download repository as zip or clone with git
2. install dependecies
3. just use it or build with either pyinstaller with this command: `pyinstaller --name "6Recoil" --windowed --icon=icon.ico --add-data "attack_operators.txt;." --add-data "defense_operators.txt;." --add-data "speed_options_new.txt;." --add-data "icon.ico;." --add-data "config.ini;." 6Recoil_v1.4.pyw` or build it with your favourite builder

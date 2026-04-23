本课程需要逐渐熟悉terminal 命令行操作

讲课以win11+wsl为主

Mac/ubuntu的 terminal 比win更流畅
安装wsl ubuntu
1.win 商店下载ubuntu系统
2.排除wsl配置错误
3.设置账户名密码进入系统
报错解决:

管理员权限打开 
powershell(Windows Command Prompt)

运行
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart 
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

wsl.exe --update
用户名不可以是简单的数字
别忘记密码, 密码输入没有显示
安装ros2
1.运行脚本
2.跑验证的小乌龟ros程序
打开Ubuntu终端，运行一键安装脚本

wget http://fishros.com/install -O fishros
bash fishros
요일 수업


一键安装
不换源
ros官方
ros-humble-desktop
验证ROS2安装
# 启动小乌龟
ros2 run turtlesim turtlesim_node

# 另一个终端启动控制
ros2 run turtlesim turtle_teleop_key

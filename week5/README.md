ubuntu(linux) 终端操作/目录操作
ubuntu(linux)学习资料与学习用途


panda机器人的运动学展示

机器人基本概念：关节空间/坐标空间、正运动学/逆运动学
进入小区，保安会问你的人生三大终极问题：
你是谁？
who
你从哪里来？
pwd  当前位置目录
ls  当前位置的文件和文件夹
你要去哪里？
cd 目标目录地址
绝对地址
/开头


相对地址
直接开始
由./开始
由../开始
自学linux用途：

服务器运维
服务器网站搭建

梯子/翻墙
vps（Virtual Private Server，虚拟专用服务器）
将一台物理服务器通过虚拟化技术划分为多个独立虚拟服务器的服务。
每个VPS都拥有独立的公网IP、操作系统（OS）、内存、磁盘空间及CPU资源，
用户获得“独占”体验，可自行安装程序、重启服务器

在程序里感受坐标系
https://github.com/ai-robot-class/ai-robot-frank
关节空间是基于机器人**每一个驱动电机（关节）**的状态来描述位姿的。
定义方式：用一组向量 $\theta = [\theta_1, \theta_2, ..., \theta_n]$ 来表示。对于你的 Panda 机器人，它有 7 个旋转关节，所以关节空间是一个七维空间。
坐标单位：通常是弧度 (rad) 或 角度 (deg)。
物理意义：直接对应电机转动的角度。当你改变滑块 J0 时，你是在关节空间中移动。
特点：
唯一性：给定一组关节角度，机器人在空间中的形状是唯一确定的。
非直观性：人很难通过脑补“J1转30度，J2转-10度”来判断机器人末端具体在哪个坐标点。

坐标空间（通常指笛卡尔空间）是基于**外部参考系（世界坐标系）**来描述机器人末端执行器（Hand/Gripper）的位置和姿态的。
定义方式：通常用位置 $(x, y, z)$ 和姿态（如欧拉角 $Roll, Pitch, Yaw$ 或四元数）来表示。
坐标单位：米 (m) 或 毫米 (mm)，以及弧度/角度。
物理意义：描述末端夹爪在三维世界里的具体位置。当你输入 0.5, 0.2, 0.0 抓取物体时，你是在坐标空间中操作。
特点：
直观性：符合人类对物理世界的认知（前后、上下、左右）。
多解性（冗余性）：对于同一个坐标点，机器人可能可以用好几种不同的姿态（关节组合）去触碰它。

在机器人学中，**关节空间（Joint Space）与笛卡尔坐标空间（Cartesian/Task Space）**是描述机器人位姿的两套完全不同但又紧密相关的“语言”。
简单来说，关节空间关注的是**“机器人自己是怎么长的”，而坐标空间关注的是“机器人在世界上是怎么动的”**。
正向运动学 (Forward Kinematics, FK)
方向：关节空间 $\rightarrow$ 坐标空间
过程：已知每个关节转了多少度，计算出末端夹爪在哪。
计算难度：简单且唯一。通过简单的三角函数组合（齐次变换矩阵）即可算出。

逆向运动学 (Inverse Kinematics, IK)
方向：坐标空间 $\rightarrow$ 关节空间
过程：已知目标物体在 [0.5, 0.05, 0.1]，计算 7 个电机分别要转多少度。
计算难度：困难且复杂。可能存在无解（够不着）、唯一解或多解（比如你可以手肘向上或者手肘向下抓同一个杯子）。这就是为什么我们在程序中需要调用 p.calculateInverseKinematics 让计算机去迭代求解。

# 画圆形状的伪代码示例 
for theta in range(0, 360, step):    
  x = center_x + R * cos(theta) 
  y = center_y + R * sin(theta) 
  z = center_z robot.move_lin(x, y, z) 

# 直线运动到下一个微小点
计算逆运动学：
p.calculateInverseKinematics( pandaId, 11, [tx, ty, tz], 
```import pybullet as p
import pybullet_data as pd
import time
import math

# --- 1. 환경 초기화 | 环境初始化 | Environment Initialization ---
p.connect(p.GUI)
p.setAdditionalSearchPath(pd.getDataPath())
p.setGravity(0, 0, -9.8) # 표준 Z-Up 중력 | 标准Z轴重力 | Standard Z-Up gravity
p.configureDebugVisualizer(p.COV_ENABLE_GUI, 1)
# 카메라 위치 설정 | 设置摄像头视角 | Set camera view
p.resetDebugVisualizerCamera(1.5, 45, -30, [0.5, 0, 0.65])

# 지면 및 테이블 로드 | 加载地面与桌子 | Load plane and table
p.loadURDF("plane.urdf")
table_pos = [0.5, 0, 0] 
p.loadURDF("table/table.urdf", table_pos, useFixedBase=True)

# 로봇 암 로드 (테이블 위에 고정) | 加载并固定机器人 | Load & fix robot on table
panda_pos = [0.5, 0, 0.625] # Z=0.625는 테이블 높이 | 桌面高度 | Table height
pandaId = p.loadURDF("franka_panda/panda.urdf", panda_pos, useFixedBase=True)

# --- 2. 컨트롤 패널 생성 | 创建控制面板 | Create Control Panel ---
# 모드 전환 스위치 (체크 시 IK 모드) | 模式切换开关 | Mode toggle (Checked = IK)
mode_toggle = p.addUserDebugParameter("RUN IK (Checked) / RUN JOINT (Unchecked)", 1, 0, 0)

# A. 데카르트 좌표계 슬라이더 | 笛卡尔坐标滑块 | Cartesian Sliders (X, Y, Z)
p.addUserDebugText("--- CARTESIAN SETTINGS ---", [1.2, 0.5, 1.2], [0,0,1], 1)
ctrl_x = p.addUserDebugParameter("Target_X", 0.3, 0.8, 0.6)
ctrl_y = p.addUserDebugParameter("Target_Y", -0.4, 0.4, 0.0)
ctrl_z = p.addUserDebugParameter("Target_Z", 0.65, 1.2, 0.8)

# B. 관절 공간 슬라이더 | 关节空间滑块 | Joint Space Sliders (J0-J6)
p.addUserDebugText("--- JOINT SETTINGS ---", [1.2, -0.5, 1.2], [0,0.5,0], 1)
joint_params = []
joint_names = ["J0_Base", "J1_Shoulder", "J2_Arm", "J3_Elbow", "J4_Forearm", "J5_Wrist", "J6_Flange"]
# Panda 관절 한계 설정 | 关节限位设置 | Joint limits for Panda
joint_limits = [(-2.89, 2.89), (-1.76, 1.76), (-2.89, 2.89), (-3.07, -0.06), (-2.89, 2.89), (-0.01, 3.75), (-2.89, 2.89)]
for i in range(7):
    joint_params.append(p.addUserDebugParameter(joint_names[i], joint_limits[i][0], joint_limits[i][1], 0.0))

info_id = -1 # 디버그 텍스트 ID | 调试文本ID | Debug text ID

# --- 3. 메인 로직 루프 | 核心逻辑循环 | Main Logic Loop ---
try:
    while True:
        # 스위치 상태 확인 | 读取开关状态 | Read mode toggle state
        run_ik = p.readUserDebugParameter(mode_toggle)
        
        if run_ik > 0.5:
            # ======= 모드 1: 역운동학 (IK) | 模式1: 逆向运动学 | Mode 1: Inverse Kinematics =======
            tx = p.readUserDebugParameter(ctrl_x)
            ty = p.readUserDebugParameter(ctrl_y)
            tz = p.readUserDebugParameter(ctrl_z)
            
            # IK 계산: 목표 좌표 -> 관절 각도 | 计算关节角度 | Calculate joint angles from XYZ
            joint_poses = p.calculateInverseKinematics(
                pandaId, 11, [tx, ty, tz], 
                p.getQuaternionFromEuler([math.pi, 0, 0]) # 집게가 아래를 향하도록 설정 | 保持夹爪向下 | Gripper face down
            )
            
            # 모터 제어 적용 | 应用电机控制 | Apply motor control
            for i in range(7):
                p.setJointMotorControl2(pandaId, i, p.POSITION_CONTROL, joint_poses[i], force=500)
            
            mode_str = "CURRENT MODE: CARTESIAN (IK)"
        
        else:
            # ======= 모드 2: 관절 직접 제어 (FK) | 模式2: 关节直接控制 | Mode 2: Joint Direct Control =======
            for i in range(7):
                target_val = p.readUserDebugParameter(joint_params[i])
                p.setJointMotorControl2(pandaId, i, p.POSITION_CONTROL, target_val, force=500)
            
            mode_str = "CURRENT MODE: JOINT SPACE (Direct)"

        # --- 4. 데이터 피드백 표시 | 数据反馈显示 | Data Feedback Display ---
        # 엔드 이펙터 실제 위치 획득 (순운동학 결과) | 获取末端实际位置 | Get actual EE position (FK result)
        ee_state = p.getLinkState(pandaId, 11)
        curr_p = ee_state[0]
        # 실제 관절 각도 읽기 | 读取实际关节角度 | Read actual joint states
        curr_j = [p.getJointState(pandaId, i)[0] for i in range(7)]

        # 화면 텍스트 업데이트 | 更新屏幕文本 | Update screen text
        if info_id != -1:
            p.removeUserDebugItem(info_id)
        
        display_text = f"{mode_str}\n"
        display_text += f"End-Effector [X,Y,Z]: [{curr_p[0]:.2f}, {curr_p[1]:.2f}, {curr_p[2]:.2f}]\n"
        display_text += "-"*30 + "\n"
        display_text += "Real-time Joints (rad):\n" + "\n".join([f"J{i}: {curr_j[i]:.2f}" for i in range(7)])
        
        # 텍스트 위치 및 색상 설정 | 设置文本位置与颜色 | Set text position and color
        info_id = p.addUserDebugText(display_text, [0.4, -0.8, 0.8], [0,0,0], 1.2)

        p.stepSimulation() # 시뮬레이션 한 단계 진행 | 步进仿真 | Step simulation
        time.sleep(1./120.) # 실행 속도 조절 | 控制运行频率 | Control execution frequency

except Exception as e:
    print(f"Error occurred: {e}")
finally:
    p.disconnect() # 연결 종료 | 断开连接 | Disconnect
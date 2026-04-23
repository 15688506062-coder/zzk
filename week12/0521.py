import pybullet as p
import pybullet_data
import time
import numpy as np
import math


class QuadrupedController:
    """简单四足机器人控制器（慢速行走版）"""

    def __init__(self, robot_id):
        self.robot_id = robot_id

        # Laikago 实际腿部关节ID
        self.leg_joints = {
            'LF': [0, 1, 2],     # 左前
            'RF': [4, 5, 6],     # 右前
            'LH': [8, 9, 10],    # 左后
            'RH': [12, 13, 14]   # 右后
        }

        # 行走参数（调慢）
        self.stance_height = 0.42
        self.step_height = 0.03
        self.step_length = 0.04

    def trot_gait(self, t, leg_name, frequency=0.3):
        """
        慢速Trot步态
        """

        # 对角腿同步
        if leg_name in ['LF', 'RH']:
            phase = 0
        else:
            phase = np.pi

        cycle = (2 * np.pi * frequency * t + phase) % (2 * np.pi)

        # x 前后摆动
        if cycle < np.pi:
            progress = cycle / np.pi

            # 抬腿阶段
            x = self.step_length * (progress - 0.5)

            # 平滑抬腿
            z = self.step_height * np.sin(np.pi * progress)

        else:
            progress = (cycle - np.pi) / np.pi

            # 着地向后
            x = self.step_length * (0.5 - progress)
            z = 0

        # ===== 简化逆运动学 =====

        hip = 0

        # 更稳定的腿部角度
        thigh_base = 0.7
        calf_base = -1.4

        thigh = thigh_base + x * 4 - z * 2
        calf = calf_base + z * 3

        return [hip, thigh, calf]

    def stand_pose(self):
        """机器人先站稳"""

        for leg_name, joint_ids in self.leg_joints.items():

            target_angles = [0, 0.7, -1.4]

            for joint_id, angle in zip(joint_ids, target_angles):

                p.setJointMotorControl2(
                    self.robot_id,
                    joint_id,
                    p.POSITION_CONTROL,
                    targetPosition=angle,
                    force=40
                )

    def step(self, t, frequency=0.3):

        for leg_name, joint_ids in self.leg_joints.items():

            target_angles = self.trot_gait(
                t,
                leg_name,
                frequency
            )

            for joint_id, angle in zip(joint_ids, target_angles):

                p.setJointMotorControl2(
                    self.robot_id,
                    joint_id,
                    p.POSITION_CONTROL,
                    targetPosition=angle,
                    force=40
                )


def main():

    # 连接 PyBullet
    p.connect(p.GUI)

    p.setAdditionalSearchPath(pybullet_data.getDataPath())

    p.setGravity(0, 0, -9.8)

    p.setTimeStep(1. / 240.)

    # 地面
    p.loadURDF("plane.urdf")

    # 机器人朝向
    start_orientation = p.getQuaternionFromEuler(
        [math.pi / 2, 0, math.pi / 2]
    )

    # 加载机器人
    robot_id = p.loadURDF(
        "laikago/laikago_toes.urdf",
        [0, 0, 0.48],
        start_orientation
    )

    # 创建控制器
    controller = QuadrupedController(robot_id)

    # ===== 先站稳 =====
    print("机器人站立中...")

    for _ in range(240):

        controller.stand_pose()

        p.stepSimulation()

        time.sleep(1. / 240.)

    # ===== 开始慢慢走 =====
    print("开始慢速行走...")

    t = 0
    dt = 1. / 240.

    # 只走几步
    walk_duration = 12

    while t < walk_duration:

        controller.step(
            t,
            frequency=0.3
        )

        p.stepSimulation()

        time.sleep(dt)

        t += dt

    print("行走结束")

    # 保持画面
    while True:
        p.stepSimulation()
        time.sleep(dt)


if __name__ == '__main__':
    main()
import numpy as np
import time
import random
from pymavlink import mavutil

# MAVLink bağlantıları
drone2 = mavutil.mavlink_connection('127.0.0.1:9003')
drone3 = mavutil.mavlink_connection('127.0.0.1:9013')
drone1 = mavutil.mavlink_connection('127.0.0.1:9023')
drones_mav = [drone1, drone2, drone3]

# MAVLink bağlantılarını bekle
for drone in drones_mav:
    drone.wait_heartbeat()
    print(f"✅ Drone {drone.target_system} bağlı")

# Mode, Arm ve Takeoff
def set_mode(drone, mode):
    mode_id = drone.mode_mapping()[mode]
    drone.mav.set_mode_send(
        drone.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )

def arm_drone(drone):
    drone.mav.command_long_send(
        drone.target_system,
        drone.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1, 0, 0, 0, 0, 0, 0
    )
    drone.motors_armed_wait()

def takeoff_drone(drone, altitude):
    drone.mav.command_long_send(
        drone.target_system,
        drone.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0,
        altitude
    )
    time.sleep(1)

# Başlangıç pozisyonlarını al
def get_initial_position(drone):
    print(f"📡 Drone {drone.target_system} pozisyon alınıyor...")
    while True:
        msg = drone.recv_match(type='LOCAL_POSITION_NED', blocking=True, timeout=5)
        if msg:
            return [msg.x, msg.y, -msg.z]

# Droneları hazırla
for drone in drones_mav:
    set_mode(drone, 'GUIDED')
    arm_drone(drone)
    takeoff_drone(drone, 1.0)

time.sleep(5)

# Başlangıç pozisyonlarını al
start_positions = [get_initial_position(d) for d in drones_mav]

# Hedefler
relative_targets = [
    [1.0, 2.0, 4.0], [2.0, 4.0, 2.0], [3.0, 2.0, 2.0]   # sağ (yüksek)
]
target_positions = [
    np.array(start_positions[i]) + np.array(relative_targets[i])
    for i in range(3)
]

# PID Parametreleri
tolerance = 0.03
safe_distance = 0.5
collision_distance = 0.2
Kp, Ki, Kd = 0.25, 0.005, 0.1

class DroneNode:
    def __init__(self, drone_id, mav, target_pos):
        self.id = drone_id
        self.mav = mav
        self.position = np.zeros(3)
        self.target = np.array(target_pos, dtype=np.float64)
        self.prev_error = np.zeros(3)
        self.integral = np.zeros(3)
        self.reached = False
        self.active = True  # Drone aktif mi (ekipte mi)

    def update_position_from_sim(self):
        msg = self.mav.recv_match(type='LOCAL_POSITION_NED', blocking=False)
        if msg:
            self.position = np.array([msg.x, msg.y, -msg.z])
            return True
        return False

    def communicate(self, all_drones):
        return [d.position for d in all_drones if d.id != self.id and d.active]

    def repulsive_force(self, others):
        force = np.zeros(3)
        for pos in others:
            diff = self.position - pos
            dist = np.linalg.norm(diff)
            if 0 < dist < safe_distance:
                scale = 0.5 if self.id == 1 else 1.0
                force += scale * (diff / dist) * ((safe_distance - dist) ** 2)
        return force

    def pid_velocity(self):
        error = self.target - self.position
        self.integral += error
        derivative = error - self.prev_error
        self.prev_error = error
        return Kp * error + Ki * self.integral + Kd * derivative

    def update(self, frame, all_drones):
        if self.reached or not self.active:
            return

        if not self.update_position_from_sim():
            return

        others = self.communicate(all_drones)
        velocity = self.pid_velocity() + self.repulsive_force(others)

        self.mav.mav.set_position_target_local_ned_send(
            int((time.time() * 1000) % 2**32),
            self.mav.target_system, self.mav.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            int(0b0000111111000111),
            0, 0, 0,
            velocity[0], velocity[1], -velocity[2],
            0, 0, 0,
            0, 0
        )

        if np.linalg.norm(self.position - self.target) < tolerance:
            self.reached = True
            print(f"✅ Drone {self.id} hedefe ulaştı: {np.round(self.position, 3)} ≈ {self.target}")

def check_collision(drones):
    for i in range(len(drones)):
        for j in range(i + 1, len(drones)):
            if drones[i].active and drones[j].active:
                dist = np.linalg.norm(drones[i].position - drones[j].position)
                if dist < collision_distance:
                    print(f"⚠️ Çarpışma Uyarısı: Drone {i} ↔ Drone {j}, Mesafe: {dist:.2f}")

# Drone nesnelerini oluştur
drones = [
    DroneNode(i, drones_mav[i], target_positions[i])
    for i in range(3)
]

# Rastgele ayrılacak drone için bayraklar
leaving_drone_index = random.randint(0, 2)
rtl_sent = False

# Ana kontrol döngüsü
for frame in range(10000):
    print(f"\n🔁 Frame {frame}")

    # Drone ayrılması (10 saniye sonra)
    if frame == 100:
        leaving = drones[leaving_drone_index]
        print(f"\n🚀 Drone {leaving.id} ekipten ayrılıyor ve RTL moduna geçiyor.")
        set_mode(leaving.mav, 'RTL')
        leaving.active = False
        rtl_sent = True

    check_collision(drones)

    for drone in drones:
        drone.update(frame, drones)
        print(f"Drone {drone.id} → Pozisyon: {np.round(drone.position, 3)} | Hedef: {np.round(drone.target, 3)} | Aktif: {drone.active}")

    if all(d.reached or not d.active for d in drones):
        print("\n🌟 Aktif kalan tüm dronelar hedefe ulaştı.")
        break

    time.sleep(0.1)  # 10 Hz

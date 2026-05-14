import numpy as np
import matplotlib.pyplot as plt

# Параметры сетки
Nx, Ny, Nz = 8, 8, 16  # Увеличим разрешение по Z для гладкости профиля
S_0 = 1.0              # Скалярный параметр порядка

# Граничные углы директора на подложках
# Нижняя подложка (z = 0): лежит в плоскости вдоль X (theta=0, phi=0)
theta_bottom, phi_bottom = 0.0, 0.0
# Верхняя подложка (z = Nz-1): лежит в плоскости вдоль Y (theta=0, phi=pi/2)
theta_top, phi_top = 0.0, np.pi / 2

def angles_to_Q_components(theta, phi, S=S_0):
    """Преобразует физические углы theta и phi в 5 компонент тензора Q"""
    nx = np.cos(theta) * np.cos(phi)
    ny = np.cos(theta) * np.sin(phi)
    nz = np.sin(theta)
    
    Qxx = S * (nx*nx - 1.0/3.0)
    Qyy = S * (ny*ny - 1.0/3.0)
    Qxy = S * (nx*ny)
    Qxz = S * (nx*nz)
    Qyz = S * (ny*nz)
    return np.array([Qxx, Qyy, Qxy, Qxz, Qyz])

def Q_to_angles(Q_vector, S=S_0):
    """Преобразует 5 компонент тензора Q обратно в углы theta и phi"""
    Qxx, Qyy, Qxy, Qxz, Qyz = Q_vector
    Qzz = -(Qxx + Qyy)
    
    # Расчет азимутального угла phi
    phi = 0.5 * np.arctan2(2.0 * Qxy, Qxx - Qyy)
    
    # Расчет полярного угла theta (с ограничением под аргументом арксинуса от ошибок округления)
    sin2_theta = Qzz / S + 1.0 / 3.0
    sin2_theta = np.clip(sin2_theta, 0.0, 1.0)
    theta = np.arcsin(np.sqrt(sin2_theta))
    
    return theta, phi

# --- 1. ГЕНЕРАЦИЯ ГРАНИЧНЫХ СОСТОЯНИЙ ДЛЯ NEB ---
Q_start_3d = np.zeros((Nx, Ny, Nz, 5))
Q_end_3d = np.zeros((Nx, Ny, Nz, 5))

for z_idx in range(Nz):
    # Доля расстояния от нижней пластины (от 0.0 до 1.0)
    fraction = z_idx / (Nz - 1)
    
    # НАЧАЛЬНОЕ СОСТОЯНИЕ (Поле E = 0): 
    # Директор плавно закручивается от оси X к оси Y, оставаясь в плоскости пластин (theta = 0)
    th_start = 0.0
    ph_start = phi_bottom + fraction * (phi_top - phi_bottom)
    Q_start_3d[:, :, z_idx, :] = angles_to_Q_components(th_start, ph_start)
    
    # КОНЕЧНОЕ СОСТОЯНИЕ (Поле E -> бесконечность):
    # В объеме директор встает строго вертикально (theta = pi/2). 
    # На самых границах сильное сцепление удерживает углы подложек.
    if z_idx == 0:
        th_end, ph_end = theta_bottom, phi_bottom
    elif z_idx == Nz - 1:
        th_end, ph_end = theta_top, phi_top
    else:
        th_end = np.pi / 2  # Молекулы встали по полю вдоль Z
        ph_end = 0.0        # При вертикальной ориентации азимутальный угол вырождается
        
    Q_end_3d[:, :, z_idx, :] = angles_to_Q_components(th_end, ph_end)

# --- 2. ЭМУЛЯЦИЯ РЕЗУЛЬТАТА МЕТОДА NEB ---
# (В реальном расчете здесь вызывается функция run_3d_lc_neb из прошлого ответа)
# Для демонстрации построения траектории создадим промежуточные имиджи интерполяцией
num_images = 1000
# Форма пути: (num_images + 2, Nx, Ny, Nz, 5)
simulated_path = np.array([Q_start_3d + (Q_end_3d - Q_start_3d) * (i / (num_images + 1)) for i in range(num_images + 2)])

# --- 3. ИЗВЛЕЧЕНИЕ ТРАЕКТОРИИ ДЛЯ ЗАДАННОГО Z ---
# Задаем индекс координаты z (например, середина слоя ячейки)
z_target_idx = Nz // 2 
# Выберем центральный узел по осям X и Y (в однородной по площади задаче они эквивалентны)
x_target, y_target = Nx // 2, Ny // 2

theta_trajectory = []
phi_trajectory = []

# Проходим по всем имиджам упругой ленты (от начального до конечного)
for img_idx in range(num_images + 2):
    Q_at_point = simulated_path[img_idx, x_target, y_target, z_target_idx, :]
    theta, phi = Q_to_angles(Q_at_point)
    
    theta_trajectory.append(np.degrees(theta))
    phi_trajectory.append(np.degrees(phi))

# --- 4. ВИЗУАЛИЗАЦИЯ ТРАЕКТОРИИ ПЕРЕХОДА ---
plt.figure(figsize=(8, 6))

# Измените 'o-' на '-' (чтобы убрать маркеры у линии) или добавьте ms=4 для уменьшения точек линии
plt.plot(phi_trajectory, theta_trajectory, 'o-', color='royalblue', linewidth=2, ms=1, label='Путь NEB')

# Параметр s=30 делает маркеры начального и конечного состояний значительно меньше (было 150)
plt.scatter(phi_trajectory[0], theta_trajectory[0], color='green', s=30, zorder=5, label='Старт (E=0)')
plt.scatter(phi_trajectory[-1], theta_trajectory[-1], color='red', s=30, zorder=5, label='Финиш (E $\to \infty$)')

plt.xlabel('Азимутальный угол $\phi$ (градусы)', fontsize=12)
plt.ylabel('Полярный угол подъема $\theta$ (градусы)', fontsize=12)
plt.xlim(-5, 95)
plt.ylim(-5, 95)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='best')
plt.savefig('norm.png')

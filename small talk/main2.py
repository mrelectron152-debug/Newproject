import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# 1. ПАРАМЕТРЫ СИСТЕМЫ
# =========================================================
N = 100               # Число узлов (больше = точнее, но медленнее)
L = 1.0               # Толщина ячейки
dz = L / N            # Шаг сетки
K = 1.0               # Упругая постоянная
eps_delta = 5.0       # Диэлектрическая анизотропия

# Предпочтительные направления (силы F1 и F2)
# z=0 (нижняя): вдоль X (phi=0, theta=90°)
# z=L (верхняя): вдоль Y (phi=90°, theta=90°)
phi_0_pref = 0
phi_L_pref = np.pi / 2
theta_pref = np.pi / 2

# =========================================================
# 2. СИЛЫ ЯКОРЕНИЯ (Энергия Рапини-Папуляра)
# =========================================================
# W1 > W2 означает, что нижняя пластинка держит сильнее
W_theta_1 = 100.0  # Сила якорения для угла theta внизу (сильная)
W_theta_2 = 10.0   # Сила якорения для угла theta вверху (слабая)

W_phi_1 = 100.0    # Сила якорения для угла phi внизу
W_phi_2 = 10.0     # Сила якорения для угла phi вверху

print(f"Якорение theta: W1={W_theta_1} (низ), W2={W_theta_2} (верх)")
print(f"Якорение phi:   W1={W_phi_1} (низ), W2={W_phi_2} (верх)")

# =========================================================
# 3. ФУНКЦИЯ МИНИМИЗАЦИИ (МЕТОД УПРУГОЙ ЛЕНТЫ)
# =========================================================
def relax_profile_asym(theta, phi, E, n_steps=5000):
    """Релаксация с асимметричными условиями на границах"""
    
    # Коэффициенты релаксации
    alpha_vol = 0.005 * dz**2  # Для объёма
    alpha_surf = 0.01          # Для границ (поверхностная энергия обычно "жестче")
    
    for step in range(n_steps):
        theta_new = theta.copy()
        phi_new = phi.copy()
        
        # --- А. ОБЪЁМ (внутренние точки 1...N-1) ---
        for i in range(1, N):
            sin_th = np.sin(theta[i])
            cos_th = np.cos(theta[i])
            
            # Вторые производные (упругость)
            d2theta = (theta[i+1] - 2*theta[i] + theta[i-1]) / dz**2
            d2phi = (phi[i+1] - 2*phi[i] + phi[i-1]) / dz**2
            
            # Производные первого порядка (для связи углов)
            dtheta = (theta[i+1] - theta[i-1]) / (2*dz)
            dphi = (phi[i+1] - phi[i-1]) / (2*dz)
            
            # Уравнения Эйлера-Лагранжа (объёмные силы)
            # Минус перед E^2, т.к. поле стремится к theta=0
            eq_theta = K * d2theta - K * sin_th * cos_th * dphi**2 - \
                       eps_delta * E**2 * sin_th * cos_th
            eq_phi = sin_th**2 * d2phi + 2 * sin_th * cos_th * dtheta * dphi
            
            # Обновление
            theta_new[i] += alpha_vol * eq_theta
            phi_new[i] += alpha_vol * eq_phi
            
        # --- Б. ГРАНИЦЫ (z=0 и z=L) ---
        # Здесь работает баланс: Упругость <-> Якорение (W)
        
        # 1. Нижняя граница (i=0)
        # Упругая сила: стремится к значению в точке 1
        elastic_theta_0 = K * (theta[1] - theta[0]) / dz
        elastic_phi_0   = np.sin(theta[0])**2 * (phi[1] - phi[0]) / dz
        
        # Сила якорения: стремится вернуть к preferred
        # d/dtheta [W/2 sin^2(theta-pref)] = W sin(theta-pref)cos(theta-pref)
        anchoring_theta_0 = -W_theta_1 * np.sin(theta[0] - theta_pref) * np.cos(theta[0] - theta_pref)
        anchoring_phi_0   = -W_phi_1 * np.sin(phi[0] - phi_0_pref) * np.cos(phi[0] - phi_0_pref)
        
        # Обновляем границы
        theta_new[0] += alpha_surf * (elastic_theta_0 + anchoring_theta_0)
        phi_new[0]   += alpha_surf * (elastic_phi_0 + anchoring_phi_0)
        
        # 2. Верхняя граница (i=N)
        # Упругая сила: стремится к значению в точке N-1 (знак меняется)
        elastic_theta_L = K * (theta[N-1] - theta[N]) / dz
        elastic_phi_L   = np.sin(theta[N])**2 * (phi[N-1] - phi[N]) / dz
        
        # Сила якорения (W2 - слабее!)
        anchoring_theta_L = -W_theta_2 * np.sin(theta[N] - theta_pref) * np.cos(theta[N] - theta_pref)
        anchoring_phi_L   = -W_phi_2 * np.sin(phi[N] - phi_L_pref) * np.cos(phi[N] - phi_L_pref)
        
        theta_new[N] += alpha_surf * (elastic_theta_L + anchoring_theta_L)
        phi_new[N]   += alpha_surf * (elastic_phi_L + anchoring_phi_L)
        
        # Ограничения и нормализация
        theta_new = np.clip(theta_new, 0.001, np.pi - 0.001)
        theta = theta_new
        phi = phi_new
        
        # Критерий сходимости
        if step % 1000 == 0 and step > 0:
            if np.max(np.abs(theta_new - theta)) < 1e-6:
                break
                
    return theta, phi

# =========================================================
# 4. ОСНОВНОЙ ЦИКЛ РАСЧЁТА
# =========================================================
print("\nЗапуск расчёта...")
z = np.linspace(0, L, N+1)

# Начальное условие: почти плоско, с малым возмущением
theta = np.full(N+1, np.pi/2)
phi = np.linspace(phi_0_pref, phi_L_pref, N+1)
perturbation = 0.05 * np.exp(-((z - 0.5)/0.15)**2)
theta = theta - perturbation

E_values = np.linspace(0, 12, 40)
profiles = {}
E_to_save = [0, 4, 8, 12]

for E in E_values:
    theta, phi = relax_profile_asym(theta, phi, E, n_steps=3000)
    
    # Сохраняем интересные кадры
    for E_save in E_to_save:
        if abs(E - E_save) < 0.2:
            profiles[E_save] = (theta.copy(), phi.copy())
            break

# =========================================================
# 5. ВИЗУАЛИЗАЦИЯ
# =========================================================

# --- ГРАФИК 1: ТРАЕКТОРИЯ В ЦЕНТРЕ ---
plt.figure(figsize=(6, 5))
theta_mid = [profiles[E][0][N//2] for E in E_to_save if E in profiles]
phi_mid = [profiles[E][1][N//2] for E in E_to_save if E in profiles]

plt.plot(phi_mid, theta_mid, 'bo-', markersize=8)
plt.xlabel(r'$\phi$ (азимут)', fontsize=12)
plt.ylabel(r'$\theta$ (зенит)', fontsize=12)
plt.title('Траектория центра ячейки', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.show()

# --- ГРАФИК 2: ПРОФИЛИ (АСИММЕТРИЯ!) ---
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for idx, E_val in enumerate(E_to_save):
    if E_val in profiles:
        th, ph = profiles[E_val]
        
        # Строим theta
        axes[idx].plot(z, th*180/np.pi, 'b-', linewidth=2.5, label=r'$\theta(z)$')
        
        # Для наглядности асимметрии, нарисуем линию среднего значения
        axes[idx].axhline(y=90, color='gray', linestyle=':', alpha=0.3)
        
        axes[idx].set_title(f'Профиль $\theta$ при E = {E_val}', fontsize=14)
        axes[idx].set_ylabel('Угол (градусы)', fontsize=12)
        axes[idx].set_xlabel('Координата z', fontsize=12)
        axes[idx].set_ylim(0, 100)
        axes[idx].grid(True, linestyle=':', alpha=0.6)
        axes[idx].legend()

plt.suptitle('Асимметрия профиля из-за W1 > W2', fontsize=16, y=1.02)
plt.tight_layout()
plt.savefig('plot.png')

print("Расчёт завершен. Обратите внимание на графики профилей при E=12.")
print("Минимум должен быть смещен в сторону z=1 (где якорение W2 слабее).")

import numpy as np
import matplotlib.pyplot as plt

N = 100    # число слоев нематика           
L = 1.0    # толщина
dz = L / N
K = 1.0   #jlyjrjycnfynjyjt ghb,kb;tybt
eps_delta = 5.0     #анизотропия

phi_0 = 0
phi_L = np.pi / 2
theta_bc = np.pi / 2
def relax_profile(theta, phi, E, n_steps=5000):
    alpha = 0.005 * dz**2 
    
    for step in range(n_steps):
        theta_new = theta.copy()
        phi_new = phi.copy()
        
        for i in range(1, N):
            sin_th = np.sin(theta[i])
            cos_th = np.cos(theta[i])
            
            d2theta = (theta[i+1] - 2*theta[i] + theta[i-1]) / dz**2
            d2phi = (phi[i+1] - 2*phi[i] + phi[i-1]) / dz**2
            dtheta = (theta[i+1] - theta[i-1]) / (2*dz)
            dphi = (phi[i+1] - phi[i-1]) / (2*dz)
            
            residual_theta = K * d2theta - K * sin_th * cos_th * dphi**2 - \
                             eps_delta * E**2 * sin_th * cos_th
            residual_phi = sin_th**2 * d2phi + 2 * sin_th * cos_th * dtheta * dphi
            
            theta_new[i] += alpha * residual_theta
            phi_new[i] += alpha * residual_phi
        
        theta_new[0] = theta_bc
        theta_new[N] = theta_bc
        phi_new[0] = phi_0
        phi_new[N] = phi_L
        
        theta_new = np.clip(theta_new, 0.001, np.pi - 0.001)
        
        theta = theta_new
        phi = phi_new
        
        if step % 1000 == 0 and step > 0:
            if np.max(np.abs(theta_new - theta)) < 1e-8:
                break
                
    return theta, phi



z = np.linspace(0, L, N+1)

theta = np.full(N+1, np.pi/2)
perturbation = 0.0001 * np.exp(-((z - 0.5)/0.15)**2) 
theta = theta - perturbation

phi = np.linspace(phi_0, phi_L, N+1)

E_values = np.linspace(0, 12, 60)

theta_mid = []
phi_mid = []

# ИСПРАВЛЕНИЕ: сохраняем профили для ключевых значений E
profiles = {}
E_to_save = [0, 2, 4, 6, 8, 10, 12, 16, 18, 20, 22, 24]

for E in E_values:
    theta, phi = relax_profile(theta, phi, E, n_steps=3000)
    
    # Сохраняем профили для определённых E
    for E_save in E_to_save:
        if abs(E - E_save) < 0.1:  # ближайшее значение
            profiles[E_save] = (theta.copy(), phi.copy())
            break
    
    mid = N // 2
    theta_mid.append(theta[mid])
    phi_mid.append(phi[mid])

# =========================================================
# ВИЗУАЛИЗАЦИЯ 1: ТРАЕКТОРИЯ (В ЕДИНИЦАХ PI)
# =========================================================
plt.figure(figsize=(8, 6))

# Переводим массивы углов в единицы pi
phi_mid_pi = np.array(phi_mid) / np.pi
theta_mid_pi = np.array(theta_mid) / np.pi

plt.plot(phi_mid_pi, theta_mid_pi, 'b-o', linewidth=2, markersize=3, label='Траектория')

# Стрелки направления с учетом масштаба pi
for i in range(0, len(phi_mid_pi)-1, 5):
    plt.arrow(phi_mid_pi[i], theta_mid_pi[i], 
             0.2*(phi_mid_pi[i+1]-phi_mid_pi[i]), 0.2*(theta_mid_pi[i+1]-theta_mid_pi[i]),
             head_width=0.01, fc='green', ec='green', alpha=0.6)

# Граничные условия в единицах pi
plt.scatter([phi_0/np.pi, phi_L/np.pi], [theta_bc/np.pi, theta_bc/np.pi], 
            color='red', s=50, zorder=5, label='Граничные условия')

# Настройка названий осей
plt.xlabel(r'$\phi \ / \ \pi$', fontsize=12)
plt.ylabel(r'$\theta \ / \ \pi$', fontsize=12)
plt.title('Траектория директора в центре слоя', fontsize=12)

# Сетка и метки в долях pi (от 0 до 0.5)
ticks = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
tick_labels = ['0', '0.1', '0.2', '0.3', '0.4', '0.5']

plt.xticks(ticks, tick_labels)
plt.yticks(ticks, tick_labels)

plt.xlim(-0.05, 0.55)
plt.ylim(0.0, 0.55)

plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig('Vova.png')

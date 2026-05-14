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
perturbation = 0.1 * np.exp(-((z - 0.5)/0.15)**2) 
theta = theta - perturbation

phi = np.linspace(phi_0, phi_L, N+1)

E_values = np.linspace(0, 12, 60)

theta_mid = []
phi_mid = []

# ИСПРАВЛЕНИЕ: сохраняем профили для ключевых значений E
profiles = {}
E_to_save = [0, 2, 4, 6, 8, 10, 12]

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

import matplotlib.ticker as ticker

# =========================================================
# ВИЗУАЛИЗАЦИЯ 1: ТРАЕКТОРИЯ (В ЕДИНИЦАХ PI)
# =========================================================
plt.figure(figsize=(8, 6))

# Делим массивы на np.pi для перевода координат
phi_mid_pi = np.array(phi_mid) / np.pi
theta_mid_pi = np.array(theta_mid) / np.pi

# Строим график в новых координатах
plt.plot(phi_mid_pi, theta_mid_pi, 'b-o', linewidth=2, markersize=3, label='Траектория')

plt.xlabel(r'$\phi / \pi$', fontsize=12)
plt.ylabel(r'$\theta / \pi$', fontsize=12)
plt.title('Траектория директора (в единицах $\pi$)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()

# Настройка красивых меток осей с шагом 0.1 * pi
ax = plt.gca()
ax.xaxis.set_major_locator(ticker.MultipleLocator(0.1))
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))

# Ограничения осей в долях pi (от -0.05 до 0.55)
plt.xlim(-0.05, 0.55)
plt.ylim(-0.05, 0.55)

plt.tight_layout()
plt.savefig('plotforce.png')


# =========================================================
# ВИЗУАЛИЗАЦИЯ 2: ПРОФИЛИ
# =========================================================
E_to_save = [0, 2, 4, 6, 8, 10, 12]  # 7 значений
n_profiles = len(E_to_save)

# Создаем 2 ряда: 4 в первом, 3 во втором
fig, axes = plt.subplots(2, 4, figsize=(20, 8))
axes = axes.flatten()

for idx, E_val in enumerate(E_to_save):
    if E_val in profiles:
        th_t, ph_t = profiles[E_val]
        axes[idx].plot(z, th_t*180/np.pi, 'b-', linewidth=2, label=r'$\theta$')
        axes[idx].plot(z, ph_t, 'r--', linewidth=2, label=r'$\phi$')
        axes[idx].set_title(f'E = {E_val}', fontsize=11)
        axes[idx].set_xlabel('z')
        axes[idx].legend(fontsize=8)
        axes[idx].grid(True, linestyle=':', alpha=0.6)
        axes[idx].set_ylim(0, 100)

# Удаляем 8-й пустой график
fig.delaxes(axes[7])
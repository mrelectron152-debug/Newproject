import numpy as np
import math

#Коэффициенты Франка
K1 = 1
K2 = 1
K3 = 1

#Размер ячейки:
Lx = 1
Ly = 1
Lz = 100
d = 1 # шаг сетки

A = 10 #Коэффициент для силы, направленной вдоль оси OX и находящейся на нижней плоскости (z=0)
B = 20 #Коэффициент для силы, направленной вдоль оси OY и находящейся на верхней плоскости (z=max)
S = 1 #Параметр порядка

#Параметры Climbing Image NEB:
N = 10 #Количество точек
first = [math.pi, 0] #Координаты начальной точки teta, psi
last = [0,0] #Координаты конечной точки teta, psi

x = np.arange(0, Lx, d)
y = np.arange(0, Ly, d)
z = np.arange(0, Lz, d)
X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

E = 0.5*K1

grad_E_x, grad_E_y, grad_E_z = np.gradient(E, d, d, d)


#def SurfaceEnergy(A, B, tetaA, phiA, tetaB, phiB, S):


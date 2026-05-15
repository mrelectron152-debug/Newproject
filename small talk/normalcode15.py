import numpy as np

#Коэффициенты Франка
K1=1
K2=1
K3=1

#Размер ячейки:
Lx=1
Ly=1
Lz=100
d=1 # шаг сетки

A=10 #Коэффициент для силы, направленной вдоль оси OX и находящейся на нижней плоскости (z=0)
B=20 #Коэффициент для силы, направленной вдоль оси OY и находящейся на верхней плоскости (z=max)
S=1 #Параметр порядка


x = np.arange(0, Lx, d)
y = np.arange(0, Ly, d)
z = np.arange(0, Lz, d)
X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

grad_E_x, grad_E_y, grad_E_z = np.gradient(E, dx, dy, dz)


def SurfaceEnergy(A, B, tetaA, phiA, tetaB, phiB, S):


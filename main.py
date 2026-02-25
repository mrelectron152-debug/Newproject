import random
import math
N=100
L=10
l=1
r=0.1
Nsteps=100
freq=10
count=0
step=1

def distant(L, xi, yi, zi, xj, yj, zj):
    dx=math.fabs(xi-xj)
    dy=math.fabs(yi-yj)
    dz=math.fabs(zi-zj)
    if dx>L/2:
        dx=L-dx
    if dy>L/2:
        dy=L-dy
    if dz>L-dz:
        dz=L-dz
    return math.sqrt(dx**2+dy**2+dz**2)


with open ('file.txt', 'w', encoding='utf-8') as f:
    f.write("")

x = [0]*N
y = [0]*N
z = [0]*N

w=[0, 0, 0]

for i in range(N):
    x[i] = random.uniform(0,L)
    y[i] = random.uniform(0,L)
    z[i] = random.uniform(0,L)  
    
    for j in range(i):
        if distant(L, x[i], y[i], z[i], x[j], y[j], z[j])<r:
            i-=1

for i in range(Nsteps):
    m=random.randint(0,N-1)
    w=[x[m], y[m], z[m]]
    x[m]+=random.uniform(-l/2,l/2)
    if x[m]>L: x[m]-=L
    if x[m]<=0: x[m]+=L
    y[m]+=random.uniform(-l/2,l/2)
    if y[m]>L: y[m]-=L
    if y[m]<=0: y[m]+=L
    z[m]+=random.uniform(-l/2,l/2)
    if z[m]>L: z[m]-=L
    if z[m]<=0: z[m]+=L

    for j in range(N):
        if j!=m:
            if distant(L, x[m], y[m], z[m], x[j], y[j], z[j])<r:
                x[m]=w[0]
                y[m]=w[1]
                z[m]=w[2]
                print("шар", m)

    count+=1
    if count==freq:
        count=0
        with open ('file.txt', 'a', encoding='utf-8') as f:
            f.write(str(N))
            f.write("\nSTEP=")
            f.write(str(step))
        for j in range(N):
            with open ('file.txt', 'a', encoding='utf-8') as f:
                f.write("\nAr ")
                f.write(str(x[j]))
                f.write(" ")
                f.write(str(y[j]))
                f.write(" ")
                f.write(str(z[j]))
        with open ('file.txt', 'a', encoding='utf-8') as f:
            f.write("\n")
        step+=1

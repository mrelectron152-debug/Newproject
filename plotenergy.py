import numpy as np
import matplotlib.pyplot as plt
filename="energy.txt"
data=np.loadtxt(filename)

y=data
x=np.arange(len(y))

plt.figure(figsize=(8,6))
plt.plot(x,y)

plt.savefig("energy.png")

plt.show()
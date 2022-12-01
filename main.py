import numpy as np
import matplotlib.pyplot as plt

def euclid_dist(a, b):
    return np.sqrt(np.square(a)+np.square(b))

ax = plt.figure().add_subplot(projection='3d')

# Prepare arrays x, y, z
t = np.linspace(1, -5, 10000, dtype=np.complex128)
a = t**t

a = np.stack((a.real,a.imag),-1)
ax.scatter(t, a[:, 0], zs=a[:, 1], label="Imaginary part")
ax.scatter(t, euclid_dist(a[:, 0], a[:, 1]), label = "Real Part")
ax.legend()

plt.show()
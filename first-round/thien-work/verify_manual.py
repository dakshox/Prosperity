import numpy as np
import matplotlib.pyplot as plt

# N = 10000
# reserve_prices = np.max(np.random.rand(N, 2) * 100 + 900, axis=1)

# def evaluate(p1, p2):
#     return max(0, (1000-p1) * np.sum(reserve_prices < p1) + (1000-p2) * (np.sum((p1 < reserve_prices) & (reserve_prices < p2))))

def evaluate(p1, p2):
    return (1000-p1) * (p1-900) ** 2 / 10000 + (1000 - p2) * max(0, (p2-900) ** 2 - (p1-900) ** 2) / 10000

print(evaluate(952, 978))

ev = np.array([[evaluate(p1, p2) for p1 in range(900, 1001)] for p2 in range(900, 1001)])
plt.imshow(ev, origin="lower")
plt.colorbar()
plt.contour(ev, levels=np.arange(0, 21), colors='black')
plt.scatter([52], [78], color='red', marker='x')
plt.xlabel('p1')
plt.ylabel('p2')
plt.show()
import numpy as np
import data_unpack
import matplotlib.pyplot as plt

data = data_unpack.get_data(r'c:\temp\0_data.npy')
label = data_unpack.get_data(r'c:\temp\0_label.npy')

plt.subplot(3, 1, 1)
plt.plot(label[:, 0], 'o')
plt.subplot(3, 1, 2)
plt.plot(label[:, 1], 'o')
plt.subplot(3, 1, 3)
plt.plot(label[:, 2], 'o')
plt.show()
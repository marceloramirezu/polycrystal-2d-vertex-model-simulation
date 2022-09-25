from tempfile import TemporaryFile
import numpy as np

x= np.arange(10)
with open('test.npy', 'wb') as f:
    np.save(f, x)
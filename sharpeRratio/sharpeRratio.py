
import numba
import numpy as np
import pandas as pd

from scipy.interpolate import interpolate
from scipy import stats

import helpers

numba.jit()
def estimateSNR(x,permutations=1000):
    """A moment-free Sharpe (signal-to-noise) ratio estimator.

    This function accepts a vector of price returns (or any possibly heavy-tailed
    data) and returns a list containing the moment-free estimator, the vanilla 
    estimator.
     
    Parameters
    ----------
    x : numpy array of shape = [n_samples]
        A (non-empty) numeric vector of values.

    permutations: 
        The basic assumption of the estimator is that the sample data
        are independent and indentically distributed. To improve the efficiency 
        (precision) of the test, it is a good idea to average it over several random
        index permutations.

    Example
    -------
    >>> x = numpy.random.rand(100)
    >>> snr,r0bar,n = estimateSNR(x,numPerm=1000)


    Returns
    -------
    snr:  The signal-to-noise ratio. To have something comparable with
          a t-statistics, multiply by sqrt(length(x)).

    r0bar:  The average number of upper records minus lower records over
            the permutations of the cumulated sum of x.

    n:  The length of the vector x. It may be smaller than the input
        length if x contains NaNs.
    
    """   
    N = x.shape[0]
    
    # Compute nu
    nu, _, _ = stats.t.fit(x)

    # Compute r0bar over permutations
    r0bar = np.mean([helpers.compute_r0(x[np.random.permutation(x.shape[0])]) 
                     for perm in range(permutations)])

    # Get spline data
    a_data = pd.read_csv('spline_data.csv',index_col=0)

    # Estimate Spline
    f_a = interpolate.interp1d(a_data['x'], a_data['a'], kind='cubic')

    # Compute signal to noise ratio
    snr = np.sign(r0bar/N)*f_a(np.abs(r0bar/N))*(1.0-8.0/3.0 * nu**(-1.5))

    # Return snr
    return snr
"""Functions for testing convergence rates using grid convergence

  .. module:: grid_conv.py
     :synopsis: Functions for testing convergence rates using grid convergence
  .. moduleauthor:: Jonathan Gross <jarthurgross@gmail.com>

"""

import numpy as np

def l1_norm(vec):
    return np.sum(np.abs(vec))

def double_increments(times, U1s, U2s=None):
    r"""Construct longer time and Wiener increments from shorter increments.

    Take a list of times (assumed to be evenly spaced) and standard-normal
    random variables used to define the Ito integrals on the intervals and
    return the equivalent lists for doubled time intervals. The new
    standard-normal random variables are defined in terms of the old ones by

    .. math::

       \begin{align}
       \tilde{U}_{1,n}&=\frac{U_{1,n}+U_{1,n+1}}{\sqrt{2}} \\
       \tilde{U}_{2,n}&=\frac{\sqrt{3}}{2}\frac{U_{1,n}-U_{1,n+1}}{\sqrt{2}}
                        +\frac{1}{2}\frac{U_{2,n}+U_{2,n+1}}{\sqrt{2}}
       \end{align}

    Parameters
    ----------
    times : numpy.array
        List of evenly spaced times defining an even number of time intervals.
    U1s : numpy.array(N, len(times) - 1)
        Samples from a standard-normal distribution used to construct Wiener
        increments :math:`\Delta W` for each time interval. Multiple rows may
        be included for independent trajectories.
    U2s : numpy.array(N, len(times) - 1)
        Samples from a standard-normal distribution used to construct
        multiple-Ito increments :math:`\Delta Z` for each time interval.
        Multiple rows may be included for independent trajectories.

    Returns
    -------
    times: numpy.array(len(times)//2 + 1)
        Times sampled at half the frequency.
    U1s : numpy.array(len(times)//2)
        Standard-normal-random-variable samples for the longer intervals.
    U2s : numpy.array(len(times)//2), optional
        Standard-normal-random-variable samples for the longer intervals (not
        returned if `U2s` is ``None``.

    """

    new_times = times[::2]
    even_U1s = U1s[::2]
    odd_U1s = U1s[1::2]
    new_U1s = (even_U1s + odd_U1s)/np.sqrt(2)

    if U2s is None:
        return new_times, new_U1s
    else:
        even_U2s = U2s[::2]
        odd_U2s = U2s[1::2]
        new_U2s = (np.sqrt(3)*(even_U1s - odd_U1s) +
                   even_U2s + odd_U2s)/(2*np.sqrt(2))
        return new_times, new_U1s, new_U2s

def calc_rate(integrator, rho_0, times, U1s=None, U2s=None):
    r"""Calculate the convergence rate for some integrator.

    Parameters
    ----------
    integrator :
        An Integrator object.
    rho_0 : numpy.array
        The initial state of the system
    times :
        Sequence of times (assumed to be evenly spaced, defining
                        a number of increments divisible by 4).
    U1s : numpy.array(len(times) - 1), optional
        Samples from a standard-normal distribution used to construct Wiener
        increments :math:`\Delta W` for each time interval. If not provided
        will be generated by the function.
    U2s : numpy.array(len(times) - 1), optional
        Samples from a standard-normal distribution used to construct
        multiple-Ito increments :math:`\Delta Z` for each time interval. If not
        provided will be generated by the function.

    Returns
    -------
    float
        The convergence rate as a power of :math:`\Delta t`.

    """
    increments = len(times) - 1
    if U1s is None:
        U1s = np.random.randn(increments)
    if U2s is None:
        U2s = np.random.randn(increments)

    # Calculate times and random variables for the double and quadruple
    # intervals
    times_2, U1s_2, U2s_2 = double_increments(times, U1s, U2s)
    times_4, U1s_4, U2s_4 = double_increments(times_2, U1s_2, U2s_2)

    rhos = integrator.integrate(rho_0, times, U1s, U2s).vec_soln
    rhos_2 = integrator.integrate(rho_0, times_2, U1s_2, U2s_2).vec_soln
    rhos_4 = integrator.integrate(rho_0, times_4, U1s_4, U2s_4).vec_soln
    rate = (np.log(l1_norm(rhos_4[-1] - rhos_2[-1])) -
            np.log(l1_norm(rhos_2[-1] - rhos[-1])))/np.log(2)

    return rate

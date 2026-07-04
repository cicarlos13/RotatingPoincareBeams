import numpy as np
import matplotlib.pyplot as plt
import copy
import math
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def get_zernike_phase_screen(N, D_r0, J_max, carrier_tilt=15.0):
    """
    Generates an atmospheric turbulence phase screen using the Noll method.
    """
    if J_max < 2:
        raise ValueError("J_max must be at least 2.")

    # 1. Setup Grid
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, N)
    xx, yy = np.meshgrid(x, y)
    r = np.sqrt(xx**2 + yy**2)
    theta = np.arctan2(yy, xx)
    mask = r <= 1.0  # Circular aperture mask

    # 2. Build Noll Lookup (j -> n, m)
    noll_lookup = {}
    j = 1
    for n in range(0, 200):
        for m_abs in range(n, -1, -1):
            if (n - m_abs) % 2 == 0:
                if m_abs == 0:
                    noll_lookup[j] = (n, 0)
                    j += 1
                else:
                    noll_lookup[j] = (n, m_abs)
                    j += 1
                    noll_lookup[j] = (n, -m_abs)
                    j += 1
            if j > J_max + 1: break
        if j > J_max + 1: break

    # --- Zernike Polynomial Generator ---
    def radial_poly(n, m, rho):
        R = np.zeros_like(rho)
        for s in range(0, int((n - np.abs(m)) / 2) + 1):
            c = ((-1)**s * math.factorial(n - s) /
                 (math.factorial(s) * math.factorial(int((n + np.abs(m)) / 2) - s) *
                  math.factorial(int((n - np.abs(m)) / 2) - s)))
            R += c * rho**(n - 2 * s)
        return R

    def get_zernike(n, m, rho, phi):
        if m >= 0:
            return np.sqrt(n + 1) * radial_poly(n, m, rho) * np.cos(m * phi)
        else:
            return np.sqrt(n + 1) * radial_poly(n, -m, rho) * np.sin(-m * phi)
    # ----------------------------------

    # 3. Base Phase + Artificial Carrier Tilt
    phase = carrier_tilt * yy 

    # 4. Generate Random Turbulence
    scaling_factor = 0.103 * (D_r0**(5/3))
    for j_val in range(2, J_max + 1):
        n, m = noll_lookup[j_val]
        # Approximate variance scaling
        sigma = np.sqrt(scaling_factor / (n + 1))
        coeff = np.random.normal(0, sigma)
        Z_j = get_zernike(n, m, r, theta)
        phase += coeff * Z_j

    # 5. Apply Mask (Use NaN for outside the pupil to allow gray background)
    phase[~mask] = np.nan
    
    return phase

def visualize_four_screens(N=1024):
    # Fixed the label typo from your screenshot (High D/r0 = 4.0, High J = 50)
    params = [
        {'D_r0': 1.0, 'J_max': 50, 'title': 'Low D/r0, Low J'},
        {'D_r0': 2.0, 'J_max': 20, 'title': 'High D/r0, Low J'},
        {'D_r0': 3.0, 'J_max': 50, 'title': 'Low D/r0, High J'},
        {'D_r0': 4.0, 'J_max': 100, 'title': 'High D/r0, High J'}
    ]

    fig, axs = plt.subplots(2, 2, figsize=(10, 10))
    axs = axs.ravel()
    clim = (0, 2 * np.pi)

    # Create a custom colormap that paints NaN values gray
    cmap = copy.copy(plt.cm.gray)
    cmap.set_bad(color='#999999') # Neutral mid-gray

    for i, p in enumerate(params):
        ax = axs[i]
        
        # Generate phase with a fixed carrier tilt to create horizontal fringes
        phase = get_zernike_phase_screen(N, p['D_r0'], p['J_max'], carrier_tilt=15.0)

        # Modulo 2pi handles NaNs smoothly in numpy
        wrapped_phase = phase % (2 * np.pi)

        im = ax.imshow(wrapped_phase, cmap=cmap, clim=clim, origin='lower', extent=[-1, 1, -1, 1])
        #ax.set_title(f"{p['title']}\n(D/r0={p['D_r0']}, J={p['J_max']})")
        ax.set_title(f"(D/r0={p['D_r0']}, J={p['J_max']})")
        ax.axis('off')

    axins = inset_axes(ax, width="10%", height="100%", loc='lower left',
                       bbox_to_anchor=(1.01, 0., 1, 1),
                       bbox_transform=ax.transAxes,
                       borderpad=0)
    #plt.colorbar(im, ax=ax, cax=axins)
    cbar = fig.colorbar(im, cax=axins, ticks=[0, 2 * np.pi])
    cbar.set_ticklabels(['0', r'2$\pi$'])
    #cbar.set_label('Phase')
    cbar.ax.tick_params(labelsize=30, direction='in')

    plt.suptitle(r"Noll Phase Screens")
    plt.show()

if __name__ == "__main__":
    visualize_four_screens()
    
    
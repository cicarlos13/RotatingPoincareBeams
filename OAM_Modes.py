import plotly.graph_objects as go
from scipy.special import genlaguerre
import numpy as np

# --- Custom MATLAB "Parula" Colorscale ---
parula_scale = [
    [0.0, '#352a87'], [0.125, '#0363e1'], [0.25, '#1485d4'], 
    [0.375, '#06a7c6'], [0.5, '#38b99e'], [0.625, '#92bf73'], 
    [0.75, '#d9ba56'], [0.875, '#fcce2e'], [1.0, '#f9fb0e']
]

# --- Parameters ---
w0 = 0.5   # Beam waist
p = 0      # Radial index (p=0 gives the standard single donut ring)
l = 3      # Topological charge
num_twists = 2    
pitch = 1.0         

# --- Grid Generation ---
r = np.linspace(0.15, 1.0, 30)  
beam_length = num_twists * pitch
z_prop = np.linspace(0, beam_length, 150)
R, Z_prop = np.meshgrid(r, z_prop)

# --- Helper functions for Intensity and Phase
def get_lg_intensity(R, l, p, w0):
    """Calculates the transverse intensity profile of a Laguerre-Gaussian beam."""
    rho = 2 * (R**2) / (w0**2)
    L_pl = genlaguerre(p, np.abs(l))
    intensity = (rho**np.abs(l)) * (L_pl(rho)**2) * np.exp(-rho)
    
    # Normalize 0 to 1
    if np.max(intensity) > 0:
        intensity = intensity / np.max(intensity)
    return intensity

def get_lg_phase(R, Theta, l, p, w0):
    """
    Calculates the transverse phase profile of a Laguerre-Gaussian beam at z=0.
    """
    # Radial term scaled by the beam waist
    rho = 2 * (R**2) / (w0**2)
    
    # Generate the associated Laguerre polynomial
    L_pl = genlaguerre(p, np.abs(l))
    
    # Calculate the real amplitude distribution
    # Note: Using sqrt(rho) here because amplitude scales with r, not r^2
    amplitude = (np.sqrt(rho)**np.abs(l)) * L_pl(rho) * np.exp(-rho / 2)
    
    # Calculate the complex electric field by multiplying by the azimuthal phase term
    E_field = amplitude * np.exp(-1j * l * Theta)
    
    # Return the phase angle in the range [-pi, pi]
    return np.angle(E_field)

Intensity = get_lg_intensity(R, l, p, w0)

fig = go.Figure()

# -----------------------------------------------
# ------------- PLOTTING THE HELICES ------------
# -----------------------------------------------

for i in range(abs(l)):
    Theta = Z_prop * (2 * np.pi / pitch) + i * (2 * np.pi / l)
    
    fig.add_trace(go.Surface(
        x=Z_prop, 
        y=R * np.cos(Theta), 
        z=R * np.sin(Theta), 
        surfacecolor=Intensity,             # Map the color to the radius
        colorscale=parula_scale,    # Use our custom parula
        reversescale=False,          # Change to False to invert the color mapping!
        showscale=False
    ))

# --- Central Arrow (Beam Axis) ---
# 1. The Line
fig.add_trace(go.Scatter3d(
    #x=[-0.5, beam_length + 1.0], y=[0, 0], z=[0, 0],
    x=[-0.5, beam_length + 0.25], y=[0, 0], z=[0, 0],
    mode='lines', 
    line=dict(color='red', width=8),
    showlegend=False
))

# 2. The Arrowhead (3D Cone)
fig.add_trace(go.Cone(
    #x=[beam_length + 1.0], y=[0], z=[0], # Position at the end of the line
    x=[beam_length + 0.25], y=[0], z=[0], # Position at the end of the line
    u=[1], v=[0], w=[0],                 # Pointing in the +X direction
    sizemode="absolute", 
    sizeref=0.25,                         # Size of the arrowhead
    anchor="tail", 
    showscale=False, 
    colorscale=[[0, 'red'], [1, 'red']] # Force the cone to be solid lime green
))

# --- Formatting ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectratio=dict(x=2.5, y=1, z=1), # Stretch along propagation axis
        camera=dict(
            #eye=dict(x=1.5, y=-1.5, z=0.5) # Default viewing angle
            eye=dict(x=2.5, y=-1.5, z=0.5) # Default viewing angle
        )
    ),
    margin=dict(l=0, r=0, b=0, t=0),       # Remove white borders
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()


# -----------------------------------------------
# ----- Plotting the Single Intensity Plane -----
# -----------------------------------------------
# --- Grid Generation ---
# For intensity, we definitely start at r=0.0 to show the central structure
r = np.linspace(0.0, 1.0, 100)  # High resolution for a smooth image
theta = np.linspace(0, 2 * np.pi, 150)
R, Theta = np.meshgrid(r, theta)

# Calculate the physical intensity map
Intensity = get_lg_intensity(R, l, p, w0)
Phase = get_lg_phase(R, Theta, l, p, w0)

fig = go.Figure()

# We place it at constant x=0.0
X_plot = np.full_like(R, 0.0)
Y_plot = R * np.cos(Theta)
Z_plot = R * np.sin(Theta)

fig.add_trace(go.Surface(
    x=X_plot, 
    y=Y_plot, 
    z=Z_plot, 
    #surfacecolor=Intensity,     # Map color to the calculated physical intensity!
    surfacecolor=Phase,
    colorscale=hsv_colorscale,    # Apply MATLAB Parula
    #colorscale=parula_scale,
    reversescale=False,         # Bright yellow (1.0) = High Intensity
    showscale=True,
    # Turn off contour lines for a clean, image-like look
    contours=dict(x=dict(show=False), y=dict(show=False), z=dict(show=False))
))

# --- Formatting for 2D View ---
fig.update_layout(
    scene=dict(
        # Hide all axes and grids
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        
        # Lock aspect ratio so the circular mode isn't stretched
        aspectratio=dict(x=0.1, y=1, z=1), # Squish the unused X dimension
        
        # CAMERA CONTROL: Look directly down the X-axis (propagation direction)
        camera=dict(
            # Position the 'eye' far along the X-axis looking back at origin
            eye=dict(x=2.0, y=0.0, z=0.0), 
            up=dict(x=0.0, y=0.0, z=1.0) # Tell Plotly which way is 'up' (Z)
        )
    ),
    # Optimize margin for an image
    margin=dict(l=0, r=0, b=0, t=0),       
    plot_bgcolor='white',
    paper_bgcolor='white',
    # Ensure the output window starts with square proportions for the circle
    width=700,
    height=700
)

fig.show()
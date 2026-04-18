import sys
import subprocess

# Function to ensure we have the necessary library installed
def ensure_vpython():
    try:
        import vpython
    except ImportError:
        print("VPython library not found. Installing now. Please wait...")
        # Installing vpython using pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "vpython"])
        print("VPython installed successfully!\n")

ensure_vpython()

from vpython import *

def draw_gear(center, axis_dir, radius, gear_color, thickness=0.5, teeth=20):
    """
    Constructs a 3D gear using VPython compound objects.
    """
    start_pos = center - axis_dir * (thickness / 2)
    gear_parts = []
    
    # Central cylinder body
    c = cylinder(pos=start_pos, axis=axis_dir * thickness, radius=radius*0.85, color=gear_color)
    gear_parts.append(c)
    
    # Calculate orthogonal vectors to place the teeth around the circumference
    ax = norm(axis_dir)
    if abs(ax.x) < 0.9:
        v1 = norm(cross(ax, vector(1,0,0)))
    else:
        v1 = norm(cross(ax, vector(0,1,0)))
    v2 = norm(cross(ax, v1))
    
    # Generate the teeth
    for i in range(teeth):
        angle = (2 * pi / teeth) * i
        tooth_dir = v1 * cos(angle) + v2 * sin(angle)
        
        # Position the tooth at the edge
        tooth_pos = start_pos + tooth_dir * (radius * 0.95) + ax * (thickness / 2)
        
        # Create identical teeth 
        t = box(pos=tooth_pos, length=radius*0.3, height=thickness, width=max(0.1, radius*0.15), color=gear_color)
        t.axis = tooth_dir
        t.up = ax
        gear_parts.append(t)
        
    # Group the shape into a single manipulable 3D compound object
    g = compound(gear_parts)
    return g

def main():
    print("=== 3D Orthogonal Gears Generator ===")
    
    # 1. Take 3 radii as input
    try:
        r1 = float(input("Enter radius for Gear 1 (e.g., 2.0): "))
        r2 = float(input("Enter radius for Gear 2 (e.g., 3.0): "))
        r3 = float(input("Enter radius for Gear 3 (e.g., 4.0): "))
    except ValueError:
        print("Invalid inputs detected. Defaulting to radii: 2.0, 3.0, 4.0")
        r1, r2, r3 = 2.0, 3.0, 4.0

    # 2. Track point functionality
    print("\nDo you want to track a point on Gear 1? (y/n)")
    track_ans = input().strip().lower()
    track_point = track_ans in ['y', 'yes']

    point_color = color.red
    if track_point:
        print("Enter a color for the tracked point (red, green, blue, yellow, magenta, cyan). Default is red:")
        col_ans = input().strip().lower()
        color_map = {
            'red': color.red,
            'green': color.green,
            'blue': color.blue,
            'yellow': color.yellow,
            'magenta': color.magenta,
            'cyan': color.cyan,
            'white': color.white
        }
        point_color = color_map.get(col_ans, color.red)
        if col_ans not in color_map:
            print("Color not recognized. Defaulting to red.")

    print("\nStarting 3D environment...")
    print("A browser window will pop up with your 3D view. Give it a few seconds.")
    print("\n*** CONTROLS TO GLIDE AROUND ***")
    print(" - GLIDE / ROTATE : Right-click and drag (or CTRL + drag)")
    print(" - ZOOM : Scroll wheel (or ALT + drag)")
    print(" - PAN : SHIFT + drag")

    # 3. Setup the 3D scene
    scene = canvas(title='Orthogonal 3D Gears', width=1000, height=700)
    scene.background = color.gray(0.1)
    
    # We will orient them so they intersect/arrange orthogonally edge-to-edge
    # Gear 1: XY plane, rotating on Z axis
    axis1 = vector(0, 0, 1)
    pos1 = vector(0, 0, 0)
    
    # Gear 2: YZ plane, rotating on X axis
    axis2 = vector(1, 0, 0)
    pos2 = vector(0, r1 + r2, 0)
    
    # Gear 3: ZX plane, rotating on Y axis
    axis3 = vector(0, 1, 0)
    pos3 = vector(r1 + r3, 0, 0)

    # 4. Generate the Orthogonal Gears
    gear1 = draw_gear(pos1, axis1, r1, color.cyan, teeth=max(6, int(r1*8)))
    gear2 = draw_gear(pos2, axis2, r2, color.magenta, teeth=max(6, int(r2*8)))
    gear3 = draw_gear(pos3, axis3, r3, color.yellow, teeth=max(6, int(r3*8)))

    # Setup the tracker option
    tracker = None
    if track_point:
        tracker_pos = pos1 + vector(r1, 0, 0)
        tracker = sphere(pos=tracker_pos, radius=min(r1, r2, r3)*0.15, color=point_color, make_trail=True, retain=300)

    # Angular velocities to sync their teeth ratio
    dt = 0.01
    w1 = 2.0
    w2 = w1 * (r1 / r2)
    w3 = w1 * (r1 / r3)

    # 5. Animation loop
    while True:
        rate(100) # Limits loop to 100 frames per second
        
        # Rotating all gears across perpendicular rotational axes
        gear1.rotate(angle=w1*dt, axis=axis1, origin=pos1)
        gear2.rotate(angle=-w2*dt, axis=axis2, origin=pos2)
        gear3.rotate(angle=-w3*dt, axis=axis3, origin=pos3)
        
        # Keeping tracker pinned to the rotating gear without rotating its trail
        if tracker:
            tracker.pos = tracker.pos.rotate(angle=w1*dt, axis=axis1, origin=pos1)

if __name__ == '__main__':
    main()

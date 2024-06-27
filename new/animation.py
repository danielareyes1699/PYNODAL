#%%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

#%%
# Datos proporcionados
q_test = 282
pwf_test = 1765
pr = 2085
pb = 2100
pwf = [0, 300, 700, 1000, 1300, 1618, 1765, 1800, 2085]

# Cálculo de IPR
q_ipr = np.linspace(0, q_test, 282)
Pwf_ipr = pr - q_ipr * (pr - pb) / q_test

# Cálculo de VLP
DeltaP = np.array(pwf) - pwf_test
q_vlp = q_test * DeltaP / (pr - pb)
Pwf_vlp = np.array(pwf)

# Punto de intersección IPR-VLP
q_intersect = (pr - pb) * pwf_test / (pr - pb + pwf_test)
Pwf_intersect = pr - q_intersect * (pr - pb) / q_test

print("q_vlp:", q_vlp)
print("Pwf_vlp:", Pwf_vlp)

# Crear la figura y ejes
fig, ax = plt.subplots()
ax.set_xlim(0, q_test)
ax.set_ylim(pb, pr)
line_ipr, = ax.plot([], [], lw=2, label='IPR', color='blue')
line_vlp, = ax.plot([], [], lw=2, label='VLP', color='red')
ax.legend()
ax.set_xlabel('Tasa de producción (q)')
ax.set_ylabel('Presión de fondo fluyente (Pwf)')

# Línea vertical para mostrar el punto de intersección
line_intersect = ax.axvline(x=q_intersect, ymin=0, ymax=1, color='gray', linestyle='--')

# Función de inicialización para la animación
def init():
    line_ipr.set_data([], [])
    line_vlp.set_data([], [])
    line_intersect.set_xdata([q_intersect])
    return line_ipr, line_vlp, line_intersect

# Función de actualización para la animación
def update(frame):
    line_ipr.set_data(q_ipr[:frame], Pwf_ipr[:frame])
    line_vlp.set_data(q_vlp[:frame], Pwf_vlp[:frame])
    return line_ipr, line_vlp, line_intersect

# Crear la animación
ani = animation.FuncAnimation(fig, update, frames=len(q_ipr), init_func=init, blit=True, interval=20)

# Obtener la ruta al directorio PycharmProjects
try:
    project_dir = r'C:\Users\danie\PycharmProjects'
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)  # Crear directorio si no existe

    # Guardar la animación como un archivo GIF en el directorio PycharmProjects
    output_path = os.path.join(project_dir, 'analisis_nodal.gif')
    ani.save(output_path, writer='pillow')

    print(f"Animación guardada correctamente en: {output_path}")

except Exception as e:
    print(f"Error al guardar la animación: {e}")

plt.show()

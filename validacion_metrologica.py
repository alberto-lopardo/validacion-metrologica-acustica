"""
================================================================================
  VALIDACIÓN METROLÓGICA AUTOMÁTICA DE CAMPAÑA DE MONITOREO ACÚSTICO
  Detección de deriva · Trazabilidad de calibración · Reporte ISO 17025

  ⚠️  AVISO: Proyecto de portafolio con datos 100% SINTÉTICOS (simulando
  exportaciones de sonómetros). No guarda relación con proyectos reales,
  clientes, metodologías propietarias ni datos confidenciales de empleadores
  actuales o anteriores. Normativas citadas (ISO 17025, IEC 61672) son de
  conocimiento público y su aplicación es meramente ilustrativa.

  Autor  : Alberto Lopardo
  LinkedIn: linkedin.com/in/alberto-lopardo-acustica
  Ref.   : ISO 17025:2017 / IEC 61672-1:2013 / ISO 1996-2:2017
================================================================================
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ── Paleta ────────────────────────────────────────────────────────────────────
C_NAVY   = '#1B3A5C'
C_BLUE   = '#2E7DBF'
C_GREEN  = '#2E8B57'
C_RED    = '#C0392B'
C_ORANGE = '#E07B39'
C_AMBER  = '#F0A500'
C_MID    = '#4A4A4A'
C_GRID   = '#DDE3EA'
C_LIGHT  = '#F4F7FA'

plt.rcParams.update({
    'font.family':       'DejaVu Sans',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.grid':         True,
    'grid.color':        C_GRID,
    'grid.linewidth':    0.55,
    'axes.labelcolor':   C_NAVY,
    'xtick.color':       C_MID,
    'ytick.color':       C_MID,
    'figure.facecolor':  'white',
})

NOTE_TEXT = ('⚠  Datos sintéticos generados para demostración técnica — '
             'no representan mediciones reales ni datos de ningún cliente o empleador.')

# ==============================================================================
# 1. PARÁMETROS METROLÓGICOS (IEC 61672-1 Clase 1)
# ==============================================================================
CAL_REF          = 94.0   # dB — valor de referencia del calibrador (pistófono)
UMBRAL_DERIVA    = 0.5    # dB — deriva máxima permitida pre/post campaña
UMBRAL_ERROR_ABS = 0.5    # dB — error absoluto máximo respecto al valor de referencia
INCERTIDUMBRE_K2 = 0.2   # dB — incertidumbre expandida (k=2) del calibrador

EQUIPO     = 'Sonómetro Clase 1  SN: 2024-001'
CALIBRADOR = 'Pistófono de referencia  SN: CAL-2024-007'
OPERADOR   = 'A. Lopardo'

# ==============================================================================
# 2. GENERACIÓN DE DATOS SINTÉTICOS
#    Campaña de 3 días, 5 puntos/día, intervalos de 2 h
# ==============================================================================
rng = np.random.default_rng(2024)

FECHA_INICIO   = datetime(2024, 11, 4, 8, 0, 0)
N_MEDICIONES   = 15
PUNTOS         = [f'P{p+1:02d}' for p in range(5)]   # 5 puntos de medición

registros = []
for i in range(N_MEDICIONES):
    ts      = FECHA_INICIO + timedelta(hours=i * 2)
    punto   = PUNTOS[i % 5]

    # Calibración pre-medición: pequeña variación aleatoria en ±0.2 dB
    cal_pre = CAL_REF + rng.normal(0, 0.10)

    # Calibración post-medición: la mayoría estable; tres casos con deriva excesiva
    if i in [3, 9, 13]:
        deriva_inducida = rng.choice([-0.72, +0.81, -0.93])
        cal_post = cal_pre + deriva_inducida
    else:
        cal_post = cal_pre + rng.normal(0, 0.12)

    # Niveles medidos — perfil realista según hora del día
    hora    = ts.hour
    base_leq = 54 + 6 * np.exp(-((hora - 8) / 3)**2) + 5 * np.exp(-((hora - 17) / 2.5)**2)
    leq     = round(base_leq + rng.normal(0, 2.5), 1)
    l10     = round(leq + rng.normal(3.5, 0.8), 1)
    l90     = round(leq - rng.normal(8.0, 1.2), 1)
    lmax    = round(l10 + rng.normal(8.0, 1.5), 1)

    registros.append({
        'ID'           : f'M{i+1:03d}',
        'FechaHora'    : ts,
        'Punto'        : punto,
        'Cal_Pre_dB'   : round(cal_pre,  3),
        'Cal_Post_dB'  : round(cal_post, 3),
        'Leq_dBA'      : leq,
        'L10_dBA'      : l10,
        'L90_dBA'      : l90,
        'Lmax_dBA'     : lmax,
        'Duracion_min' : 15,
        'Equipo'       : EQUIPO,
        'Calibrador'   : CALIBRADOR,
        'Operador'     : OPERADOR,
    })

df = pd.DataFrame(registros)
print(f"✅  {N_MEDICIONES} registros sintéticos generados  |  "
      f"{FECHA_INICIO.strftime('%d/%m/%Y')} — "
      f"{(FECHA_INICIO + timedelta(hours=(N_MEDICIONES-1)*2)).strftime('%d/%m/%Y')}")

# ==============================================================================
# 3. VALIDACIÓN METROLÓGICA (ISO 17025 / IEC 61672-1)
# ==============================================================================

def validar(row):
    """
    Evalúa tres criterios de aceptación metrológica por medición:
      A — Deriva pre/post ≤ UMBRAL_DERIVA
      B — Error absoluto de calibración pre ≤ UMBRAL_ERROR_ABS
      C — Error absoluto de calibración post ≤ UMBRAL_ERROR_ABS
    """
    deriva         = row['Cal_Post_dB'] - row['Cal_Pre_dB']
    error_pre      = abs(row['Cal_Pre_dB']  - CAL_REF)
    error_post     = abs(row['Cal_Post_dB'] - CAL_REF)

    fallas = []
    if abs(deriva)  > UMBRAL_DERIVA:    fallas.append(f'Deriva {deriva:+.3f} dB > ±{UMBRAL_DERIVA} dB')
    if error_pre    > UMBRAL_ERROR_ABS: fallas.append(f'Error pre {error_pre:.3f} dB > {UMBRAL_ERROR_ABS} dB')
    if error_post   > UMBRAL_ERROR_ABS: fallas.append(f'Error post {error_post:.3f} dB > {UMBRAL_ERROR_ABS} dB')

    estado = 'VÁLIDA' if not fallas else 'INVÁLIDA'
    accion = 'Aceptar' if not fallas else 'Descartar y repetir'

    return {
        'Deriva_dB'      : round(deriva,    4),
        'Error_Pre_dB'   : round(error_pre,  4),
        'Error_Post_dB'  : round(error_post, 4),
        'N_Criterios_OK' : 3 - len(fallas),
        'Fallas'         : '; '.join(fallas) if fallas else '—',
        'Estado'         : estado,
        'Accion'         : accion,
    }

val = df.apply(validar, axis=1, result_type='expand')
df  = pd.concat([df, val], axis=1)

validas   = (df['Estado'] == 'VÁLIDA').sum()
invalidas = (df['Estado'] == 'INVÁLIDA').sum()
tasa_val  = validas / N_MEDICIONES * 100

print(f"✅  Validación completada — {validas}/{N_MEDICIONES} mediciones válidas "
      f"({tasa_val:.1f}%)")

# ==============================================================================
# 4. FIGURA 1 — DASHBOARD METROLÓGICO (6 paneles)
# ==============================================================================

fig = plt.figure(figsize=(16, 12))
gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.50, wspace=0.38)

c_bar = [C_RED if e == 'INVÁLIDA' else C_GREEN for e in df['Estado']]
ids   = df['ID'].values

# ── Panel 1: Deriva por medición ─────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
bars = ax1.bar(ids, df['Deriva_dB'], color=c_bar, alpha=0.85, zorder=3)
ax1.axhline(+UMBRAL_DERIVA,  color=C_AMBER, lw=1.8, ls='--',
            label=f'Límite ±{UMBRAL_DERIVA} dB (IEC 61672)')
ax1.axhline(-UMBRAL_DERIVA,  color=C_AMBER, lw=1.8, ls='--')
ax1.axhline(0, color='black', lw=0.7)
# Etiquetas en barras inválidas
for bar, row in zip(bars, df.itertuples()):
    if row.Estado == 'INVÁLIDA':
        ax1.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + (0.02 if bar.get_height() >= 0 else -0.06),
                 f'{row.Deriva_dB:+.2f}', ha='center', va='bottom',
                 fontsize=7.5, color=C_RED, fontweight='bold')
ax1.set_xticks(range(N_MEDICIONES))
ax1.set_xticklabels(ids, rotation=45, ha='right', fontsize=8)
ax1.set_xlabel('ID Medición', fontsize=10, fontweight='bold')
ax1.set_ylabel('Deriva (dB)', fontsize=10, fontweight='bold')
ax1.set_title('1 — Deriva de Calibración Pre/Post Medición', fontsize=10,
              fontweight='bold', color=C_NAVY)
ax1.legend(fontsize=8.5, framealpha=.92)

# ── Panel 2: Calibraciones pre vs post ───────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
x2  = np.arange(N_MEDICIONES)
w   = 0.38
ax2.bar(x2 - w/2, df['Cal_Pre_dB'],  w, color=C_BLUE,  alpha=.82, label='Cal. pre-medición',  zorder=3)
ax2.bar(x2 + w/2, df['Cal_Post_dB'], w, color=C_ORANGE, alpha=.78, label='Cal. post-medición', zorder=3)
ax2.axhline(CAL_REF,                     color=C_GREEN, lw=1.8, ls='--',
            label=f'Referencia {CAL_REF} dB')
ax2.axhspan(CAL_REF - UMBRAL_ERROR_ABS,
            CAL_REF + UMBRAL_ERROR_ABS,
            alpha=.08, color=C_GREEN, label=f'Tolerancia ±{UMBRAL_ERROR_ABS} dB')
ax2.set_xticks(x2)
ax2.set_xticklabels(ids, rotation=45, ha='right', fontsize=8)
ax2.set_ylim(CAL_REF - 1.4, CAL_REF + 1.4)
ax2.set_xlabel('ID Medición', fontsize=10, fontweight='bold')
ax2.set_ylabel('Nivel calibración (dB)', fontsize=10, fontweight='bold')
ax2.set_title('2 — Niveles de Calibración Pre y Post Medición', fontsize=10,
              fontweight='bold', color=C_NAVY)
ax2.legend(fontsize=8, framealpha=.92, ncol=2)

# ── Panel 3: Timeline Leq con estado de validez ───────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
for _, row in df.iterrows():
    c  = C_GREEN if row['Estado'] == 'VÁLIDA' else C_RED
    mk = 'o'     if row['Estado'] == 'VÁLIDA' else 'D'
    sz = 70      if row['Estado'] == 'VÁLIDA' else 90
    ax3.scatter(row['FechaHora'], row['Leq_dBA'], c=c, marker=mk, s=sz,
                edgecolors='white', lw=0.6, zorder=4)
ax3.plot(df['FechaHora'], df['Leq_dBA'], color=C_NAVY, lw=1.0, alpha=.35, zorder=3)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m\n%H:%M'))
ax3.xaxis.set_major_locator(mdates.HourLocator(interval=8))
ax3.set_xlabel('Fecha / Hora', fontsize=10, fontweight='bold')
ax3.set_ylabel('Leq (dBA)', fontsize=10, fontweight='bold')
ax3.set_title('3 — Timeline de Mediciones con Estado de Validez', fontsize=10,
              fontweight='bold', color=C_NAVY)
leyenda = [Line2D([0],[0], marker='o', color='w', markerfacecolor=C_GREEN, ms=9, label='Válida'),
           Line2D([0],[0], marker='D', color='w', markerfacecolor=C_RED,   ms=9, label='Inválida')]
ax3.legend(handles=leyenda, fontsize=9, framealpha=.92)

# ── Panel 4: Distribución de deriva (histograma + curva normal) ───────────────
ax4 = fig.add_subplot(gs[1, 1])
derivas = df['Deriva_dB'].values
mu, sigma = derivas.mean(), derivas.std()
bins = np.linspace(derivas.min()-0.1, derivas.max()+0.1, 14)
ax4.hist(derivas, bins=bins, color=C_BLUE, alpha=0.75, edgecolor='white', lw=0.5,
         label='Distribución deriva', zorder=3)
# Curva normal teórica
x_norm = np.linspace(bins[0], bins[-1], 200)
y_norm = (N_MEDICIONES * (bins[1]-bins[0]) *
          np.exp(-0.5*((x_norm-mu)/sigma)**2) / (sigma*np.sqrt(2*np.pi)))
ax4.plot(x_norm, y_norm, color=C_NAVY, lw=2.0, label='Normal teórica')
ax4.axvline(+UMBRAL_DERIVA,  color=C_AMBER, lw=1.6, ls='--', label=f'±{UMBRAL_DERIVA} dB')
ax4.axvline(-UMBRAL_DERIVA,  color=C_AMBER, lw=1.6, ls='--')
ax4.axvline(mu, color=C_GREEN, lw=1.4, ls=':', label=f'Media {mu:+.3f} dB')
ax4.set_xlabel('Deriva (dB)', fontsize=10, fontweight='bold')
ax4.set_ylabel('Frecuencia', fontsize=10, fontweight='bold')
ax4.set_title('4 — Distribución de la Deriva de Calibración', fontsize=10,
              fontweight='bold', color=C_NAVY)
ax4.legend(fontsize=8.5, framealpha=.92)
ax4.text(0.97, 0.95, f'μ = {mu:+.3f} dB\nσ = {sigma:.3f} dB',
         transform=ax4.transAxes, ha='right', va='top', fontsize=9,
         color=C_NAVY, bbox=dict(boxstyle='round,pad=0.3', fc=C_LIGHT, ec=C_GRID))

# ── Panel 5: Tasa de validez y resumen por criterio ──────────────────────────
ax5 = fig.add_subplot(gs[2, 0])
ax5.axis('off')

# Tabla resumen
tabla_data = [
    ['Parámetro', 'Valor', 'Criterio', 'Estado'],
    ['Mediciones totales',     str(N_MEDICIONES),         '—',                    '—'],
    ['Mediciones válidas',     str(validas),               f'N/A',                 '✅'],
    ['Mediciones inválidas',   str(invalidas),             f'—',                   '❌' if invalidas > 0 else '✅'],
    ['Tasa de validez',        f'{tasa_val:.1f} %',        '≥ 80 % recomendado',   '✅' if tasa_val >= 80 else '⚠️'],
    ['Deriva promedio',        f'{mu:+.3f} dB',            f'|Δ| ≤ {UMBRAL_DERIVA} dB',  '✅' if abs(mu) <= UMBRAL_DERIVA else '❌'],
    ['Deriva máx. absoluta',   f'{df["Deriva_dB"].abs().max():.3f} dB', f'≤ {UMBRAL_DERIVA} dB', '—'],
    ['Incertidumbre calibrador', f'± {INCERTIDUMBRE_K2} dB', 'k = 2 (95 %)',      '—'],
    ['Norma de referencia',    'ISO 17025 / IEC 61672-1',  '—',                    '—'],
]

tbl = ax5.table(cellText=tabla_data[1:], colLabels=tabla_data[0],
                cellLoc='center', loc='center', bbox=[0, 0, 1, 1],
                colWidths=[0.32, 0.22, 0.30, 0.16])
tbl.auto_set_font_size(False)
tbl.set_fontsize(8.5)
for (r, c), cell in tbl.get_celld().items():
    cell.set_edgecolor('#BCC8D4')
    if r == 0:
        cell.set_facecolor(C_NAVY)
        cell.set_text_props(color='white', fontweight='bold', fontsize=9)
    elif r % 2 == 0:
        cell.set_facecolor('#EEF3F8')
    else:
        cell.set_facecolor('white')
ax5.set_title('5 — Tabla Resumen de Validación (ISO 17025)', fontsize=10,
              fontweight='bold', color=C_NAVY, pad=8)

# ── Panel 6: Detalle de mediciones inválidas (Leq / L10 / L90 / Lmax) ────────
ax6 = fig.add_subplot(gs[2, 1])
df_inv = df[df['Estado'] == 'INVÁLIDA'].copy()
df_val = df[df['Estado'] == 'VÁLIDA'].copy()

x6_v = np.arange(len(df_val))
x6_i = np.arange(len(df_inv))

ax6.errorbar(x6_v, df_val['Leq_dBA'],
             yerr=[df_val['Leq_dBA'] - df_val['L90_dBA'],
                   df_val['L10_dBA'] - df_val['Leq_dBA']],
             fmt='o', color=C_GREEN, ms=7, lw=1.4, capsize=4,
             label='Mediciones válidas (Leq ± [L90–L10])', zorder=4)
ax6.scatter(x6_v, df_val['Lmax_dBA'], marker='^', color=C_GREEN, s=30,
            alpha=.6, zorder=3, label='Lmax (válidas)')

if len(df_inv):
    xi = np.arange(len(df_val), len(df_val) + len(df_inv))
    ax6.errorbar(xi, df_inv['Leq_dBA'],
                 yerr=[df_inv['Leq_dBA'] - df_inv['L90_dBA'],
                       df_inv['L10_dBA'] - df_inv['Leq_dBA']],
                 fmt='D', color=C_RED, ms=8, lw=1.4, capsize=4,
                 label='Mediciones inválidas (descartar)', zorder=5)
    for xi_, row in zip(xi, df_inv.itertuples()):
        ax6.annotate(row.ID, xy=(xi_, row.Leq_dBA), xytext=(xi_+0.15, row.Leq_dBA+1.5),
                     fontsize=7.5, color=C_RED, fontweight='bold')

ax6.set_xlabel('Índice de medición (válidas → inválidas)', fontsize=10, fontweight='bold')
ax6.set_ylabel('Nivel (dBA)', fontsize=10, fontweight='bold')
ax6.set_title('6 — Niveles Acústicos: Válidas vs. Inválidas (Leq / L10 / L90 / Lmax)',
              fontsize=10, fontweight='bold', color=C_NAVY)
ax6.legend(fontsize=8, framealpha=.92)

fig.suptitle('Validación Metrológica Automática — Campaña de Monitoreo Acústico\n'
             f'Equipo: {EQUIPO}  |  Calibrador: {CALIBRADOR}  |  Op.: {OPERADOR}',
             fontsize=12, fontweight='bold', color=C_NAVY, y=1.01)
fig.text(0.01, -0.01, NOTE_TEXT, fontsize=7.5, color='gray', style='italic')

plt.savefig('/home/claude/validacion_metrologica_fig1.png', dpi=160, bbox_inches='tight')
plt.close()
print("Fig 1 — Dashboard metrológico: OK")

# ==============================================================================
# 5. FIGURA 2 — CARTA DE CONTROL DE DERIVA (Shewhart)
# ==============================================================================

fig2, axes2 = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
fig2.subplots_adjust(hspace=0.08)

derivas_ser = df['Deriva_dB'].values
n_ser       = len(derivas_ser)
x_ser       = np.arange(n_ser)
mov_rango   = np.abs(np.diff(derivas_ser))  # rango móvil

# Límites de control (3σ con estimación por rango móvil)
d2     = 1.128   # constante para n=2
sigma_est = mov_rango.mean() / d2
LCS    = mu + 3 * sigma_est   # Límite Control Superior
LCI    = mu - 3 * sigma_est   # Límite Control Inferior
LAV    = UMBRAL_DERIVA         # Límite de Acción Superior (normativo)
LAI    = -UMBRAL_DERIVA

# Gráfico I (valores individuales)
ax_i = axes2[0]
c_pts = [C_RED if abs(d) > UMBRAL_DERIVA else C_NAVY for d in derivas_ser]
ax_i.plot(x_ser, derivas_ser, color=C_NAVY, lw=1.2, alpha=.6, zorder=2)
ax_i.scatter(x_ser, derivas_ser, c=c_pts, s=55, zorder=4, edgecolors='white', lw=0.5)
ax_i.axhline(mu,   color=C_GREEN, lw=1.4, ls='-',  label=f'Media {mu:+.3f} dB')
ax_i.axhline(LCS,  color=C_BLUE,  lw=1.2, ls='--', label=f'LCS {LCS:+.3f} dB (3σ)')
ax_i.axhline(LCI,  color=C_BLUE,  lw=1.2, ls='--', label=f'LCI {LCI:+.3f} dB (3σ)')
ax_i.axhline(LAV,  color=C_RED,   lw=1.5, ls=':',  label=f'Límite normativo ±{UMBRAL_DERIVA} dB')
ax_i.axhline(LAI,  color=C_RED,   lw=1.5, ls=':')
ax_i.fill_between(x_ser, LCI, LCS, alpha=.06, color=C_BLUE)
# Marcar puntos fuera de límite normativo
for xi, di in zip(x_ser, derivas_ser):
    if abs(di) > UMBRAL_DERIVA:
        ax_i.annotate(f'{di:+.2f}', xy=(xi, di),
                      xytext=(xi + 0.3, di + (0.04 if di > 0 else -0.08)),
                      fontsize=8, color=C_RED, fontweight='bold')
ax_i.set_ylabel('Deriva (dB)', fontsize=10, fontweight='bold')
ax_i.set_title('Carta de Control I-MR — Deriva de Calibración (Gráfico I)',
               fontsize=10, fontweight='bold', color=C_NAVY)
ax_i.legend(fontsize=8.5, framealpha=.92, ncol=3)
ax_i.set_xlim(-0.5, n_ser - 0.5)

# Gráfico MR (rango móvil)
ax_mr = axes2[1]
lcsmr = 3.267 * mov_rango.mean()   # D4 para n=2
ax_mr.bar(x_ser[1:], mov_rango, color=C_BLUE, alpha=0.75, width=0.6, zorder=3,
          label='Rango móvil')
ax_mr.axhline(mov_rango.mean(), color=C_GREEN, lw=1.4, ls='-',
              label=f'MR̄ {mov_rango.mean():.3f} dB')
ax_mr.axhline(lcsmr, color=C_RED, lw=1.4, ls='--',
              label=f'LCS {lcsmr:.3f} dB (D4 × MR̄)')
ax_mr.set_xlabel('Índice de medición', fontsize=10, fontweight='bold')
ax_mr.set_ylabel('|Δi − Δi-1| (dB)', fontsize=10, fontweight='bold')
ax_mr.set_title('Carta de Control I-MR — Deriva de Calibración (Gráfico MR)',
               fontsize=10, fontweight='bold', color=C_NAVY)
ax_mr.legend(fontsize=8.5, framealpha=.92)
ax_mr.set_xticks(x_ser)
ax_mr.set_xticklabels(df['ID'].values, rotation=45, ha='right', fontsize=8)

fig2.suptitle('Carta de Control Estadístico de Proceso (I-MR) — Deriva de Calibración\n'
              'Herramienta de trazabilidad metrológica · ISO 17025:2017',
              fontsize=12, fontweight='bold', color=C_NAVY, y=1.01)
fig2.text(0.01, -0.03, NOTE_TEXT, fontsize=7.5, color='gray', style='italic')
plt.savefig('/home/claude/validacion_metrologica_fig2.png', dpi=160, bbox_inches='tight')
plt.close()
print("Fig 2 — Carta de control I-MR: OK")

# ==============================================================================
# 6. REPORTE DE CONSOLA
# ==============================================================================

print()
print("=" * 72)
print("  REPORTE DE VALIDACIÓN METROLÓGICA — ISO 17025 / IEC 61672-1")
print("=" * 72)
print(f"  Equipo     : {EQUIPO}")
print(f"  Calibrador : {CALIBRADOR}  (ref. {CAL_REF} dB  |  U = ±{INCERTIDUMBRE_K2} dB, k=2)")
print(f"  Operador   : {OPERADOR}")
print(f"  Período    : {FECHA_INICIO.strftime('%d/%m/%Y')} — "
      f"{(FECHA_INICIO + timedelta(hours=(N_MEDICIONES-1)*2)).strftime('%d/%m/%Y')}")
print("-" * 72)
print(f"  {'ID':<7} {'Fecha/Hora':<18} {'Punto':<7} "
      f"{'ΔCal (dB)':<12} {'Leq (dBA)':<12} {'Estado':<10} {'Fallas'}")
print("-" * 72)
for _, r in df.iterrows():
    flag = '✅' if r['Estado'] == 'VÁLIDA' else '❌'
    print(f"  {r['ID']:<7} {r['FechaHora'].strftime('%d/%m/%Y %H:%M'):<18} "
          f"{r['Punto']:<7} {r['Deriva_dB']:>+8.3f} dB  "
          f"{r['Leq_dBA']:>7.1f} dBA  {flag} {r['Estado']:<10} {r['Fallas']}")
print("-" * 72)
print(f"  Resultado: {validas}/{N_MEDICIONES} válidas ({tasa_val:.1f} %)")
print(f"  Deriva: μ = {mu:+.4f} dB  |  σ = {df['Deriva_dB'].std():.4f} dB  |  "
      f"máx. abs. = {df['Deriva_dB'].abs().max():.4f} dB")
print("=" * 72)

if invalidas:
    print(f"\n  ⚠️  MEDICIONES INVÁLIDAS — ACCIÓN REQUERIDA:")
    for _, r in df[df['Estado'] == 'INVÁLIDA'].iterrows():
        print(f"     {r['ID']}  {r['FechaHora'].strftime('%d/%m/%Y %H:%M')}  "
              f"Punto {r['Punto']}  →  {r['Fallas']}")
    print(f"     Acción: descartar y repetir con equipo verificado.")

# Exportar (opcional)
# df.to_csv('campana_validada.csv', index=False, encoding='utf-8-sig')
# print("\n✅ Dataset exportado a 'campana_validada.csv'")

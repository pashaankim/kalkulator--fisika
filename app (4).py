
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import re

# ==================== CONFIG ====================
st.set_page_config(
    page_title="Smart Physics Calculator",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .hero {
        padding: 2.5rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .hero h1 { font-size: 2.8rem; font-weight: 800; margin-bottom: 0.5rem; }
    .hero p { font-size: 1.1rem; opacity: 0.95; max-width: 600px; margin: 0 auto; }

    .result-box {
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
        border-left: 5px solid #4f46e5;
        margin: 1rem 0;
    }
    .result-value { font-size: 2.2rem; font-weight: 800; color: #4f46e5; }

    .formula-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .formula-card:hover { border-color: #4f46e5; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

    .tag {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    .tag-me { background: #dbeafe; color: #1e40af; }
    .tag-el { background: #fef3c7; color: #92400e; }
    .tag-wa { background: #d1fae5; color: #065f46; }
    .tag-fl { background: #fce7f3; color: #9d174d; }
    .tag-th { background: #e0e7ff; color: #3730a3; }

    .step-item {
        padding: 0.6rem 0;
        border-bottom: 1px dashed #cbd5e1;
        font-size: 0.95rem;
    }
    .step-item:last-child { border-bottom: none; font-weight: 700; color: #4f46e5; }

    .quiz-option {
        padding: 1rem;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .quiz-option:hover { border-color: #4f46e5; background: #f5f3ff; }

    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
</style>
""", unsafe_allow_html=True)

# ==================== DATA ====================
CONSTANTS = {
    'g': {'value': 9.8, 'unit': 'm/s²', 'name': 'Percepatan gravitasi bumi'},
    'c': {'value': 3e8, 'unit': 'm/s', 'name': 'Kecepatan cahaya dalam vakum'},
    'G': {'value': 6.674e-11, 'unit': 'N·m²/kg²', 'name': 'Konstanta gravitasi universal'},
    'e': {'value': 1.602e-19, 'unit': 'C', 'name': 'Muatan dasar elektron'},
    'h': {'value': 6.626e-34, 'unit': 'J·s', 'name': 'Konstanta Planck'},
    'R': {'value': 8.314, 'unit': 'J/(mol·K)', 'name': 'Konstanta gas ideal'},
    'N_A': {'value': 6.022e23, 'unit': 'mol⁻¹', 'name': 'Bilangan Avogadro'},
    'k': {'value': 1.381e-23, 'unit': 'J/K', 'name': 'Konstanta Boltzmann'},
}

FORMULAS = {
    'newton': {
        'name': 'Hukum Newton II',
        'category': 'Mekanika',
        'formula_latex': r'F = m \cdot a',
        'formula_text': 'F = m × a',
        'variables': {'m': 'Massa (kg)', 'a': 'Percepatan (m/s²)'},
        'result': {'var': 'F', 'name': 'Gaya', 'unit': 'N'},
        'calculate': lambda d: d['m'] * d['a'],
        'explanation': 'Gaya resultan sama dengan massa dikali percepatan.'
    },
    'kinetic_energy': {
        'name': 'Energi Kinetik',
        'category': 'Mekanika',
        'formula_latex': r'E_k = \frac{1}{2}mv^2',
        'formula_text': 'E_k = ½mv²',
        'variables': {'m': 'Massa (kg)', 'v': 'Kecepatan (m/s)'},
        'result': {'var': 'E_k', 'name': 'Energi Kinetik', 'unit': 'J'},
        'calculate': lambda d: 0.5 * d['m'] * d['v']**2,
        'explanation': 'Energi kinetik adalah energi yang dimiliki benda karena geraknya.'
    },
    'potential_energy': {
        'name': 'Energi Potensial Gravitasi',
        'category': 'Mekanika',
        'formula_latex': r'E_p = mgh',
        'formula_text': 'E_p = mgh',
        'variables': {'m': 'Massa (kg)', 'h': 'Ketinggian (m)'},
        'result': {'var': 'E_p', 'name': 'Energi Potensial', 'unit': 'J'},
        'calculate': lambda d: d['m'] * 9.8 * d['h'],
        'explanation': 'Energi potensial gravitasi bergantung pada massa, gravitasi, dan ketinggian.'
    },
    'work': {
        'name': 'Usaha',
        'category': 'Mekanika',
        'formula_latex': r'W = F \cdot s',
        'formula_text': 'W = F × s',
        'variables': {'F': 'Gaya (N)', 's': 'Jarak (m)'},
        'result': {'var': 'W', 'name': 'Usaha', 'unit': 'J'},
        'calculate': lambda d: d['F'] * d['s'],
        'explanation': 'Usaha adalah gaya yang bekerja dikali perpindahan dalam arah gaya.'
    },
    'momentum': {
        'name': 'Momentum',
        'category': 'Mekanika',
        'formula_latex': r'p = m \cdot v',
        'formula_text': 'p = m × v',
        'variables': {'m': 'Massa (kg)', 'v': 'Kecepatan (m/s)'},
        'result': {'var': 'p', 'name': 'Momentum', 'unit': 'kg·m/s'},
        'calculate': lambda d: d['m'] * d['v'],
        'explanation': 'Momentum adalah ukuran kuantitas gerak suatu benda.'
    },
    'impulse': {
        'name': 'Impuls',
        'category': 'Mekanika',
        'formula_latex': r'I = F \cdot \Delta t',
        'formula_text': 'I = F × Δt',
        'variables': {'F': 'Gaya (N)', 't': 'Waktu (s)'},
        'result': {'var': 'I', 'name': 'Impuls', 'unit': 'N·s'},
        'calculate': lambda d: d['F'] * d['t'],
        'explanation': 'Impuls adalah perubahan momentum yang sama dengan gaya dikali selang waktu.'
    },
    'ohm': {
        'name': 'Hukum Ohm',
        'category': 'Listrik',
        'formula_latex': r'V = I \cdot R',
        'formula_text': 'V = I × R',
        'variables': {'I': 'Arus (A)', 'R': 'Hambatan (Ω)'},
        'result': {'var': 'V', 'name': 'Tegangan', 'unit': 'V'},
        'calculate': lambda d: d['I'] * d['R'],
        'explanation': 'Tegangan listrik pada suatu penghantar sebanding dengan arus dan hambatannya.'
    },
    'electric_power': {
        'name': 'Daya Listrik',
        'category': 'Listrik',
        'formula_latex': r'P = V \cdot I',
        'formula_text': 'P = V × I',
        'variables': {'V': 'Tegangan (V)', 'I': 'Arus (A)'},
        'result': {'var': 'P', 'name': 'Daya', 'unit': 'W'},
        'calculate': lambda d: d['V'] * d['I'],
        'explanation': 'Daya listrik adalah laju transfer energi listrik.'
    },
    'resistance_series': {
        'name': 'Hambatan Seri',
        'category': 'Listrik',
        'formula_latex': r'R_{total} = R_1 + R_2',
        'formula_text': 'R_total = R₁ + R₂',
        'variables': {'R1': 'Hambatan 1 (Ω)', 'R2': 'Hambatan 2 (Ω)'},
        'result': {'var': 'R_total', 'name': 'Hambatan Total', 'unit': 'Ω'},
        'calculate': lambda d: d['R1'] + d['R2'],
        'explanation': 'Dalam rangkaian seri, hambatan total adalah jumlah semua hambatan.'
    },
    'resistance_parallel': {
        'name': 'Hambatan Paralel',
        'category': 'Listrik',
        'formula_latex': r'\frac{1}{R_{total}} = \frac{1}{R_1} + \frac{1}{R_2}',
        'formula_text': '1/R_total = 1/R₁ + 1/R₂',
        'variables': {'R1': 'Hambatan 1 (Ω)', 'R2': 'Hambatan 2 (Ω)'},
        'result': {'var': 'R_total', 'name': 'Hambatan Total', 'unit': 'Ω'},
        'calculate': lambda d: 1 / (1/d['R1'] + 1/d['R2']),
        'explanation': 'Dalam rangkaian paralel, kebalikan hambatan total sama dengan jumlah kebalikan hambatan.'
    },
    'frequency': {
        'name': 'Frekuensi',
        'category': 'Gelombang',
        'formula_latex': r'f = \frac{1}{T}',
        'formula_text': 'f = 1/T',
        'variables': {'T': 'Periode (s)'},
        'result': {'var': 'f', 'name': 'Frekuensi', 'unit': 'Hz'},
        'calculate': lambda d: 1 / d['T'],
        'explanation': 'Frekuensi adalah banyaknya siklus gelombang per satuan waktu.'
    },
    'wave_speed': {
        'name': 'Cepat Rambat Gelombang',
        'category': 'Gelombang',
        'formula_latex': r'v = f \cdot \lambda',
        'formula_text': 'v = f × λ',
        'variables': {'f': 'Frekuensi (Hz)', 'lambda': 'Panjang gelombang (m)'},
        'result': {'var': 'v', 'name': 'Cepat Rambat', 'unit': 'm/s'},
        'calculate': lambda d: d['f'] * d['lambda'],
        'explanation': 'Cepat rambat gelombang sama dengan frekuensi dikali panjang gelombang.'
    },
    'pressure': {
        'name': 'Tekanan',
        'category': 'Fluida',
        'formula_latex': r'P = \frac{F}{A}',
        'formula_text': 'P = F/A',
        'variables': {'F': 'Gaya (N)', 'A': 'Luas (m²)'},
        'result': {'var': 'P', 'name': 'Tekanan', 'unit': 'Pa'},
        'calculate': lambda d: d['F'] / d['A'],
        'explanation': 'Tekanan adalah gaya yang bekerja tegak lurus per satuan luas permukaan.'
    },
    'archimedes': {
        'name': 'Hukum Archimedes',
        'category': 'Fluida',
        'formula_latex': r'F_a = \rho \cdot V \cdot g',
        'formula_text': 'F_a = ρ × V × g',
        'variables': {'rho': 'Massa jenis fluida (kg/m³)', 'V': 'Volume benda tercelup (m³)'},
        'result': {'var': 'F_a', 'name': 'Gaya Apung', 'unit': 'N'},
        'calculate': lambda d: d['rho'] * d['V'] * 9.8,
        'explanation': 'Gaya apung sama dengan berat fluida yang dipindahkan oleh benda.'
    },
    'flow_rate': {
        'name': 'Debit',
        'category': 'Fluida',
        'formula_latex': r'Q = \frac{V}{t}',
        'formula_text': 'Q = V/t',
        'variables': {'V': 'Volume (m³)', 't': 'Waktu (s)'},
        'result': {'var': 'Q', 'name': 'Debit', 'unit': 'm³/s'},
        'calculate': lambda d: d['V'] / d['t'],
        'explanation': 'Debit adalah volume fluida yang mengalir per satuan waktu.'
    },
    'density': {
        'name': 'Massa Jenis',
        'category': 'Fluida',
        'formula_latex': r'\rho = \frac{m}{V}',
        'formula_text': 'ρ = m/V',
        'variables': {'m': 'Massa (kg)', 'V': 'Volume (m³)'},
        'result': {'var': 'rho', 'name': 'Massa Jenis', 'unit': 'kg/m³'},
        'calculate': lambda d: d['m'] / d['V'],
        'explanation': 'Massa jenis adalah massa per satuan volume suatu zat.'
    },
    'ideal_gas': {
        'name': 'Persamaan Gas Ideal',
        'category': 'Termodinamika',
        'formula_latex': r'PV = nRT',
        'formula_text': 'PV = nRT',
        'variables': {'P': 'Tekanan (Pa)', 'V': 'Volume (m³)', 'n': 'Mol (mol)', 'T': 'Suhu (K)'},
        'result': {'var': 'check', 'name': 'Selisih PV - nRT', 'unit': 'J'},
        'calculate': lambda d: d['P'] * d['V'] - d['n'] * 8.314 * d['T'],
        'explanation': 'Persamaan keadaan gas ideal yang menghubungkan tekanan, volume, suhu, dan jumlah mol.'
    },
}

CONVERSIONS = {
    'length': {
        'name': 'Panjang',
        'units': {'m': 1, 'cm': 0.01, 'mm': 0.001, 'km': 1000, 'inch': 0.0254, 'ft': 0.3048, 'mile': 1609.34, 'yard': 0.9144},
        'base': 'm'
    },
    'mass': {
        'name': 'Massa',
        'units': {'kg': 1, 'g': 0.001, 'mg': 1e-6, 'ton': 1000, 'lb': 0.453592, 'oz': 0.0283495},
        'base': 'kg'
    },
    'time': {
        'name': 'Waktu',
        'units': {'s': 1, 'min': 60, 'hour': 3600, 'day': 86400, 'week': 604800, 'year': 31536000},
        'base': 's'
    },
    'temperature': {
        'name': 'Suhu',
        'type': 'special',
        'units': ['C', 'F', 'K']
    },
    'energy': {
        'name': 'Energi',
        'units': {'J': 1, 'kJ': 1000, 'cal': 4.184, 'kcal': 4184, 'eV': 1.602e-19, 'Wh': 3600, 'kWh': 3.6e6},
        'base': 'J'
    },
    'force': {
        'name': 'Gaya',
        'units': {'N': 1, 'kN': 1000, 'dyne': 1e-5, 'kgf': 9.80665, 'lbf': 4.44822},
        'base': 'N'
    },
    'velocity': {
        'name': 'Kecepatan',
        'units': {'m/s': 1, 'km/h': 0.277778, 'mph': 0.44704, 'knot': 0.514444, 'ft/s': 0.3048},
        'base': 'm/s'
    },
    'pressure': {
        'name': 'Tekanan',
        'units': {'Pa': 1, 'kPa': 1000, 'MPa': 1e6, 'bar': 1e5, 'atm': 101325, 'psi': 6894.76, 'mmHg': 133.322},
        'base': 'Pa'
    },
    'power': {
        'name': 'Daya',
        'units': {'W': 1, 'kW': 1000, 'MW': 1e6, 'hp': 745.7, 'BTU/h': 0.293071},
        'base': 'W'
    }
}

QUESTIONS = [
    {
        'id': 1,
        'question': 'Sebuah balok bermassa 5 kg ditarik dengan gaya 20 N di atas lantai licin. Berapa percepatannya?',
        'options': ['2 m/s²', '4 m/s²', '5 m/s²', '10 m/s²'],
        'answer': 1,
        'explanation': 'Menggunakan Hukum Newton II: a = F/m = 20/5 = 4 m/s²',
        'category': 'SMA',
        'difficulty': 'Mudah'
    },
    {
        'id': 2,
        'question': 'Sebuah mobil bermassa 1000 kg bergerak dengan kecepatan 20 m/s. Berapa energi kinetiknya?',
        'options': ['100 kJ', '200 kJ', '400 kJ', '800 kJ'],
        'answer': 1,
        'explanation': 'E_k = ½mv² = 0.5 × 1000 × 20² = 200.000 J = 200 kJ',
        'category': 'SMA',
        'difficulty': 'Mudah'
    },
    {
        'id': 3,
        'question': 'Dalam suatu rangkaian, arus listrik 2 A mengalir melalui hambatan 10 Ω. Berapa tegangannya?',
        'options': ['5 V', '10 V', '15 V', '20 V'],
        'answer': 3,
        'explanation': 'Menggunakan Hukum Ohm: V = I × R = 2 × 10 = 20 V',
        'category': 'SMA',
        'difficulty': 'Mudah'
    },
    {
        'id': 4,
        'question': 'Sebuah benda dengan massa jenis 800 kg/m³ memiliki volume 0,5 m³ ketika dimasukkan ke dalam air (ρ = 1000 kg/m³). Berapa gaya apung yang bekerja?',
        'options': ['1960 N', '3920 N', '4900 N', '7840 N'],
        'answer': 2,
        'explanation': 'F_a = ρ_air × V × g = 1000 × 0.5 × 9.8 = 4900 N',
        'category': 'SMA',
        'difficulty': 'Sedang'
    },
    {
        'id': 5,
        'question': 'Gelombang bunyi memiliki frekuensi 440 Hz dan panjang gelombang 0,75 m. Berapa cepat rambatnya?',
        'options': ['220 m/s', '330 m/s', '440 m/s', '660 m/s'],
        'answer': 1,
        'explanation': 'v = f × λ = 440 × 0.75 = 330 m/s',
        'category': 'SMA',
        'difficulty': 'Mudah'
    },
    {
        'id': 6,
        'question': 'Sebuah pegas memiliki konstanta 200 N/m diregangkan sejauh 0,1 m. Berapa energi potensial pegasnya?',
        'options': ['0.5 J', '1 J', '2 J', '4 J'],
        'answer': 1,
        'explanation': 'E_p = ½kx² = 0.5 × 200 × (0.1)² = 1 J',
        'category': 'SMA',
        'difficulty': 'Sedang'
    },
    {
        'id': 7,
        'question': 'Benda bermassa 2 kg jatuh bebas dari ketinggian 45 m. Berapa kecepatan benda saat menyentuh tanah? (g = 10 m/s²)',
        'options': ['20 m/s', '25 m/s', '30 m/s', '35 m/s'],
        'answer': 2,
        'explanation': 'v² = 2gh = 2 × 10 × 45 = 900 → v = 30 m/s',
        'category': 'SMA',
        'difficulty': 'Sedang'
    },
    {
        'id': 8,
        'question': 'Sebuah resistor 4 Ω dan 6 Ω disusun paralel. Berapa hambatan totalnya?',
        'options': ['2 Ω', '2.4 Ω', '10 Ω', '24 Ω'],
        'answer': 1,
        'explanation': '1/R_total = 1/4 + 1/6 = 5/12 → R_total = 12/5 = 2.4 Ω',
        'category': 'SMA',
        'difficulty': 'Sedang'
    }
]

# ==================== SESSION STATE ====================
if 'quiz_index' not in st.session_state:
    st.session_state.quiz_index = 0
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_answered' not in st.session_state:
    st.session_state.quiz_answered = False
if 'selected_formula' not in st.session_state:
    st.session_state.selected_formula = None
if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

# ==================== HELPER FUNCTIONS ====================
def generate_steps(formula_id, values, result):
    formula = FORMULAS[formula_id]
    steps = []
    steps.append(f"📐 **Rumus**: {formula['formula_text']}")
    steps.append("📝 **Diketahui**:")
    for var, desc in formula['variables'].items():
        unit = desc.split('(')[-1].strip(')')
        steps.append(f"   • {var} = {values[var]} {unit}")
    steps.append(f"❓ **Ditanya**: {formula['result']['name']} ({formula['result']['var']})")
    steps.append("🔢 **Penyelesaian**:")

    if formula_id == 'newton':
        steps.append(f"   F = m × a = {values['m']} × {values['a']} = **{result:.4g} N**")
    elif formula_id == 'kinetic_energy':
        steps.append(f"   E_k = ½ × m × v² = 0.5 × {values['m']} × {values['v']}² = **{result:.4g} J**")
    elif formula_id == 'potential_energy':
        steps.append(f"   E_p = m × g × h = {values['m']} × 9.8 × {values['h']} = **{result:.4g} J**")
    elif formula_id == 'work':
        steps.append(f"   W = F × s = {values['F']} × {values['s']} = **{result:.4g} J**")
    elif formula_id == 'momentum':
        steps.append(f"   p = m × v = {values['m']} × {values['v']} = **{result:.4g} kg·m/s**")
    elif formula_id == 'impulse':
        steps.append(f"   I = F × Δt = {values['F']} × {values['t']} = **{result:.4g} N·s**")
    elif formula_id == 'ohm':
        steps.append(f"   V = I × R = {values['I']} × {values['R']} = **{result:.4g} V**")
    elif formula_id == 'electric_power':
        steps.append(f"   P = V × I = {values['V']} × {values['I']} = **{result:.4g} W**")
    elif formula_id == 'resistance_series':
        steps.append(f"   R_total = R₁ + R₂ = {values['R1']} + {values['R2']} = **{result:.4g} Ω**")
    elif formula_id == 'resistance_parallel':
        r1, r2 = values['R1'], values['R2']
        steps.append(f"   1/R_total = 1/{r1} + 1/{r2} = {1/r1 + 1/r2:.6f}")
        steps.append(f"   R_total = 1 / {1/r1 + 1/r2:.6f} = **{result:.4g} Ω**")
    elif formula_id == 'frequency':
        steps.append(f"   f = 1/T = 1/{values['T']} = **{result:.4g} Hz**")
    elif formula_id == 'wave_speed':
        steps.append(f"   v = f × λ = {values['f']} × {values['lambda']} = **{result:.4g} m/s**")
    elif formula_id == 'pressure':
        steps.append(f"   P = F/A = {values['F']} / {values['A']} = **{result:.4g} Pa**")
    elif formula_id == 'archimedes':
        steps.append(f"   F_a = ρ × V × g = {values['rho']} × {values['V']} × 9.8 = **{result:.4g} N**")
    elif formula_id == 'flow_rate':
        steps.append(f"   Q = V/t = {values['V']} / {values['t']} = **{result:.4g} m³/s**")
    elif formula_id == 'density':
        steps.append(f"   ρ = m/V = {values['m']} / {values['V']} = **{result:.4g} kg/m³**")
    elif formula_id == 'ideal_gas':
        pv = values['P'] * values['V']
        nrt = values['n'] * 8.314 * values['T']
        steps.append(f"   PV = {values['P']} × {values['V']} = {pv:.2f} Pa·m³")
        steps.append(f"   nRT = {values['n']} × 8.314 × {values['T']} = {nrt:.2f} J")
        steps.append(f"   Selisih = {pv:.2f} - {nrt:.2f} = **{result:.4g}** (mendekati 0 = gas ideal)")

    steps.append(f"✅ **Jadi**, {formula['result']['name']} = **{result:.6g} {formula['result']['unit']}**")
    return steps

def convert_temperature(value, from_unit, to_unit):
    if from_unit == to_unit: return value
    if from_unit == 'C': celsius = value
    elif from_unit == 'F': celsius = (value - 32) * 5/9
    elif from_unit == 'K': celsius = value - 273.15
    if to_unit == 'C': return celsius
    elif to_unit == 'F': return celsius * 9/5 + 32
    elif to_unit == 'K': return celsius + 273.15

def parse_ai_query(query):
    query = query.lower()
    patterns = [
        (r'energi\s+kinetik.*?([0-9]+(?:[.,][0-9]+)?)\s*kg.*?([0-9]+(?:[.,][0-9]+)?)\s*m/s',
         lambda m: {'formula': 'kinetic_energy', 'values': {'m': float(m.group(1).replace(',', '.')), 'v': float(m.group(2).replace(',', '.'))}}),
        (r'(?:gaya|newton).*?([0-9]+(?:[.,][0-9]+)?)\s*kg.*?([0-9]+(?:[.,][0-9]+)?)\s*m/s',
         lambda m: {'formula': 'newton', 'values': {'m': float(m.group(1).replace(',', '.')), 'a': float(m.group(2).replace(',', '.'))}}),
        (r'(?:tegangan|ohm|volt).*?([0-9]+(?:[.,][0-9]+)?)\s*A.*?([0-9]+(?:[.,][0-9]+)?)\s*ohm',
         lambda m: {'formula': 'ohm', 'values': {'I': float(m.group(1).replace(',', '.')), 'R': float(m.group(2).replace(',', '.'))}}),
        (r'energi\s+potensial.*?([0-9]+(?:[.,][0-9]+)?)\s*kg.*?([0-9]+(?:[.,][0-9]+)?)\s*m',
         lambda m: {'formula': 'potential_energy', 'values': {'m': float(m.group(1).replace(',', '.')), 'h': float(m.group(2).replace(',', '.'))}}),
        (r'usaha.*?([0-9]+(?:[.,][0-9]+)?)\s*N.*?([0-9]+(?:[.,][0-9]+)?)\s*m',
         lambda m: {'formula': 'work', 'values': {'F': float(m.group(1).replace(',', '.')), 's': float(m.group(2).replace(',', '.'))}}),
        (r'momentum.*?([0-9]+(?:[.,][0-9]+)?)\s*kg.*?([0-9]+(?:[.,][0-9]+)?)\s*m/s',
         lambda m: {'formula': 'momentum', 'values': {'m': float(m.group(1).replace(',', '.')), 'v': float(m.group(2).replace(',', '.'))}}),
        (r'(?:daya|power).*?([0-9]+(?:[.,][0-9]+)?)\s*V.*?([0-9]+(?:[.,][0-9]+)?)\s*A',
         lambda m: {'formula': 'electric_power', 'values': {'V': float(m.group(1).replace(',', '.')), 'I': float(m.group(2).replace(',', '.'))}}),
        (r'tekanan.*?([0-9]+(?:[.,][0-9]+)?)\s*N.*?([0-9]+(?:[.,][0-9]+)?)\s*m',
         lambda m: {'formula': 'pressure', 'values': {'F': float(m.group(1).replace(',', '.')), 'A': float(m.group(2).replace(',', '.'))}}),
    ]
    for pattern, extractor in patterns:
        match = re.search(pattern, query)
        if match:
            return extractor(match)
    return None

def get_tag_class(cat):
    return {'Mekanika':'tag-me','Listrik':'tag-el','Gelombang':'tag-wa','Fluida':'tag-fl','Termodinamika':'tag-th'}.get(cat,'tag-me')

# ==================== SIDEBAR ====================
st.sidebar.title("⚛️ Smart Physics")
st.sidebar.markdown("*Super App Fisika*")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navigasi",
    ["🏠 Beranda", "🧮 Kalkulator", "📚 Rumus", "🔄 Konverter", "📊 Grafik", 
     "🤖 AI Asisten", "🔬 Lab Virtual", "📝 Latihan", "🔢 Scientific", "📋 Ringkasan"]
)

st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Pengaturan")
if st.sidebar.toggle("🌓 Dark Mode", value=False):
    st.markdown("<style>.stApp { background: #0f172a; color: #f8fafc; }</style>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("v1.0 | Streamlit Edition")

# ==================== HOME ====================
if menu == "🏠 Beranda":
    st.markdown("""
    <div class="hero">
        <h1>⚛️ Smart Physics Calculator</h1>
        <p>Kalkulator fisika cerdas dengan penjelasan langkah demi langkah, grafik interaktif, simulasi virtual, dan latihan soal — semua dalam satu aplikasi.</p>
    </div>
    """, unsafe_allow_html=True)

    search = st.text_input("🔍 Cari rumus atau konsep fisika...", placeholder="Contoh: energi kinetik, hukum ohm, tekanan...")

    cols = st.columns(4)
    quick_links = [
        ("🍎 Newton", "Mekanika", "newton"),
        ("⚡ Energi", "Mekanika", "kinetic_energy"),
        ("🔌 Listrik", "Listrik", "ohm"),
        ("〰️ Gelombang", "Gelombang", "wave_speed"),
        ("💧 Fluida", "Fluida", "pressure"),
        ("🔄 Konverter", "Alat", None),
        ("📊 Grafik", "Visual", None),
        ("📝 Latihan", "Latihan", None),
    ]

    for i, (title, cat, fid) in enumerate(quick_links):
        with cols[i % 4]:
            with st.container():
                st.markdown(f"""
                <div class="formula-card" style="text-align:center; cursor:pointer;">
                    <h3>{title}</h3>
                    <span class="tag {get_tag_class(cat)}">{cat}</span>
                </div>
                """, unsafe_allow_html=True)
                if fid and st.button(f"Buka →", key=f"quick_{fid}_{i}"):
                    st.session_state.selected_formula = fid
                    st.rerun()
                elif not fid and cat == "Alat" and st.button(f"Buka →", key=f"quick_conv_{i}"):
                    st.rerun()

    if search:
        st.subheader("🔎 Hasil Pencarian")
        found = False
        for fid, f in FORMULAS.items():
            if search.lower() in f['name'].lower() or search.lower() in f['category'].lower():
                found = True
                with st.container():
                    st.markdown(f"""
                    <div class="formula-card">
                        <h4>{f['name']}</h4>
                        <span class="tag {get_tag_class(f['category'])}">{f['category']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.latex(f['formula_latex'])
                    if st.button("Gunakan Kalkulator", key=f"search_{fid}"):
                        st.session_state.selected_formula = fid
                        st.rerun()
        if not found:
            st.info("Tidak ditemukan rumus yang cocok. Coba kata kunci lain.")

    st.divider()
    st.subheader("🎯 Kenapa Smart Physics?")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("📐 Rumus", len(FORMULAS))
        st.caption("Rumus lengkap dari mekanika hingga termodinamika")
    with c2:
        st.metric("📊 Grafik", "5 Jenis")
        st.caption("Visualisasi gelombang, GLBB, jatuh bebas, dan osilasi")
    with c3:
        st.metric("📝 Soal", len(QUESTIONS))
        st.caption("Latihan soal pilihan ganda dengan pembahasan")

# ==================== CALCULATOR ====================
elif menu == "🧮 Kalkulator":
    st.title("🧮 Smart Calculator")
    st.caption("Pilih rumus fisika, masukkan nilai yang diketahui, dan dapatkan hasil dengan langkah pengerjaan lengkap.")

    formula_options = {k: f"{v['name']} ({v['category']})" for k, v in FORMULAS.items()}

    default_idx = 0
    if st.session_state.selected_formula and st.session_state.selected_formula in formula_options:
        default_idx = list(formula_options.keys()).index(st.session_state.selected_formula)
        st.session_state.selected_formula = None

    formula_id = st.selectbox("Pilih Rumus Fisika", options=list(formula_options.keys()), 
                               format_func=lambda x: formula_options[x], index=default_idx)

    f = FORMULAS[formula_id]

    col1, col2 = st.columns([1, 1])
    with col1:
        st.latex(f['formula_latex'])
        st.caption(f"Kategori: {f['category']} | {f['explanation']}")

        inputs = {}
        cols_input = st.columns(len(f['variables']))
        for i, (var, desc) in enumerate(f['variables'].items()):
            with cols_input[i]:
                inputs[var] = st.number_input(desc, value=0.0, step=0.1, key=f"calc_{formula_id}_{var}")

        if st.button("🔢 Hitung & Jelaskan", type="primary", use_container_width=True):
            try:
                result = f['calculate'](inputs)
                steps = generate_steps(formula_id, inputs, result)

                st.session_state.calc_history.append({
                    'formula': f['name'],
                    'result': result,
                    'unit': f['result']['unit']
                })

                with col2:
                    st.markdown(f"""
                    <div class="result-box">
                        <div style="font-size:0.9rem; opacity:0.8; margin-bottom:0.5rem;">{f['name']}</div>
                        <div class="result-value">{result:.6g} {f['result']['unit']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("📋 Langkah Pengerjaan Lengkap", expanded=True):
                        for step in steps:
                            st.markdown(f"<div class='step-item'>{step}</div>", unsafe_allow_html=True)

                    st.success(f"✅ {f['result']['name']} = {result:.6g} {f['result']['unit']}")
            except ZeroDivisionError:
                st.error("❌ Tidak bisa dibagi dengan nol!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    if st.session_state.calc_history:
        with st.sidebar.expander("🕒 Riwayat"):
            for item in st.session_state.calc_history[-5:]:
                st.write(f"**{item['formula']}**: {item['result']:.4g} {item['unit']}")

# ==================== FORMULA LIBRARY ====================
elif menu == "📚 Rumus":
    st.title("📚 Formula Library")
    st.caption("Koleksi lengkap rumus fisika dengan penjelasan variabel dan satuan SI.")

    search = st.text_input("🔍 Cari rumus...", placeholder="Ketik nama rumus atau kategori")

    tabs = st.tabs(["Semua", "Mekanika", "Listrik", "Gelombang", "Fluida", "Termodinamika"])
    categories = ["Semua", "Mekanika", "Listrik", "Gelombang", "Fluida", "Termodinamika"]

    for tab, cat in zip(tabs, categories):
        with tab:
            for fid, f in FORMULAS.items():
                if cat != "Semua" and f['category'] != cat:
                    continue
                if search and search.lower() not in f['name'].lower() and search.lower() not in f['category'].lower():
                    continue

                with st.container():
                    st.markdown(f"""
                    <div class="formula-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4>{f['name']}</h4>
                            <span class="tag {get_tag_class(f['category'])}">{f['category']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.latex(f['formula_latex'])

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f"**Hasil**: {f['result']['name']}")
                    with c2:
                        st.markdown(f"**Satuan**: {f['result']['unit']}")
                    with c3:
                        if st.button("🧮 Gunakan", key=f"lib_{fid}"):
                            st.session_state.selected_formula = fid
                            st.rerun()
                    st.caption(f['explanation'])
                    st.divider()

# ==================== CONVERTER ====================
elif menu == "🔄 Konverter":
    st.title("🔄 Auto Unit Converter")
    st.caption("Konversi satuan otomatis dengan notasi ilmiah.")

    cat = st.selectbox("Kategori Konversi", options=list(CONVERSIONS.keys()), 
                       format_func=lambda x: CONVERSIONS[x]['name'])

    conv = CONVERSIONS[cat]
    units = conv['units'] if conv.get('type') != 'special' else conv['units']

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        val = st.number_input("Nilai", value=1.0, step=0.1)
        from_unit = st.selectbox("Dari", options=units if isinstance(units, list) else list(units.keys()))
    with col2:
        st.write("")
        st.write("")
        if st.button("⇄ Tukar", use_container_width=True):
            st.session_state.conv_swap = True
    with col3:
        to_unit = st.selectbox("Ke", options=units if isinstance(units, list) else list(units.keys()), 
                                index=1 if len(units) > 1 else 0)

    if st.button("🔄 Konversi", type="primary", use_container_width=True):
        try:
            if cat == 'temperature':
                result = convert_temperature(val, from_unit, to_unit)
            else:
                base = val * units[from_unit]
                result = base / units[to_unit]

            st.success(f"✅ **{val} {from_unit}** = **{result:.6g} {to_unit}**")

            # Scientific notation
            st.info(f"🔬 Notasi Ilmiah: **{result:.4e} {to_unit}**")
        except Exception as e:
            st.error(f"Error: {e}")

# ==================== GRAPH ====================
elif menu == "📊 Grafik":
    st.title("📊 Interactive Graph")
    st.caption("Visualisasi grafik fisika dengan parameter yang dapat diatur.")

    gtype = st.selectbox("Jenis Grafik", [
        "〰️ Gelombang Sinus", "🍎 Jatuh Bebas", "📈 GLBB (Kecepatan vs Waktu)", 
        "📍 Posisi vs Waktu (GLB)", "🌀 Osilasi Pegas"
    ])

    fig, ax = plt.subplots(figsize=(10, 5))

    if gtype == "〰️ Gelombang Sinus":
        c1, c2 = st.columns(2)
        with c1:
            A = st.slider("Amplitudo (A)", 0.1, 5.0, 1.0, 0.1)
        with c2:
            omega = st.slider("Frekuensi Sudut (ω)", 0.1, 10.0, 1.0, 0.1)
        t = np.linspace(0, 4*np.pi, 1000)
        y = A * np.sin(omega * t)
        ax.plot(t, y, 'b-', linewidth=2.5)
        ax.set_title(f'Gelombang Sinus: y = {A} sin({omega}t)', fontweight='bold')
        ax.set_xlabel('Waktu (s)'); ax.set_ylabel('Amplitudo')
        ax.grid(True, alpha=0.3); ax.axhline(0, color='k', linewidth=0.5)

    elif gtype == "🍎 Jatuh Bebas":
        h0 = st.slider("Ketinggian Awal (m)", 10, 200, 100, 5)
        t_max = math.sqrt(2 * h0 / 9.8)
        t = np.linspace(0, t_max, 500)
        y = h0 - 0.5 * 9.8 * t**2
        v = 9.8 * t
        ax.plot(t, y, 'r-', linewidth=2.5, label='Posisi (m)')
        ax.set_title('Simulasi Jatuh Bebas', fontweight='bold')
        ax.set_xlabel('Waktu (s)'); ax.set_ylabel('Ketinggian (m)')
        ax.legend(); ax.grid(True, alpha=0.3)
        st.metric("Waktu Jatuh", f"{t_max:.2f} s")

    elif gtype == "📈 GLBB (Kecepatan vs Waktu)":
        c1, c2 = st.columns(2)
        with c1:
            a = st.slider("Percepatan (m/s²)", -10.0, 10.0, 2.0, 0.5)
        with c2:
            v0 = st.slider("Kecepatan Awal (m/s)", -50.0, 50.0, 0.0, 1.0)
        t = np.linspace(0, 10, 500)
        v = v0 + a * t
        ax.plot(t, v, 'g-', linewidth=2.5)
        ax.set_title('Grafik Kecepatan vs Waktu (GLBB)', fontweight='bold')
        ax.set_xlabel('Waktu (s)'); ax.set_ylabel('Kecepatan (m/s)')
        ax.grid(True, alpha=0.3); ax.axhline(0, color='k', linewidth=0.5)

    elif gtype == "📍 Posisi vs Waktu (GLB)":
        v = st.slider("Kecepatan (m/s)", -20.0, 20.0, 5.0, 0.5)
        t = np.linspace(0, 10, 500)
        x = v * t
        ax.plot(t, x, 'purple', linewidth=2.5)
        ax.set_title('Grafik Posisi vs Waktu (GLB)', fontweight='bold')
        ax.set_xlabel('Waktu (s)'); ax.set_ylabel('Posisi (m)')
        ax.grid(True, alpha=0.3)

    elif gtype == "🌀 Osilasi Pegas":
        c1, c2, c3 = st.columns(3)
        with c1:
            A = st.slider("Amplitudo (m)", 0.1, 3.0, 1.0, 0.1)
        with c2:
            k = st.slider("Konstanta Pegas (N/m)", 1, 50, 10, 1)
        with c3:
            m = st.slider("Massa (kg)", 0.1, 5.0, 1.0, 0.1)
        t = np.linspace(0, 4*np.pi, 1000)
        omega = np.sqrt(k/m)
        y = A * np.cos(omega * t)
        ax.plot(t, y, 'orange', linewidth=2.5)
        ax.set_title(f'Osilasi Pegas (ω = {omega:.2f} rad/s)', fontweight='bold')
        ax.set_xlabel('Waktu (s)'); ax.set_ylabel('Perpindahan (m)')
        ax.grid(True, alpha=0.3); ax.axhline(0, color='k', linewidth=0.5)
        st.metric("Periode", f"{2*np.pi/omega:.2f} s")

    plt.tight_layout()
    st.pyplot(fig)

# ==================== AI ASSISTANT ====================
elif menu == "🤖 AI Asisten":
    st.title("🤖 AI Physics Assistant")
    st.caption("Asisten pintar untuk menghitung dan menjelaskan soal fisika secara otomatis.")

    query = st.text_area("Tanyakan soal fisika Anda:", 
                         placeholder="Contoh: Hitung energi kinetik benda 2 kg dengan kecepatan 10 m/s",
                         height=80)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🚀 Tanya AI", type="primary", use_container_width=True):
            if not query:
                st.warning("Masukkan pertanyaan terlebih dahulu!")
            else:
                parsed = parse_ai_query(query)
                if parsed:
                    formula_id = parsed['formula']
                    values = parsed['values']
                    formula = FORMULAS[formula_id]
                    try:
                        result = formula['calculate'](values)
                        steps = generate_steps(formula_id, values, result)

                        st.success(f"✅ Saya mengenali perhitungan **{formula['name']}** dari pertanyaan Anda.")
                        st.markdown(f"""
                        <div class="result-box">
                            <div class="result-value">{result:.6g} {formula['result']['unit']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        with st.expander("📋 Langkah Pengerjaan", expanded=True):
                            for step in steps:
                                st.markdown(f"<div class='step-item'>{step}</div>", unsafe_allow_html=True)

                        st.caption(f"💡 {formula['explanation']}")
                    except Exception as e:
                        st.error(f"Error perhitungan: {e}")
                else:
                    st.info("🤖 Maaf, saya belum bisa mengenali pertanyaan tersebut dengan pasti.")
                    st.write("**Coba gunakan format seperti ini:**")
                    examples = [
                        "Hitung energi kinetik benda 2 kg dengan kecepatan 10 m/s",
                        "Hitung gaya benda 5 kg dengan percepatan 2 m/s²",
                        "Hitung tegangan arus 2 A dengan hambatan 10 ohm",
                        "Hitung energi potensial benda 3 kg pada ketinggian 10 m",
                        "Hitung usaha gaya 50 N dengan jarak 10 m",
                        "Hitung momentum benda 4 kg dengan kecepatan 5 m/s"
                    ]
                    for ex in examples:
                        st.markdown(f"- `{ex}`")

    with col2:
        st.markdown("##### 💡 Contoh Pertanyaan")
        chips = [
            ("Energi Kinetik", "Hitung energi kinetik benda 2 kg dengan kecepatan 10 m/s"),
            ("Hukum Newton", "Hitung gaya benda 5 kg dengan percepatan 2 m/s²"),
            ("Hukum Ohm", "Hitung tegangan arus 2 A dengan hambatan 10 ohm"),
            ("Energi Potensial", "Hitung energi potensial benda 3 kg pada ketinggian 10 m"),
        ]
        cols = st.columns(len(chips))
        for i, (label, text) in enumerate(chips):
            with cols[i]:
                if st.button(label, key=f"chip_{i}", use_container_width=True):
                    st.session_state.ai_query_preset = text
                    st.rerun()

    if 'ai_query_preset' in st.session_state:
        query = st.session_state.ai_query_preset
        del st.session_state.ai_query_preset

# ==================== VIRTUAL LAB ====================
elif menu == "🔬 Lab Virtual":
    st.title("🔬 Virtual Physics Lab")
    st.caption("Simulasi fisika interaktif dengan kontrol parameter.")

    lab_mode = st.selectbox("Pilih Simulasi", ["🍎 Jatuh Bebas", "〰️ Gelombang", "🌀 Pegas"])

    if lab_mode == "🍎 Jatuh Bebas":
        c1, c2, c3 = st.columns(3)
        with c1:
            mass = st.slider("Massa (kg)", 0.1, 10.0, 1.0, 0.1)
        with c2:
            h0 = st.slider("Ketinggian (m)", 10, 200, 100, 5)
        with c3:
            g = st.slider("Gravitasi (m/s²)", 1.0, 20.0, 9.8, 0.1)

        t_max = math.sqrt(2 * h0 / g)
        t = st.slider("Waktu Simulasi", 0.0, t_max, 0.0, 0.1)

        y = 0.5 * g * t**2
        v = g * t
        current_h = max(h0 - y, 0)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, h0 + 20)
        ax.axhline(0, color='brown', linewidth=8, label='Tanah')
        ax.scatter([5], [current_h], s=100 + mass*50, c='red', zorder=5, label=f'Benda ({mass} kg)')

        # Ruler
        for i in range(0, h0+1, 20):
            ax.axhline(i, xmin=0.85, xmax=0.9, color='gray', linewidth=1)
            ax.text(9.2, i, f'{i}m', fontsize=8, va='center')

        ax.set_title(f'Jatuh Bebas t = {t:.2f}s', fontweight='bold')
        ax.set_ylabel('Ketinggian (m)')
        ax.set_xticks([])
        ax.legend(loc='upper right')
        plt.tight_layout()
        st.pyplot(fig)

        m1, m2, m3 = st.columns(3)
        m1.metric("Kecepatan", f"{v:.2f} m/s")
        m2.metric("Jatuh", f"{y:.2f} m")
        m3.metric("Sisa Tinggi", f"{current_h:.2f} m")

    elif lab_mode == "〰️ Gelombang":
        c1, c2, c3 = st.columns(3)
        with c1:
            amp = st.slider("Amplitudo", 10, 100, 50)
        with c2:
            freq = st.slider("Frekuensi", 1, 10, 2)
        with c3:
            phase = st.slider("Fase (waktu)", 0.0, 2*np.pi, 0.0, 0.1)

        x = np.linspace(0, 4*np.pi, 500)
        y = amp * np.sin(freq * x - phase)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(x, y, 'b-', linewidth=2.5)
        ax.axhline(0, color='k', linewidth=0.5)
        ax.set_title('Gelombang Sinus Snapshot', fontweight='bold')
        ax.set_xlabel('Posisi (x)'); ax.set_ylabel('Amplitudo (y)')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

    elif lab_mode == "🌀 Pegas":
        c1, c2, c3 = st.columns(3)
        with c1:
            mass = st.slider("Massa (kg)", 0.5, 5.0, 1.0, 0.1)
        with c2:
            k = st.slider("Konstanta Pegas (N/m)", 5, 50, 10, 1)
        with c3:
            t = st.slider("Waktu", 0.0, 4*np.pi, 0.0, 0.1)

        omega = np.sqrt(k/mass)
        y = 40 * np.cos(omega * t)  # 40px amplitude for viz

        fig, ax = plt.subplots(figsize=(6, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(-100, 100)
        ax.axhline(0, color='gray', linestyle='--', alpha=0.5)

        # Ceiling & spring
        ax.plot([4, 6], [90, 90], 'k-', linewidth=4)
        spring_x = [5 + (i%2)*2 - 1 for i in range(12)]
        spring_y = np.linspace(90, y, 12)
        ax.plot(spring_x, spring_y, 'r-', linewidth=2)

        # Mass
        rect = plt.Rectangle((3.5, y-8), 3, 16, facecolor='blue', edgecolor='darkblue')
        ax.add_patch(rect)

        ax.set_title(f'Osilasi Pegas (ω={omega:.2f} rad/s)', fontweight='bold')
        ax.set_xticks([])
        plt.tight_layout()
        st.pyplot(fig)

        st.metric("Perpindahan", f"{y:.1f} px")
        st.metric("Periode", f"{2*np.pi/omega:.2f} s")

# ==================== PRACTICE ====================
elif menu == "📝 Latihan":
    st.title("📝 Practice Questions")
    st.caption("Latihan soal pilihan ganda dengan pembahasan otomatis.")

    q = QUESTIONS[st.session_state.quiz_index]

    progress = (st.session_state.quiz_index + 1) / len(QUESTIONS)
    st.progress(progress, text=f"Soal {st.session_state.quiz_index + 1} dari {len(QUESTIONS)}")

    col_badge1, col_badge2 = st.columns(2)
    with col_badge1:
        st.markdown(f"<span class='tag tag-me'>{q['category']}</span>", unsafe_allow_html=True)
    with col_badge2:
        diff_color = 'tag-wa' if q['difficulty'] == 'Mudah' else 'tag-el'
        st.markdown(f"<span class='tag {diff_color}'>{q['difficulty']}</span>", unsafe_allow_html=True)

    st.subheader(q['question'])

    answer = st.radio("Pilih jawaban:", q['options'], index=None, key=f"quiz_opt_{q['id']}")

    if st.button("✅ Periksa Jawaban", type="primary"):
        if answer is None:
            st.warning("Pilih jawaban terlebih dahulu!")
        else:
            correct_idx = q['answer']
            selected_idx = q['options'].index(answer)
            if selected_idx == correct_idx:
                st.success("🎉 Benar! Jawaban Anda tepat.")
                if not st.session_state.quiz_answered:
                    st.session_state.quiz_score += 1
            else:
                st.error(f"❌ Salah. Jawaban yang benar: **{q['options'][correct_idx]}**")

            st.info(f"💡 **Pembahasan**: {q['explanation']}")
            st.session_state.quiz_answered = True

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Sebelumnya", disabled=st.session_state.quiz_index == 0, use_container_width=True):
            st.session_state.quiz_index -= 1
            st.session_state.quiz_answered = False
            st.rerun()
    with col2:
        st.metric("Skor", f"{st.session_state.quiz_score}/{len(QUESTIONS)}")
    with col3:
        if st.button("Selanjutnya →", disabled=st.session_state.quiz_index == len(QUESTIONS)-1, use_container_width=True):
            st.session_state.quiz_index += 1
            st.session_state.quiz_answered = False
            st.rerun()

# ==================== SCIENTIFIC CALCULATOR ====================
elif menu == "🔢 Scientific":
    st.title("🔢 Scientific Calculator")
    st.caption("Kalkulator ilmiah dengan fungsi trigonometri, logaritma, dan eksponen.")

    expr = st.text_input("Ekspresi Matematika", value="", placeholder="Contoh: sin(30) + log(100) * sqrt(16)")

    # Button grid
    btn_rows = [
        ['sin(', 'cos(', 'tan(', 'log('],
        ['ln(', 'sqrt(', 'abs(', 'exp('],
        ['7', '8', '9', '/'],
        ['4', '5', '6', '*'],
        ['1', '2', '3', '-'],
        ['0', '.', '^', '+'],
        ['(', ')', 'pi', 'e'],
    ]

    for row in btn_rows:
        cols = st.columns(len(row))
        for i, btn in enumerate(row):
            with cols[i]:
                if st.button(btn, key=f"sc_{btn}", use_container_width=True):
                    st.session_state.sc_expr = (st.session_state.get('sc_expr', '') + btn).replace('pi', '3.14159').replace('^', '**')
                    st.rerun()

    if 'sc_expr' in st.session_state:
        expr = st.session_state.sc_expr
        del st.session_state.sc_expr

    if st.button("🧮 Hitung =", type="primary", use_container_width=True):
        if not expr:
            st.warning("Masukkan ekspresi!")
        else:
            try:
                safe_dict = {
                    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                    'log': math.log10, 'ln': math.log, 'sqrt': math.sqrt,
                    'abs': abs, 'exp': math.exp, 'factorial': math.factorial,
                    'pi': math.pi, 'e': math.e
                }
                # Convert degrees to radians for trig if user likely using degrees
                # But standard scientific calc uses radians. We'll note this.
                result = eval(expr, {"__builtins__": {}}, safe_dict)
                st.success(f"**Hasil:** {result}")
                st.session_state.calc_history.append({'formula': f'Calc: {expr}', 'result': result, 'unit': ''})
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.caption("💡 Tips: Gunakan radian untuk trigonometri. Contoh: sin(3.14159/2) = 1.0")

    if st.session_state.calc_history:
        with st.expander("🕒 Riwayat Perhitungan"):
             st.session_state.calc_history[-10:]:
                st.write(f"**{item['formula']}** = {item['result']}")

# ==================== CHEAT SHEET ====================
elif menu == "📋 Ringkasan":
    st.title("📋 Physics Cheat Sheet")
    st.caption("Ringkasan cepat rumus penting, satuan SI, dan konstanta fisika.")

    tab1, tab2, tab3, tab4 = st.tabs(["📐 Rumus", "🔬 Konstanta", "📏 Prefix", "📊 Tabel Satuan"])

    with tab1:
        st.subheader("Mekanika")
        mech_data = [
            ["Gaya", r"F = m \cdot a", "N (Newton)"],
            ["Energi Kinetik", r"E_k = \frac{1}{2}mv^2", "J (Joule)"],
            ["Energi Potensial", r"E_p = mgh", "J"],
            ["Usaha", r"W = F \cdot s", "J"],
            ["Momentum", r"p = m \cdot v", "kg·m/s"],
            ["Impuls", r"I = F \cdot \Delta t", "N·s"],
        ]
        for name, latex, unit in mech_data:
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown(f"**{name}** ({unit})")
                with c2:
                    st.latex(latex)
                st.divider()

        st.subheader("Listrik")
        elec_data = [
            ["Hukum Ohm", r"V = I \cdot R", "V (Volt)"],
            ["Daya Listrik", r"P = V \cdot I = I^2R", "W (Watt)"],
            ["Hambatan Seri", r"R_{tot} = R_1 + R_2", "Ω (Ohm)"],
            ["Hambatan Paralel", r"\frac{1}{R_{tot}} = \frac{1}{R_1} + \frac{1}{R_2}", "Ω"],
        ]
        for name, latex, unit in elec_data:
            c1, c2 = st.columns([1, 2])
            with c1: st.markdown(f"**{name}** ({unit})")
            with c2: st.latex(latex)
            st.divider()

        st.subheader("Gelombang & Fluida")
        wave_data = [
            ["Cepat Rambat", r"v = f \cdot \lambda", "m/s"],
            ["Frekuensi", r"f = \frac{1}{T}", "Hz"],
            ["Tekanan", r"P = \frac{F}{A} = \rho gh", "Pa"],
            ["Archimedes", r"F_a = \rho V g", "N"],
            ["Debit", r"Q = \frac{V}{t}", "m³/s"],
        ]
        for name, latex, unit in wave_data:
            c1, c2 = st.columns([1, 2])
            with c1: st.markdown(f"**{name}** ({unit})")
            with c2: st.latex(latex)
            st.divider()

    with tab2:
        st.subheader("Konstanta Fisika Universal")
        const_data = []
        for sym, info in CONSTANTS.items():
            val_str = f"{info['value']:.3e}" if info['value'] < 0.01 else str(info['value'])
            const_data.append([sym, info['name'], val_str, info['unit']])
        st.table(const_data)

    with tab3:
        st.subheader("Prefix SI")
        prefix_data = [
            ["Tera", "T", "10¹²"], ["Giga", "G", "10⁹"], ["Mega", "M", "10⁶"],
            ["Kilo", "k", "10³"], ["Centi", "c", "10⁻²"], ["Milli", "m", "10⁻³"],
            ["Micro", "μ", "10⁻⁶"], ["Nano", "n", "10⁻⁹"], ["Pico", "p", "10⁻¹²"],
        ]
        st.table(prefix_data)

    with tab4:
        st.subheader("Satuan Dasar SI")
        si_data = [
            ["Panjang", "meter", "m"], ["Massa", "kilogram", "kg"], ["Waktu", "second", "s"],
            ["Arus Listrik", "ampere", "A"], ["Suhu", "kelvin", "K"],
            ["Jumlah Zat", "mole", "mol"], ["Intensitas Cahaya", "candela", "cd"],
        ]
        st.table(si_data)

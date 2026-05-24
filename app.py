
import math
import json
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import re

app = Flask(__name__)

# ==================== DATA FISIKA ====================
CONSTANTS = {
    'g': {'value': 9.8, 'unit': 'm/s²', 'name': 'Percepatan gravitasi bumi'},
    'c': {'value': 3e8, 'unit': 'm/s', 'name': 'Kecepatan cahaya'},
    'G': {'value': 6.674e-11, 'unit': 'N·m²/kg²', 'name': 'Konstanta gravitasi'},
    'e': {'value': 1.602e-19, 'unit': 'C', 'name': 'Muatan elektron'},
    'h': {'value': 6.626e-34, 'unit': 'J·s', 'name': 'Konstanta Planck'},
    'R': {'value': 8.314, 'unit': 'J/(mol·K)', 'name': 'Konstanta gas ideal'},
    'N_A': {'value': 6.022e23, 'unit': 'mol⁻¹', 'name': 'Bilangan Avogadro'},
    'k': {'value': 1.381e-23, 'unit': 'J/K', 'name': 'Konstanta Boltzmann'},
}

FORMULAS = {
    'newton': {
        'name': 'Hukum Newton II',
        'category': 'Mekanika',
        'formula': 'F = m × a',
        'variables': {'m': 'Massa (kg)', 'a': 'Percepatan (m/s²)'},
        'result': {'var': 'F', 'name': 'Gaya', 'unit': 'N'},
        'calculate': lambda d: d['m'] * d['a'],
        'explanation': 'Gaya resultan sama dengan massa dikali percepatan.'
    },
    'kinetic_energy': {
        'name': 'Energi Kinetik',
        'category': 'Mekanika',
        'formula': 'E_k = ½mv²',
        'variables': {'m': 'Massa (kg)', 'v': 'Kecepatan (m/s)'},
        'result': {'var': 'E_k', 'name': 'Energi Kinetik', 'unit': 'J'},
        'calculate': lambda d: 0.5 * d['m'] * d['v']**2,
        'explanation': 'Energi kinetik adalah energi yang dimiliki benda karena geraknya.'
    },
    'potential_energy': {
        'name': 'Energi Potensial',
        'category': 'Mekanika',
        'formula': 'E_p = mgh',
        'variables': {'m': 'Massa (kg)', 'h': 'Ketinggian (m)'},
        'result': {'var': 'E_p', 'name': 'Energi Potensial', 'unit': 'J'},
        'calculate': lambda d: d['m'] * 9.8 * d['h'],
        'explanation': 'Energi potensial gravitasi bergantung pada massa, gravitasi, dan ketinggian.'
    },
    'work': {
        'name': 'Usaha',
        'category': 'Mekanika',
        'formula': 'W = F × s',
        'variables': {'F': 'Gaya (N)', 's': 'Jarak (m)'},
        'result': {'var': 'W', 'name': 'Usaha', 'unit': 'J'},
        'calculate': lambda d: d['F'] * d['s'],
        'explanation': 'Usaha adalah gaya yang bekerja dikali perpindahan.'
    },
    'momentum': {
        'name': 'Momentum',
        'category': 'Mekanika',
        'formula': 'p = m × v',
        'variables': {'m': 'Massa (kg)', 'v': 'Kecepatan (m/s)'},
        'result': {'var': 'p', 'name': 'Momentum', 'unit': 'kg·m/s'},
        'calculate': lambda d: d['m'] * d['v'],
        'explanation': 'Momentum adalah ukuran kuantitas gerak suatu benda.'
    },
    'impulse': {
        'name': 'Impuls',
        'category': 'Mekanika',
        'formula': 'I = F × Δt',
        'variables': {'F': 'Gaya (N)', 't': 'Waktu (s)'},
        'result': {'var': 'I', 'name': 'Impuls', 'unit': 'N·s'},
        'calculate': lambda d: d['F'] * d['t'],
        'explanation': 'Impuls adalah perubahan momentum yang sama dengan gaya dikali selang waktu.'
    },
    'ohm': {
        'name': 'Hukum Ohm',
        'category': 'Listrik',
        'formula': 'V = I × R',
        'variables': {'I': 'Arus (A)', 'R': 'Hambatan (Ω)'},
        'result': {'var': 'V', 'name': 'Tegangan', 'unit': 'V'},
        'calculate': lambda d: d['I'] * d['R'],
        'explanation': 'Tegangan listrik sebanding dengan arus dan hambatannya.'
    },
    'electric_power': {
        'name': 'Daya Listrik',
        'category': 'Listrik',
        'formula': 'P = V × I',
        'variables': {'V': 'Tegangan (V)', 'I': 'Arus (A)'},
        'result': {'var': 'P', 'name': 'Daya', 'unit': 'W'},
        'calculate': lambda d: d['V'] * d['I'],
        'explanation': 'Daya listrik adalah laju transfer energi listrik.'
    },
    'resistance_series': {
        'name': 'Hambatan Seri',
        'category': 'Listrik',
        'formula': 'R_total = R₁ + R₂',
        'variables': {'R1': 'Hambatan 1 (Ω)', 'R2': 'Hambatan 2 (Ω)'},
        'result': {'var': 'R_total', 'name': 'Hambatan Total', 'unit': 'Ω'},
        'calculate': lambda d: d['R1'] + d['R2'],
        'explanation': 'Dalam rangkaian seri, hambatan total adalah jumlah semua hambatan.'
    },
    'resistance_parallel': {
        'name': 'Hambatan Paralel',
        'category': 'Listrik',
        'formula': '1/R_total = 1/R₁ + 1/R₂',
        'variables': {'R1': 'Hambatan 1 (Ω)', 'R2': 'Hambatan 2 (Ω)'},
        'result': {'var': 'R_total', 'name': 'Hambatan Total', 'unit': 'Ω'},
        'calculate': lambda d: 1 / (1/d['R1'] + 1/d['R2']),
        'explanation': 'Dalam paralel, kebalikan hambatan total = jumlah kebalikan hambatan.'
    },
    'frequency': {
        'name': 'Frekuensi',
        'category': 'Gelombang',
        'formula': 'f = 1/T',
        'variables': {'T': 'Periode (s)'},
        'result': {'var': 'f', 'name': 'Frekuensi', 'unit': 'Hz'},
        'calculate': lambda d: 1 / d['T'],
        'explanation': 'Frekuensi adalah banyaknya siklus gelombang per satuan waktu.'
    },
    'wave_speed': {
        'name': 'Cepat Rambat Gelombang',
        'category': 'Gelombang',
        'formula': 'v = f × λ',
        'variables': {'f': 'Frekuensi (Hz)', 'lambda': 'Panjang gelombang (m)'},
        'result': {'var': 'v', 'name': 'Cepat Rambat', 'unit': 'm/s'},
        'calculate': lambda d: d['f'] * d['lambda'],
        'explanation': 'Cepat rambat gelombang = frekuensi × panjang gelombang.'
    },
    'pressure': {
        'name': 'Tekanan',
        'category': 'Fluida',
        'formula': 'P = F/A',
        'variables': {'F': 'Gaya (N)', 'A': 'Luas (m²)'},
        'result': {'var': 'P', 'name': 'Tekanan', 'unit': 'Pa'},
        'calculate': lambda d: d['F'] / d['A'],
        'explanation': 'Tekanan adalah gaya tegak lurus per satuan luas permukaan.'
    },
    'archimedes': {
        'name': 'Hukum Archimedes',
        'category': 'Fluida',
        'formula': 'F_a = ρ × V × g',
        'variables': {'rho': 'Massa jenis fluida (kg/m³)', 'V': 'Volume (m³)'},
        'result': {'var': 'F_a', 'name': 'Gaya Apung', 'unit': 'N'},
        'calculate': lambda d: d['rho'] * d['V'] * 9.8,
        'explanation': 'Gaya apung = berat fluida yang dipindahkan oleh benda.'
    },
    'flow_rate': {
        'name': 'Debit',
        'category': 'Fluida',
        'formula': 'Q = V/t',
        'variables': {'V': 'Volume (m³)', 't': 'Waktu (s)'},
        'result': {'var': 'Q', 'name': 'Debit', 'unit': 'm³/s'},
        'calculate': lambda d: d['V'] / d['t'],
        'explanation': 'Debit adalah volume fluida yang mengalir per satuan waktu.'
    },
    'density': {
        'name': 'Massa Jenis',
        'category': 'Fluida',
        'formula': 'ρ = m/V',
        'variables': {'m': 'Massa (kg)', 'V': 'Volume (m³)'},
        'result': {'var': 'rho', 'name': 'Massa Jenis', 'unit': 'kg/m³'},
        'calculate': lambda d: d['m'] / d['V'],
        'explanation': 'Massa jenis adalah massa per satuan volume suatu zat.'
    },
    'ideal_gas': {
        'name': 'Persamaan Gas Ideal',
        'category': 'Termodinamika',
        'formula': 'PV = nRT',
        'variables': {'P': 'Tekanan (Pa)', 'V': 'Volume (m³)', 'n': 'Mol (mol)', 'T': 'Suhu (K)'},
        'result': {'var': 'check', 'name': 'Selisih PV - nRT', 'unit': 'J'},
        'calculate': lambda d: d['P'] * d['V'] - d['n'] * 8.314 * d['T'],
        'explanation': 'Persamaan keadaan gas ideal.'
    },
}

CONVERSIONS = {
    'length': {
        'name': 'Panjang',
        'units': {'m': 1, 'cm': 0.01, 'mm': 0.001, 'km': 1000, 'inch': 0.0254, 'ft': 0.3048, 'mile': 1609.34},
        'base': 'm'
    },
    'mass': {
        'name': 'Massa',
        'units': {'kg': 1, 'g': 0.001, 'mg': 1e-6, 'ton': 1000, 'lb': 0.453592, 'oz': 0.0283495},
        'base': 'kg'
    },
    'time': {
        'name': 'Waktu',
        'units': {'s': 1, 'min': 60, 'hour': 3600, 'day': 86400, 'week': 604800},
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
        'units': {'m/s': 1, 'km/h': 0.277778, 'mph': 0.44704, 'knot': 0.514444},
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

# ==================== HELPER FUNCTIONS ====================
def generate_steps(formula_id, values, result):
    formula = FORMULAS[formula_id]
    steps = []
    steps.append(f"📐 Rumus: {formula['formula']}")
    steps.append("📝 Diketahui:")
    for var, desc in formula['variables'].items():
        unit = desc.split('(')[-1].strip(')')
        steps.append(f"   • {var} = {values[var]} {unit}")
    steps.append(f"❓ Ditanya: {formula['result']['name']}")
    steps.append("🔢 Penyelesaian:")
    
    if formula_id == 'newton':
        steps.append(f"   F = m × a = {values['m']} × {values['a']} = {result:.4g} N")
    elif formula_id == 'kinetic_energy':
        steps.append(f"   E_k = ½ × m × v² = 0.5 × {values['m']} × {values['v']}² = {result:.4g} J")
    elif formula_id == 'potential_energy':
        steps.append(f"   E_p = m × g × h = {values['m']} × 9.8 × {values['h']} = {result:.4g} J")
    elif formula_id == 'work':
        steps.append(f"   W = F × s = {values['F']} × {values['s']} = {result:.4g} J")
    elif formula_id == 'momentum':
        steps.append(f"   p = m × v = {values['m']} × {values['v']} = {result:.4g} kg·m/s")
    elif formula_id == 'impulse':
        steps.append(f"   I = F × Δt = {values['F']} × {values['t']} = {result:.4g} N·s")
    elif formula_id == 'ohm':
        steps.append(f"   V = I × R = {values['I']} × {values['R']} = {result:.4g} V")
    elif formula_id == 'electric_power':
        steps.append(f"   P = V × I = {values['V']} × {values['I']} = {result:.4g} W")
    elif formula_id == 'resistance_series':
        steps.append(f"   R_total = R₁ + R₂ = {values['R1']} + {values['R2']} = {result:.4g} Ω")
    elif formula_id == 'resistance_parallel':
        r1, r2 = values['R1'], values['R2']
        steps.append(f"   1/R_total = 1/{r1} + 1/{r2} = {1/r1 + 1/r2:.6f}")
        steps.append(f"   R_total = 1 / {1/r1 + 1/r2:.6f} = {result:.4g} Ω")
    elif formula_id == 'frequency':
        steps.append(f"   f = 1/T = 1/{values['T']} = {result:.4g} Hz")
    elif formula_id == 'wave_speed':
        steps.append(f"   v = f × λ = {values['f']} × {values['lambda']} = {result:.4g} m/s")
    elif formula_id == 'pressure':
        steps.append(f"   P = F/A = {values['F']} / {values['A']} = {result:.4g} Pa")
    elif formula_id == 'archimedes':
        steps.append(f"   F_a = ρ × V × g = {values['rho']} × {values['V']} × 9.8 = {result:.4g} N")
    elif formula_id == 'flow_rate':
        steps.append(f"   Q = V/t = {values['V']} / {values['t']} = {result:.4g} m³/s")
    elif formula_id == 'density':
        steps.append(f"   ρ = m/V = {values['m']} / {values['V']} = {result:.4g} kg/m³")
    elif formula_id == 'ideal_gas':
        pv = values['P'] * values['V']
        nrt = values['n'] * 8.314 * values['T']
        steps.append(f"   PV = {values['P']} × {values['V']} = {pv:.2f}")
        steps.append(f"   nRT = {values['n']} × 8.314 × {values['T']} = {nrt:.2f}")
        steps.append(f"   Selisih = {pv:.2f} - {nrt:.2f} = {result:.4g}")
    
    steps.append(f"✅ Jadi, {formula['result']['name']} = {result:.6g} {formula['result']['unit']}")
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

# ==================== ROUTES ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    formula_id = data.get('formula')
    values = data.get('values', {})
    
    if formula_id not in FORMULAS:
        return jsonify({'error': 'Rumus tidak ditemukan'}), 404
    
    formula = FORMULAS[formula_id]
    try:
        numeric_values = {var: float(values[var]) for var in formula['variables']}
        result = formula['calculate'](numeric_values)
        steps = generate_steps(formula_id, numeric_values, result)
        return jsonify({
            'success': True,
            'result': round(result, 10),
            'unit': formula['result']['unit'],
            'steps': steps,
            'formula_name': formula['name'],
            'explanation': formula['explanation']
        })
    except ZeroDivisionError:
        return jsonify({'error': 'Tidak bisa dibagi dengan nol'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/convert', methods=['POST'])
def convert():
    data = request.json
    category = data.get('category')
    value = float(data.get('value', 0))
    from_unit = data.get('from')
    to_unit = data.get('to')
    
    if category not in CONVERSIONS:
        return jsonify({'error': 'Kategori tidak ditemukan'}), 404
    
    conv = CONVERSIONS[category]
    try:
        if category == 'temperature':
            result = convert_temperature(value, from_unit, to_unit)
        else:
            base_value = value * conv['units'][from_unit]
            result = base_value / conv['units'][to_unit]
        return jsonify({
            'success': True,
            'result': round(result, 10),
            'from': f"{value} {from_unit}",
            'to': f"{result:.6g} {to_unit}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/graph', methods=['POST'])
def graph():
    data = request.json
    graph_type = data.get('type')
    
    try:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        
        if graph_type == 'wave':
            t = np.linspace(0, 4*np.pi, 1000)
            A = float(data.get('amplitude', 1))
            omega = float(data.get('omega', 1))
            y = A * np.sin(omega * t)
            ax.plot(t, y, 'b-', linewidth=2.5)
            ax.set_xlabel('Waktu (s)', fontsize=12)
            ax.set_ylabel('Amplitudo', fontsize=12)
            ax.set_title(f'Gelombang Sinus: y = {A} sin({omega}t)', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linewidth=0.5)
            
        elif graph_type == 'free_fall':
            g = 9.8
            h0 = float(data.get('h0', 100))
            t_max = math.sqrt(2 * h0 / g)
            t = np.linspace(0, t_max, 500)
            y = h0 - 0.5 * g * t**2
            ax.plot(t, y, 'r-', linewidth=2.5, label='Posisi (m)')
            ax.set_xlabel('Waktu (s)', fontsize=12)
            ax.set_ylabel('Ketinggian (m)', fontsize=12)
            ax.set_title('Simulasi Jatuh Bebas', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
        elif graph_type == 'glbb':
            a = float(data.get('a', 2))
            v0 = float(data.get('v0', 0))
            t = np.linspace(0, 10, 500)
            v = v0 + a * t
            ax.plot(t, v, 'g-', linewidth=2.5, label='Kecepatan (m/s)')
            ax.set_xlabel('Waktu (s)', fontsize=12)
            ax.set_ylabel('Kecepatan (m/s)', fontsize=12)
            ax.set_title('Grafik Kecepatan vs Waktu (GLBB)', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
        elif graph_type == 'position_time':
            v = float(data.get('velocity', 5))
            t = np.linspace(0, 10, 500)
            x = v * t
            ax.plot(t, x, 'purple', linewidth=2.5)
            ax.set_xlabel('Waktu (s)', fontsize=12)
            ax.set_ylabel('Posisi (m)', fontsize=12)
            ax.set_title('Grafik Posisi vs Waktu (GLB)', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
        elif graph_type == 'spring':
            t = np.linspace(0, 4*np.pi, 1000)
            A = float(data.get('amplitude', 1))
            k = float(data.get('k', 10))
            m = float(data.get('mass', 1))
            omega = np.sqrt(k/m)
            y = A * np.cos(omega * t)
            ax.plot(t, y, 'orange', linewidth=2.5)
            ax.set_xlabel('Waktu (s)', fontsize=12)
            ax.set_ylabel('Perpindahan (m)', fontsize=12)
            ax.set_title(f'Grafik Osilasi Pegas (ω = {omega:.2f} rad/s)', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linewidth=0.5)
        
        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{image_base64}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/questions')
def get_questions():
    return jsonify({'success': True, 'questions': QUESTIONS})

@app.route('/api/check-answer', methods=['POST'])
def check_answer():
    data = request.json
    qid = data.get('id')
    answer = data.get('answer')
    
    question = next((q for q in QUESTIONS if q['id'] == qid), None)
    if not question:
        return jsonify({'error': 'Soal tidak ditemukan'}), 404
    
    is_correct = answer == question['answer']
    return jsonify({
        'success': True,
        'correct': is_correct,
        'explanation': question['explanation'],
        'correct_answer': question['answer']
    })

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant():
    data = request.json
    query = data.get('query', '')
    
    parsed = parse_ai_query(query)
    
    if parsed:
        formula_id = parsed['formula']
        values = parsed['values']
        formula = FORMULAS[formula_id]
        
        try:
            result = formula['calculate'](values)
            steps = generate_steps(formula_id, values, result)
            
            return jsonify({
                'success': True,
                'understood': True,
                'formula_name': formula['name'],
                'result': round(result, 6),
                'unit': formula['result']['unit'],
                'steps': steps,
                'explanation': formula['explanation'],
                'message': f"✅ Saya mengenali perhitungan **{formula['name']}** dari pertanyaan Anda."
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({
            'success': True,
            'understood': False,
            'message': '🤖 Maaf, saya belum bisa mengenali pertanyaan tersebut dengan pasti. Coba gunakan format seperti contoh di bawah:',
            'suggestions': [
                'Hitung energi kinetik benda 2 kg dengan kecepatan 10 m/s',
                'Hitung gaya benda 5 kg dengan percepatan 2 m/s²',
                'Hitung tegangan arus 2 A dengan hambatan 10 ohm',
                'Hitung energi potensial benda 3 kg pada ketinggian 10 m',
                'Hitung usaha gaya 50 N dengan jarak 10 m',
                'Hitung momentum benda 4 kg dengan kecepatan 5 m/s'
            ]
        })

if __name__ == '__main__':
    print("🚀 Smart Physics Calculator berjalan di http://localhost:5000")
    app.run(debug=True, port=5000)

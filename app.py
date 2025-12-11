#!/usr/bin/env python3
"""
HYLLTEKNIK - Kapoptimering Webb-App
Med visuella kapmönster
"""

from flask import Flask, render_template, request, jsonify
from itertools import product
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')

class KapOptimering:
    def __init__(self, stock_length=6000, fixture_rest=50, saw_kerf=2.5):
        self.stock_length = stock_length
        self.fixture_rest = fixture_rest
        self.saw_kerf = saw_kerf
        self.usable_length = stock_length - fixture_rest

    def pattern_length(self, counts, lengths):
        total = sum(lengths[i] * counts[i] for i in range(len(lengths)))
        num_pieces = sum(counts)
        if num_pieces == 0:
            return 0
        return total + num_pieces * self.saw_kerf

    def generate_patterns(self, lengths):
        patterns = []
        max_counts = [int(self.usable_length / (l + self.saw_kerf)) for l in lengths]

        # Begränsa för snabbare beräkning
        if len(lengths) > 3:
            # Rekursiv generering med pruning
            self._generate_recursive(lengths, max_counts, [0] * len(lengths), 0, patterns)
        else:
            for counts in product(*[range(m + 1) for m in max_counts]):
                if sum(counts) == 0:
                    continue
                length = self.pattern_length(counts, lengths)
                if length <= self.usable_length:
                    patterns.append({
                        'counts': counts,
                        'waste': self.usable_length - length,
                        'length': length
                    })

        patterns.sort(key=lambda p: p['waste'])
        return patterns

    def _generate_recursive(self, lengths, max_counts, current, idx, patterns):
        if idx == len(lengths):
            if sum(current) > 0:
                length = self.pattern_length(current, lengths)
                if length <= self.usable_length:
                    patterns.append({
                        'counts': tuple(current),
                        'waste': self.usable_length - length,
                        'length': length
                    })
            return

        # Beräkna kvarvarande utrymme
        current_length = self.pattern_length(current[:idx] + [0] * (len(lengths) - idx), lengths[:idx])
        remaining = self.usable_length - current_length

        # Max antal av denna längd som får plats
        max_this = min(max_counts[idx], int(remaining / (lengths[idx] + self.saw_kerf)) + 1)

        for count in range(max_this + 1):
            current[idx] = count
            self._generate_recursive(lengths, max_counts, current, idx + 1, patterns)
        current[idx] = 0

    def solve(self, order):
        if not order:
            return None

        lengths = sorted(order.keys(), reverse=True)
        remaining = [order[l] for l in lengths]
        patterns = self.generate_patterns(lengths)
        solution = []

        while any(r > 0 for r in remaining):
            best_pattern = None
            best_score = -1

            for p in patterns:
                if not all(p['counts'][i] <= remaining[i] for i in range(len(lengths))):
                    continue
                pieces_used = sum(min(p['counts'][i], remaining[i]) for i in range(len(lengths)))
                if pieces_used == 0:
                    continue
                score = (p['length'] / self.usable_length) * 1000 + pieces_used
                if score > best_score:
                    best_score = score
                    best_pattern = p

            if best_pattern is None:
                break

            times = min(remaining[i] // best_pattern['counts'][i]
                       for i in range(len(lengths)) if best_pattern['counts'][i] > 0)
            times = max(1, times)

            for i in range(len(lengths)):
                remaining[i] -= best_pattern['counts'][i] * times

            # Build visual pieces for this pattern
            pieces = []
            for i, count in enumerate(best_pattern['counts']):
                for _ in range(count):
                    pieces.append({
                        'length': lengths[i],
                        'label': f"{lengths[i]}mm"
                    })

            solution.append({
                'counts': dict(zip(lengths, best_pattern['counts'])),
                'waste': best_pattern['waste'],
                'used': best_pattern['length'],
                'tube_count': times,
                'pieces': pieces,
                'lengths': lengths
            })

        return solution


@app.route('/')
def index():
    return render_template('index.html')


def calculate_buffer_suggestions(order, optimizer, current_results):
    """Beräkna förslag på spillätare för att förbättra utnyttjande"""
    if current_results['utilization'] >= 98:
        return []

    usable = optimizer.usable_length
    lengths = sorted(order.keys())
    suggestions = []

    # Testa olika bufferlängder
    test_lengths = set(lengths)

    # Lägg till halva längder och komplement till långa bitar
    for l in lengths:
        if l > usable * 0.4:
            complement = int(usable - l - optimizer.saw_kerf * 2)
            if complement > 100:
                test_lengths.add(complement)
        test_lengths.add(l // 2)

    # Testa standardlängder
    for std in [100, 150, 200, 250, 300, 400, 500]:
        test_lengths.add(std)

    for buffer_len in sorted(test_lengths):
        if buffer_len < 50 or buffer_len > usable * 0.4:
            continue

        for buffer_qty in [5, 10, 15, 20, 30, 50]:
            test_order = order.copy()
            test_order[buffer_len] = test_order.get(buffer_len, 0) + buffer_qty

            test_solution = optimizer.solve(test_order)
            if not test_solution:
                continue

            # Beräkna resultat
            test_tubes = sum(s['tube_count'] for s in test_solution)
            test_waste = sum(s['waste'] * s['tube_count'] for s in test_solution)
            test_util = (1 - test_waste / (test_tubes * usable)) * 100

            improvement = test_util - current_results['utilization']

            if improvement > 1.5:
                suggestions.append({
                    'length': buffer_len,
                    'quantity': buffer_qty,
                    'new_utilization': round(test_util, 2),
                    'improvement': round(improvement, 2),
                    'extra_tubes': test_tubes - current_results['total_tubes'],
                    'waste_reduction': round((current_results['total_waste_mm'] - test_waste) / 1000, 2)
                })

    # Sortera och ta unika
    suggestions.sort(key=lambda x: (-x['improvement'], x['quantity']))

    # Filtrera för att få varierade förslag
    unique = []
    seen_lengths = set()
    for s in suggestions:
        if s['length'] not in seen_lengths and len(unique) < 5:
            unique.append(s)
            seen_lengths.add(s['length'])

    return unique


@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json

    # Parse parameters
    stock_length = float(data.get('stock_length', 6000))
    fixture_rest = float(data.get('fixture_rest', 50))
    saw_kerf = float(data.get('saw_kerf', 2.5))

    # Parse order
    order = {}
    for item in data.get('items', []):
        length = int(item['length'])
        qty = int(item['quantity'])
        if length > 0 and qty > 0:
            order[length] = order.get(length, 0) + qty

    if not order:
        return jsonify({'error': 'Ingen beställning angiven'}), 400

    # Run optimization
    optimizer = KapOptimering(stock_length, fixture_rest, saw_kerf)
    solution = optimizer.solve(order)

    if not solution:
        return jsonify({'error': 'Kunde inte hitta lösning'}), 400

    # Calculate totals
    total_tubes = sum(s['tube_count'] for s in solution)
    total_waste = sum(s['waste'] * s['tube_count'] for s in solution)

    # Verify production
    produced = {}
    for s in solution:
        for length, count in s['counts'].items():
            produced[length] = produced.get(length, 0) + count * s['tube_count']

    verification = []
    for length in sorted(order.keys(), reverse=True):
        needed = order[length]
        got = produced.get(length, 0)
        verification.append({
            'length': length,
            'needed': needed,
            'produced': got,
            'ok': got >= needed
        })

    # Beräkna nuvarande resultat för buffer-analys
    current_results = {
        'total_tubes': total_tubes,
        'total_waste_mm': total_waste,
        'utilization': round((1 - total_waste / (total_tubes * (stock_length - fixture_rest))) * 100, 2) if total_tubes > 0 else 0
    }

    # Beräkna buffer-förslag om utnyttjandet är lågt
    buffer_suggestions = []
    if current_results['utilization'] < 97:
        buffer_suggestions = calculate_buffer_suggestions(order, optimizer, current_results)

    return jsonify({
        'success': True,
        'job_name': data.get('job_name', ''),
        'material': data.get('material', ''),
        'parameters': {
            'stock_length': stock_length,
            'fixture_rest': fixture_rest,
            'saw_kerf': saw_kerf,
            'usable_length': stock_length - fixture_rest
        },
        'patterns': solution,
        'summary': {
            'total_tubes': total_tubes,
            'total_waste_mm': total_waste,
            'total_waste_m': round(total_waste / 1000, 3),
            'total_material_m': round(total_tubes * stock_length / 1000, 1),
            'utilization': current_results['utilization']
        },
        'verification': verification,
        'buffer_suggestions': buffer_suggestions,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
    })


if __name__ == '__main__':
    app.run(debug=True, port=5050)

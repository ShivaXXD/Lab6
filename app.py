# Модель: Математичне моделювання та аналіз струмів у електричних колах постійного струму за законами Кірхгофа (5 семестр)
# Автор: Власійчук Данило, група АІ-235

from flask import Flask, request, jsonify
import numpy as np
import json

app = Flask(__name__)

class CircuitSimulator:
    def __init__(self, num_nodes, components):
        self.num_equations = num_nodes - 1
        self.num_nodes_total = num_nodes
        self.components = components
        self.reference_node = num_nodes - 1
        self.G_matrix = np.zeros((self.num_equations, self.num_equations))
        self.I_vector = np.zeros(self.num_equations)

    def build_system_equations(self):
        for comp in self.components:
            n1, n2, R, E = comp
            if R <= 0: continue
            g = 1.0 / R
            I_eq = E * g
            if n1 != self.reference_node:
                self.G_matrix[n1, n1] += g
            if n2 != self.reference_node:
                self.G_matrix[n2, n2] += g
            if n1 != self.reference_node and n2 != self.reference_node:
                self.G_matrix[n1, n2] -= g
                self.G_matrix[n2, n1] -= g
            if n1 != self.reference_node:
                self.I_vector[n1] -= I_eq
            if n2 != self.reference_node:
                self.I_vector[n2] += I_eq

    def solve(self):
        self.build_system_equations()
        try:
            node_voltages_calc = np.linalg.solve(self.G_matrix, self.I_vector)
            voltages = np.append(node_voltages_calc, 0.0).tolist()
            
            currents = []
            for n1, n2, R, E in self.components:
                if R <= 0:
                    currents.append(None)
                    continue
                current = (voltages[n1] - voltages[n2] + E) / R
                currents.append(current)
                
            return {"voltages": voltages, "currents": currents}
        except Exception as e:
            return {"error": str(e)}

@app.route('/calculate', methods=['GET'])
def calculate():
    num_nodes = request.args.get('num_nodes', type=int)
    components_str = request.args.get('components')
    
    if not num_nodes or not components_str:
        return jsonify({"error": "Missing parameters"}), 400
        
    try:
        components = json.loads(components_str)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid components format"}), 400
        
    simulator = CircuitSimulator(num_nodes, components)
    result = simulator.solve()
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
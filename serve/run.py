"""Simple web service for libem"""
from flask import Flask, request, jsonify

import libem

app = Flask(__name__)


@app.route('/match', methods=['POST'])
def match():
    left = request.json.get('e1')
    right = request.json.get('e2')

    if left is None or right is None:
        return jsonify({'error': 'Both e1 and e2 must be provided'}), 400

    try:
        is_match = libem.match(left, right)
        return jsonify({'is_match': is_match})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

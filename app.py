from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Store game state in memory
game_state = {
    'players': {},
    'hider': None,
    'seekers': [],
    'game_over': False
}

# Route for player to join game
@app.route('/join', methods=['POST'])
def join_game():
    player_id = request.json.get('player_id')
    if not player_id:
        return jsonify({'error': 'Player ID required'}), 400
    if player_id in game_state['players']:
        return jsonify({'error': 'Player ID already in use'}), 400
    game_state['players'][player_id] = {'x': 0, 'y': 0, 'is_hider': False, 'is_caught': False}
    return jsonify({'message': 'Player joined game'}), 200

# Route for player to update game state
@app.route('/update', methods=['POST'])
def update_game():
    player_id = request.json.get('player_id')
    x = request.json.get('x')
    y = request.json.get('y')
    if x is not None and y is not None:
        game_state['players'][player_id]['x'] = x
        game_state['players'][player_id]['y'] = y
    return jsonify(game_state), 200
    
@app.route('/details', methods=['POST'])
def get_details():
    return jsonify(game_state), 200

# Route to start the game
@app.route('/start', methods=['POST'])
def start_game():
    if len(game_state['players']) < 2:
        return jsonify({'error': 'Not enough players to start game'}), 400
    game_state['hider'] = random.choice(list(game_state['players'].keys()))
    for player_id in game_state['players']:
        if player_id == game_state['hider']:
            game_state['players'][player_id]['is_hider'] = True
        else:
            game_state['seekers'].append(player_id)
    return jsonify({'message': 'Game started'}), 200

@app.route('/started', methods=['POST'])
def is_started():
    if game_state['hider'] is None:
        return jsonify({'error': 'Game not started'}), 400
    return jsonify({'message': 'Game started'}), 200

@app.route('/done', methods=['POST'])
def is_game_over():
    if game_state['game_over']:
        return jsonify({'message': 'Game ended'}), 200
    return jsonify({'error': 'Game not ended'}), 400

@app.route('/restart', methods=['POST'])
def restart():
    game_state['players'] = {}
    game_state['hider'] = None
    game_state['seekers'] = []
    game_state['game_over'] = False
    return jsonify({'message': 'Game ended'}), 200
    
# Route for seeker to catch hider
@app.route('/catch', methods=['POST'])
def catch_hider():
    seeker_id = request.json.get('seeker_id')
    if not seeker_id:
        return jsonify({'error': 'Seeker ID required'}), 400
    if seeker_id not in game_state['seekers']:
        return jsonify({'error': 'Seeker not found'}), 404
    if game_state['hider'] is None:
        return jsonify({'error': 'Game not started'}), 400
    if game_state['players'][game_state['hider']]['is_caught']:
        return jsonify({'error': 'Hider already caught'}), 400
    game_state['players'][game_state['hider']]['is_caught'] = True
    game_state['game_over'] = True
    return jsonify({'message': 'Game ended'}), 200
    
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)

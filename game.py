from flask import Blueprint, Flask, json, render_template, jsonify, request, session
import random
from models import db,User

game_routes = Blueprint('game', __name__,url_prefix='/game')


# 初始化遊戲
def initialize_game():
    board = [[0] * 4 for _ in range(4)]
    add_random_tile(board)
    add_random_tile(board)
    return {
        'score': 0,
        'board': board
    }

# 添加隨機數字（2 或 4）到空白位置
def add_random_tile(board):
    empty_cells = [(i, j) for i in range(4) for j in range(4) if board[i][j] == 0]
    if empty_cells:
        i, j = random.choice(empty_cells)
        board[i][j] = random.choice([2, 4])

# 移動並合併數字到左側
def move_left(board, score):
    new_board = []
    for row in board:
        new_row = [num for num in row if num != 0]  # 去除零的元素
        if len(new_row) == 0:
            new_board.append([0] * 4)  # 如果新行為空，填充零
            continue
        
        i = 0  # 使用一個指針來遍歷新行
        while i < len(new_row):
            # 如果當前元素和下一個元素相等，則合併
            if i < len(new_row) - 1 and new_row[i] == new_row[i + 1]:
                new_row[i] *= 2  # 合併
                score += new_row[i]  # 更新分數
                new_row.pop(i + 1)  # 移除合併的元素
            i += 1  # 移動到下一個元素

        # 添加剩下的元素到新行，並用零填充到長度為4
        new_board.append(new_row + [0] * (4 - len(new_row)))
    
    return new_board, score

# 向右移動
def move_right(board, score):
    board = [row[::-1] for row in board]

    new_board, score = move_left(board, score)
    
    new_board =  [row[::-1] for row in new_board]
    
    return new_board, score

# 向上移動
def move_up(board, score):
    rotated_board = list(zip(*board))  # 轉置矩陣
    new_board, score = move_left([list(row) for row in rotated_board], score)
    return [list(row) for row in zip(*new_board)], score

# 向下移動
def move_down(board, score):
    rotated_board = list(zip(*board))
    new_board, score = move_right([list(row) for row in rotated_board], score)
    return [list(row) for row in zip(*new_board)], score

# 主頁面
@game_routes.route('/')
def index():
    user_id = session.get('user_id')
    if user_id:
        game_data = load_game_progress(user_id)
        return render_template('gameUser.html', game=game_data)
    else:
        game_data = initialize_game()
        return render_template('gameGuest.html', game=game_data)

# 重置遊戲
@game_routes.route('/reset', methods=['POST'])
def reset_game():
    game = initialize_game()
    return jsonify(game)

# 檢查是否還可以移動
def can_move(board):
    for i in range(4):
        for j in range(4):
            # 檢查空白格
            if board[i][j] == 0:
                return True
            # 檢查橫向和縱向相鄰格是否可以合併
            if (j < 3 and board[i][j] == board[i][j + 1]) or (i < 3 and board[i][j] == board[i + 1][j]):
                return True
    return False


# 更新遊戲狀態 (根據滑動方向)
@game_routes.route('/move', methods=['POST'])
def move():
    data = request.json
    direction = data.get('direction')
    board = data.get('board')
    score = data.get('score')

    # 檢查 board 結構是否為 4x4
    if not isinstance(board, list) or len(board) != 4 or any(len(row) != 4 for row in board):
        print("Invalid board structure:", board)  # 輸出無效的 board 結構
        return jsonify({'error': 'Invalid board structure'}), 400

    try:
        original_board = [row[:] for row in board]  # 儲存原始的 board 用於比較
        if direction == 'left':
            board, score = move_left(board, score)
        elif direction == 'right':
            board, score = move_right(board, score)
        elif direction == 'up':
            board, score = move_up(board, score)
        elif direction == 'down':
            board, score = move_down(board, score)
        else:
            return jsonify({'error': 'Invalid move'}), 400

        if not can_move(board):
            return jsonify({'score': score, 'board': board, 'game_over': True})
        
        # 只有當 board 發生變化時，才添加新的數字
        if board != original_board:
            add_random_tile(board)

        return jsonify({'score': score, 'board': board, 'game_over': False})

    except Exception as e:
        print(f"Error during move: {e}")  # 捕捉並顯示錯誤訊息
        return jsonify({'error': 'An error occurred during move processing'}), 500

@game_routes.route('/save', methods=['POST'])
def save_game_progress():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.json
    score = data.get('score')
    board = data.get('board')
    
    user = User.query.get(user_id)
    if user:
        # 將遊戲數據轉為 JSON 字串後儲存
        user.game_data = json.dumps({'score': score, 'board': board})
        db.session.commit()
        return jsonify({'message': 'Game progress saved successfully'}), 200

    return jsonify({'error': 'User not found'}), 404

def load_game_progress(user_id):
    user = User.query.get(user_id)
    if user and user.game_data:
        # 將 game_data 解析為字典
        game_data = json.loads(user.game_data)
        
        # 提取遊戲數據
        result = {
            'score': game_data['score'],
            'board': game_data['board'],
        }
        
        # 清空紀錄
        user.game_data = None
        db.session.commit()
        return result

    return initialize_game()
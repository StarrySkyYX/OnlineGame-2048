document.addEventListener('keydown', (event) => {
    let direction;
    switch (event.key) {
        case 'ArrowLeft':
            direction = 'left';
            break;
        case 'ArrowRight':
            direction = 'right';
            break;
        case 'ArrowUp':
            direction = 'up';
            break;
        case 'ArrowDown':
            direction = 'down';
            break;
        default:
            return; // 如果不是方向鍵，直接返回
    }
    move(direction); // 呼叫移動函數，傳入方向
});

function move(direction) {
    const board = [];
    const cells = document.querySelectorAll('.cell');
    for (let i = 0; i < 4; i++) {
        const row = [];
        for (let j = 0; j < 4; j++) {
            row.push(Number(cells[i * 4 + j].textContent) || 0);
        }
        board.push(row);
    }
    
    const score = Number(document.getElementById('score').textContent);
    
    fetch('/game/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ direction, board, score }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Server error:', data.error);
        } else {
            updateBoard(data.board, data.score);
        }
        if(data.game_over){
            alert("遊戲結束！"); 
        }
    })
    .catch(error => console.error('Fetch error:', error));
}

function updateBoard(board, score) {
    const cells = document.querySelectorAll('.cell');
    cells.forEach((cell, index) => {
        const row = Math.floor(index / 4);
        const col = index % 4;
        cell.textContent = board[row][col] === 0 ? '' : board[row][col];
    });
    document.getElementById('score').textContent = score;
}


document.getElementById('reset-btn').addEventListener('click', function() {
    // 發送請求到重置遊戲的 API
    fetch('/game/reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // 更新遊戲區域的內容
        updateBoard(data.board, 0);
    })
    .catch(error => {
        console.error('Error resetting game:', error);
    });
});

document.getElementById('save-btn').addEventListener('click', function() {
    const board = [];
    const cells = document.querySelectorAll('.cell');
    for (let i = 0; i < 4; i++) {
        const row = [];
        for (let j = 0; j < 4; j++) {
            row.push(Number(cells[i * 4 + j].textContent) || 0);
        }
        board.push(row);
    }
    
    const score = Number(document.getElementById('score').textContent);

    const gameData = {
        score: score,  
        board: board   
    };

    fetch('/game/save', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(gameData)  // 傳送 JSON 格式的數據
    })
    .then(response => response.json())
    .then(data => {
        console.log('Save response:', data);
    })
    .catch(error => {
        console.error('Error saving game:', error);
    });
});


document.getElementById('logout-btn').addEventListener('click', function() {
    const board = [];
    const cells = document.querySelectorAll('.cell');
    for (let i = 0; i < 4; i++) {
        const row = [];
        for (let j = 0; j < 4; j++) {
            row.push(Number(cells[i * 4 + j].textContent) || 0);
        }
        board.push(row);
    }
    
    const score = Number(document.getElementById('score').textContent);

    const gameData = {
        score: score,  
        board: board   
    };

    fetch('/game/save', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(gameData)
    })
    .then(response => {
        if (response.ok) {
            return fetch('/user/logout');
        } else {
            throw new Error('Game save failed');
        }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;  // 重定向到登出后页面
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

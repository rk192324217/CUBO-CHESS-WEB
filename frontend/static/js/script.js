$(document).ready(function() {
    const userId = "user_" + Math.random().toString(36).substr(2, 9);
    const game = new Chess();
    let isBotThinking = false;
    const moveSound = new Audio('/static/sounds/move.mp3'); // Ensure this file exists

    const board = Chessboard('board', {
        position: 'start',
        draggable: true,
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
        onDragStart: onDragStart,
        onDrop: onDrop
    });

    function onDragStart(source, piece) {
        return !game.game_over() &&
               !isBotThinking &&
               piece.startsWith('w') &&
               game.turn() === 'w';
    }

    function onDrop(source, target) {
        if (isBotThinking) return 'snapback';

        const move = game.move({
            from: source,
            to: target,
            promotion: 'q'
        });

        if (move === null) return 'snapback';

        board.position(game.fen());
        highlightMove(source, target);
        moveSound.play();
        addMoveToHistory(move, 'You');
        updateCapturedPieces();

        if (game.game_over()) {
            setTimeout(() => alert(getGameResult()), 100);
            return;
        }

        makeBotMove(move.from + move.to);
    }

    async function makeBotMove(userMove) {
        isBotThinking = true;
        $('#board').addClass('thinking');

        try {
            const difficulty = $('#difficulty').val();
            const response = await $.ajax({
                url: '/move',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    fen: game.fen(),
                    difficulty: difficulty,
                    user_id: userId,
                    move: userMove
                })
            });

            console.log("Bot move received:", response.move);

            const move = game.move({
                from: response.move.substring(0, 2),
                to: response.move.substring(2, 4),
                promotion: 'q'
            });

            board.position(game.fen());
            highlightMove(response.move.substring(0, 2), response.move.substring(2, 4));
            moveSound.play();
            console.log("Updated board FEN after bot move:", game.fen());
            addMoveToHistory(move, 'Bot');
            updateCapturedPieces();

            if (game.game_over()) {
                setTimeout(() => alert(getGameResult()), 100);
            }
        } catch (error) {
            console.error("Error:", error);
        } finally {
            isBotThinking = false;
            $('#board').removeClass('thinking');
        }
    }

    function addMoveToHistory(move, player) {
        const moveNum = Math.ceil(game.history().length / 2);
        let moveText = move.san;

        if (player === 'You' && game.turn() === 'b') {
            moveText = `${moveNum}. ${moveText}`;
        } else if (player === 'Bot') {
            moveText = `${moveNum}... ${moveText}`;
        }

        $('#move-history').append(
            `<div class="move ${player.toLowerCase()}">${moveText}</div>`
        );
        $('#move-history').scrollTop($('#move-history')[0].scrollHeight);
    }

    function getGameResult() {
        if (game.in_checkmate()) {
            return game.turn() === 'w' ? "Checkmate! You lost!" : "Checkmate! You won!";
        }
        if (game.in_draw()) {
            return "Game drawn!";
        }
        return "Game over!";
    }

    $('#reset').click(function() {
        if (isBotThinking) return;
        game.reset();
        board.start();
        $('#move-history').empty();
        $('.highlight-square').removeClass('highlight-square');
        $('#captured-white').empty();
        $('#captured-black').empty();
    });

    function highlightMove(from, to) {
        $('.highlight-square').removeClass('highlight-square');
        $(`#board .square-${from}`).addClass('highlight-square');
        $(`#board .square-${to}`).addClass('highlight-square');
    }

    function updateCapturedPieces() {
        const history = game.history({ verbose: true });
        const whiteCaptured = [];
        const blackCaptured = [];

        const pieceMap = {
            p: '♟', n: '♞', b: '♝', r: '♜', q: '♛', k: '♚'
        };

        for (let move of history) {
            if (move.captured) {
                if (move.color === 'w') {
                    blackCaptured.push(pieceMap[move.captured]);
                } else {
                    whiteCaptured.push(pieceMap[move.captured]);
                }
            }
        }

        $('#captured-white').html(whiteCaptured.join(' '));
        $('#captured-black').html(blackCaptured.join(' '));
    }
});

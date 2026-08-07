import streamlit as st

st.set_page_config(page_title="Mini Futebol Multiplayer", page_icon="⚽", layout="centered")

st.title("⚽ Mini Futebol Multiplayer Online")
st.write("Crie sua sala, escolha o time e chame a galera para jogar pelo celular ou PC!")

# Entrada para o código da sala
sala = st.text_input("Código da Sala:", value="sala-principal-1")

html_futebol = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ background: #111; color: white; text-align: center; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
        #hud {{ font-size: 18px; font-weight: bold; margin: 5px; }}
        canvas {{ background: #2e7d32; border: 4px solid white; display: block; margin: 0 auto; box-shadow: 0 0 15px rgba(0,0,0,0.5); max-width: 100%; }}
        .controls {{ display: flex; justify-content: center; gap: 10px; margin-top: 10px; }}
        button {{ padding: 10px 20px; font-size: 16px; cursor: pointer; background: #333; color: white; border: 2px solid white; border-radius: 5px; }}
        button:active {{ background: #555; }}
        .dpad {{ display: grid; grid-template-columns: repeat(3, 50px); grid-gap: 5px; justify-content: center; margin-top: 10px; }}
        .dpad button {{ width: 50px; height: 50px; padding: 0; font-size: 20px; }}
    </style>
</head>
<body>
    <div id="hud">
        🔵 <span id="scoreAzul">0</span> | <span id="tempo">TEMPO</span> | <span id="scoreAmarelo">0</span> 🟡
    </div>
    
    <canvas id="campo" width="600" height="300"></canvas>

    <div class="controls">
        <button onclick="escolherTime('azul')">Entrar Time Azul</button>
        <button onclick="escolherTime('amarelo')">Entrar Time Amarelo</button>
    </div>

    <!-- Controles Mobile / D-Pad -->
    <div class="dpad">
        <div></div>
        <button ontouchstart="press('w')" ontouchend="release('w')" onmousedown="press('w')" onmouseup="release('w')">⬆️</button>
        <div></div>
        <button ontouchstart="press('a')" ontouchend="release('a')" onmousedown="press('a')" onmouseup="release('a')">⬅️</button>
        <button ontouchstart="press('s')" ontouchend="release('s')" onmousedown="press('s')" onmouseup="release('s')">⬇️</button>
        <button ontouchstart="press('d')" ontouchend="release('d')" onmousedown="press('d')" onmouseup="release('d')">➡️</button>
    </div>

    <!-- Importa o Socket.io para comunicação em tempo real -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.js"></script>
    <script>
        const socket = io("https://serversocket-exemplo.onrender.com"); // Servidor público de teste ou local
        const canvas = document.getElementById('campo');
        const ctx = canvas.getContext('2d');

        const salaId = "{sala}";
        let meuTime = "azul";
        let myData = {{ x: 150, y: 150, vx: 0, vy: 0, radius: 15, color: '#2196f3' }};
        let ball = {{ x: 300, y: 150, radius: 10, vx: 0, vy: 0 }};
        let scores = {{ azul: 0, amarelo: 0 }};
        let players = {{}};
        let keys = {{}};

        socket.emit('entrarSala', {{ sala: salaId, time: meuTime }});

        function escolherTime(time) {{
            meuTime = time;
            myData.color = (time === 'azul') ? '#2196f3' : '#ffeb3b';
            myData.x = (time === 'azul') ? 150 : 450;
            socket.emit('mudarTime', {{ sala: salaId, time: time }});
        }}

        window.addEventListener('keydown', (e) => keys[e.key.toLowerCase()] = true);
        window.addEventListener('keyup', (e) => keys[e.key.toLowerCase()] = false);

        function press(k) {{ keys[k] = true; }}
        function release(k) {{ keys[k] = false; }}

        function update() {{
            let speed = 4;
            if (keys['arrowup'] || keys['w']) myData.y -= speed;
            if (keys['arrowdown'] || keys['s']) myData.y += speed;
            if (keys['arrowleft'] || keys['a']) myData.x -= speed;
            if (keys['arrowright'] || keys['d']) myData.x += speed;

            myData.x = Math.max(myData.radius, Math.min(canvas.width - myData.radius, myData.x));
            myData.y = Math.max(myData.radius, Math.min(canvas.height - myData.radius, myData.y));

            socket.emit('atualizarPosicao', {{ sala: salaId, player: myData }});
        }}

        socket.on('estadoAtual', (state) => {{
            if(state.ball) ball = state.ball;
            if(state.scores) {{
                scores = state.scores;
                document.getElementById('scoreAzul').innerText = scores.azul;
                document.getElementById('scoreAmarelo').innerText = scores.amarelo;
            }}
            if(state.players) players = state.players;
        }});

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Linhas de campo e gols
            ctx.strokeStyle = "white";
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(canvas.width / 2, canvas.height / 2, 50, 0, Math.PI * 2);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(canvas.width / 2, 0);
            ctx.lineTo(canvas.width / 2, canvas.height);
            ctx.stroke();

            // Gols nas pontas
            ctx.strokeRect(0, 100, 10, 100);
            ctx.strokeRect(canvas.width - 10, 100, 10, 100);

            // Desenha a bola
            ctx.fillStyle = "white";
            ctx.beginPath();
            ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
            ctx.fill();

            // Desenha todos os jogadores conectados
            for (let id in players) {{
                let p = players[id];
                ctx.fillStyle = p.color || '#fff';
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = "#000";
                ctx.stroke();
            }}
        }}

        function loop() {{
            update();
            draw();
            requestAnimationFrame(loop);
        }}

        loop();
    </script>
</body>
</html>
"""

st.components.v1.html(html_futebol, height=520)

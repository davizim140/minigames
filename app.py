import streamlit as st

st.set_page_config(page_title="Arcade de Minijogos", page_icon="🎮", layout="centered")

st.title("🎮 Fliperama da Família")
st.write("Escolha um minijogo abaixo e divirta-se direto pelo navegador!")

# Abas para separar os jogos
aba1, aba2 = st.tabs(["⚽ Mini Futebol Interativo", "🧠 Quiz Rápido"])

with aba1:
    st.subheader("Mini Futebol 2D")
    st.write("Use as setas do teclado ou W,A,S,D para controlar o jogador e chutar a bola para o gol!")

    # Código HTML/JS do jogo embutido diretamente no Streamlit
    html_futebol = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            body { background: #111; color: white; text-align: center; font-family: Arial, sans-serif; margin: 0; padding: 0; }
            canvas { background: #2e7d32; border: 4px solid white; display: block; margin: 10px auto; box-shadow: 0 0 15px rgba(0,0,0,0.5); }
        </style>
    </head>
    <body>
        <canvas id="campo" width="600" height="300"></canvas>
        <script>
            const canvas = document.getElementById('campo');
            const ctx = canvas.getContext('2d');

            let player = { x: 150, y: 150, radius: 15, speed: 4 };
            let ball = { x: 300, y: 150, radius: 10, vx: 0, vy: 0 };
            let keys = {};

            window.addEventListener('keydown', (e) => keys[e.key.toLowerCase()] = true);
            window.addEventListener('keyup', (e) => keys[e.key.toLowerCase()] = false);

            function update() {
                if (keys['arrowup'] || keys['w']) player.y -= player.speed;
                if (keys['arrowdown'] || keys['s']) player.y += player.speed;
                if (keys['arrowleft'] || keys['a']) player.x -= player.speed;
                if (keys['arrowright'] || keys['d']) player.x += player.speed;

                // Limites do campo
                player.x = Math.max(player.radius, Math.min(canvas.width - player.radius, player.x));
                player.y = Math.max(player.radius, Math.min(canvas.height - player.radius, player.y));

                // Movimento da bola
                ball.x += ball.vx;
                ball.y += ball.vy;
                ball.vx *= 0.98;
                ball.vy *= 0.98;

                // Paredes
                if (ball.x < ball.radius || ball.x > canvas.width - ball.radius) ball.vx *= -1;
                if (ball.y < ball.radius || ball.y > canvas.height - ball.radius) ball.vy *= -1;

                // Colisão Jogador-Bola
                let distX = ball.x - player.x;
                let distY = ball.y - player.y;
                let distance = Math.sqrt(distX * distX + distY * distY);

                if (distance < player.radius + ball.radius) {
                    ball.vx = distX * 0.25;
                    ball.vy = distY * 0.25;
                }
            }

            function draw() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Meio de campo
                ctx.strokeStyle = "white";
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.arc(canvas.width / 2, canvas.height / 2, 50, 0, Math.PI * 2);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(canvas.width / 2, 0);
                ctx.lineTo(canvas.width / 2, canvas.height);
                ctx.stroke();

                // Bola
                ctx.fillStyle = "white";
                ctx.beginPath();
                ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
                ctx.fill();

                // Jogador
                ctx.fillStyle = "#ffeb3b";
                ctx.beginPath();
                ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = "#000";
                ctx.stroke();
            }

            function loop() {
                update();
                draw();
                requestAnimationFrame(loop);
            }

            loop();
        </script>
    </body>
    </html>
    """
    
    # Renderiza o jogo de futebol na tela do Streamlit com altura ajustada
    st.components.v1.html(html_futebol, height=350)

with aba2:
    st.subheader("Quiz Rápido de Cultura Pop e Jogos")
    
    pergunta = "Qual destes jogos o criador deste site mais joga/conhece bem?"
    opcoes = ["Dark Souls 2", "Tetris clássico", "Campo Minado", "Pac-Man"]
    
    resposta_usuario = st.radio(pergunta, opcoes, key="quiz_geral")
    
    if st.button("Enviar Resposta do Quiz"):
        if resposta_usuario == "Dark Souls 2":
            st.balloons()
            st.success("Exato! Mestre dos games difíceis.")
        else:
            st.error("Errou! Tente de novo.")

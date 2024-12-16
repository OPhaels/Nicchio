from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from plataforma.db import get_db_connection
from plataforma import db  # Importando o db do init.py para SQLAlchemy
from functools import wraps
import os
from werkzeug.utils import secure_filename

# Função de proteção de rota, exige login
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_name' not in session:
            return redirect(url_for('login'))  # Redireciona para a página de login
        return f(*args, **kwargs)
    return wrap

# Função para registrar as rotas no app
def register_routes(app):

    #1 Rota de login
    @app.route('/', methods=['GET', 'POST'])
    def login():
        if 'user_name' in session:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            email = request.form['email'].strip().lower()
            senha = request.form['senha'].strip()

            conn = get_db_connection()
            if conn is None:
                flash("Erro de conexão com o banco de dados", "error")
                return redirect(url_for('login'))

            cur = conn.cursor()

            try:
                cur.execute("SELECT id, nome, email, senha FROM registros.cadastros WHERE LOWER(email) = %s", (email,))
                user = cur.fetchone()

                if user:
                    if user[3] == senha:
                        session['user_name'] = user[1]
                        return redirect(url_for('dashboard'))
                    else:
                        flash("Senha incorreta!", "error")
                else:
                    flash("E-mail não encontrado!", "error")
            except Exception as e:
                flash(f"Erro ao realizar login: {str(e)}", "error")

            cur.close()
            conn.close()
            return redirect(url_for('login'))

        return render_template('login.html')

    #2 Rota de cadastro
    @app.route('/cadastro/', methods=['GET', 'POST'])
    def cadastro():
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email'].strip().lower()
            senha = request.form['senha']
            confirmar_senha = request.form['confirmar_senha']

            if senha != confirmar_senha:
                flash('As senhas não coincidem!', 'error')
                return redirect(url_for('cadastro'))

            conn = get_db_connection()
            if conn is None:
                flash("Erro de conexão com o banco de dados", "error")
                return redirect(url_for('cadastro'))

            cur = conn.cursor()

            try:
                cur.execute("SELECT id FROM registros.cadastros WHERE LOWER(email) = %s", (email,))
                user = cur.fetchone()

                if user:
                    flash('E-mail já cadastrado. Tente outro e-mail.', 'error')
                    return redirect(url_for('cadastro'))

                cur.execute(
                    "INSERT INTO registros.cadastros (nome, email, senha) VALUES (%s, %s, %s)",
                    (nome, email, senha)
                )
                conn.commit()
                flash('Cadastro realizado com sucesso!', 'success')
                return redirect(url_for('login'))

            except Exception as e:
                flash(f"Erro ao cadastrar: {str(e)}", 'error')

            finally:
                cur.close()
                conn.close()

        return render_template('cadastro.html')

    #3 Rota de dashboard
    @app.route('/dashboard/')
    @login_required
    def dashboard():
        flash(f"LOG: {session['user_name'].upper()}", 'success')
        return render_template("dashboard.html")

    #4 Rota de perfil
    @app.route('/perfil/')
    def profile():
        flash(f"LOG: {session.get('user_name', 'Usuario').upper()}", 'success')
        return render_template("profile.html")
    
    #5 Rota de upload de foto de perfil
    @app.route('/upload_profile_picture', methods=['POST'])
    def upload_profile_picture():
        if 'profile_picture' not in request.files:
            flash('Nenhuma imagem selecionada', 'error')
            return redirect(url_for('profile'))

        file = request.files['profile_picture']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            session['profile_picture'] = f'imagens/perfis/{filename}'

            flash('Foto de perfil atualizada com sucesso!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Tipo de arquivo não permitido. Por favor, envie uma imagem.', 'error')
            return redirect(url_for('profile'))

    #6 Rota de logout
    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        session.pop('user_name', None)
        flash("Você foi desconectado com sucesso!", "success")
        return redirect(url_for('login'))

    #7 Rota de buscar
    @app.route('/buscar', methods=['POST'])
    def buscar():
        try:
            data = request.get_json()
            print(f"Dados recebidos: {data}")

            saida = data.get('saida')
            destino = data.get('destino')
            sacos = data.get('sacos')

            if sacos not in ['320', '360', '440']:
                return jsonify({"error": "Quantidade de sacos inválida! Escolha entre 320, 360 ou 440."}), 400

            tabela = ''
            if saida == 'Colatina' and destino == 'Rio de Janeiro':
                tabela = 'colrio'
            elif saida == 'Colatina' and destino == 'Vitória':
                tabela = 'colvit'
            elif saida == 'Minas Gerais' and destino == 'Rio de Janeiro':
                tabela = 'minrio'
            elif saida == 'Minas Gerais' and destino == 'Vitória':
                tabela = 'minvit'
            else:
                return jsonify({"error": "Destino ou saída inválidos!"}), 400

            conn = get_db_connection()
            if conn is None:
                return jsonify({"error": "Erro de conexão com o banco de dados"}), 500

            cur = conn.cursor()

            try:
                query = f"""
                SELECT item, qnt, thc, certificado, fumigacao, ccc, cecafe, ovacao, 
                    despacho, taxa_porto_isps, taxa_bl, lacre, retirada_container, 
                    taxa_scanner, taxa_elf, forracao, pesagem, pre_steking, envio_dhl, 
                    despacho_banc, sacaria
                FROM registros.{tabela}
                WHERE qnt = %s
                """
                cur.execute(query, (sacos,))
                results = cur.fetchall()

                if not results:
                    return jsonify({"message": "Nenhum resultado encontrado."}), 404

                data = [
                    {
                        "item": row[0],
                        "qnt": row[1],
                        "thc": row[2],
                        "certificado": row[3],
                        "fumigacao": row[4],
                        "ccc": row[5],
                        "cecafe": row[6],
                        "ovacao": row[7],
                        "despacho": row[8],
                        "taxa_porto_isps": row[9],
                        "taxa_bl": row[10],
                        "lacre": row[11],
                        "retirada_container": row[12],
                        "taxa_scanner": row[13],
                        "taxa_elf": row[14],
                        "forracao": row[15],
                        "pesagem": row[16],
                        "pre_steking": row[17],
                        "envio_dhl": row[18],
                        "despacho_banc": row[19],
                        "sacaria": row[20]
                    }
                    for row in results
                ]
                return jsonify(data)

            except Exception as e:
                print(f"Erro ao executar a consulta: {e}")
                return jsonify({"error": str(e)}), 500

            finally:
                cur.close()
                conn.close()

        except Exception as e:
            print(f"Erro na requisição: {e}")
            return jsonify({"error": str(e)}), 500

    #8 Rota de atualização
    @app.route('/atualizar', methods=['POST'])
    @login_required
    def atualizar():
        try:
            data = request.get_json()
            print(f"Dados recebidos: {data}")

            saida = data.get('saida')
            destino = data.get('destino')
            item_id = data.get('itemId')
            campo = data.get('campo')
            novo_valor = data.get('novoValor')

            if not (saida and destino and item_id and campo and novo_valor):
                return jsonify({"error": "Todos os campos devem ser preenchidos."}), 400

            conn = get_db_connection()
            cur = conn.cursor()

            campos_validos = [
                'qnt', 'thc', 'certificado', 'fumigacao', 'ccc', 'cecafe', 'ovacao',
                'despacho', 'taxa_porto_isps', 'taxa_bl', 'lacre', 'retirada_container',
                'taxa_scanner', 'taxa_elf', 'forracao', 'pesagem', 'pre_steking',
                'envio_dhl', 'despacho_banc', 'sacaria'
            ]

            if campo not in campos_validos:
                return jsonify({"error": "Campo inválido."}), 400

            tabela = ''
            if saida == 'Colatina' and destino == 'Rio de Janeiro':
                tabela = 'colrio'
            elif saida == 'Colatina' and destino == 'Vitória':
                tabela = 'colvit'
            elif saida == 'Minas Gerais' and destino == 'Rio de Janeiro':
                tabela = 'minrio'
            elif saida == 'Minas Gerais' and destino == 'Vitória':
                tabela = 'minvit'
            else:
                return jsonify({"error": "Destino ou saída inválidos!"}), 400

            query = f"""
                UPDATE registros.{tabela}
                SET {campo} = %s
                WHERE item = %s
            """
            cur.execute(query, (novo_valor, item_id))
            conn.commit()

            if cur.rowcount > 0:
                return jsonify({"message": f"Valor de {campo} atualizado com sucesso!"}), 200
            else:
                return jsonify({"error": "Nenhuma atualização realizada. Verifique os dados."}), 404

        except Exception as e:
            print(f"Erro ao atualizar: {e}")
            return jsonify({"error": f"Erro ao atualizar: {str(e)}"}), 500
        finally:
            cur.close()
            conn.close()

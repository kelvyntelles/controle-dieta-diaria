from flask import Flask, request, jsonify
from models.user import User
from models.refeicao import Refeicao
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from database import db
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin123@127.0.0.1:3306/controle_dieta'

login_manager = LoginManager()
db.init_app(app)

login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({'message': 'Login bem-sucedido'})

    return jsonify({'message': 'Credenciais inválidas'}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout bem-sucedido'})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_password, role='user')
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Usuário criado com sucesso'})

    return jsonify({'message': 'Dados inválidos'}), 400

@app.route('/user/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = User.query.get(user_id)

    if user:
        return jsonify({'id': user.id, 'username': user.username})
    
    return jsonify({'message': 'Usuário não encontrado'}), 404

@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.json
    user = User.query.get(user_id)

    if user_id != current_user.id and current_user.role == 'user':
        return jsonify({'message': 'Operação não permitida'}), 403

    if user and data.get('password'):
        user.password = data.get('password')
        db.session.commit()
        return jsonify({'message': f'Usuário {user_id} atualizado com sucesso'})
    
    return jsonify({'message': 'Usuário não encontrado'}), 404

@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if current_user.role != 'admin':
        return jsonify({'message': 'Operação não permitida'}), 403

    if user_id == current_user.id:
        return jsonify({'message': 'Você não pode deletar seu próprio usuário'}), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': f'Usuário {user_id} deletado com sucesso'})

    return jsonify({'message': 'Usuário não encontrado'}), 404

@app.route('/refeicao', methods=['POST'])
@login_required
def create_refeicao():
    data = request.json
    nome = data.get('nome')
    descricao = data.get('descricao')
    data_e_hora = datetime.now()
    e_dieta = data.get('e_dieta')

    if nome and e_dieta is not None:
        refeicao = Refeicao(nome=nome, descricao=descricao, data_e_hora=data_e_hora, e_dieta=e_dieta, user_id=current_user.id)
        db.session.add(refeicao)
        db.session.commit()
        return jsonify({'message': 'Refeição criada com sucesso'})

    return jsonify({'message': 'Dados inválidos'}), 400

@app.route('/refeicao/<int:refeicao_id>', methods=['GET'])
@login_required
def get_refeicao(refeicao_id):
    refeicao = Refeicao.query.get(refeicao_id)

    if refeicao and refeicao.user_id == current_user.id:
        return jsonify({
            'id': refeicao.id,
            'nome': refeicao.nome,
            'descricao': refeicao.descricao,
            'data_e_hora': refeicao.data_e_hora,
            'e_dieta': refeicao.e_dieta
        })
    
    return jsonify({'message': 'Refeição não encontrada'}), 404

@app.route('/refeicao/<int:refeicao_id>', methods=['PUT'])
@login_required
def update_refeicao(refeicao_id):
    data = request.json
    refeicao = Refeicao.query.get(refeicao_id)

    if refeicao and refeicao.user_id == current_user.id:
        refeicao.nome = data.get('nome', refeicao.nome)
        refeicao.descricao = data.get('descricao', refeicao.descricao)
        refeicao.e_dieta = data.get('e_dieta', refeicao.e_dieta)
        db.session.commit()
        return jsonify({'message': f'Refeição {refeicao_id} atualizada com sucesso'})
    
    return jsonify({'message': 'Refeição não encontrada'}), 404

@app.route('/refeicao/<int:refeicao_id>', methods=['DELETE'])
@login_required
def delete_refeicao(refeicao_id):
    refeicao = Refeicao.query.get(refeicao_id)

    if refeicao and refeicao.user_id == current_user.id:
        db.session.delete(refeicao)
        db.session.commit()
        return jsonify({'message': f'Refeição {refeicao_id} deletada com sucesso'})

    return jsonify({'message': 'Refeição não encontrada'}), 404

if __name__ == '__main__':
    app.run(debug=True)

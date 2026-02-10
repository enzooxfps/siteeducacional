import streamlit as st
import json
import os
import bcrypt
import random
import string
import time
import re
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Sistema Acadêmico")

# --- Configuração de Caminhos Absolutos ---
# Garante que os arquivos fiquem na mesma pasta do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_USER_FILE = os.path.join(BASE_DIR, "dados_usuarios.json")
DATA_ASSESSMENT_FILE = os.path.join(BASE_DIR, "dados_avaliacoes.json")
DATA_GRADE_FILE = os.path.join(BASE_DIR, "dados_registros.json")
DATA_CLASS_FILE = os.path.join(BASE_DIR, "dados_grupos.json")

# Chave secreta para criar conta de Professor
INSTRUCTOR_SECRET_KEY = "PROFE123"

# --- Ferramentas de Administração (Sidebar) ---
def render_debug_sidebar():
    """Barra lateral para baixar e visualizar os arquivos JSON."""
    with st.sidebar.expander("📂 Gerenciador de Arquivos (Admin)", expanded=True):
        st.caption(f"📍 Local de Salvamento:\n`{BASE_DIR}`")
        
        st.markdown("---")
        st.write("**Baixar Arquivos Atuais:**")
        
        files = {
            "Usuários (JSON)": DATA_USER_FILE,
            "Notas (JSON)": DATA_GRADE_FILE,
            "Avaliações (JSON)": DATA_ASSESSMENT_FILE,
            "Turmas (JSON)": DATA_CLASS_FILE
        }
        
        for label, filepath in files.items():
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Baixar {label}",
                        data=f,
                        file_name=os.path.basename(filepath),
                        mime="application/json",
                        key=f"btn_{label}"
                    )
            else:
                st.warning(f"{label} ainda não existe.")

        st.markdown("---")
        st.write("**Visualizador Rápido:**")
        selected_file = st.selectbox("Escolha o arquivo:", list(files.keys()))
        target_path = files[selected_file]
        
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding='utf-8') as f:
                    st.json(json.load(f), expanded=False)
            except:
                st.error("Erro ao ler arquivo.")

# --- Inicialização de Arquivos ---
def init_files():
    files = [DATA_USER_FILE, DATA_ASSESSMENT_FILE, DATA_GRADE_FILE, DATA_CLASS_FILE]
    for data_file in files:
        if not os.path.exists(data_file):
            with open(data_file, "w", encoding='utf-8') as f:
                json.dump({}, f)
        else:
            try:
                with open(data_file, "r", encoding='utf-8') as f:
                    content = f.read()
                    if not content: raise ValueError
                    json.loads(content)
            except:
                with open(data_file, "w", encoding='utf-8') as f:
                    json.dump({}, f)

# --- Geração de Dados Iniciais ---
def populate_default_db():
    try:
        with open(DATA_CLASS_FILE, 'r', encoding='utf-8') as f:
            classes = json.load(f)
    except: classes = {}
    
    if "Turma Exemplo" not in classes:
        classes["Turma Exemplo"] = [] 
        with open(DATA_CLASS_FILE, 'w', encoding='utf-8') as f:
            json.dump(classes, f, indent=4)

    try:
        with open(DATA_ASSESSMENT_FILE, 'r', encoding='utf-8') as f:
            assessments = json.load(f)
    except: assessments = {}

    default_assessments = {
        "Matemática - Básico": {
            "assigned_class": "Turma Exemplo",
            "instructor_id": "SYSTEM",
            "questions": {
                "1": {"text": "Quanto é 15 + 27?", "A": "32", "B": "42", "C": "40", "D": "35", "E": "50", "correct": "B"},
                "2": {"text": "Qual a raiz quadrada de 144?", "A": "10", "B": "11", "C": "12", "D": "13", "E": "14", "correct": "C"}
            }
        },
        "Português - Gramática": {
            "assigned_class": "Turma Exemplo",
            "instructor_id": "SYSTEM",
            "questions": {
                "1": {"text": "Qual é o sujeito da frase: 'O gato dormiu no sofá'?", "A": "No sofá", "B": "Dormiu", "C": "O gato", "D": "Gato", "E": "O", "correct": "C"},
                "2": {"text": "Qual destas palavras está escrita corretamente?", "A": "Exceção", "B": "Eceção", "C": "Ezceção", "D": "Ecceção", "E": "Exseção", "correct": "A"}
            }
        },
        "História - Geral": {
            "assigned_class": "Turma Exemplo",
            "instructor_id": "SYSTEM",
            "questions": {
                "1": {"text": "Quem descobriu o Brasil?", "A": "Cristóvão Colombo", "B": "Pedro Álvares Cabral", "C": "Vasco da Gama", "D": "Dom Pedro I", "E": "Tiradentes", "correct": "B"},
                "2": {"text": "Em que ano a Segunda Guerra Mundial terminou?", "A": "1939", "B": "1940", "C": "1942", "D": "1945", "E": "1950", "correct": "D"}
            }
        },
        "Geografia - Capitais": {
            "assigned_class": "Turma Exemplo",
            "instructor_id": "SYSTEM",
            "questions": {
                "1": {"text": "Qual a capital da França?", "A": "Londres", "B": "Berlim", "C": "Madrid", "D": "Paris", "E": "Roma", "correct": "D"},
                "2": {"text": "Onde fica a Amazônia?", "A": "África", "B": "Europa", "C": "América do Sul", "D": "Ásia", "E": "Oceania", "correct": "C"}
            }
        },
        "Ciências - Corpo Humano": {
            "assigned_class": "Turma Exemplo",
            "instructor_id": "SYSTEM",
            "questions": {
                "1": {"text": "Qual o maior órgão do corpo humano?", "A": "Fígado", "B": "Coração", "C": "Pele", "D": "Pulmão", "E": "Cérebro", "correct": "C"},
                "2": {"text": "Quantos ossos tem um adulto (aprox.)?", "A": "100", "B": "150", "C": "206", "D": "300", "E": "500", "correct": "C"}
            }
        },
        "Física - Conceitos": {
            "assigned_class": "Turma Exemplo",
            "instructor_id": "SYSTEM",
            "questions": {
                "1": {"text": "Qual é a fórmula da velocidade média?", "A": "V = d/t", "B": "V = d*t", "C": "V = t/d", "D": "V = m*a", "E": "V = m/v", "correct": "A"},
                "2": {"text": "A gravidade puxa os objetos para...", "A": "Cima", "B": "Lado", "C": "Centro da Terra", "D": "Espaço", "E": "Nenhuma das anteriores", "correct": "C"}
            }
        },
        "Química - Elementos": {
            "assigned_class": "Turma Exemplo",
            "instructor_id": "SYSTEM",
            "questions": {
                "1": {"text": "Qual o símbolo químico da água?", "A": "CO2", "B": "H2O", "C": "O2", "D": "NaCl", "E": "H2", "correct": "B"},
                "2": {"text": "O que é 'Au' na tabela periódica?", "A": "Prata", "B": "Cobre", "C": "Alumínio", "D": "Ouro", "E": "Argônio", "correct": "D"}
            }
        },
        "Biologia - Seres Vivos": {
            "assigned_class": "Turma Exemplo",
            "instructor_id": "SYSTEM",
            "questions": {
                "1": {"text": "O que as plantas usam para fazer fotossíntese?", "A": "Apenas água", "B": "Apenas terra", "C": "Luz solar, água e CO2", "D": "Vento", "E": "Fogo", "correct": "C"},
                "2": {"text": "Qual destes é um mamífero?", "A": "Tubarão", "B": "Águia", "C": "Baleia", "D": "Sapo", "E": "Cobra", "correct": "C"}
            }
        },
        "Inglês - Básico": {
            "assigned_class": "Turma Exemplo",
            "instructor_id": "SYSTEM",
            "questions": {
                "1": {"text": "Como se diz 'Vermelho' em inglês?", "A": "Blue", "B": "Green", "C": "Yellow", "D": "Red", "E": "Black", "correct": "D"},
                "2": {"text": "Traduza: 'The book is on the table'.", "A": "O livro está sob a mesa", "B": "O livro está sobre a mesa", "C": "O livro está na cadeira", "D": "A mesa está no livro", "E": "O caderno é azul", "correct": "B"}
            }
        },
        "Artes - Cores e Formas": {
            "assigned_class": "Turma Exemplo",
            "instructor_id": "SYSTEM",
            "questions": {
                "1": {"text": "Quais são as cores primárias?", "A": "Verde, Roxo, Laranja", "B": "Preto e Branco", "C": "Azul, Amarelo, Vermelho", "D": "Rosa, Cinza, Marrom", "E": "Ciano, Magenta, Amarelo", "correct": "C"},
                "2": {"text": "Quem pintou a Mona Lisa?", "A": "Van Gogh", "B": "Picasso", "C": "Leonardo da Vinci", "D": "Michelangelo", "E": "Donatello", "correct": "C"}
            }
        }
    }

    updated = False
    for name, data in default_assessments.items():
        if name not in assessments:
            assessments[name] = data
            updated = True
    
    if updated:
        with open(DATA_ASSESSMENT_FILE, 'w', encoding='utf-8') as f:
            json.dump(assessments, f, indent=4)

# --- Funções Auxiliares de Persistência ---

def load_data(filename):
    if not os.path.exists(filename): return {}
    with open(filename, "r", encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(filename, data_structure):
    """Salva forçando a escrita no disco para evitar cache."""
    try:
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(data_structure, f, indent=4)
            f.flush()
            os.fsync(f.fileno())
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def generate_id_register(user_role):
    prefix = "S" if user_role == "student" else "I"
    all_users = load_data(DATA_USER_FILE)
    while True:
        reg_id = prefix + ''.join(random.choices(string.digits, k=6))
        if reg_id not in all_users:
            return reg_id

def validate_password(password):
    if len(password) < 8:
        return False, "A senha deve ter no mínimo 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "A senha deve conter pelo menos uma letra maiúscula."
    if not re.search(r"\d", password):
        return False, "A senha deve conter pelo menos um número."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "A senha deve conter pelo menos um caractere especial."
    return True, ""

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed_password):
    try:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
    except Exception:
        return False

# --- Gestão de Estado ---

def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'quiz_in_progress' not in st.session_state:
        st.session_state.quiz_in_progress = None
    if 'new_registration_id' not in st.session_state:
        st.session_state.new_registration_id = None

def set_page(page_name):
    st.session_state.page = page_name
    st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.user_profile = None
    st.session_state.quiz_in_progress = None
    set_page('login')

def delete_account():
    user = st.session_state.user_profile
    reg_id = user["reg_id"]
    
    if not st.session_state.get('confirm_delete', False):
        st.session_state.confirm_delete = True
        st.warning("Tem certeza? Esta ação é irreversível.")
        st.button("Confirmar Exclusão Definitiva", on_click=delete_account)
        return

    all_users = load_data(DATA_USER_FILE)
    all_grades = load_data(DATA_GRADE_FILE)
    all_classes = load_data(DATA_CLASS_FILE)
    all_assessments = load_data(DATA_ASSESSMENT_FILE)
    
    if reg_id in all_users: del all_users[reg_id]
    if reg_id in all_grades: del all_grades[reg_id]
    
    # Remove das turmas
    for cls, students in all_classes.items():
        if reg_id in students:
            all_classes[cls] = [s for s in students if s != reg_id]
            
    # Remove provas criadas pelo professor
    if reg_id.startswith("I"):
         assessments_to_delete = [n for n, a in all_assessments.items() if a.get("instructor_id") == reg_id]
         for name in assessments_to_delete:
             del all_assessments[name]

    save_data(DATA_USER_FILE, all_users)
    save_data(DATA_GRADE_FILE, all_grades)
    save_data(DATA_CLASS_FILE, all_classes)
    save_data(DATA_ASSESSMENT_FILE, all_assessments)
    
    st.success("Conta excluída.")
    time.sleep(1)
    logout()

# --- Telas ---

def render_registration_screen():
    if st.session_state.new_registration_id:
        st.title("✅ Cadastro Realizado!")
        st.balloons()
        st.info("Anote seu ID abaixo. Ele é seu login.")
        st.error(f"SEU ID:  {st.session_state.new_registration_id}")
        
        if st.button("Já anotei, ir para Login", type="primary"):
            st.session_state.new_registration_id = None
            set_page('login')
        return

    st.title("📝 Novo Cadastro")
    with st.form("register_form"):
        role_display = st.radio("Perfil:", ["Estudante", "Professor"])
        role = "student" if role_display == "Estudante" else "instructor"
        
        name = st.text_input("Nome Completo")
        age = st.text_input("Idade")
        
        # Professor key
        auth_key = ""
        if role == "instructor":
            st.warning("🔒 Área Restrita")
            auth_key = st.text_input("Chave de Acesso (Professor)", type="password")
            
        st.info("Senha segura: Mín 8 chars, 1 Maiúscula, 1 Número, 1 Especial")
        password = st.text_input("Senha", type="password")
        
        consent = st.checkbox("Aceito os termos de uso")
        if st.form_submit_button("Cadastrar", type="primary"):
            if not consent:
                st.error("Aceite os termos.")
                return
            if not name or not age:
                st.error("Preencha todos os campos.")
                return
            if role == "instructor" and auth_key != INSTRUCTOR_SECRET_KEY:
                st.error("Chave de professor inválida.")
                return
            
            valid, msg = validate_password(password)
            if not valid:
                st.error(msg)
                return
                
            try: age_val = int(age)
            except: 
                st.error("Idade inválida")
                return

            new_id = generate_id_register(role)
            all_users = load_data(DATA_USER_FILE)
            all_users[new_id] = {
                "full_name": name,
                "age": age_val,
                "password_hash": hash_password(password),
                "user_role": role
            }
            
            if save_data(DATA_USER_FILE, all_users):
                # Matricular aluno
                if role == "student":
                    classes = load_data(DATA_CLASS_FILE)
                    if "Turma Exemplo" in classes:
                        classes["Turma Exemplo"].append(new_id)
                        save_data(DATA_CLASS_FILE, classes)
                
                st.session_state.new_registration_id = new_id
                st.rerun()
            else:
                st.error("Erro ao salvar.")

    st.button("Voltar", on_click=lambda: set_page('login'))

def render_login_screen():
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.title("🔐 Login")
        
        with st.form("login"):
            uid = st.text_input("ID de Usuário").strip().upper()
            pwd = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", type="primary"):
                users = load_data(DATA_USER_FILE)
                if uid in users and check_password(pwd, users[uid].get("password_hash","")):
                    st.session_state.logged_in = True
                    st.session_state.user_profile = {"reg_id": uid, **users[uid]}
                    if uid.startswith("S"): set_page('student_menu')
                    else: set_page('instructor_menu')
                else:
                    st.error("Credenciais inválidas.")
        
        st.markdown("---")
        with st.expander("🔄 Trocar Senha"):
            with st.form("change_pass"):
                c_id = st.text_input("Seu ID").strip().upper()
                c_old = st.text_input("Senha Antiga", type="password")
                c_new = st.text_input("Nova Senha", type="password")
                if st.form_submit_button("Atualizar"):
                    users = load_data(DATA_USER_FILE)
                    if c_id in users and check_password(c_old, users[c_id].get("password_hash","")):
                        valid, msg = validate_password(c_new)
                        if valid:
                            users[c_id]["password_hash"] = hash_password(c_new)
                            save_data(DATA_USER_FILE, users)
                            st.success("Senha alterada!")
                        else:
                            st.error(msg)
                    else:
                        st.error("Dados incorretos.")

        st.markdown("---")
        st.button("Criar Conta", on_click=lambda: set_page('register'))

def render_student_menu():
    user = st.session_state.user_profile
    st.title(f"🎓 Olá, {user['full_name']}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝 Fazer Prova", use_container_width=True): set_page('take_assessment')
    with c2:
        if st.button("📊 Minhas Notas", use_container_width=True): set_page('view_student_grades')
        
    st.divider()
    if st.button("⚙️ Perfil"): set_page('manage_profile')
    if st.button("Sair"): logout()

def render_instructor_menu():
    user = st.session_state.user_profile
    st.title(f"👨‍🏫 Olá, Prof. {user['full_name']}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝 Criar Avaliação", use_container_width=True): set_page('create_assessment')
        if st.button("📊 Relatório de Notas", use_container_width=True): set_page('view_instructor_grades')
    with c2:
        if st.button("🏫 Gestão de Turmas", use_container_width=True): set_page('class_management')
        if st.button("⚙️ Perfil", use_container_width=True): set_page('manage_profile')
        
    st.divider()
    if st.button("Sair"): logout()

def render_manage_profile():
    user = st.session_state.user_profile
    st.title("⚙️ Perfil")
    
    new_name = st.text_input("Nome", value=user['full_name'])
    if st.button("Salvar Nome"):
        users = load_data(DATA_USER_FILE)
        users[user['reg_id']]['full_name'] = new_name
        save_data(DATA_USER_FILE, users)
        st.session_state.user_profile['full_name'] = new_name
        st.success("Salvo!")
        
    st.markdown("---")
    if st.button("❌ Excluir Conta"): delete_account()
    st.button("Voltar", on_click=lambda: set_page('student_menu' if user['user_role'] == 'student' else 'instructor_menu'))

# --- NOVAS FUNÇÕES DE GESTÃO E CRIAÇÃO ---

def render_class_management_screen():
    st.title("🏫 Gestão de Turmas")
    
    classes = load_data(DATA_CLASS_FILE)
    users = load_data(DATA_USER_FILE)
    
    tab1, tab2 = st.tabs(["➕ Criar Nova Turma", "👥 Gerenciar Alunos"])
    
    # --- ABA 1: CRIAR TURMA ---
    with tab1:
        st.subheader("Criar Nova Turma")
        with st.form("create_class_form"):
            new_class_name = st.text_input("Nome da Turma (ex: História 2025)")
            submitted = st.form_submit_button("Criar Turma")
            
            if submitted:
                if not new_class_name:
                    st.error("Digite um nome para a turma.")
                elif new_class_name in classes:
                    st.error("Essa turma já existe!")
                else:
                    classes[new_class_name] = []
                    if save_data(DATA_CLASS_FILE, classes):
                        st.success(f"Turma '{new_class_name}' criada!")
                        time.sleep(1)
                        st.rerun()

    # --- ABA 2: ADICIONAR/REMOVER ALUNOS ---
    with tab2:
        st.subheader("Matricular Alunos")
        
        if not classes:
            st.info("Nenhuma turma criada ainda.")
        else:
            selected_class = st.selectbox("Selecione a Turma:", list(classes.keys()))
            current_students = classes[selected_class]
            
            st.write(f"**Alunos matriculados ({len(current_students)}):**")
            
            if current_students:
                student_data = []
                for sid in current_students:
                    s_name = users.get(sid, {}).get("full_name", "Desconhecido")
                    student_data.append({"ID": sid, "Nome": s_name})
                st.dataframe(pd.DataFrame(student_data), use_container_width=True)
            else:
                st.caption("Nenhum aluno nesta turma.")
            
            st.divider()
            
            c1, c2 = st.columns([3, 1])
            with c1:
                student_id_input = st.text_input("ID do Aluno para adicionar:", placeholder="Ex: S123456").strip().upper()
            with c2:
                st.write("") 
                st.write("") 
                add_btn = st.button("Adicionar Aluno", type="primary")
            
            if add_btn:
                if student_id_input in current_students:
                    st.warning("Aluno já está na turma.")
                elif student_id_input not in users:
                    st.error("ID de usuário não encontrado.")
                elif users[student_id_input].get("user_role") != "student":
                    st.error("Este ID não é de um Aluno.")
                else:
                    classes[selected_class].append(student_id_input)
                    if save_data(DATA_CLASS_FILE, classes):
                        st.success("Aluno matriculado!")
                        time.sleep(0.5)
                        st.rerun()

    st.button("Voltar ao Menu", on_click=lambda: set_page('instructor_menu'))

def render_create_assessment():
    st.title("📝 Criar Nova Avaliação")
    
    classes = load_data(DATA_CLASS_FILE)
    if not classes:
        st.warning("Crie uma Turma antes de criar uma prova.")
        st.button("Voltar", on_click=lambda: set_page('instructor_menu'))
        return

    st.subheader("1. Configurações")
    c1, c2 = st.columns(2)
    with c1:
        exam_name = st.text_input("Nome da Avaliação")
    with c2:
        target_class = st.selectbox("Aplicar para:", list(classes.keys()))
        
    num_questions = st.slider("Quantidade de Questões:", 1, 10, 2)
    
    st.divider()
    st.subheader("2. Questões")
    
    with st.form("create_assessment_form"):
        questions_data = {}
        chars = ['A', 'B', 'C', 'D', 'E']
        
        for i in range(1, num_questions + 1):
            st.markdown(f"**Questão {i}**")
            q_text = st.text_input(f"Enunciado {i}:", key=f"q_txt_{i}")
            
            col_opts = st.columns(5)
            opts = {}
            for idx, char in enumerate(chars):
                with col_opts[idx]:
                    opts[char] = st.text_input(f"Opção {char}", key=f"q_{i}_{char}")
            
            correct = st.selectbox(f"Gabarito {i}:", chars, key=f"correct_{i}")
            st.markdown("---")
            
            questions_data[str(i)] = {
                "text": q_text,
                "A": opts['A'], "B": opts['B'], "C": opts['C'], "D": opts['D'], "E": opts['E'],
                "correct": correct
            }
        
        submitted = st.form_submit_button("💾 Publicar Prova", type="primary")
        
        if submitted:
            if not exam_name:
                st.error("Nome da prova obrigatório!")
                return
            
            # Validação simples
            for q_id, q_val in questions_data.items():
                if not q_val['text']:
                    st.error(f"Questão {q_id} sem enunciado.")
                    return
                if not q_val['A'] or not q_val['B']:
                    st.error(f"Questão {q_id} precisa de opções.")
                    return

            all_assessments = load_data(DATA_ASSESSMENT_FILE)
            if exam_name in all_assessments:
                st.error("Nome de prova já existe.")
                return
                
            all_assessments[exam_name] = {
                "assigned_class": target_class,
                "instructor_id": st.session_state.user_profile["reg_id"],
                "questions": questions_data
            }
            
            if save_data(DATA_ASSESSMENT_FILE, all_assessments):
                st.success("Prova criada!")
                time.sleep(2)
                set_page('instructor_menu')
            else:
                st.error("Erro ao salvar.")

    st.button("Cancelar", on_click=lambda: set_page('instructor_menu'))

def render_take_assessment():
    st.title("📝 Provas")
    user_id = st.session_state.user_profile['reg_id']
    
    if st.session_state.quiz_in_progress:
        render_quiz_questions(user_id)
        return

    assessments = load_data(DATA_ASSESSMENT_FILE)
    classes = load_data(DATA_CLASS_FILE)
    
    # Filtra matérias da turma do aluno
    my_classes = [c for c, students in classes.items() if user_id in students]
    available = {k:v for k,v in assessments.items() if v['assigned_class'] in my_classes}
    
    if not available:
        st.info("Nenhuma prova disponível. Verifique se você está matriculado em uma turma.")
        st.button("Voltar", on_click=lambda: set_page('student_menu'))
        return
        
    for name, data in available.items():
        with st.expander(name):
            st.caption(f"Turma: {data['assigned_class']}")
            if st.button(f"Iniciar {name}", key=f"start_{name}"):
                start_quiz(user_id, name, data)
                
    st.button("Voltar", on_click=lambda: set_page('student_menu'))

def start_quiz(user_id, name, data):
    grades = load_data(DATA_GRADE_FILE)
    attempts = grades.get(user_id, {}).get("attempts", {}).get(name, 0)
    
    if attempts >= 3:
        st.error("Limite de tentativas esgotado.")
    else:
        st.session_state.quiz_in_progress = {
            "name": name,
            "attempts": attempts,
            "questions": data["questions"],
            "answers": {}
        }
        st.rerun()

def render_quiz_questions(user_id):
    quiz = st.session_state.quiz_in_progress
    st.subheader(quiz['name'])
    st.info(f"Tentativa {quiz['attempts']+1}/3")
    
    with st.form("quiz"):
        for qid, qdata in quiz['questions'].items():
            st.markdown(f"**{qid}. {qdata['text']}**")
            opts = [f"{k}) {qdata[k]}" for k in ['A','B','C','D','E'] if k in qdata]
            quiz['answers'][qid] = st.radio("Resp:", opts, key=f"rad_{qid}")
            st.write("---")
            
        if st.form_submit_button("Enviar"):
            process_quiz_result(user_id, quiz)
            
    if st.button("Cancelar"):
        st.session_state.quiz_in_progress = None
        st.rerun()

def process_quiz_result(user_id, quiz):
    correct = 0
    total = len(quiz['questions'])
    
    for qid, qdata in quiz['questions'].items():
        ans = quiz['answers'].get(qid, "")
        if ans.startswith(qdata['correct']):
            correct += 1
            
    raw_score = (correct / total) * 10
    final_score = max(raw_score - quiz['attempts'], 0)
    
    grades_db = load_data(DATA_GRADE_FILE)
    if user_id not in grades_db:
        grades_db[user_id] = {"full_name": st.session_state.user_profile['full_name'], "grades": {}, "attempts": {}}
        
    grades_db[user_id]["grades"][quiz['name']] = final_score
    grades_db[user_id]["attempts"][quiz['name']] = quiz['attempts'] + 1
    
    save_data(DATA_GRADE_FILE, grades_db)
    st.session_state.quiz_in_progress = None
    st.success(f"Nota: {final_score:.1f}")
    time.sleep(2)
    st.rerun()

def render_student_grade_consultation():
    st.title("Boletim")
    uid = st.session_state.user_profile['reg_id']
    data = load_data(DATA_GRADE_FILE).get(uid, {})
    
    if not data.get("grades"):
        st.info("Sem notas.")
    else:
        rows = []
        for subj, score in data["grades"].items():
            att = data["attempts"].get(subj, 0)
            rows.append({"Matéria": subj, "Nota": f"{score:.1f}", "Tentativas": att})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        
    st.button("Voltar", on_click=lambda: set_page('student_menu'))

def render_instructor_view_all_grades():
    st.title("Relatório Geral")
    all_data = load_data(DATA_GRADE_FILE)
    
    if not all_data:
        st.info("Sem dados.")
    else:
        rows = []
        subjects = set()
        for uid, info in all_data.items():
            row = {"ID": uid, "Nome": info.get("full_name", "")}
            grades = info.get("grades", {})
            subjects.update(grades.keys())
            for s, v in grades.items():
                row[s] = v
            rows.append(row)
            
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        
        if subjects:
            st.bar_chart(df[list(subjects)].mean(numeric_only=True))
            
    st.button("Voltar", on_click=lambda: set_page('instructor_menu'))

# --- Main ---
if __name__ == "__main__":
    init_files()
    populate_default_db()
    render_debug_sidebar()
    initialize_session_state()
    
    pages = {
        'login': render_login_screen,
        'register': render_registration_screen,
        'student_menu': render_student_menu,
        'instructor_menu': render_instructor_menu,
        'take_assessment': render_take_assessment,
        'view_student_grades': render_student_grade_consultation,
        'view_instructor_grades': render_instructor_view_all_grades,
        'manage_profile': render_manage_profile,
        'class_management': render_class_management_screen,
        'create_assessment': render_create_assessment
    }
    
    if st.session_state.page in pages:
        pages[st.session_state.page]()
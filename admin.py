import streamlit as st
import sqlite3
import pandas as pd

# =========================================================
# 1. CONFIGURAÇÕES INICIAIS E BANCO DE DADOS
# =========================================================

# Configuração da Página (Sempre o primeiro comando Streamlit)
st.set_page_config(page_title="Painel Administrativo - Contracheques", layout="wide")

def conectar_bd():
    """Estabelece conexão com o banco de dados SQLite local."""
    return sqlite3.connect('portal_contracheque.db')



# --- ESTILIZAÇÃO CSS PERSONALIZADA (COMPLETA E COMPACTA) ---
st.markdown("""
    <style>
    /* Estilo para os botões grandes da página inicial (Home) */
    div.stButton > button:first-child {
        height: 120px;
        width: 100%;
        font-size: 20px;
        font-weight: bold;
        border-radius: 15px;
        border: 2px solid #4CAF50;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #4CAF50;
        color: white;
    }
    /* Estilo para Status Ativa/Inativa com Cores e Bordas */
    .status-ativa { 
        color: #28a745; font-weight: bold; border: 1px solid #28a745; 
        padding: 4px 12px; border-radius: 6px; background-color: #f8fff9;
    }
    .status-inativa { 
        color: #dc3545; font-weight: bold; border: 1px solid #dc3545; 
        padding: 4px 12px; border-radius: 6px; background-color: #fff8f8;
    }
    /* REDUÇÃO AGRESSIVA DE ESPAÇOS PARA FICAR COMPACTO (GRADE) */
    [data-testid="stVerticalBlock"] > div {
        gap: 0rem !important;
    }
    div[data-testid="column"] {
        padding: 0px 5px !important;
        line-height: 1.0 !important;
    }
    .stMarkdown p {
        margin-bottom: 0px !important;
    }
    /* Tamanho dos botões de ação para não esticarem a grade */
    div.stButton > button {
        padding: 0px 5px !important;
        height: 28px !important;
        min-height: 28px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 2. JANELAS FLUTUANTES (MODAIS) DE SEGURANÇA - EMPRESAS
# =========================================================

@st.dialog("Confirmar Alteração de Empresa")
def modal_editar_empresa(dados):
    """Janela flutuante para editar empresa com confirmação obrigatória."""
    st.write(f"Editando dados de: **{dados['nome_fantasia']}**")
    with st.form("form_edicao_emp_full"):
        n_cod = st.text_input("Código Empresa", value=dados['codigo_empresa'])
        n_nome = st.text_input("Nome Fantasia", value=dados['nome_fantasia'])
        n_cnpj = st.text_input("CNPJ", value=dados['cnpj'])
        n_status = st.selectbox("Status", ["Ativa", "Inativa"], index=0 if dados['status'] == "Ativa" else 1)
        
        st.write("---")
        st.warning("⚠️ Você confirma que os dados acima estão corretos?")
        check_edit = st.checkbox("Sim, confirmo as alterações e desejo salvar no banco.")
        
        if st.form_submit_button("✅ SALVAR ALTERAÇÕES"):
            if check_edit:
                conn = conectar_bd()
                try:
                    conn.execute("UPDATE empresas SET codigo_empresa=?, nome_fantasia=?, cnpj=?, status=? WHERE id=?", 
                                 (n_cod, n_nome, n_cnpj, n_status, dados['id']))
                    conn.commit()
                    st.success("Empresa atualizada com sucesso!"); st.rerun()
                except Exception as e: st.error(f"Erro ao salvar: {e}")
                finally: conn.close()
            else:
                st.error("Marque a confirmação para salvar.")

@st.dialog("🚨 CONFIRMAR EXCLUSÃO DE EMPRESA")
def modal_excluir_empresa(dados):
    """Janela flutuante para exclusão definitiva de empresa."""
    st.error(f"ATENÇÃO: Deseja excluir permanentemente a empresa: **{dados['nome_fantasia']}**?")
    st.write("Esta ação não pode ser desfeita e afetará os colaboradores vinculados.")
    c_s, c_n = st.columns(2)
    if c_n.button("❌ CANCELAR"): st.rerun()
    if c_s.button("🗑️ SIM, EXCLUIR AGORA", type="primary"):
        conn = conectar_bd()
        conn.execute("DELETE FROM empresas WHERE id=?", (dados['id'],))
        conn.commit(); conn.close(); st.rerun()

# =========================================================
# 3. JANELAS FLUTUANTES (MODAIS) DE SEGURANÇA - COLABORADORES
# =========================================================

@st.dialog("Confirmar Alteração de Colaborador")
def modal_editar_colaborador(dados):
    """Janela flutuante para editar colaborador com confirmação."""
    st.write(f"Editando dados de: **{dados['nome']}**")
    with st.form("form_edit_colab_full"):
        n_nome = st.text_input("Nome Completo", value=dados['nome'])
        n_cod = st.text_input("Cód. Funcional", value=dados['codigo_funcionario'])
        n_cpf = st.text_input("CPF", value=dados['cpf'])
        n_nasc = st.text_input("Data Nascimento", value=dados['data_nascimento'])
        
        st.write("---")
        st.warning("⚠️ Confirma as alterações deste colaborador?")
        check_colab = st.checkbox("Sim, os dados estão corretos e confirmo a atualização.")
        
        if st.form_submit_button("✅ ATUALIZAR DADOS"):
            if check_colab:
                conn = conectar_bd()
                try:
                    conn.execute("UPDATE colaboradores SET nome=?, codigo_funcionario=?, cpf=?, data_nascimento=? WHERE id=?",
                                 (n_nome, n_cod, n_cpf, n_nasc, dados['id']))
                    conn.commit()
                    st.success("Colaborador atualizado!"); st.rerun()
                except Exception as e: st.error(f"Erro: {e}")
                finally: conn.close()
            else: st.error("Marque a confirmação para salvar.")

@st.dialog("🚨 CONFIRMAR EXCLUSÃO DE COLABORADOR")
def modal_excluir_colaborador(dados):
    """Janela flutuante para exclusão de colaborador."""
    st.error(f"Deseja excluir permanentemente o colaborador: **{dados['nome']}**?")
    c1, c2 = st.columns(2)
    if c2.button("❌ CANCELAR"): st.rerun()
    if c1.button("🗑️ SIM, EXCLUIR", type="primary"):
        conn = conectar_bd(); conn.execute("DELETE FROM colaboradores WHERE id=?", (dados['id'],))
        conn.commit(); conn.close(); st.rerun()

# =========================================================
# 4. FUNÇÃO PRINCIPAL (MAIN)
# =========================================================

def main():
    if 'pagina' not in st.session_state:
        st.session_state.pagina = 'home'

    # ---------------------------------------------------------
    # TELA PRINCIPAL (HOME)
    # ---------------------------------------------------------
    if st.session_state.pagina == 'home':
        st.title("🛡️ Sistema de Gestão - Portal de Contracheques")
        st.subheader("Painel Administrativo Principal")
        st.write("---")
        c1, c2, c3 = st.columns(3)
        if c1.button("🏢 GERENCIAR\nEMPRESAS"): st.session_state.pagina = 'empresas'; st.rerun()
        if c2.button("👥 GERENCIAR\nCOLABORADORES"): st.session_state.pagina = 'colaboradores'; st.rerun()
        if c3.button("📊 VER\nRELATÓRIOS"): st.session_state.pagina = 'relatorios'; st.rerun()
        st.write("---")

    # ---------------------------------------------------------
    # MÓDULO EMPRESAS
    # ---------------------------------------------------------
    elif st.session_state.pagina == 'empresas':
        st.title("🏢 Gerenciamento de Empresas")
        if st.button("⬅️ Voltar"): st.session_state.pagina = 'home'; st.rerun()
        
        # Cadastro de Empresa
        with st.expander("➕ CADASTRAR NOVA EMPRESA", expanded=False):
            with st.form("f_nova_emp_full", clear_on_submit=True):
                ca, cb, cc, cd = st.columns(4)
                f_cod = ca.text_input("Código")
                f_nome = cb.text_input("Nome Fantasia")
                f_cnpj = cc.text_input("CNPJ")
                f_st = cd.selectbox("Status", ["Ativa", "Inativa"])
                st.write("---")
                check_inc = st.checkbox("Confirmo a inclusão desta empresa no sistema.")
                if st.form_submit_button("💾 GRAVAR EMPRESA"):
                    if check_inc and f_cod and f_nome and f_cnpj:
                        conn = conectar_bd()
                        try:
                            conn.execute("INSERT INTO empresas (codigo_empresa, nome_fantasia, cnpj, status) VALUES (?,?,?,?)", (f_cod, f_nome, f_cnpj, f_st))
                            conn.commit(); st.success("Cadastrada com sucesso!"); st.rerun()
                        except: st.error("Erro: Dados duplicados.")
                        finally: conn.close()
                    else: st.warning("Preencha tudo e confirme.")

        st.write("---")
        
        # Grade de Empresas
        st.subheader("Lista de Empresas Cadastradas")
        conn = conectar_bd(); df_e = pd.read_sql_query("SELECT * FROM empresas", conn); conn.close()
        if not df_e.empty:
            h = st.columns([1, 3, 2, 1, 1.5])
            h[0].write("**Cód**"); h[1].write("**Empresa**"); h[2].write("**CNPJ**"); h[3].write("**ST**"); h[4].write("**Ações**")
            st.divider()
            for _, row in df_e.iterrows():
                c = st.columns([1, 3, 2, 1, 1.5])
                c[0].write(row['codigo_empresa']); c[1].write(row['nome_fantasia']); c[2].write(row['cnpj'])
                cl = "status-ativa" if row['status'] == "Ativa" else "status-inativa"
                c[3].markdown(f'<span class="{cl}">{row["status"]}</span>', unsafe_allow_html=True)
                
                ed_col, del_col = c[4].columns(2)
                if ed_col.button("📝", key=f"e_{row['id']}"): modal_editar_empresa(row)
                if del_col.button("🗑️", key=f"d_{row['id']}"): modal_excluir_empresa(row)
        else: st.info("Nenhuma empresa encontrada.")

    # ---------------------------------------------------------
    # MÓDULO COLABORADORES (FLUXO INVERTIDO DINÂMICO)
    # ---------------------------------------------------------
    elif st.session_state.pagina == 'colaboradores':
        st.title("👥 Gerenciamento de Colaboradores")
        if st.button("⬅️ Voltar ao Início"): st.session_state.pagina = 'home'; st.rerun()
        st.write("---")

        # 1. PASSO: SELEÇÃO DA EMPRESA
        conn = conectar_bd()
        empresas_ativas = conn.execute("SELECT id, nome_fantasia FROM empresas WHERE status = 'Ativa'").fetchall()
        conn.close()

        if not empresas_ativas:
            st.warning("⚠️ Não há empresas 'Ativa' cadastradas. Cadastre uma empresa primeiro.")
        else:
            dict_filtro = {id_e: nome_e for id_e, nome_e in empresas_ativas}
            st.subheader("1️⃣ Selecione a Empresa para Gerenciar Funcionários")
            emp_selecionada = st.selectbox("Escolha a empresa abaixo:", options=dict_filtro.keys(), 
                                           format_func=lambda x: dict_filtro[x], key="seletor_emp_func")
            
            if st.button("🔎 CARREGAR COLABORADORES DA EMPRESA"):
                st.session_state.id_emp_trabalho = emp_selecionada

            # 2. PASSO: LIBERAR CADASTRO E GRADE APENAS PARA A EMPRESA SELECIONADA
            if 'id_emp_trabalho' in st.session_state:
                id_trabalho = st.session_state.id_emp_trabalho
                nome_trabalho = dict_filtro[id_trabalho]
                st.success(f"📍 Gerenciando agora: **{nome_trabalho}**")
                st.write("---")

                # FORMULÁRIO DE CADASTRO VINCULADO
                with st.expander(f"➕ Cadastrar Novo Colaborador em {nome_trabalho}"):
                    with st.form("form_novo_colab_vinculado", clear_on_submit=True):
                        c1, c2 = st.columns(2)
                        f_nome = c1.text_input("Nome Completo do Funcionário")
                        f_cod_f = c2.text_input("Cód. de Cadastro")
                        f_cpf = c1.text_input("CPF (Apenas números)")
                        f_nasc = c2.text_input("Nascimento (AAAA-MM-DD)")
                        st.write("---")
                        check_f = st.checkbox(f"Confirmo que os dados estão corretos para inclusão na empresa {nome_trabalho}.")
                        if st.form_submit_button("💾 GRAVAR COLABORADOR"):
                            if check_f and f_nome and f_cpf:
                                conn = conectar_bd()
                                try:
                                    conn.execute("INSERT INTO colaboradores (empresa_id, codigo_funcionario, nome, cpf, data_nascimento) VALUES (?,?,?,?,?)",
                                                 (id_trabalho, f_cod_f, f_nome, f_cpf, f_nasc))
                                    conn.commit(); st.success("Colaborador cadastrado!"); st.rerun()
                                except Exception as e: st.error(f"Erro ao salvar: {e}")
                                finally: conn.close()
                            else: st.warning("Preencha todos os campos e marque a confirmação.")

                # GRADE DE COLABORADORES DA EMPRESA ATIVA
                st.subheader(f"Lista de Funcionários: {nome_trabalho}")
                conn = conectar_bd()
                df_c = pd.read_sql_query(f"SELECT * FROM colaboradores WHERE empresa_id = {id_trabalho}", conn)
                conn.close()

                if not df_c.empty:
                    h_c = st.columns([1, 3, 2, 1.5])
                    h_c[0].write("**Cód**"); h_c[1].write("**Nome**"); h_c[2].write("**CPF**"); h_c[3].write("**Ações**")
                    st.divider()
                    for _, row in df_c.iterrows():
                        c_row = st.columns([1, 3, 2, 1.5])
                        c_row[0].write(row['codigo_funcionario']); c_row[1].write(row['nome']); c_row[2].write(row['cpf'])
                        
                        btn_e, btn_d = c_row[3].columns(2)
                        if btn_e.button("📝", key=f"edit_c_{row['id']}"): modal_editar_colaborador(row)
                        if btn_d.button("🗑️", key=f"del_c_{row['id']}"): modal_excluir_colaborador(row)
                else:
                    st.info(f"A empresa {nome_trabalho} ainda não possui colaboradores cadastrados.")

    # ---------------------------------------------------------
    # MÓDULO RELATÓRIOS
    # ---------------------------------------------------------
    elif st.session_state.pagina == 'relatorios':
        st.title("📊 Central de Relatórios e Exportação")
        if st.button("⬅️ Voltar ao Início"): st.session_state.pagina = 'home'; st.rerun()
        st.write("---")
        st.write("Área destinada à exportação de dados em formatos Excel e CSV.")

if __name__ == "__main__":
    main()

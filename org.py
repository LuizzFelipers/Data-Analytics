import os
import shutil
from datetime import datetime
import streamlit as st
import json
import time

# Nome do arquivo de log
LOG_FILE = "organizador_log.json"

def carregar_log():
    """Carrega o histórico de operações do arquivo de log"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    return []

def salvar_log(operacao):
    """Salva uma nova operação no arquivo de log"""
    log = carregar_log()
    log.append(operacao)
    with open(LOG_FILE, 'w') as f:
        json.dump(log, f)

def organizar_por_extensao(pasta_origem):
    """Organiza arquivos por extensão (.pdf, .xlsx, etc.)"""
    try:
        total_arquivos = 0
        operacao = {
            'tipo': 'extensao',
            'pasta': pasta_origem,
            'timestamp': datetime.now().isoformat(),
            'movimentos': []
        }
        
        with st.spinner('Organizando por extensão...'):
            for arquivo in os.listdir(pasta_origem):
                caminho_completo = os.path.join(pasta_origem, arquivo)
                if os.path.isfile(caminho_completo):
                    extensao = os.path.splitext(arquivo)[1][1:]  # remove o ponto( .pdf -> pdf)
                    if not extensao:  # para arquivos sem extensão
                        extensao = "sem_extensao"
                    pasta_destino = os.path.join(pasta_origem, extensao.upper())
                    os.makedirs(pasta_destino, exist_ok=True)
                    destino_final = os.path.join(pasta_destino, arquivo)
                    shutil.move(caminho_completo, destino_final)
                    
                    # Registra o movimento
                    operacao['movimentos'].append({
                        'origem': caminho_completo,
                        'destino': destino_final
                    })
                    total_arquivos += 1
        
        salvar_log(operacao)
        st.success(f"✅ Organização concluída! {total_arquivos} arquivos movidos.")
        return True
    except Exception as e:
        st.error(f"❌ Erro ao organizar por extensão: {e}")
        return False

def organizar_por_data(pasta_origem):
    """Organiza arquivos por ano-mês (ex: 2024-07)"""
    try:
        total_arquivos = 0
        operacao = {
            'tipo': 'data',
            'pasta': pasta_origem,
            'timestamp': datetime.now().isoformat(),
            'movimentos': []
        }
        
        with st.spinner('Organizando por data...'):
            for arquivo in os.listdir(pasta_origem):
                caminho_completo = os.path.join(pasta_origem, arquivo)
                if os.path.isfile(caminho_completo):
                    data_modificacao = os.path.getmtime(caminho_completo)
                    data = datetime.fromtimestamp(data_modificacao).strftime("%Y-%m")
                    pasta_destino = os.path.join(pasta_origem, data)
                    os.makedirs(pasta_destino, exist_ok=True)
                    destino_final = os.path.join(pasta_destino, arquivo)
                    shutil.move(caminho_completo, destino_final)
                    
                    # Registra o movimento
                    operacao['movimentos'].append({
                        'origem': caminho_completo,
                        'destino': destino_final
                    })
                    total_arquivos += 1
        
        salvar_log(operacao)
        st.success(f"✅ Organização concluída! {total_arquivos} arquivos movidos.")
        return True
    except Exception as e:
        st.error(f"❌ Erro ao organizar por data: {e}")
        return False

def reverter_ultima_operacao():
    """Reverte a última operação de organização"""
    log = carregar_log()
    if not log:
        st.warning("Não há operações para reverter.")
        return False
    
    ultima_operacao = log[-1]
    
    try:
        with st.spinner('Revertendo última operação...'):
            # Reverte na ordem inversa para evitar conflitos
            for movimento in reversed(ultima_operacao['movimentos']):
                if os.path.exists(movimento['destino']):
                    shutil.move(movimento['destino'], movimento['origem'])
            
            # Remove a operação do log
            log.pop()
            with open(LOG_FILE, 'w') as f:
                json.dump(log, f)
            
            # Remove pastas vazias criadas na organização
            if ultima_operacao['tipo'] == 'extensao':
                for movimento in ultima_operacao['movimentos']:
                    pasta = os.path.dirname(movimento['destino'])
                    if os.path.exists(pasta) and not os.listdir(pasta):
                        os.rmdir(pasta)
            elif ultima_operacao['tipo'] == 'data':
                for movimento in ultima_operacao['movimentos']:
                    pasta = os.path.dirname(movimento['destino'])
                    if os.path.exists(pasta) and not os.listdir(pasta):
                        os.rmdir(pasta)
        
        st.success(f"✅ Operação revertida com sucesso!")
        return True
    except Exception as e:
        st.error(f"❌ Erro ao reverter operação: {e}")
        return False

def main():
    st.title("📁 Organizador de Arquivos (com Reversão)")
    st.write("""
    Este aplicativo organiza seus arquivos automaticamente por extensão ou data de modificação.
    Você pode reverter a última operação se necessário.
    """)
    
    # Sidebar com histórico e reversão
    with st.sidebar:
        st.subheader("Histórico de Operações")
        log = carregar_log()
        
        if not log:
            st.write("Nenhuma operação registrada.")
        else:
            for i, op in enumerate(reversed(log), 1):
                st.write(f"{i}. {op['tipo'].capitalize()} - {op['timestamp']}")
        
        if st.button("↩️ Reverter Última Operação", disabled=not log):
            if reverter_ultima_operacao():
                st.rerun()
    
    # Área principal
    with st.expander("ℹ️ Como usar"):
        st.write("""
        1. Selecione a pasta que deseja organizar
        2. Escolha o critério de organização
        3. Clique em "Organizar Arquivos"
        4. Se necessário, reverta a operação na sidebar
        
        **Dica:** A reversão só funciona para a última operação realizada.
        """)
    
    pasta = st.text_input("Digite o caminho completo da pasta a ser organizada:")
    
    if pasta and not os.path.isdir(pasta):
        st.warning("⚠️ A pasta especificada não existe. Verifique o caminho.")
    
    criterio = st.radio(
        "Selecione o critério de organização:",
        ["Extensão", "Data de modificação"],
        horizontal=True
    )
    
    if st.button("Organizar Arquivos", type="primary"):
        if not pasta:
            st.warning("Por favor, informe o caminho da pasta.")
        elif not os.path.isdir(pasta):
            st.warning("A pasta especificada não existe.")
        else:
            if criterio == "Extensão":
                organizar_por_extensao(pasta)
            else:
                organizar_por_data(pasta)
            time.sleep(1)
            st.rerun()

if __name__ == "__main__":
    main()
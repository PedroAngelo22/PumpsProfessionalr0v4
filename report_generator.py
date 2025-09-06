# report_generator.py (Versão 2.0)

from fpdf import FPDF
from datetime import datetime
import io

class PDFReport(FPDF):
    def __init__(self, project_name, scenario_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_name = project_name
        self.scenario_name = scenario_name
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        """ Cria o cabeçalho do relatório em cada página. """
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Relatório de Análise Hidráulica', 0, 1, 'C')
        
        # ALTERAÇÃO 4: Adicionando a nova linha no cabeçalho
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, 'PumpsProfessional by Process & Accords', 0, 1, 'C')

        self.set_font('Arial', 'I', 10)
        self.cell(0, 6, f'Projeto: {self.project_name}', 0, 1, 'C')
        self.cell(0, 6, f'Cenário: {self.scenario_name}', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        """ Cria o rodapé do relatório em cada página. """
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        self.set_x(10)
        self.cell(0, 10, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 0, 'L')

    def add_section_title(self, title):
        """ Adiciona um título de seção formatado. """
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, title, 0, 1, 'L', fill=True)
        self.ln(4)

    def add_key_value_table(self, data_dict):
        """ Cria uma tabela simples de Chave-Valor. """
        self.set_font('Arial', '', 10)
        for key, value in data_dict.items():
            self.set_font('', 'B')
            self.cell(60, 8, f'{key}:', border=1)
            self.set_font('', '')
            self.cell(0, 8, f' {value}', border=1)
            self.ln()
        self.ln(5)

    def add_results_metrics(self, metrics_data):
        """ Adiciona as métricas de resultado em colunas. """
        self.set_font('Arial', 'B', 11)
        num_metrics = len(metrics_data)
        cell_width = 190 / num_metrics if num_metrics > 0 else 190
        for title, _ in metrics_data:
            self.cell(cell_width, 7, title, 1, 0, 'C')
        self.ln()
        self.set_font('', '')
        for _, value in metrics_data:
            self.cell(cell_width, 10, value, 1, 0, 'C')
        self.ln()
        self.ln(5)
    
    # NOVO: Função para adicionar o resumo da rede
    def add_network_summary_table(self, network_data):
        """ Adiciona uma tabela com o resumo dos trechos da rede. """
        self.set_font('Arial', 'B', 10)
        # Cabeçalho da Tabela
        self.cell(80, 7, 'Trecho / Ramal', 1, 0, 'C')
        self.cell(25, 7, 'L (m)', 1, 0, 'C')
        self.cell(25, 7, 'Ø (mm)', 1, 0, 'C')
        self.cell(60, 7, 'Material', 1, 1, 'C')
        
        self.set_font('Arial', '', 9)

        # Função auxiliar para desenhar as linhas
        def draw_rows(title, trechos):
            if trechos:
                self.set_font('', 'B')
                self.cell(0, 7, title, 1, 1, 'L')
                self.set_font('', '')
                for i, trecho in enumerate(trechos):
                    self.cell(80, 7, f'  - Trecho {i+1}', 1, 0, 'L')
                    self.cell(25, 7, f"{trecho['comprimento']:.2f}", 1, 0, 'C')
                    self.cell(25, 7, f"{trecho['diametro']:.2f}", 1, 0, 'C')
                    self.cell(60, 7, trecho['material'], 1, 1, 'L')

        draw_rows('Trechos em Série (Antes)', network_data.get('antes', []))
        
        # Lógica para ramais em paralelo
        if network_data.get('paralelo'):
             self.set_font('', 'B')
             self.cell(0, 7, 'Ramais em Paralelo', 1, 1, 'L')
             self.set_font('', '')
             for ramal_name, trechos_ramal in network_data['paralelo'].items():
                 for i, trecho in enumerate(trechos_ramal):
                    self.cell(80, 7, f'  - {ramal_name} (T{i+1})', 1, 0, 'L')
                    self.cell(25, 7, f"{trecho['comprimento']:.2f}", 1, 0, 'C')
                    self.cell(25, 7, f"{trecho['diametro']:.2f}", 1, 0, 'C')
                    self.cell(60, 7, trecho['material'], 1, 1, 'L')

        draw_rows('Trechos em Série (Depois)', network_data.get('depois', []))
        self.ln(5)

    def add_image_from_bytes(self, image_bytes):
        """ Adiciona uma imagem (PNG/JPG) a partir de um objeto de bytes. """
        image_buffer = io.BytesIO(image_bytes)
        self.image(image_buffer, x=self.get_x(), y=self.get_y(), w=190)
        image_buffer.close()
        self.ln(5)

# ALTERADO: A assinatura da função agora aceita os novos dados
def generate_report(project_name, scenario_name, params_data, results_data, metrics_data, 
                    network_data, diagram_image_bytes, chart_figure):
    """
    Função principal que orquestra a criação do PDF.
    Recebe todos os dados necessários e retorna o PDF como bytes.
    """
    pdf = PDFReport(project_name, scenario_name)
    pdf.add_page()
    
    pdf.add_section_title('Parâmetros Gerais da Simulação')
    pdf.add_key_value_table(params_data)

    # ALTERAÇÃO 3: Adicionando a seção de resumo da rede
    pdf.add_section_title('Resumo da Rede de Tubulação')
    pdf.add_network_summary_table(network_data)

    # ALTERAÇÃO 2: Adicionando o diagrama da rede
    pdf.add_section_title('Diagrama da Rede')
    pdf.add_image_from_bytes(diagram_image_bytes)
    
    pdf.add_section_title('Resultados no Ponto de Operação')
    pdf.add_results_metrics(metrics_data)
    
    pdf.add_section_title('Análise de Custo Energético')
    pdf.add_key_value_table(results_data)

    pdf.add_section_title('Gráfico: Curva da Bomba vs. Curva do Sistema')
    # Renomeado a função para ser mais genérica
    pdf.add_image_from_bytes(chart_figure)

    return bytes(pdf.output())

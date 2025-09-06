# report_generator.py (Versão 2.1 - Com ajustes de paginação e layout)

from fpdf import FPDF
from datetime import datetime
import io

class PDFReport(FPDF):
    def __init__(self, project_name, scenario_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_name = project_name
        self.scenario_name = scenario_name
        # Ajustado a margem inferior para dar mais espaço ao rodapé
        self.set_auto_page_break(auto=True, margin=20) 

    def header(self):
        """ Cria o cabeçalho do relatório em cada página. """
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Relatório de Análise Hidráulica', 0, 1, 'C')
        
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, 'PumpsProfessional by Process & Accords', 0, 1, 'C')

        self.set_font('Arial', 'I', 10)
        self.cell(0, 6, f'Projeto: {self.project_name}', 0, 1, 'C')
        self.cell(0, 6, f'Cenário: {self.scenario_name}', 0, 1, 'C')
        self.ln(5) # Espaçamento menor no cabeçalho

    def footer(self):
        """ Cria o rodapé do relatório em cada página. """
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        self.set_x(10)
        self.cell(0, 10, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 0, 'L')

    def add_section_title(self, title):
        """ Adiciona um título de seção formatado e garante espaço. """
        self.ln(5) # Garante um pequeno espaçamento antes do título da seção
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230)
        # Verificando se há espaço suficiente para o título + um pouco de conteúdo
        if self.get_y() + 20 > self.page_break_trigger: # 20mm para título e um pouco de texto
            self.add_page()
        self.cell(0, 8, title, 0, 1, 'L', fill=True)
        self.ln(4) # Espaçamento após o título da seção

    def add_key_value_table(self, data_dict):
        """ Cria uma tabela simples de Chave-Valor. """
        self.set_font('Arial', '', 10)
        for key, value in data_dict.items():
            # Verifica se a linha vai ultrapassar o limite da página
            if self.get_y() + 8 > self.page_break_trigger:
                self.add_page()
                self.add_section_title("Continuação dos Parâmetros") # Adiciona um título de continuação
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
        # Largura útil da página: 210 (A4) - 2*10 (margens) = 190mm
        cell_width = 190 / num_metrics if num_metrics > 0 else 190
        
        # Garante que a tabela comece em uma nova página se não houver espaço suficiente
        if self.get_y() + 25 > self.page_break_trigger: # 25mm para títulos e valores
            self.add_page()
            self.add_section_title("Resultados no Ponto de Operação (Continuação)")

        # Títulos
        for title, _ in metrics_data:
            self.cell(cell_width, 7, title, 1, 0, 'C')
        self.ln()

        # Valores
        self.set_font('', '')
        for _, value in metrics_data:
            self.cell(cell_width, 10, value, 1, 0, 'C')
        self.ln()
        self.ln(5)

    def add_network_summary_table(self, network_data):
        """ Adiciona uma tabela com o resumo dos trechos da rede. """
        self.set_font('Arial', 'B', 10)
        
        # Garante que a tabela comece em uma nova página se não houver espaço suficiente para o cabeçalho
        if self.get_y() + 20 > self.page_break_trigger: # 20mm para cabeçalho da tabela
            self.add_page()
            self.add_section_title("Resumo da Rede de Tubulação (Continuação)")

        self.cell(80, 7, 'Trecho / Ramal', 1, 0, 'C')
        self.cell(25, 7, 'L (m)', 1, 0, 'C')
        self.cell(25, 7, 'Ø (mm)', 1, 0, 'C')
        self.cell(60, 7, 'Material', 1, 1, 'C')
        
        self.set_font('Arial', '', 9)

        def draw_rows(title, trechos):
            if trechos:
                # Garante que o título da subseção caiba
                if self.get_y() + 15 > self.page_break_trigger:
                    self.add_page()
                    self.add_section_title(f"Resumo da Rede - {title} (Continuação)")
                self.set_font('', 'B')
                self.cell(0, 7, title, 1, 1, 'L')
                self.set_font('', '')
                for i, trecho in enumerate(trechos):
                    # Garante que a linha do trecho caiba
                    if self.get_y() + 7 > self.page_break_trigger:
                        self.add_page()
                        self.add_section_title(f"Resumo da Rede - {title} (Continuação)")
                        # Repete o cabeçalho da tabela se for uma nova página dentro da seção
                        self.set_font('Arial', 'B', 10)
                        self.cell(80, 7, 'Trecho / Ramal', 1, 0, 'C')
                        self.cell(25, 7, 'L (m)', 1, 0, 'C')
                        self.cell(25, 7, 'Ø (mm)', 1, 0, 'C')
                        self.cell(60, 7, 'Material', 1, 1, 'C')
                        self.set_font('Arial', '', 9) # Volta para a fonte normal

                    self.cell(80, 7, f'  - Trecho {i+1}', 1, 0, 'L')
                    self.cell(25, 7, f"{trecho['comprimento']:.2f}", 1, 0, 'C')
                    self.cell(25, 7, f"{trecho['diametro']:.2f}", 1, 0, 'C')
                    self.cell(60, 7, trecho['material'], 1, 1, 'L')

        draw_rows('Trechos em Série (Antes)', network_data.get('antes', []))
        
        if network_data.get('paralelo'):
             if self.get_y() + 15 > self.page_break_trigger:
                 self.add_page()
                 self.add_section_title("Resumo da Rede - Ramais em Paralelo (Continuação)")
             self.set_font('', 'B')
             self.cell(0, 7, 'Ramais em Paralelo', 1, 1, 'L')
             self.set_font('', '')
             for ramal_name, trechos_ramal in network_data['paralelo'].items():
                 for i, trecho in enumerate(trechos_ramal):
                    if self.get_y() + 7 > self.page_break_trigger:
                        self.add_page()
                        self.add_section_title(f"Resumo da Rede - {ramal_name} (Continuação)")
                        self.set_font('Arial', 'B', 10)
                        self.cell(80, 7, 'Trecho / Ramal', 1, 0, 'C')
                        self.cell(25, 7, 'L (m)', 1, 0, 'C')
                        self.cell(25, 7, 'Ø (mm)', 1, 0, 'C')
                        self.cell(60, 7, 'Material', 1, 1, 'C')
                        self.set_font('Arial', '', 9)

                    self.cell(80, 7, f'  - {ramal_name} (T{i+1})', 1, 0, 'L')
                    self.cell(25, 7, f"{trecho['comprimento']:.2f}", 1, 0, 'C')
                    self.cell(25, 7, f"{trecho['diametro']:.2f}", 1, 0, 'C')
                    self.cell(60, 7, trecho['material'], 1, 1, 'L')

        draw_rows('Trechos em Série (Depois)', network_data.get('depois', []))
        self.ln(5)

    def add_image_from_bytes(self, image_bytes, max_height=0):
        """ 
        Adiciona uma imagem (PNG/JPG) a partir de um objeto de bytes, 
        redimensionando para caber na largura da página e lidando com quebras de página.
        """
        image_buffer = io.BytesIO(image_bytes)
        temp_img_path = "temp_image_for_fpdf.png" # Salva temporariamente para fpdf2 poder ler
        with open(temp_img_path, "wb") as f:
            f.write(image_buffer.getvalue())

        # Obter dimensões da imagem para cálculo
        from PIL import Image
        img_pil = Image.open(temp_img_path)
        img_width, img_height = img_pil.size
        img_pil.close()

        # Largura máxima disponível na página (190mm)
        max_page_width = 190
        # Calcular nova largura e altura para caber na página
        new_width = max_page_width
        new_height = img_height * (new_width / img_width)

        # Se a altura da imagem for muito grande, redimensionar para caber na altura útil da página
        # Considera 20mm de margem inferior para o rodapé e 10mm de margem superior.
        available_height = self.page_break_trigger - self.get_y() - 10 
        
        # Se a imagem é maior que o espaço disponível, força uma nova página ou redimensiona
        if new_height > available_height and available_height > 50: # Mínimo de 50mm para não ficar um corte estranho
            # Redimensiona para caber na altura disponível antes de ir para a próxima página, se for razoável
            scale_factor = available_height / new_height
            new_height *= scale_factor
            new_width *= scale_factor
        elif new_height > available_height: # Se ainda for muito grande ou o espaço for pequeno, nova página
            self.add_page()
            # Tenta novamente caber na página, agora com mais espaço
            available_height_new_page = self.page_break_trigger - self.get_y() - 10
            if new_height > available_height_new_page:
                 scale_factor = available_height_new_page / new_height
                 new_height *= scale_factor
                 new_width *= scale_factor

        self.image(temp_img_path, x='C', w=new_width) # 'C' para centralizar
        self.ln(5) # Espaçamento após a imagem
        import os
        os.remove(temp_img_path) # Remove o arquivo temporário


def generate_report(project_name, scenario_name, params_data, results_data, metrics_data, 
                    network_data, diagram_image_bytes, chart_figure_bytes):
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
    # A função add_image_from_bytes já cuida da quebra de página
    pdf.add_image_from_bytes(diagram_image_bytes) 
    
    pdf.add_section_title('Resultados no Ponto de Operação')
    pdf.add_results_metrics(metrics_data)
    
    pdf.add_section_title('Análise de Custo Energético')
    pdf.add_key_value_table(results_data)

    pdf.add_section_title('Gráfico: Curva da Bomba vs. Curva do Sistema')
    pdf.add_image_from_bytes(chart_figure_bytes) # Usa a mesma função para o gráfico
    
    return bytes(pdf.output())

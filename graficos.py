import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import palette
import numpy as np
from bs4 import BeautifulSoup

# Mapeamento das UTIs para cada hospital
mapeamento_hospital = {
    'INC': ['Ecoville', 'Ecoville 2', 'Ecoville UCO'],
    'Santa Casa': ['Santa Casa UTI1 CX A', 'Santa Casa UTI CX B', 'Santa Casa UTI 2', 'Santa Casa UTI 3', 'Santa Casa UTI 4'],
    'Vita Batel': ['Vita Batel 1', 'Vita Batel 2', 'Vita Batel 3'],
    'Instituto de Medicina': ['IM UTI 5', 'IM UTI 6'],
    'Hospital das Nações': ['Nações UTI', 'Nações Neuro', 'Nações UCO'],
    'Hospital São Rafael': ['São Rafael'],
    'São Lucas': ['São Lucas']
}

def mostrar_graficos(df, uti_selecionada):
    st.title('CAPTURE DATA - Gráficos')

    # Filtrar o DataFrame com base na UTI selecionada
    df_filtrado = df[df['uti_combined'] == uti_selecionada]

    if df_filtrado.empty:
        st.warning(f"Nenhum dado encontrado para a UTI: {uti_selecionada}")
    else:
        # O restante do código permanece o mesmo, adaptando a lógica de gráficos à UTI selecionada
        # Converter a coluna 'data_internamento' para datetime
        df_filtrado['data_internamento'] = pd.to_datetime(df_filtrado['data_internamento'],format='ISO8601')

        # Calcular o número de internamentos
        df_filtrado['mes_internamento'] = df_filtrado['data_internamento'].dt.strftime('%Y-%m')
        internamentos_por_mes_uti = df_filtrado.groupby(['uti_combined', 'mes_internamento']).size().reset_index(
            name='numero_internamentos')

        # Obter cores suficientes para as linhas
        unique_utis = internamentos_por_mes_uti['uti_combined'].unique()
        num_utis = len(unique_utis)
        uti_colors = [color for sublist in palette.Paired.values() for color in sublist][:num_utis]

        # Criação do gráfico de linha
        fig = go.Figure()

        # Adicionar traços e anotações para cada UTI
        for i, uti in enumerate(unique_utis):
            df_uti = internamentos_por_mes_uti [internamentos_por_mes_uti ['uti_combined'] == uti]
            fig.add_trace(
                go.Scatter(x = df_uti ['mes_internamento'], y = df_uti ['numero_internamentos'],
                           mode = 'lines+markers',
                           name = uti,
                           line = dict(color = "#257683")))

            # Adicionar anotações
            for j in range(len(df_uti)):
                fig.add_annotation(x = df_uti ['mes_internamento'].iloc [j],
                                   y = df_uti ['numero_internamentos'].iloc [j],
                                   text = f"{df_uti ['numero_internamentos'].iloc [j]:.0f}", showarrow = True,
                                   arrowhead = 2, ax = 0, ay = -10)

        # Atualizar layout
        fig.update_layout(title = 'Número de Internamentos', xaxis_title = 'Mês',
                          yaxis_title = 'Número de Internamentos', showlegend = True)
        fig.update_xaxes(tickformat = "%Y-%m")

        # Definir o valor mínimo do eixo y como 0
        fig.update_yaxes(range = [0, None])

        # Mostrar gráfico
        st.plotly_chart(fig)

        # Lista de procedências principais
        procedencias_principais = ["Centro Cirúrgico", "Enfermaria", "Hemodinâmica", "Pronto Atendimento"]

        # Calcular a procedência dos pacientes por mês
        procedencia_por_mes = df_filtrado.groupby(
            [pd.Grouper(key = 'data_internamento', freq = 'M'), 'procedencia']).size().unstack(
            fill_value = 0).reset_index()

        # Separar as procedências principais e agrupar as restantes como "Outros"
        procedencia_por_mes ['Outros'] = procedencia_por_mes.apply(
            lambda row:row [~row.index.isin(procedencias_principais + ['data_internamento'])].sum(), axis = 1)

        # Manter apenas as colunas de interesse (principais procedências + "Outros")
        procedencia_por_mes = procedencia_por_mes [['data_internamento'] + procedencias_principais + ['Outros']]

        # Calcular as porcentagens
        procedencia_por_mes_percent = procedencia_por_mes.copy()
        total_por_mes = procedencia_por_mes_percent [procedencias_principais + ['Outros']].sum(axis = 1)
        for col in procedencias_principais + ['Outros']:
            procedencia_por_mes_percent [col] = (procedencia_por_mes [col] / total_por_mes) * 100

        # Obter cores suficientes para as procedências principais + "Outros"
        num_procedencias = len(procedencia_por_mes.columns) - 1

        # Gráfico de Procedências em %
        fig_procedencia = px.bar(procedencia_por_mes_percent, x = 'data_internamento',
                                 y = procedencia_por_mes_percent.columns [1:],
                                 title = 'Procedências',
                                 labels = {'data_internamento':'Mês', 'value':'% de Pacientes',
                                           'variable':'Procedência'},
                                 barmode = 'stack',
                                 color_discrete_sequence = palette.Paired [12])
        fig_procedencia.update_layout(xaxis_title = 'Mês', yaxis_title = '% de Pacientes',
                                      legend_title = 'Procedência')
        fig_procedencia.update_xaxes(tickformat = "%m-%Y")
        fig_procedencia.update_traces(texttemplate = '%{y:.2f}%', textposition = 'inside')

        st.plotly_chart(fig_procedencia)

        # Lista de especialidades principais
        especialidades_principais = ["Cirurgia Cardíaca", "Neurocirurgia", "Neurologia"]

        # Calcular o número de pacientes por especialidade ao longo do tempo
        especialidade_por_mes = df_filtrado.groupby(
            [pd.Grouper(key = 'data_internamento', freq = 'M'), 'especialidade']).size().unstack(
            fill_value = 0).reset_index()

        # Separar as especialidades principais e agrupar as restantes como "outras"
        especialidade_por_mes ['Outros'] = especialidade_por_mes.apply(
            lambda row:row [~row.index.isin(especialidades_principais + ['data_internamento'])].sum(), axis = 1)

        # Manter apenas as colunas de interesse (principais especialidades + "outras")
        especialidade_por_mes = especialidade_por_mes [
            ['data_internamento'] + especialidades_principais + ['Outros']]

        # Calcular as porcentagens
        especialidade_por_mes_percent = especialidade_por_mes.copy()
        total_por_mes = especialidade_por_mes_percent [especialidades_principais + ['Outros']].sum(axis = 1)
        for col in especialidades_principais + ['Outros']:
            especialidade_por_mes_percent [col] = (especialidade_por_mes [col] / total_por_mes) * 100

        # Obter cores suficientes para as especialidades principais + "outras"
        num_especialidades = len(especialidade_por_mes.columns) - 1

        # Gráfico de Especialidades em %
        fig_especialidade = px.bar(especialidade_por_mes_percent, x = 'data_internamento',
                                   y = especialidade_por_mes_percent.columns [1:],
                                   title = 'Principais Especialidades',
                                   labels = {'data_internamento':'Mês', 'value':'% de Pacientes',
                                             'variable':'Especialidade'},
                                   barmode = 'stack',
                                   color_discrete_sequence = palette.Paired [12])
        fig_especialidade.update_layout(xaxis_title = 'Mês', yaxis_title = '% de Pacientes',
                                        legend_title = 'Especialidade')
        fig_especialidade.update_xaxes(tickformat = "%m-%Y")
        fig_especialidade.update_traces(texttemplate = '%{y:.2f}%', textposition = 'inside')
        st.plotly_chart(fig_especialidade)

        # Calcular o número de pacientes por sexo ao longo do tempo
        sexo_por_mes = df_filtrado.groupby(
            [pd.Grouper(key = 'data_internamento', freq = 'M'), 'sexo']).size().unstack(
            fill_value = 0).reset_index()

        # Calcular as porcentagens
        sexo_por_mes_percent = sexo_por_mes.copy()
        total_por_mes = sexo_por_mes_percent [['Feminino', 'Masculino']].sum(axis = 1)
        sexo_por_mes_percent ['Feminino'] = (sexo_por_mes ['Feminino'] / total_por_mes) * 100
        sexo_por_mes_percent ['Masculino'] = (sexo_por_mes ['Masculino'] / total_por_mes) * 100

        fig_sexo = px.bar(sexo_por_mes_percent, x = 'data_internamento', y = ['Feminino', 'Masculino'],
                          labels = {'data_internamento':'Mês', 'value':'% de Pacientes', 'variable':'Sexo'},
                          title = 'Sexo (%)',
                          barmode = 'stack',
                          color_discrete_sequence = ['#F4A460', '#257683'])
        fig_sexo.update_layout(xaxis_title = 'Mês', yaxis_title = '% de Pacientes', legend_title = 'Sexo')
        fig_sexo.update_xaxes(tickformat = "%m-%Y")
        fig_sexo.update_traces(texttemplate = '%{y:.2f}%', textposition = 'inside')
        st.plotly_chart(fig_sexo)

        # Calcular a média de idade
        media_idade_por_mes_uti =\
            df_filtrado.groupby(['uti_combined', pd.Grouper(key = 'data_internamento', freq = 'M')]) [
                'idade'].mean().reset_index()

        # Obter cores suficientes para as linhas
        unique_utis = media_idade_por_mes_uti ['uti_combined'].unique()
        num_utis = len(unique_utis)
        uti_colors = [color for sublist in palette.Paired.values() for color in sublist] [:num_utis]

        # Criação do gráfico de linha
        fig = go.Figure()

        # Adicionar traços e anotações para cada UTI
        for i, uti in enumerate(unique_utis):
            df_uti = media_idade_por_mes_uti [media_idade_por_mes_uti ['uti_combined'] == uti]
            fig.add_trace(
                go.Scatter(x = df_uti ['data_internamento'], y = df_uti ['idade'], mode = 'lines+markers', name = uti,
                           line = dict(color = "#257683")))

            # Adicionar anotações
            for j in range(len(df_uti)):
                fig.add_annotation(x = df_uti ['data_internamento'].iloc [j], y = df_uti ['idade'].iloc [j],
                                   text = f"{df_uti ['idade'].iloc [j]:.0f}", showarrow = True, arrowhead = 2, ax = 0,
                                   ay = -10)

        # Atualizar layout
        fig.update_layout(title = 'Média de Idade', xaxis_title = 'Mês', yaxis_title = 'Média de Idade',
                          showlegend = True,
                          xaxis = dict(tickformat = "%m-%Y"))

        # Definir o valor mínimo do eixo y como 0
        fig.update_yaxes(range = [0, 100])

        # Mostrar gráfico
        st.plotly_chart(fig)

        # Definir as faixas etárias
        bins = [0, 15, 20, 40, 60, 80, 100]
        labels = ['≤ 14', '15 a 19', '20 a 39', '40 a 59', '60 a 79', '80+']

        # Adicionar uma coluna com a faixa etária
        df_filtrado ['faixa_etaria'] = pd.cut(df_filtrado ['idade'], bins = bins, labels = labels, right = False)

        # Agrupar os dados por UTI, mês e faixa etária
        faixa_etaria_por_mes_uti =\
            df_filtrado.groupby(['uti_combined', pd.Grouper(key = 'data_internamento', freq = 'M'), 'faixa_etaria']) [
                'idade'].count().reset_index()

        # Renomear a coluna de contagem de idade para 'contagem'
        faixa_etaria_por_mes_uti = faixa_etaria_por_mes_uti.rename(columns = {'idade':'contagem'})

        # Calcular o total de pacientes por UTI e mês
        total_por_mes_uti = faixa_etaria_por_mes_uti.groupby(['uti_combined', 'data_internamento']) [
            'contagem'].sum().reset_index()
        total_por_mes_uti = total_por_mes_uti.rename(columns = {'contagem':'total'})

        # Mesclar para adicionar a coluna de total ao dataframe principal
        faixa_etaria_por_mes_uti = faixa_etaria_por_mes_uti.merge(total_por_mes_uti,
                                                                  on = ['uti_combined', 'data_internamento'])

        # Calcular a porcentagem para cada faixa etária
        faixa_etaria_por_mes_uti ['porcentagem'] = (faixa_etaria_por_mes_uti ['contagem'] / faixa_etaria_por_mes_uti [
            'total']) * 100

        # Criação do gráfico
        fig = px.bar(faixa_etaria_por_mes_uti, x = 'data_internamento', y = 'porcentagem', color = 'faixa_etaria',
                     barmode = 'stack', facet_col = 'uti_combined', category_orders = {'faixa_etaria':labels},
                     labels = {'data_internamento':'Mês', 'porcentagem':'Porcentagem de Pacientes (%)',
                               'faixa_etaria':'Faixa Etária', 'uti_combined':'UTI'},
                     color_discrete_sequence = palette.Paired [6])

        # Atualizar layout
        fig.update_layout(title = 'Faixa Etária (%)', xaxis_title = 'Mês',
                          yaxis_title = 'Porcentagem de Pacientes (%)', showlegend = True,
                          xaxis = dict(tickformat = "%m-%Y"))

        # Adicionar rótulos de porcentagem dentro das barras
        fig.update_traces(texttemplate = '%{y:.2f}%', textposition = 'inside')

        # Mostrar gráfico
        st.plotly_chart(fig)

        # Calcular a média do Apache
        media_apache_por_mes_uti =\
            df_filtrado.groupby(['uti_combined', pd.Grouper(key = 'data_internamento', freq = 'M')]) [
                'apache'].mean().reset_index()

        # Obter cores suficientes para as linhas
        unique_utis = media_apache_por_mes_uti ['uti_combined'].unique()
        num_utis = len(unique_utis)
        uti_colors = [color for sublist in palette.Paired.values() for color in sublist] [:num_utis]

        # Criação do gráfico de linha
        fig = go.Figure()

        # Adicionar traços e anotações para cada UTI
        for i, uti in enumerate(unique_utis):
            df_uti = media_apache_por_mes_uti [media_apache_por_mes_uti ['uti_combined'] == uti]
            fig.add_trace(
                go.Scatter(x = df_uti ['data_internamento'], y = df_uti ['apache'], mode = 'lines+markers', name = uti,
                           line = dict(color = "#257683")))

            # Adicionar anotações
            for j in range(len(df_uti)):
                fig.add_annotation(x = df_uti ['data_internamento'].iloc [j], y = df_uti ['apache'].iloc [j],
                                   text = f"{df_uti ['apache'].iloc [j]:.1f}", showarrow = True, arrowhead = 2, ax = 0,
                                   ay = -10)

        # Atualizar layout
        fig.update_layout(title = 'Apache II Médio', xaxis_title = 'Mês', yaxis_title = 'Média do Apache',
                          showlegend = True)
        fig.update_xaxes(tickformat = "%Y-%m")

        # Definir o valor mínimo do eixo y como 0
        fig.update_yaxes(range = [0, 30])

        # Mostrar gráfico
        st.plotly_chart(fig)

        # Converter a coluna 'data_escore_diario' para datetime
        df_filtrado ['data_escore_diario'] = pd.to_datetime(df_filtrado ['data_escore_diario'])

        # Filtrar os dados para os anos de 2023 e 2024
        df_filtrado ['data_escore_diario'] = pd.to_datetime(df_filtrado ['data_escore_diario'])
        df_2023_2024 = df_filtrado [df_filtrado ['data_escore_diario'].dt.year.isin([2023, 2024])]

        # Calcular a média do SOFA
        media_sofa_por_mes_uti =\
            df_2023_2024.groupby(['uti_combined', pd.Grouper(key = 'data_escore_diario', freq = 'M')]) [
                'sofa'].mean().reset_index()

        # Obter cores suficientes para as linhas
        unique_utis = media_sofa_por_mes_uti ['uti_combined'].unique()
        num_utis = len(unique_utis)
        uti_colors = [color for sublist in palette.Paired.values() for color in sublist] [:num_utis]

        # Criação do gráfico de linha
        fig = go.Figure()

        # Adicionar traços e anotações para cada UTI
        for i, uti in enumerate(unique_utis):
            df_uti = media_sofa_por_mes_uti [media_sofa_por_mes_uti ['uti_combined'] == uti]
            fig.add_trace(
                go.Scatter(x = df_uti ['data_escore_diario'], y = df_uti ['sofa'], mode = 'lines+markers', name = uti,
                           line = dict(color = "#257683")))

            # Adicionar anotações
            for j in range(len(df_uti)):
                fig.add_annotation(x = df_uti ['data_escore_diario'].iloc [j], y = df_uti ['sofa'].iloc [j],
                                   text = f"{df_uti ['sofa'].iloc [j]:.1f}", showarrow = True, arrowhead = 2, ax = 0,
                                   ay = -10)

        # Atualizar layout
        fig.update_layout(title = 'SOFA Médio', xaxis_title = 'Mês', yaxis_title = 'Média do SOFA', showlegend = True)
        fig.update_xaxes(tickformat = "%Y-%m")

        # Definir o valor mínimo do eixo y como 0
        fig.update_yaxes(range = [0, 15])

        # Mostrar gráfico
        st.plotly_chart(fig)

        # Lista de todas as letras possíveis de SAV (A, B, C, D, E)
        savs_possiveis = ["A", "B", "C", "D", "E"]

        # Dicionário de cores personalizadas para cada letra de SAV
        cores_personalizadas = {
            "A":"#006400",
            "B":"#228b22",
            "C":"#ffff00",
            "D":"#ff6347",
            "E":"#ff0000"
        }

        # Calcular a distribuição de SAVs por mês
        sav_por_mes = df_filtrado.groupby(
            [pd.Grouper(key = 'data_internamento', freq = 'M'), 'sav_admissao']
        ).size().unstack(fill_value = 0).reset_index()

        # Garantir que todas as letras possíveis estejam presentes como colunas
        for sav in savs_possiveis:
            if sav not in sav_por_mes.columns:
                sav_por_mes [sav] = 0

        # Ordenar as colunas para garantir que fiquem na ordem correta
        sav_por_mes = sav_por_mes [['data_internamento'] + savs_possiveis]

        # Calcular as porcentagens
        sav_por_mes_percent = sav_por_mes.copy()
        total_por_mes = sav_por_mes_percent.iloc [:, 1:].sum(axis = 1)  # Soma das colunas de A até E
        for col in savs_possiveis:
            sav_por_mes_percent [col] = (sav_por_mes_percent [col] / total_por_mes) * 100

        # Gráfico de SAVs em %
        fig_sav = px.bar(sav_por_mes_percent, x = 'data_internamento',
                         y = savs_possiveis,
                         title = 'SAV Admissão (%)',
                         labels = {'data_internamento':'Mês', 'value':'% de Pacientes',
                                   'variable':'SAV'},
                         barmode = 'stack',
                         color_discrete_map = cores_personalizadas)

        fig_sav.update_layout(xaxis_title = 'Mês', yaxis_title = '% de Pacientes', legend_title = 'SAV')

        # Ajustar o eixo y para variar de 60% a 100%
        fig_sav.update_yaxes(range = [70, 100])

        fig_sav.update_xaxes(tickformat = "%m-%Y")
        fig_sav.update_traces(texttemplate = '%{y:.2f}%', textposition = 'inside')

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig_sav)

        # Verifique se a coluna 'duracao_internamento' está presente no DataFrame
        if 'data_internamento' not in df_filtrado.columns or 'duracao_internamento' not in df_filtrado.columns:
            st.write("")
        else:
            # Calcular a duração da internação usando a coluna 'duracao_internamento'
            df_filtrado ['data_internamento'] = pd.to_datetime(df_filtrado ['data_internamento'])

            # Utilizando a coluna 'duracao_internamento' para representar a duração da internação
            df_filtrado = df_filtrado.dropna(
                subset = ['duracao_internamento'])  # Remove linhas com valores NaN na coluna 'duracao_internamento'

            # Verificar se o DataFrame possui dados após o filtro
            if df_filtrado.empty:
                st.write("Nenhum dado disponível após o filtro.")
            else:
                # Agrupar por mês e calcular a soma total de dias de internação
                df_filtrado ['mes_internamento'] = df_filtrado ['data_internamento'].dt.strftime('%Y-%m')
                soma_dias_por_mes = df_filtrado.groupby('mes_internamento') ['duracao_internamento'].sum().reset_index()

                # Criar o gráfico de linha
                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x = soma_dias_por_mes ['mes_internamento'],
                    y = soma_dias_por_mes ['duracao_internamento'],
                    mode = 'lines+markers',
                    line = dict(color = '#257683'),  # Cor da linha
                    marker = dict(color = '#257683'),  # Cor dos marcadores
                    name = 'Soma de Dias de Internação'
                ))

                # Adicionar anotações (números acima dos pontos)
                annotations = []
                for i, row in soma_dias_por_mes.iterrows():
                    annotations.append(dict(
                        x = row ['mes_internamento'],
                        y = row ['duracao_internamento'],
                        text = f'{int(row ["duracao_internamento"])}',
                        # Convertendo para inteiro e formatando como texto
                        showarrow = True,
                        arrowhead = 2,
                        ax = 0,
                        ay = -10
                    ))

                # Configurar layout do gráfico
                fig.update_layout(
                    title = 'Número de Diárias',
                    xaxis_title = 'Mês',
                    yaxis_title = 'Soma de Dias de Internação',
                    xaxis = dict(tickformat = "%Y-%m"),
                    yaxis = dict(range = [0, soma_dias_por_mes ['duracao_internamento'].max() + 50]),
                    # Definindo o intervalo do eixo y dinamicamente
                    annotations = annotations
                )

                # Mostrar gráfico utilizando Streamlit
                st.plotly_chart(fig)

        # Garantir que 'data_internamento' esteja no formato datetime
        df ['data_internamento'] = pd.to_datetime(df ['data_internamento'], errors = 'coerce')

        # Filtrar valores inválidos em 'data_internamento'
        df = df [df ['data_internamento'].notna()]

        # Filtrar os dados apenas para o ano de 2024
        df = df [df ['data_internamento'].dt.year == 2024]

        # Verificar se há dados após o filtro
        if df.empty:
            raise ValueError("Nenhum registro encontrado para o ano de 2024.")

        # Calcular a média mensal do tempo de permanência (usando 'data_ajustada')
        media_tempo_internamento = df.groupby(pd.Grouper(key = 'data_internamento', freq = 'M')) [
            'data_ajustada'].mean().reset_index()

        # Definir a média de referência
        media_referencia_anahp_2024 = 4.10

        # Criar figura Plotly
        fig = go.Figure()

        # Adicionar a linha da média mensal de permanência
        fig.add_trace(go.Scatter(
            x = media_tempo_internamento ['data_internamento'],
            y = media_tempo_internamento ['data_ajustada'],
            mode = 'lines+markers',
            name = 'Média Mensal de Permanência',
            line = dict(color = '#257683', width = 2),
            marker = dict(color = '#257683', size = 8,
                          line = dict(color = '#257683', width = 1)),
            text = media_tempo_internamento ['data_ajustada'],
            textposition = 'top center',
            textfont = dict(color = '#257683', size = 12)
        ))

        # Adicionar linha de referência Anahp 2024
        fig.add_trace(go.Scatter(
            x = media_tempo_internamento ['data_internamento'],
            y = [media_referencia_anahp_2024] * len(media_tempo_internamento),
            mode = 'lines',
            name = 'Referência Anahp 2024 (4.10 dias)',
            line = dict(color = 'gold', dash = 'dash')
        ))

        # Adicionar anotações (labels) sobre os pontos
        for i, row in media_tempo_internamento.iterrows():
            fig.add_annotation(
                x = row ['data_internamento'],
                y = row ['data_ajustada'],
                text = f"{row ['data_ajustada']:.2f}",
                showarrow = True,
                arrowhead = 2,
                ax = 0,
                ay = -10,
                font = dict(color = 'white', size = 12)
            )

        # Atualizar layout do gráfico
        fig.update_layout(
            title = 'Tempo Médio de Permanência',
            xaxis_title = 'Mês',
            yaxis_title = 'Dias',
            legend_title = ''
        )

        # Definir o valor mínimo do eixo y como 0
        fig.update_yaxes(range = [0, 5])

        # Mostrar o gráfico utilizando Streamlit
        st.plotly_chart(fig)

        # Calcular o número de saídas por mês
        df_filtrado ['data_hora_final'] = pd.to_datetime(df_filtrado ['data_hora_final'], format='ISO8601')
        df_filtrado ['mes_saida'] = df_filtrado ['data_hora_final'].dt.strftime('%Y-%m')
        saidas_por_mes = df_filtrado.groupby('mes_saida').size().reset_index(name = 'numero_saidas')

        # Criação do gráfico de barras
        fig = go.Figure()

        # Adicionar trace de barras
        fig.add_trace(go.Bar(
            x = saidas_por_mes ['mes_saida'],
            y = saidas_por_mes ['numero_saidas'],
            text = saidas_por_mes ['numero_saidas'],
            textposition = 'auto',
            marker_color = '#257683'  # Define a cor das barras
        ))

        # Atualizar layout
        fig.update_layout(
            title = 'Número de Saídas da UTI',
            xaxis_title = 'Mês',
            yaxis_title = 'Número de Saídas',
            xaxis = dict(tickformat = "%Y-%m")
        )

        # Mostrar gráfico utilizando Streamlit
        st.plotly_chart(fig)

        # Calcular a duração da internação em dias
        df_filtrado ['data_internamento'] = pd.to_datetime(df_filtrado ['data_internamento'], format='ISO8601')
        df_filtrado ['data_hora_final'] = pd.to_datetime(df_filtrado ['data_hora_final'], format='ISO8601')

        # Filtrar os reinternamentos
        df_reinternamentos = df_filtrado [df_filtrado ['reinternamento'] == 'Sim']

        # Agrupar por mês e contar o número de reinternamentos
        df_reinternamentos ['mes_internamento'] = df_reinternamentos ['data_internamento'].dt.strftime(
            '%Y-%m')
        reinternamentos_por_mes = df_reinternamentos.groupby('mes_internamento').size().reset_index(
            name = 'numero_reinternamentos')

        # Agrupar por mês e contar o número de saídas
        df_filtrado ['mes_saida'] = df_filtrado ['data_hora_final'].dt.strftime('%Y-%m')
        saidas_por_mes = df_filtrado.groupby('mes_saida').size().reset_index(name = 'numero_saidas')

        # Mesclar os DataFrames para ter reinternamentos e saídas no mesmo DataFrame
        df_merged = pd.merge(saidas_por_mes, reinternamentos_por_mes, left_on = 'mes_saida',
                             right_on = 'mes_internamento', how = 'left')

        # Substituir NaN por 0 para reinternamentos onde não há dados
        df_merged ['numero_reinternamentos'].fillna(0, inplace = True)

        # Calcular a porcentagem de reinternamentos
        df_merged ['percentual_reinternamentos'] = (df_merged ['numero_reinternamentos'] / df_merged [
            'numero_saidas']) * 100

        # Criar o gráfico de linha
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x = df_merged ['mes_saida'],
            y = df_merged ['percentual_reinternamentos'],
            mode = 'lines+markers',
            line = dict(color = '#257683'),  # Cor da linha
            marker = dict(color = '#257683'),  # Cor dos marcadores
            name = 'Percentual de Reinternamentos'
        ))

        # Adicionar anotações (números acima dos pontos)
        annotations = []
        for i, row in df_merged.iterrows():
            annotations.append(dict(
                x = row ['mes_saida'],
                y = row ['percentual_reinternamentos'],
                text = f'{int(row ["percentual_reinternamentos"])}%',
                # Formatar como porcentagem sem casas decimais
                showarrow = True,
                arrowhead = 2,
                ax = 0,
                ay = -10
            ))

        fig.update_layout(
            title = 'Reinternamentos (%)',
            xaxis_title = 'Mês',
            yaxis_title = 'Percentual de Reinternamentos (%)',
            xaxis = dict(tickformat = "%Y-%m"),
            yaxis = dict(range = [0, 10]),  # Ajustar conforme necessário para porcentagem
            annotations = annotations
        )

        # Mostrar gráfico utilizando Streamlit
        st.plotly_chart(fig)

        # Calcular a duração da internação em dias
        df_filtrado ['data_internamento'] = pd.to_datetime(df_filtrado ['data_internamento'], format='ISO8601')
        df_filtrado ['data_hora_final'] = pd.to_datetime(df_filtrado ['data_hora_final'], format='ISO8601')

        # Filtrar as internações com o mesmo CID em 24 horas
        df_mesmo_cid = df_filtrado [df_filtrado ['mesmo_cid_24h'] == 'Sim']

        # Agrupar por mês e contar o número de internações com o mesmo CID
        df_mesmo_cid ['mes_internamento'] = df_mesmo_cid ['data_internamento'].dt.strftime('%Y-%m')
        mesmo_cid_por_mes = df_mesmo_cid.groupby('mes_internamento').size().reset_index(
            name = 'numero_mesmo_cid')

        # Agrupar por mês e contar o número de saídas
        df_filtrado ['mes_saida'] = df_filtrado ['data_hora_final'].dt.strftime('%Y-%m')
        saidas_por_mes = df_filtrado.groupby('mes_saida').size().reset_index(name = 'numero_saidas')

        # Mesclar os DataFrames para ter internações com o mesmo CID e saídas no mesmo DataFrame
        df_merged = pd.merge(saidas_por_mes, mesmo_cid_por_mes, left_on = 'mes_saida',
                             right_on = 'mes_internamento', how = 'left')

        # Substituir NaN por 0 para internações com o mesmo CID onde não há dados
        df_merged ['numero_mesmo_cid'].fillna(0, inplace = True)

        # Calcular a porcentagem de internações com o mesmo CID
        df_merged ['percentual_mesmo_cid'] = (df_merged ['numero_mesmo_cid'] / df_merged [
            'numero_saidas']) * 100

        # Criar o gráfico de linha
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x = df_merged ['mes_saida'],
            y = df_merged ['percentual_mesmo_cid'],
            mode = 'lines+markers',
            line = dict(color = '#257683'),  # Cor da linha
            marker = dict(color = '#257683'),  # Cor dos marcadores
            name = 'Percentual de Reinternações com o Mesmo CID em 24h'
        ))

        # Adicionar anotações (números acima dos pontos)
        annotations = []
        for i, row in df_merged.iterrows():
            annotations.append(dict(
                x = row ['mes_saida'],
                y = row ['percentual_mesmo_cid'],
                text = f'{int(row ["percentual_mesmo_cid"])}%',
                # Formatar como porcentagem sem casas decimais
                showarrow = True,
                arrowhead = 2,
                ax = 0,
                ay = -10
            ))

        fig.update_layout(
            title = ' Reinternamento pelo Mesmo CID em 24 Horas (%)',
            xaxis_title = 'Mês',
            yaxis_title = 'Percentual de Reinternações (%)',
            xaxis = dict(tickformat = "%Y-%m"),
            yaxis = dict(range = [0, 10]),  # Ajustar conforme necessário para porcentagem
            annotations = annotations
        )

        # Mostrar gráfico utilizando Streamlit
        st.plotly_chart(fig)

        # Converter a coluna data_hora_final para datetime
        df_filtrado ['data_hora_obito'] = pd.to_datetime(df_filtrado ['data_hora_obito'], format='ISO8601')

        # Agrupar por mês e contar o número de óbitos
        df_filtrado ['mes_obito'] = df_filtrado ['data_hora_obito'].dt.strftime('%Y-%m')
        obitos_por_mes = df_filtrado.groupby('mes_obito').size().reset_index(name = 'numero_obitos')

        # Criar o gráfico de barras
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x = obitos_por_mes ['mes_obito'],
            y = obitos_por_mes ['numero_obitos'],
            text = obitos_por_mes ['numero_obitos'],
            textposition = 'auto',
            marker = dict(color = '#257683')  # Cor das barras
        ))

        fig.update_layout(
            title = 'Número de Óbitos',
            xaxis_title = 'Mês',
            yaxis_title = '',
            xaxis = dict(tickformat = "%Y-%m"),
            yaxis = dict(range = [0, obitos_por_mes ['numero_obitos'].max() + 10])
            # Ajustar o intervalo do eixo y conforme necessário
        )

        # Mostrar gráfico utilizando Streamlit
        st.plotly_chart(fig)

        df_filtrado ['mes'] = df_filtrado ['data_hora_final'].dt.to_period('M')
        media_apache_por_mes = df_filtrado.groupby('mes') ['apache'].mean()

        def calcular_probabilidade_morte (media_apache):
            return np.exp(-3.517 + media_apache * 0.146) / (1 + np.exp(-3.517 + media_apache * 0.146))

        probabilidade_morte_prevista = media_apache_por_mes.apply(calcular_probabilidade_morte) * 100

        obitos_por_mes = df_filtrado [df_filtrado ['desfecho_uti'] == 'Óbito'].groupby('mes').size()
        saidas_por_mes = df_filtrado.groupby('mes').size()
        taxa_mortalidade_real = (obitos_por_mes / saidas_por_mes) * 100

        ultimos_12_meses = probabilidade_morte_prevista.index [-12:]

        probabilidade_morte_prevista = probabilidade_morte_prevista [ultimos_12_meses]
        taxa_mortalidade_real = taxa_mortalidade_real [ultimos_12_meses]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x = probabilidade_morte_prevista.index.astype(str),
            y = probabilidade_morte_prevista.values,
            mode = 'lines+markers+text',
            text = [f'{val:.1f}%' for val in probabilidade_morte_prevista.values],
            textposition = 'top center',
            name = 'Taxa de Mortalidade Predita pelo APACHE II',
            line = dict(color = '#FFB257'),
            marker = dict(color = '#FFB257')
        ))

        fig.add_trace(go.Scatter(
            x = taxa_mortalidade_real.index.astype(str),
            y = taxa_mortalidade_real.values,
            mode = 'lines+markers+text',
            text = [f'{val:.1f}%' for val in taxa_mortalidade_real.values],
            textposition = 'top center',
            name = 'Taxa de Mortalidade encontrada',
            line = dict(color = '#257683', width = 2),
            marker = dict(color = '#257683', size = 8)
        ))

        fig.update_layout(
            title = 'Taxa de Mortalidade Predita pelo APACHE II x Taxa de Mortalidade',
            xaxis_title = 'Mês',
            yaxis_title = 'Taxa de Mortalidade (%)',
            xaxis = dict(type = 'category'),
            yaxis = dict(range = [0, 30]),
            legend = dict(
                yanchor = "top",
                y = 0.99,
                xanchor = "right",
                x = 1.1  # Ajuste a posição da legenda mais próxima do gráfico
            ),
            width = 1600,  # Aumentando a largura do gráfico
            height = 600  # Mantendo a mesma altura
        )

        st.plotly_chart(fig, use_container_width = False)

        # Lista de todas as letras possíveis de SAV (A, B, C, D, E)
        savs_possiveis = ["A", "B", "C", "D", "E"]

        # Dicionário de cores personalizadas para cada letra de SAV
        cores_personalizadas = {
            "A":"#006400",
            "B":"#228b22",
            "C":"#ffff00",
            "D":"#ff6347",
            "E":"#ff0000"
        }

        # Supondo que df já esteja definido e tenha as colunas corretas
        df ['data_hora_final'] = pd.to_datetime(df ['data_hora_final'], format='ISO8601')

        # Filtrar o DataFrame para incluir apenas os óbitos
        df_filtrado_obito = df [df ['desfecho_uti'] == 'Óbito']

        # Filtrar para incluir dados a partir de janeiro de 2023
        data_inicio = pd.to_datetime('2023-01-01')
        df_filtrado_obito = df_filtrado_obito [df_filtrado_obito ['data_hora_final'] >= data_inicio]

        # Calcular a distribuição de SAVs por mês, usando "data_hora_final"
        sav_por_mes_obito = df_filtrado_obito.groupby(
            [pd.Grouper(key = 'data_hora_final', freq = 'M'), 'sav_obito']
        ).size().unstack(fill_value = 0).reset_index()

        # Garantir que todas as letras possíveis estejam presentes como colunas
        for sav in savs_possiveis:
            if sav not in sav_por_mes_obito.columns:
                sav_por_mes_obito [sav] = 0

        # Ordenar as colunas para garantir que fiquem na ordem correta
        sav_por_mes_obito = sav_por_mes_obito [['data_hora_final'] + savs_possiveis]

        # Calcular as porcentagens, garantindo que somem 100% por mês
        sav_por_mes_percent_obito = sav_por_mes_obito.copy()
        total_por_mes_obito = sav_por_mes_percent_obito [savs_possiveis].sum(axis = 1)  # Soma das colunas de A até E

        for col in savs_possiveis:
            sav_por_mes_percent_obito [col] = (sav_por_mes_percent_obito [col] / total_por_mes_obito.replace(0,
                                                                                                             1)) * 100  # Evitar divisão por zero

        # Garantir que as porcentagens somem 100% para cada mês
        sav_por_mes_percent_obito [savs_possiveis] = sav_por_mes_percent_obito [savs_possiveis].apply(
            lambda x:(x / x.sum()) * 100 if x.sum() > 0 else x, axis = 1)

        # Gráfico de SAVs em %
        fig_sav_obito = px.bar(sav_por_mes_percent_obito,
                               x = 'data_hora_final',
                               y = savs_possiveis,
                               title = 'SAV Óbito (%)',
                               labels = {'data_hora_final':'Mês', 'value':'% de Pacientes', 'variable':'SAV'},
                               barmode = 'stack',
                               color_discrete_map = cores_personalizadas)

        fig_sav_obito.update_layout(xaxis_title = 'Mês', yaxis_title = '% de Pacientes', legend_title = 'SAV')

        # Ajustar o eixo y para variar de 0% a 100%
        fig_sav_obito.update_yaxes(range = [0, 100])

        # Formatando os rótulos de data no eixo X
        fig_sav_obito.update_xaxes(tickformat = "%m-%Y")

        # Exibir porcentagens dentro das barras
        fig_sav_obito.update_traces(texttemplate = '%{y:.2f}%', textposition = 'inside')

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig_sav_obito)

        # Mapeamento das descrições longas para números
        priority_mapping = {
            "<b>Prioridade 1:</b> Paciente necessita de intervenções de suporte à vida, com alta probabilidade de recuperação e sem nenhuma limitação de suporte terapêutico.":1,
            "<b>Prioridade 2:</b> Paciente necessita de monitorização intensiva, pelo alto risco de precisarem de intervenção imediata, e sem nenhuma limitação de suporte terapêutico.":2,
            "<b>Prioridade 3:</b> Paciente necessita de intervenções de suporte à vida, com baixa probabilidade de recuperação ou com limitação de intervenção terapêutica.":3,
            "<b>Prioridade 4:</b> Paciente necessita de monitorização intensiva, pelo alto risco de precisarem de intervenção imediata, mas com limitação de intervenção terapêutica.":4,
            "<b>Prioridade 5:</b> Paciente com doença em fase de terminalidade, ou moribundos, sem possibilidade de recuperação. Em geral, esses pacientes não são apropriados para admissão na UTI (exceto se forem potenciais doadores de órgãos). No entanto, seu ingresso pode ser justificado em caráter excepcional, considerando as peculiaridades do caso e condicionado ao critério do médico intensivista.":5,
        }

        # Dicionário de cores personalizadas para cada prioridade
        cores_personalizadas = {
            1:"#006400",  # Verde escuro
            2:"#228b22",  # Verde
            3:"#ffff00",  # Amarelo
            4:"#ff6347",  # Tomate
            5:"#ff0000"  # Vermelho
        }

        # Carregar o DataFrame (substitua pelo carregamento real do seu arquivo CSV)
        df = pd.read_csv('data_work.csv')

        # Aplicar o mapeamento no DataFrame
        df ['prioridade_atendimento_num'] = df ['prioridade_atendimento'].map(priority_mapping)

        # Converter colunas de data para o formato datetime
        df ['data_hora_final'] = pd.to_datetime(df ['data_hora_final'], format='ISO8601')
        df ['data_internamento'] = pd.to_datetime(df ['data_internamento'], format='ISO8601')

        # Filtrar dados a partir de 01/2023
        start_date = pd.Timestamp('2023-01-01')
        df = df [df ['data_internamento'] >= start_date]

        # Calcular a distribuição de prioridades de atendimento por mês
        prioridade_por_mes = df.groupby([
            pd.Grouper(key = 'data_internamento', freq = 'M'), 'prioridade_atendimento_num'
        ]).size().unstack(fill_value = 0).reset_index()

        # Garantir que todas as prioridades possíveis estejam presentes como colunas (de 1 a 5)
        prioridades_possiveis = [1, 2, 3, 4, 5]
        for prioridade in prioridades_possiveis:
            if prioridade not in prioridade_por_mes.columns:
                prioridade_por_mes [prioridade] = 0

        # Ordenar as colunas para garantir que fiquem na ordem correta
        prioridade_por_mes = prioridade_por_mes [['data_internamento'] + prioridades_possiveis]

        # Calcular as porcentagens
        prioridade_por_mes_percent = prioridade_por_mes.copy()
        total_por_mes_prioridade = prioridade_por_mes_percent.iloc [:, 1:].sum(
            axis = 1)  # Soma das colunas de 1 até 5
        for col in prioridades_possiveis:
            prioridade_por_mes_percent [col] = (prioridade_por_mes_percent [col] / total_por_mes_prioridade) * 100

        # Mapeamento para nomes amigáveis de prioridade
        priority_labels = {
            1:"Prioridade 1",
            2:"Prioridade 2",
            3:"Prioridade 3",
            4:"Prioridade 4",
            5:"Prioridade 5"
        }

        # Criação do gráfico de barras empilhadas para prioridades mês a mês
        fig_prioridade = px.bar(
            prioridade_por_mes_percent,
            x = 'data_internamento',
            y = prioridades_possiveis,
            title = 'Prioridade de Atendimento (%)',
            labels = {'data_internamento':'Mês', 'value':'% de Pacientes', 'variable':'Prioridade'},
            barmode = 'stack',
            color_discrete_sequence = [cores_personalizadas [p] for p in prioridades_possiveis]
        )

        # Atualizar layout
        fig_prioridade.update_layout(
            xaxis_title = 'Mês',
            yaxis_title = '%',
            legend_title = 'Prioridade',
            legend = dict(
                title = 'Prioridade',
                itemsizing = 'constant',
                font = dict(size = 10),
                title_font = dict(size = 12),
            ),
        )

        # Ajustar o eixo y para variar de 0% a 100%
        fig_prioridade.update_yaxes(range = [0, 100])

        # Formatar o texto das porcentagens dentro das barras
        fig_prioridade.update_traces(
            texttemplate = '%{y:.2f}%',
            textposition = 'inside',
            hovertemplate = '<b>Prioridade %{x}</b><br>%{y:.2f}%',
        )

        # Ajustar a legenda para exibir "Prioridade X"
        new_names = {str(i):f'Prioridade {i}' for i in prioridades_possiveis}
        fig_prioridade.for_each_trace(lambda t:t.update(name = new_names [t.name]))

        # Mostrar gráfico no Streamlit
        st.plotly_chart(fig_prioridade)

        # 1. Calculando a média do APACHE por mês
        df_filtrado ['mes'] = df_filtrado ['data_hora_final'].dt.to_period('M')
        media_apache_por_mes = df_filtrado.groupby('mes') ['apache'].mean()

        # 2. Fórmula para calcular a probabilidade de morte prevista
        def calcular_probabilidade_morte (media_apache):
            return np.exp(-3.517 + media_apache * 0.146) / (1 + np.exp(-3.517 + media_apache * 0.146))

        # Aplicando a fórmula para obter a probabilidade de morte prevista por mês
        probabilidade_morte_prevista = media_apache_por_mes.apply(
            calcular_probabilidade_morte) * 100  # Convertendo para porcentagem

        # 3. Calculando o número de óbitos por mês
        obitos_por_mes = df_filtrado [df_filtrado ['desfecho_uti'] == 'Óbito'].groupby('mes').size()

        # 4. Calculando o número de saídas por mês
        saidas_por_mes = df_filtrado.groupby('mes').size()

        # 5. Calculando a taxa de mortalidade real por mês (óbitos por saídas)
        taxa_mortalidade_real = (obitos_por_mes / saidas_por_mes) * 100  # Convertendo para porcentagem

        # 6. Filtrando para exibir apenas os últimos 12 meses
        ultimos_12_meses = probabilidade_morte_prevista.index [-12:]
        probabilidade_morte_prevista = probabilidade_morte_prevista [ultimos_12_meses]
        taxa_mortalidade_real = taxa_mortalidade_real [ultimos_12_meses]

        # Adicionando a criação do gráfico de RMP
        # 1. Calculando o RMP (Razão entre a taxa de mortalidade encontrada e a predita)
        rmp = taxa_mortalidade_real / probabilidade_morte_prevista

        # 2. Criando o gráfico de RMP com Plotly
        fig_rmp = go.Figure()

        # Adicionando a linha de RMP
        fig_rmp.add_trace(go.Scatter(
            x = rmp.index.astype(str),
            y = rmp.values,
            mode = 'lines+markers+text',
            text = [f'{val:.2f}' for val in rmp.values],
            textposition = 'top center',
            name = 'RMP',
            line = dict(color = '#257683', width = 2),
            marker = dict(color = '#257683', size = 8),
            showlegend = False
        ))

        # Adicionando a linha de referência fixa de 0,97
        fig_rmp.add_trace(go.Scatter(
            x = [str(x) for x in rmp.index],
            y = [0.97] * len(rmp),
            mode = 'lines',
            name = 'Referência (Quintairos, 2021) UTI\'s Brasileiras',
            line = dict(color = 'gold', width = 2, dash = 'dash')
        ))

        # Adicionando anotação para a linha de referência
        fig_rmp.add_annotation(
            x = str(rmp.index [-1]),  # Último mês convertido para string
            y = 0.97,
            text = '0,97',
            showarrow = True,
            arrowhead = 1,
            ax = 0,
            ay = -20
        )

        # Atualizando o layout do gráfico de RMP
        fig_rmp.update_layout(
            title = 'Razão de Mortalidade Padronizada (RMP) = Mortalidade Encontrada / Mortalidade Predita',
            xaxis_title = 'Mês',
            yaxis_title = 'RMP',
            xaxis = dict(type = 'category'),
            yaxis = dict(range = [0, 1.2]),
            legend = dict(
                yanchor = "top",
                y = 1,
                xanchor = "right",
                x = 1
            ),
            margin = dict(l = 0, r = 0, t = 50, b = 50),  # Ajusta as margens para maximizar o espaço
            width = 1500,  # Aumentando a largura do gráfico
            height = 500  # Aumentando a altura do gráfico
        )

        # Mostrar gráfico de RMP no Streamlit
        st.plotly_chart(fig_rmp, use_container_width = True)

        # Função para remover as tags HTML e normalizar os textos, tratando valores NaN
        def clean_html (raw_html):
            if isinstance(raw_html, str):
                soup = BeautifulSoup(raw_html, "html.parser")
                return soup.get_text().strip()
            return raw_html  # Retorna o valor original se não for uma string

        # Mapeamento das descrições longas para números
        priority_mapping = {
            "Muito Ativo - Pessoas que estão robustas, ativas, com energia e motivadas. Essas pessoas normalmente se exercitam regularmente. Elas estão entre as mais ativas para a sua idade.":1,
            "Ativo - Pessoas que não apresentam nenhum sintoma ativo de doença, mas estão menos ativas que as da categoria I. Frequentemente se exercitam ou são muito ativas ocasionalmente, exemplo: em determinada época do ano.":2,
            "Regular - pessoas com problemas de saúde bem controlados, mas não se exercitam regularmente além da caminhada de rotina.":3,
            "Vulnerável - Apesar de não depender dos outros para ajuda diária, frequentemente os sintomas limitam as atividades. Uma queixa comum é sentir-se mais lento e/ou mais cansado ao longo do dia.":4,
            "Levemente Frágil - Estas pessoas frequentemente apresentam lentidão evidente e precisam de ajuda para atividades instrumentais de vida diárias (AIVD) mais complexas (finanças, transporte, trabalho doméstico pesado, medicações). Tipicamente, a fragilidade leve progressivamente prejudica as compras e passeios desacompanhados, preparo de refeições e tarefas domésticas.":5,
            "Moderadamente Frágil - Pessoas que precisam de ajuda em todas as atividades externas e na manutenção da casa. Em casa, frequentemente têm dificuldades com escadas e necessitam de ajuda no banho e podem necessitar de ajuda mínima (apoio próximo) para se vestirem.":6,
            "Muito Frágil - Completamente dependentes para cuidados pessoais, por qualquer causa (física ou cognitiva). No entanto, são aparentemente estáveis e sem alto risco de morte (dentro de 6 meses).":7,
            "Severamente Frágil - Completamente dependentes, aproximando-se do fim da vida. Tipicamente incapazes de se recuperarem de uma doença leve.":8,
            "Doente Terminal - Aproximando-se do fim da vida. Esta categoria se aplica a pessoas com expectativa de vida < 6 meses, sem outra evidência de fragilidade.":9,
        }

        # Dicionário de cores personalizadas para cada fragilidade
        cores_personalizadas = {
            1:"rgb(215,48,39)",
            2:"rgb(244,109,67)",
            3:"rgb(253,174,97)",
            4:"rgb(254,224,144)",
            5:"rgb(255,255,191)",
            6:"rgb(224,243,248)",
            7:"rgb(171,217,233)",
            8:"rgb(116,173,209)",
            9:"rgb(69,117,180)",
        }

        # Carregar o DataFrame (substitua pelo carregamento real do seu arquivo CSV)
        df = pd.read_csv('data_work.csv')

        # Limpar a coluna de fragilidade para remover tags HTML
        df ['fragilidade_limpada'] = df ['fragilidade'].apply(clean_html)

        # Aplicar o mapeamento no DataFrame
        df ['fragilidade_atendimento_num'] = df ['fragilidade_limpada'].map(priority_mapping)

        # Verificar se todas as categorias de fragilidade foram mapeadas corretamente
        mapped_categories = df ['fragilidade_atendimento_num'].unique()
        print("Categorias mapeadas de fragilidade:", mapped_categories)

        # Converter colunas de data para o formato datetime
        df ['data_hora_final'] = pd.to_datetime(df ['data_hora_final'], format = 'ISO8601')
        df ['data_internamento'] = pd.to_datetime(df ['data_internamento'], format = 'ISO8601')

        # Filtrar dados a partir de 01/2023
        start_date = pd.Timestamp('2023-01-01')
        df = df [df ['data_internamento'] >= start_date]

        # Calcular a distribuição de fragilidades de atendimento por mês
        fragilidade_por_mes = df.groupby([
            pd.Grouper(key = 'data_internamento', freq = 'M'), 'fragilidade_atendimento_num'
        ]).size().unstack(fill_value = 0).reset_index()

        # Garantir que todas as fragilidades possíveis estejam presentes como colunas (de 1 a 9)
        fragilidades_possiveis = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        for fragilidade in fragilidades_possiveis:
            if fragilidade not in fragilidade_por_mes.columns:
                fragilidade_por_mes [fragilidade] = 0

        # Ordenar as colunas para garantir que fiquem na ordem correta
        fragilidade_por_mes = fragilidade_por_mes [['data_internamento'] + fragilidades_possiveis]

        # Calcular as porcentagens
        fragilidade_por_mes_percent = fragilidade_por_mes.copy()
        total_por_mes_fragilidade = fragilidade_por_mes_percent.iloc [:, 1:].sum(
            axis = 1)  # Soma das colunas de 1 até 9
        for col in fragilidades_possiveis:
            fragilidade_por_mes_percent [col] = (fragilidade_por_mes_percent [col] / total_por_mes_fragilidade) * 100

        # Transformar o DataFrame de formato wide para long para usar no gráfico
        fragilidade_por_mes_long = fragilidade_por_mes_percent.melt(
            id_vars = ['data_internamento'],
            value_vars = fragilidades_possiveis,
            var_name = 'fragilidade',
            value_name = 'percentual'
        )

        # Mapeamento para nomes amigáveis de prioridade
        priority_labels = {
            1:"Doente Terminal",
            2:"Severamente Frágil",
            3:"Muito Frágil",
            4:"Moderadamente Frágil",
            5:"Levemente Frágil",
            6:"Vulnerável",
            7:"Regular",
            8:"Ativo",
            9:"Muito Ativo",
        }

        # Criação do gráfico de barras empilhadas para fragilidades mês a mês
        fig_fragilidade = px.bar(
            fragilidade_por_mes_long,
            x = 'data_internamento',
            y = 'percentual',
            color = 'fragilidade',
            title = 'Fragilidade',
            labels = {'data_internamento':'Mês', 'percentual':'% de Pacientes', 'fragilidade':'Fragilidade'},
            barmode = 'stack',
            color_discrete_sequence = [cores_personalizadas [p] for p in fragilidades_possiveis]
        )

        # Atualizar layout
        fig_fragilidade.update_layout(
            xaxis_title = 'Mês',
            yaxis_title = '%',
            legend_title = 'Fragilidade',
            legend = dict(
                title = 'Fragilidade',
                itemsizing = 'constant',
                font = dict(size = 10),
                title_font = dict(size = 12),
            ),
        )

        # Ajustar o eixo y para variar de 0% a 100%
        fig_fragilidade.update_yaxes(range = [0, 100])

        # Formatar o texto das porcentagens dentro das barras
        fig_fragilidade.update_traces(
            texttemplate = '%{y:.2f}%',
            textposition = 'inside',
            hovertemplate = '<b>Fragilidade %{x}</b><br>%{y:.2f}%',
        )

        # Ajustar a legenda para exibir os nomes amigáveis
        fig_fragilidade.for_each_trace(lambda t:t.update(name = priority_labels [int(float(t.name))]))

        # Mostrar gráfico no Streamlit
        st.plotly_chart(fig_fragilidade)

        # Carregar os dados do arquivo CSV
        df = pd.read_csv('data_work.csv')

        # Converter a coluna 'data_internamento' para datetime, inferindo o formato
        df ['data_internamento'] = pd.to_datetime(df ['data_internamento'], errors = 'coerce',
                                                  infer_datetime_format = True)

        def grafico_taxa_ocupacao (df, uti_selecionada):
            # Filtrar o DataFrame com base na UTI selecionada
            df_filtrado = df [df ['uti_combined'] == uti_selecionada]

            if df_filtrado.empty:
                st.warning(f"Nenhum dado encontrado para a UTI: {uti_selecionada}")
                return

            # Número de leitos por UTI
            leitos_ativos = {
                "Santa Casa UTI1 CX A":9, "Santa Casa UTI CX B":9, "Santa Casa UTI 2":10, "Santa Casa UTI 3":10,
                "Santa Casa UTI 4":10,
                "IM UTI 5":10, "IM UTI 6":10,
                "Nações UTI":20, "Nações Neuro":20, "Nações UCO":20,
                "São Rafael":10,
                "São Lucas":10,
                "Vita Batel 1":11, "Vita Batel 2":12, "Vita Batel 3":12,
                "Ecoville":10, "Ecoville 2":10, "Ecoville UCO":11
            }

            # Mapear número de leitos para cada UTI
            df_filtrado ["leitos_ativos"] = df_filtrado ["uti_combined"].map(leitos_ativos)

            # Filtrar apenas UTIs com leitos ativos
            df_valid = df_filtrado [df_filtrado ["leitos_ativos"] > 0]

            # Agrupar por UTI e mês
            df_grouped = df_valid.groupby(
                [pd.Grouper(key = "data_internamento", freq = "M"), "uti_combined"]
            ).agg({
                "data_ajustada":"sum",  # Soma dos dias de internação
                "leitos_ativos":"mean"  # Número médio de leitos no mês
            }).reset_index()

            # Calcular a taxa de ocupação
            df_grouped ["taxa_ocupacao"] = (df_grouped ["data_ajustada"] / (df_grouped ["leitos_ativos"] * 30)) * 100

            # Verificar se há dados para o gráfico
            if df_grouped.empty:
                st.warning("Nenhum dado disponível para criar o gráfico de Taxa de Ocupação.")
                return

            # Criação do gráfico
            fig = go.Figure()

            # Adicionar linhas e valores para a UTI selecionada
            df_uti = df_grouped [df_grouped ["uti_combined"] == uti_selecionada]
            fig.add_trace(
                go.Scatter(
                    x = df_uti ["data_internamento"],
                    y = df_uti ["taxa_ocupacao"],
                    mode = "lines+markers+text",
                    name = uti_selecionada,
                    text = df_uti ["taxa_ocupacao"].round(2).astype(str) + "%",
                    textposition = "top center",
                    line = dict(color = "#257683"),
                )
            )

            # Layout do gráfico
            fig.update_layout(
                title = "Taxa de Ocupação dos Leitos (%)",
                xaxis_title = "Mês",
                yaxis_title = "Taxa de Ocupação (%)",
                xaxis = dict(tickformat = "%Y-%m"),
                yaxis = dict(range = [0, 110]),
                legend_title = "UTI",
                template = "plotly_white",
            )

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig)

        grafico_taxa_ocupacao(df, uti_selecionada)
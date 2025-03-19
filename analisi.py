import streamlit  as st 
import pandas as pd 
import numpy as np 
import plotly.graph_objects as go
#import datetime as dt



st.set_page_config(layout='wide')
sx,dx = st.columns([10,1])
with sx:
    st.title('Dashboard Qualità Galizio Torresi')
with dx:
    st.image('https://github.com/alebelluco/galizio/blob/main/Screenshot%202025-03-19%20alle%2017.56.33.png?raw=True')

f_size = 10
f_angle =-45

stile = {
        'colore_barre':'#A6A6A6',
        'colore_linea':'#CD3128',
        'name_bar':'NC',
        'name_cum':'cum_pct',
        'y_name': 'NC',
        'y2_name': 'pct_cumulativa',
        'tick_size':12,
        'angle':-45
    }

#595959
#D9D9D9 grigio chiaro

def pareto(df, label, value ,stile):
    '''
    - La funzione crea l'aggregazione dei valori per categoria, ordina decrescente e calcola la pct cumulativa
    - Fa il grafico
    - Label è la colonna con la categoria da raggruppare
    - Value è il valore, che viene SOMMATO
    
    '''
    df_work = df[[label, value]].groupby(by=label, as_index=False).sum()

    df_work = df_work.sort_values(by=value, ascending=False)
    df_work['pct'] = df_work[value] / df_work[value].sum()
    df_work['pct_cum'] = df_work['pct'].cumsum()
    df_work[label] = np.where(df_work.pct_cum > 0.95, 'Other', df_work[label])
    pareto = go.Figure()

    pareto.add_trace(go.Bar(
        x=df_work[label],
        y=df_work[value],
        name=stile['name_bar'],
        marker_color=stile['colore_barre']
    ))

    pareto.add_trace(go.Scatter(
        x=df_work[label],
        y=df_work['pct_cum'],
        yaxis='y2',
        name=stile['name_cum'],
        marker_color=stile['colore_linea']
        )
    )

    pareto.update_layout(
        showlegend=False,
        yaxis=dict(
            title=dict(text=stile['y_name'], font = dict(size=stile['tick_size'])),
            side="left",
            tickfont=dict(size=stile['tick_size'])
            
        ),
        yaxis2=dict(
            title=dict(text=stile['y2_name'], font = dict(size=stile['tick_size'])),
            side="right",
            range=[0, 1],
            overlaying="y",
            tickmode="sync",
            tickformat=".0%",
            tickfont=dict(size=stile['tick_size'])

        ),
        xaxis=dict(
            tickfont=dict(size=stile['tick_size']),
            tickangle=stile['angle']
        )
    )

    return pareto

def runchart(df_work, x, y ,stile):
    grap = go.Figure()

    grap.add_trace(go.Scatter(
        x=df_work[x],
        y=df_work[y],
        marker_color=stile['colore_linea']
        )
    )

    grap.update_layout(
        showlegend=False,
        yaxis=dict(
            title=dict(text='Scarto%', font = dict(size=stile['tick_size'])),
            side="left",
            tickformat=".0%",
            tickfont=dict(size=stile['tick_size'])
            
        ),
        yaxis2=dict(
            title=dict(text=stile['y2_name'], font = dict(size=stile['tick_size'])),
            side="right",
            range=[0, 1],
            overlaying="y",
            tickmode="sync",
            tickformat=".0%",
            tickfont=dict(size=stile['tick_size'])

        ),
        xaxis=dict(
            tickfont=dict(size=stile['tick_size']),
            tickangle=stile['angle']
        )
    )

    return grap

@st.cache_data
def upload(path_list):
    df_list = []
    for path in path_list:
        df = pd.read_excel(path)
        df_list.append(df)
    frame = pd.concat(df_list)
    return frame

path = st.sidebar.file_uploader('caricare excel scarti', accept_multiple_files=True)
if not path:
    st.stop()

df = upload(path)

path_prod = st.sidebar.file_uploader('caricare excel produzione', accept_multiple_files=True)
if not path_prod:
    st.stop()

df_prod = upload(path_prod)

df_prod['week'] = [data.date().isocalendar().week for data in df_prod['Data Reparto']]
df_prod['anno'] = [data.date().year for data in df_prod['Data Reparto']]
df_prod['week'] = np.where(df_prod.week < 10, '0' + df_prod.week.astype(str), df_prod.week)
df_prod['key'] = df_prod['anno'].astype(str)+'-W'+df_prod['week'].astype(str)

reparti = {
    "FINISSAGG.MANOVIA ESTERNA -SEC":'FINISSAGGIO',
         "FINISSAGGIO":'FINISSAGGIO',
         "FINISSAGGIO MANOVIA 1 (I+F)":'FINISSAGGIO',
         "MONTAGGIO MANOVIA ESTERNA -SEC":'MONTAGGIO',
         "MONTAGGIO MANOVIA 1 (I+F)":'MONTAGGIO',
         "MONTAGGIO (solo F)":'MONTAGGIO'
         }

df_prod['Descrizione Reparto'] = [reparti[reparto] for reparto in df_prod['Descrizione Reparto']]


df['week'] = [data.date().isocalendar().week for data in df['DataRegistrazione']]
df['anno'] = [data.date().year for data in df['DataRegistrazione']]
df['week'] = np.where(df.week < 10, '0' + df.week.astype(str), df.week)
df['key'] = df['anno'].astype(str)+'-W'+df['week'].astype(str)

#st.stop()

df['Marchio'] = df['Marchio'].fillna('Non dichiarato')
gate = st.selectbox('Reparto', options=['MONTAGGIO','FINISSAGGIO'])



df_prod = df_prod.rename(columns={'Data Reparto':'data'})
df = df.rename(columns={'DataRegistrazione':'data'})

df['data'] = [pd.Timestamp.date(data) for data in df.data]
df_prod['data'] = [pd.Timestamp.date(data) for data in df_prod.data]

tomaie = df[df['DescrizioneGate']=='ACCETTAZIONE TOMAIE']
df=df[df['DescrizioneGate']==gate]
df_prod = df_prod[df_prod['Descrizione Reparto']==gate]

date_range = st.slider('sleziona intervallo date', df_prod.data.min(), df_prod.data.max(), (df_prod.data.min(), df_prod.data.max()))
df_prod = df_prod[(df_prod.data > date_range[0]) & (df_prod.data < date_range[1]) ]
df = df[(df.data > date_range[0]) & (df.data < date_range[1]) ]
tomaie = tomaie[(tomaie.data > date_range[0]) & (tomaie.data < date_range[1]) ]

#prod_gr = df_prod[['anno','week','Quantità']].groupby(by=['anno','week'], as_index=False).sum()
prod_gr = df_prod[['key','Quantità']].groupby(by='key', as_index=False).sum()

#scarti_gr = df[['anno','week','NC']].groupby(by='key', as_index=False).sum()
scarti_gr = df[['key','NC']].groupby(by='key', as_index=False).sum()

prod_gr = prod_gr.merge(scarti_gr, how='left', left_on='key', right_on='key')
prod_gr = prod_gr.fillna(0)

prod_gr['scarto%'] = prod_gr['NC']/prod_gr['Quantità']


st.divider()
st.subheader('Andamento percentuale di scarto')

a,b,c,d = st.columns([1,1,1,4])

a.metric(label='Paia prodotte', value= prod_gr['Quantità'].sum(), border=True)
b.metric(label='Scarti', value= prod_gr['NC'].sum(), border=True)
c.metric(label='Scarto%', value='{:0.2f}%'.format(prod_gr.NC.sum() / prod_gr['Quantità'].sum()*100), border=True)

andamento = runchart(prod_gr, 'key','scarto%', stile)
st.plotly_chart(andamento)


st.divider()
st.subheader('Pareto causali di scarto nel periodo selezionato')
par = pareto(df, 'DescrizioneVerifica', 'NC', stile)
par.update_layout(width=1600, height=800)
st.plotly_chart(par, use_container_width=False)

st.divider()
st.subheader('Focus Tomaie | Pareto causali di scarto nel periodo selezionato')
cause = pareto(tomaie, 'DescrizioneVerifica', 'NC', stile)
cause.update_layout(width=1600, height=800)
st.plotly_chart(cause, use_container_width=False)

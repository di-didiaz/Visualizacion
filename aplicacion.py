import streamlit as st
import pandas as pd
import altair as alt
from streamlit_option_menu import option_menu
import joblib
import numpy as np
import plotly.express as px
import json


# Crear pagina
st.set_page_config(page_title="Conoce y predice la Salud de España", page_icon="⚕️", layout="wide")

# Subir datos- metodo tomado de app de prueba de Streamlit
@st.cache_data
def load_data():
    df = pd.read_csv("datos/df_final.csv", encoding= "latin-1")
    return df

 #Se uso como referencia  https://www.youtube.com/watch?v=7E3yxq-P-a8
with st.sidebar:
    selected = option_menu(menu_title="Menú", options=["Resultados de la encuesta", "Predicción personalizada"], icons=["clipboard-pulse", "stars"], 
                           menu_icon="body-text",default_index=0)
###########################################################################################################
# Pagina de resutlados iniciales

if selected == "Resultados de la encuesta":

    df= load_data()
    st.title("Análisis y visualización de la Encuesta de Salud de España 2023")
    st.write("""Esta sección te permite visualizar datos de la
             [Encuesta de Salud de España 2023](https://www.sanidad.gob.es/estadEstudios/estadisticas/encuestaSaludEspana/home.htm).""")
    st.text("Algunas métricas relevantes:")

    lac_prom= df['Lacteos_frec'].mean(skipna=True)
    hsentado_prom=df['Sedentarismo%_horas'].mean(skipna=True)
    porc_diabetes=df['Diabetes_bin'].mean(skipna=True)*100
    
    # Se usa como referencia https://www.corecode.school/en/blog/python-streamlit

    col1,col2,col3=st.columns(3)

    col1.metric(label="Consumo de carne promedio", value=f"{lac_prom:.2f}")
    col2.metric(label="Promedio de horas sentados/dia", value=f"{hsentado_prom:.2f}")
    col3.metric(label="Porcentaje de personas diabeticas", value=f"{porc_diabetes:.2f}%")

    st.markdown("---------------------------")

 #####################################################################
 # Tabs   
  
    tab1, tab2, tab3 = st.tabs(["Composición Física", "Salud percibida", "Determinantes de Salud"]) # Referencia de https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart

###### Tab 1 ####### 
    with tab1:

        st.header("Composición fisica por comunidad autonoma")
        st.caption(" El IMC es la medida de XYZ importante porque XYZ") 

        df_mapa= df.groupby("Comunidad Autonoma").agg(IMC_prom=('IMC','mean'),peso_prom=('Peso','mean'), edad_prom= ('Edad','mean'), n=('IMC','count')).reset_index()
        
        df_prop = (df.groupby(["Comunidad Autonoma", "Salud_Percibida"]).size().reset_index(name="count"))

        # tomado de https://discuss.streamlit.io/t/interactive-maps/82782
        with open("datos/spain-communities.geojson") as r:
            geoson_mapa= json.load(r)
        

        mapaccaa= px.choropleth(df_mapa, geojson= geoson_mapa, locations="Comunidad Autonoma",
                                featureidkey="properties.name", color="IMC_prom",hover_name="Comunidad Autonoma", hover_data={'IMC_prom', 'peso_prom', 'edad_prom'}, labels={'IMC_prom': 'Promedio IMC'},
                                title="IMC medio por comunidad autonoma. Haz click y zoom para ver detalles por comunidad", color_continuous_scale="Viridis")
        mapaccaa.update_geos(fitbounds="locations", visible=False)
        mapaccaa.update_layout(margin={'r':0,'l':0, 'b':0,'t':50})
        select=st.plotly_chart(mapaccaa,width='content')

        st.markdown("----------------")

        st.subheader("Mas detalles:") 
        com_selec=st.selectbox("Selecciona o busca una comunidad de tu interes:", options=[""]+ df['Comunidad Autonoma'].dropna().unique().tolist())
        if com_selec:
            ca_elegida= df[df["Comunidad Autonoma"]==com_selec]
            tabla_ca=ca_elegida.groupby('Sexo').agg(sexo=('Sexo','count'), peso_ca= ('Peso', 'mean'), imc_ca= ('IMC','mean')).reset_index()
            st.subheader(f"Resultados de {com_selec}")
            st.dataframe(tabla_ca) #https://www.youtube.com/watch?v=7E3yxq-P-a8

        
 ###### Tab 2 #######       
    with tab2:


        st.subheader("Salud percibida y cronicidad por sexo")
        st.caption("Los encuestados podian reportar el sexo con el que se identificaban y el estado de salud como 'Muy bueno', 'Bueno','Regular','Malo'y 'Muy malo'")
        salud_per=df[df['Salud_Percibida'].notna()]
        
        mb_bueno= salud_per['Salud_Percibida'].str.contains('Bueno', case=False, na=False)
        buenos= salud_per.groupby('Sexo').apply(lambda x:mb_bueno.loc[x.index].mean()*100)
       
        cronicidad=df[df['Cronicidad_bin'].notna()]
        cont_cronicidad= cronicidad.groupby('Sexo')['Cronicidad_bin'].mean()*100

        sexos= list(buenos.index)
        st.write("Buena salud percibida por sexos reportados")
        col21, col22= st.columns(2)
        
        col21.metric(label=f"{sexos[0]}", value= f"{buenos.loc[sexos[0]]:.2f}%" )
        col22.metric(f"{sexos[1]}",f"{buenos.loc[sexos[1]]:.2f}%" )

        st.caption("Los encuestados respondieron si padecian de alguna enfermedad crónica")

        col23, col24= st.columns(2)
            
        col23.metric(f"{sexos[0]}",f"{cont_cronicidad.loc[sexos[0]]:.2f}%" )
        col24.metric(f"{sexos[1]}",f"{cont_cronicidad.loc[sexos[1]]:.2f}%" )
                                                                
        
       

 ###### Tab 3 #######   
     
    with tab3:
        st.header("Determinantes de salud: Dieta y actividad física")
        st.caption("Los determinantes de salud son XYZ")

        st.subheader("Frecuencia de alimentación")
        

        carne_prom= df['Carne_frec'].mean()
        refrescos_prom= df['Refrescos_frec'].mean()
        embutidos_prom= df['Embutidos_frec'].mean()
        lacteos_prom= df['Lacteos_frec'].mean()
        verduras_prom= df['Verduras_frec'].mean()
        st.markdown("----------")
        col31, col32, col33, col34, col35= st.columns(5)

        col31.metric(label="Carne", value=f"{lac_prom:.2f}")
        col32.metric(label="Refrescos", value= f"{refrescos_prom:.2f}")
        col33.metric(label= "Embutidos",value=f"{embutidos_prom:.2f}")
        col34.metric(label= "Lacteos", value= f"{lacteos_prom:.2f}")
        col35.metric(label= "Verduras", value= f"{verduras_prom:.2f}")

        st.caption("Promedio de veces a la semana")

        st.markdown("----------")

        lista_frec= ["Carne", "Refrescos", "Embutidos", "Lacteos", "Verduras"]
        frec_lista= {"Carne":"Carne_frec","Refrescos":"Refrescos_frec","Embutidos":"Embutidos_frec", "Lacteos":"Lacteos_frec", "Verduras":"Verduras_frec"}

        opcion= st.selectbox("Selecciona un alimento", lista_frec)
        col_df= frec_lista[opcion]
        lista_colores={"Carne": "#ECDAB2","Refrescos": "#DDBFB3","Embutidos": "#9999C9","Lacteos": "#D8D8EA","Verduras": "#000078"}
        colores=lista_colores[opcion]
        frec_hst= alt.Chart(df).mark_bar(color=colores).encode(alt.X(col_df,bin=alt.Bin(maxbins=5), title= "Frecuencia de consumo semanal de "), alt.Y("count()", title= "Encuestados")).properties(width=600, height=400, title= "Consumo de "+opcion).interactive()
        st.altair_chart(frec_hst,width='content')

        st.markdown("----------")

        st.subheader("Horas sentados al día")
        # Ver https://www.youtube.com/watch?v=rxWkIn1EZnM
        # https://altair-viz.github.io/gallery/radial_chart.html
        colores_sed=["#B6B8BEDA","#A9B3E0","#6679D8","#1724A0", "#030342"]
        df["rangos"]= pd.cut(df["Sedentarismo%_horas"], bins=[0,2,4,6,8,12,24], labels=["0-2 horas","2 a 4 horas","4-6 horas","6 a 8 horas","8 a 12 horas","Mas de 12 hoaas"],include_lowest=True)
        sedentarismo= df["rangos"].value_counts().reset_index()
        sedentarismo.columns= ["Rangos", "Personas"] 

        sedentarismo_pie= alt.Chart(sedentarismo).mark_arc().encode(theta= alt.Theta("Personas", stack= True), color= alt.Color("Rangos:N", scale=alt.Scale(range=colores_sed)), tooltip=["Rangos","Personas"]).properties(width=600, height=600, title= "Porcentaje de Horas sentados al dia").interactive()

        st.altair_chart(sedentarismo_pie,width='content')                                                            

                                                                    
        

###########################################################################################################

# Sección Predecir percepción de salud
if selected == "Predicción personalizada":
    st.title("Mis riesgos de salud")
    st.subheader("Introduce tus datos para predecir si tienes riesgo de padecer de Hipertension, Diabetes y Colesterol")
    st.caption("Recuerda: Estas predicciones no son diagnosticos de salud.")

    df = load_data()
    diabetes= joblib.load("datos/diabetes.joblib")
    hipertension= joblib.load("datos/hipertension.joblib")
    colesterol= joblib.load("datos/colesterol.joblib")
    preprocesador= joblib.load("datos/preprocesador_slt.joblib")

# Entradas de los usuarions
    st.markdown("---------------------------")
    edad= st.slider("Selecciona tu edad", 15, 100, 35, help="Desliza el punto hasta llegar a tu edad")
    altura= st.slider("Introduce tu altura estimada en centímetros", 80, 165, 210,help="Desliza el punto hasta llegar a tu altura")  
    peso= st.number_input("Introduce tu peso estimado en kilos", 35, 200, 70, help="Usa un estimado o tu última medición")
    imc= peso/(altura**2)
    estudios= st.selectbox("Selecciona tu nivel de estudios",["Enseñanzas profesionales de grado medio o equivalentes", "Educación Primaria completa", "Estudios de Bachillerato", "Primera etapa de Enseñanza Secundaria, con o sin título (2º ESO aprobado, EGB, Bachillerato Elemental)",
                                                   "Enseñanzas profesionales de grado superior o equivalentes", "Estudios universitarios o equivalentes"])
    sedentarismo=st.number_input("Horas que pasas sentadx en un dia",min_value=0, max_value=24, value=4)
    Refrescos_frec= st.selectbox("Numero de refrescos que bebes normalmente en una la semana. Si bebes más de 10, elije 10",[0,0.5, 1.5, 3,5,7,10], index=3, help="Las medidas intermedias significan que bebes un refresco y medio")

    if st.button("Predecir ahora!"):
        df_entrada= pd.DataFrame([{"Edad": edad, 'IMC': imc,"Estudios": estudios, "Refrescos_frec": Refrescos_frec,  "Sedentarismo%_horas": sedentarismo, "Peso": peso, "Altura": altura}])

        
        diabetes_pred= diabetes.predict(df_entrada)[0]
        diabetes_prob= diabetes.predict_proba(df_entrada)[0].max()

        hipertension_pred= hipertension.predict(df_entrada)[0]
        hipertension_prob= hipertension.predict_proba(df_entrada)[0].max()

        colesterol_pred= colesterol.predict(df_entrada)[0]
        colesterol_prob= colesterol.predict_proba(df_entrada)[0].max()

        noms= {0: "Genial, no tienes riesgo",1: "Hay riesgo, revisa las recomendaciones abajo"}
        diabetes_prediccion= noms[int(diabetes_pred)]
        hipertension_prediccion= noms[int(hipertension_pred)]
        colesterol_prediccion= noms[int(colesterol_pred)]
        
        st.subheader("Tus resultados")
        
        st.text(diabetes_prediccion)
        st.text(hipertension_prediccion)
        st.text(colesterol_prediccion)
        

